import hashlib
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import app
from cryptography.fernet import Fernet

from database_backup import create_backup_bundle, restore_backup_bundle
from database_runtime import DatabaseRuntime
from original_file_reconciliation import TenantDatabase, reconcile_original_file_storage
from tools.firm_offboarding_preflight import inspect_firm_offboarding
from original_file_storage import LocalPrivateObjectStore
from tools.purge_approved_original_files import purge_approved_requests



class _PurgeStateMachineMissingObject(Exception):
    response = {"Error": {"Code": "NoSuchKey"}, "ResponseMetadata": {"HTTPStatusCode": 404}}


class _PurgeStateMachineFakeS3:
    def __init__(self):
        self.objects = {}

    def head_object(self, *, Bucket, Key):
        item = self.objects.get((Bucket, Key))
        if item is None:
            raise _PurgeStateMachineMissingObject(Key)
        return {
            "ContentLength": len(item["Body"]),
            "Metadata": dict(item["Metadata"]),
            "ServerSideEncryption": "aws:kms",
            "SSEKMSKeyId": "test-kms-key",
            "ETag": '"synthetic-etag"',
        }

    def get_object(self, *, Bucket, Key):
        import io
        item = self.objects.get((Bucket, Key))
        if item is None:
            raise _PurgeStateMachineMissingObject(Key)
        return {
            "Body": io.BytesIO(item["Body"]),
            "ServerSideEncryption": "aws:kms",
            "SSEKMSKeyId": "test-kms-key",
        }

    def list_objects_v2(self, *, Bucket, Prefix, **kwargs):
        return {
            "Contents": [
                {"Key": key} for (bucket, key) in self.objects
                if bucket == Bucket and key.startswith(Prefix)
            ],
            "IsTruncated": False,
        }

    def get_bucket_versioning(self, *, Bucket):
        return {}

    def delete_object(self, *, Bucket, Key):
        self.objects.pop((Bucket, Key), None)
        return {}


class PurgeApprovedOriginalFilesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.control_path = self.root / "control.sqlite3"
        self.tenant_root = self.root / "tenants"
        self.corpus_path = self.root / "corpus.sqlite3"
        self.object_root = self.root / "objects"
        self.object_root.mkdir()
        self.backup_dir = self.root / "backups"
        self.backup_dir.mkdir()
        self.runtime = DatabaseRuntime(
            self.control_path, self.tenant_root, self.corpus_path
        )
        self.runtime.initialize()
        self.firm_id, self.tenant_path = self.runtime.provision_firm("Purge Workflow Firm")
        self.requester_id = self.runtime.create_initial_firm_owner(
            self.firm_id, "Deletion Requester", "deletion-requester@example.test", "test-password-hash"
        )
        self.approver_id = self.runtime.create_global_identity(
            "Deletion Approver", "deletion-approver@example.test", "test-password-hash"
        )
        self.runtime.create_firm_membership(self.approver_id, self.firm_id, "admin")
        self.operator_id = self.runtime.create_global_identity(
            "Purge Operator", "purge-operator@example.test", "test-password-hash"
        )
        control = self.runtime.control_connection()
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,'platform_admin')",
            (self.operator_id,),
        )
        control.commit()
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def tearDown(self):
        try:
            self.runtime.close_current_thread()
        except Exception:
            pass
        self.temp.cleanup()

    def _create_approved_request(self):
        import app

        context = self.runtime.resolve_context(self.requester_id, self.firm_id)
        firm_db = self.runtime.firm_connection(context)
        case_id = firm_db.execute(
            "INSERT INTO cases(title,firm_id) VALUES('Purge Workflow Matter',?)",
            (self.firm_id,),
        ).lastrowid
        original = b"approved purge original bytes"
        _, document_id = app.save_doc(
            firm_db,
            {"id": self.requester_id, "firm_id": self.firm_id, "name": "Deletion Requester"},
            case_id,
            "purge-original.txt",
            "Extracted text for the original document",
            content_hash=hashlib.sha256(original).hexdigest(),
            content_type="text/plain",
            byte_size=len(original),
        )
        store = LocalPrivateObjectStore(self.object_root)
        staged = store.stage(self.firm_id, original)
        store.finalize(self.firm_id, staged.object_id)
        firm_db.execute(
            "INSERT INTO original_file_objects("
            "object_id,document_id,firm_id,storage_backend,sha256,byte_size,content_type,state"
            ") VALUES(?,?,?,'local',?,?,?,'ready')",
            (
                staged.object_id, document_id, self.firm_id, staged.sha256,
                staged.byte_size, "text/plain",
            ),
        )
        cursor = firm_db.execute(
            "INSERT INTO original_file_deletion_requests("
            "object_id,document_id,firm_id,requested_by_user_id,request_reason"
            ") VALUES(?,?,?,?,?)",
            (
                staged.object_id, document_id, self.firm_id, self.requester_id,
                "Approved export completed; remove duplicate original",
            ),
        )
        request_id = int(cursor.lastrowid)
        firm_db.execute(
            "UPDATE original_file_deletion_requests SET status='approved',"
            "approved_by_user_id=?,approved_at=datetime('now'),"
            "approval_reason='Second administrator approved after export review' "
            "WHERE id=?",
            (self.approver_id, request_id),
        )
        firm_db.commit()
        return staged, request_id

    def test_interrupted_purge_after_unlink_is_manual_review_and_never_claims_success(self):
        staged, request_id = self._create_approved_request()
        self.runtime.disable_firm(self.firm_id)
        control = self.runtime.control_connection()
        control.execute(
            "UPDATE firm_memberships SET status='suspended',updated_at=datetime('now') "
            "WHERE firm_id=?",
            (self.firm_id,),
        )
        control.commit()
        self.runtime.close_current_thread()

        original_delete = LocalPrivateObjectStore.delete

        def unlink_then_interrupt(store, firm_id, object_id):
            removed = original_delete(store, firm_id, object_id)
            self.assertTrue(removed)
            raise RuntimeError("simulated interruption after filesystem unlink")

        with patch.object(LocalPrivateObjectStore, "delete", new=unlink_then_interrupt):
            result = purge_approved_requests(
                self.tenant_path,
                self.object_root,
                self.firm_id,
                self.operator_id,
                apply=True,
                control_database_path=self.control_path,
                tenant_root=self.tenant_root,
                corpus_database_path=self.corpus_path,
            )

        self.assertEqual(result["purged_count"], 0)
        self.assertEqual(result["results"][0]["status"], "manual_review_required")
        tenant = sqlite3.connect(self.tenant_path)
        try:
            request = tenant.execute(
                "SELECT status FROM original_file_deletion_requests WHERE id=?",
                (request_id,),
            ).fetchone()
            metadata = tenant.execute(
                "SELECT purged_at FROM original_file_objects WHERE object_id=?",
                (staged.object_id,),
            ).fetchone()
            self.assertEqual(request[0], "approved")
            self.assertIsNone(metadata[0])
        finally:
            tenant.close()
        self.assertFalse(
            (self.object_root / f"firm-{self.firm_id}" / f"{staged.object_id}.blob").exists()
        )
        preflight = inspect_firm_offboarding(
            self.control_path, self.tenant_root, self.corpus_path,
            self.object_root, self.firm_id,
        )
        self.assertFalse(preflight["purge_preflight_clear"])
        self.assertIn("missing_object", {item["code"] for item in preflight["findings"]})

    def test_purge_operation_rejects_production_mode_before_touching_storage(self):
        with patch.dict("os.environ", {
            "COPILOT_ENV": "production",
            "COPILOT_OBJECT_STORAGE_BACKEND": "local",
        }):
            with self.assertRaisesRegex(RuntimeError, "disabled in production"):
                purge_approved_requests(
                    self.tenant_path,
                    self.object_root,
                    self.firm_id,
                    self.operator_id,
                    apply=True,
                    control_database_path=self.control_path,
                    tenant_root=self.tenant_root,
                    corpus_database_path=self.corpus_path,
                )

    def test_purge_operation_rejects_active_firm_even_when_request_is_approved(self):
        staged, _ = self._create_approved_request()
        with self.assertRaisesRegex(RuntimeError, "Firm must be disabled"):
            purge_approved_requests(
                self.tenant_path,
                self.object_root,
                self.firm_id,
                self.operator_id,
                apply=True,
                control_database_path=self.control_path,
                tenant_root=self.tenant_root,
                corpus_database_path=self.corpus_path,
            )
        self.assertTrue(LocalPrivateObjectStore(self.object_root).verify(
            self.firm_id, staged.object_id,
            expected_sha256=staged.sha256, expected_size=staged.byte_size,
        ))

    def test_purge_operation_rejects_operator_without_platform_admin_role(self):
        staged, _ = self._create_approved_request()
        self.runtime.disable_firm(self.firm_id)
        control = self.runtime.control_connection()
        control.execute(
            "UPDATE firm_memberships SET status='suspended',updated_at=datetime('now') "
            "WHERE firm_id=?",
            (self.firm_id,),
        )
        control.commit()
        self.runtime.close_current_thread()
        with self.assertRaisesRegex(RuntimeError, "active platform administrator"):
            purge_approved_requests(
                self.tenant_path,
                self.object_root,
                self.firm_id,
                self.requester_id,
                apply=True,
                control_database_path=self.control_path,
                tenant_root=self.tenant_root,
                corpus_database_path=self.corpus_path,
            )
        self.assertTrue(LocalPrivateObjectStore(self.object_root).verify(
            self.firm_id, staged.object_id,
            expected_sha256=staged.sha256, expected_size=staged.byte_size,
        ))

    def test_purge_retains_tombstone_and_immutable_audit_through_backup_restore(self):
        staged, request_id = self._create_approved_request()
        self.runtime.disable_firm(self.firm_id)
        control = self.runtime.control_connection()
        control.execute(
            "UPDATE firm_memberships SET status='suspended',updated_at=datetime('now') "
            "WHERE firm_id=?",
            (self.firm_id,),
        )
        control.commit()
        self.runtime.close_current_thread()

        result = purge_approved_requests(
            self.tenant_path,
            self.object_root,
            self.firm_id,
            self.operator_id,
            apply=True,
            control_database_path=self.control_path,
            tenant_root=self.tenant_root,
            corpus_database_path=self.corpus_path,
        )

        self.assertEqual(result["purged_count"], 1, result["results"])
        self.assertEqual(result["results"][0]["status"], "purged")
        self.assertFalse(
            (self.object_root / f"firm-{self.firm_id}" / f"{staged.object_id}.blob").exists()
        )

        tenant = sqlite3.connect(self.tenant_path)
        tenant.row_factory = sqlite3.Row
        try:
            metadata = tenant.execute(
                "SELECT purged_at,purged_by_user_id,purge_reason,legal_hold "
                "FROM original_file_objects WHERE object_id=?",
                (staged.object_id,),
            ).fetchone()
            self.assertIsNotNone(metadata["purged_at"])
            self.assertEqual(metadata["purged_by_user_id"], self.operator_id)
            self.assertIn("Approved export completed", metadata["purge_reason"])
            self.assertEqual(metadata["legal_hold"], 0)
            request = tenant.execute(
                "SELECT status,completed_by_user_id FROM original_file_deletion_requests WHERE id=?",
                (request_id,),
            ).fetchone()
            self.assertEqual(request["status"], "completed")
            self.assertEqual(request["completed_by_user_id"], self.operator_id)
            events = tenant.execute(
                "SELECT action,actor_user_id FROM original_file_deletion_events "
                "WHERE request_id=? ORDER BY id",
                (request_id,),
            ).fetchall()
            self.assertEqual([event["action"] for event in events], [
                "requested", "approved", "purging", "completed"
            ])
            self.assertEqual(events[-1]["actor_user_id"], self.operator_id)
            with self.assertRaises(sqlite3.IntegrityError):
                tenant.execute(
                    "UPDATE original_file_deletion_events SET reason='rewrite' WHERE request_id=?",
                    (request_id,),
                )
            tenant.rollback()
        finally:
            tenant.close()

        report = reconcile_original_file_storage(
            self.object_root, [TenantDatabase(self.firm_id, self.tenant_path)]
        )
        self.assertTrue(report.clean, report.findings)

        bundle = create_backup_bundle(
            self.runtime, self.cipher, self.backup_dir,
            quiesced=True, object_storage_root=self.object_root,
        )
        restored = restore_backup_bundle(bundle, self.cipher, self.root / "restored")
        self.assertFalse(
            (restored["object_storage"] / f"firm-{self.firm_id}" / f"{staged.object_id}.blob").exists()
        )
        restored_tenant = next((restored["tenant_root"]).glob("tenant-*.sqlite3"))
        connection = sqlite3.connect(restored_tenant)
        try:
            tombstone = connection.execute(
                "SELECT purged_at,purged_by_user_id FROM original_file_objects WHERE object_id=?",
                (staged.object_id,),
            ).fetchone()
            self.assertIsNotNone(tombstone[0])
            self.assertEqual(tombstone[1], self.operator_id)
        finally:
            connection.close()


    def _prepare_s3_purge(self, *, legal_hold=False):
        import io
        from s3_original_file_storage import S3PrivateObjectStore

        staged, request_id = self._create_approved_request()
        client = _PurgeStateMachineFakeS3()
        bucket = "purge-state-machine-test"
        key = f"firms/{self.firm_id}/originals/{staged.object_id}.blob"
        payload = b"approved purge original bytes"
        client.objects[(bucket, key)] = {
            "Body": payload,
            "Metadata": {"sha256": staged.sha256, "firm-id": str(self.firm_id)},
        }
        tenant = sqlite3.connect(self.tenant_path)
        try:
            tenant.execute(
                "UPDATE original_file_objects SET storage_backend='s3',legal_hold=? WHERE object_id=?",
                (1 if legal_hold else 0, staged.object_id),
            )
            tenant.commit()
        finally:
            tenant.close()
        local_path = self.object_root / f"firm-{self.firm_id}" / f"{staged.object_id}.blob"
        if local_path.exists():
            local_path.unlink()
        store = S3PrivateObjectStore(client, bucket=bucket, kms_key_id="test-kms-key")
        self.runtime.disable_firm(self.firm_id)
        control = self.runtime.control_connection()
        control.execute(
            "UPDATE firm_memberships SET status='suspended',updated_at=datetime('now') WHERE firm_id=?",
            (self.firm_id,),
        )
        control.commit()
        self.runtime.close_current_thread()
        return staged, request_id, store, client, bucket, key

    def test_s3_state_machine_refuses_legal_hold_without_deleting_object(self):
        staged, request_id, store, client, bucket, key = self._prepare_s3_purge(legal_hold=True)
        with patch.dict("os.environ", {
            "COPILOT_OBJECT_STORAGE_BACKEND": "s3",
            "COPILOT_ENV": "test",
        }):
            with patch("tools.purge_approved_original_files._validate_s3_apply_authorization"):
                with self.assertRaisesRegex(RuntimeError, "offboarding preflight findings"):
                    purge_approved_requests(
                        self.tenant_path, None, self.firm_id, self.operator_id,
                        apply=True, control_database_path=self.control_path,
                        tenant_root=self.tenant_root, corpus_database_path=self.corpus_path,
                        object_store=store, quiesced=True,
                    )
        self.assertIn((bucket, key), client.objects)
        tenant = sqlite3.connect(self.tenant_path)
        try:
            request = tenant.execute(
                "SELECT status FROM original_file_deletion_requests WHERE id=?", (request_id,)
            ).fetchone()
            metadata = tenant.execute(
                "SELECT legal_hold,purged_at FROM original_file_objects WHERE object_id=?",
                (staged.object_id,),
            ).fetchone()
            self.assertEqual(request[0], "approved")
            self.assertEqual(metadata, (1, None))
        finally:
            tenant.close()

    def test_s3_state_machine_commit_failure_records_manual_review_after_delete(self):
        staged, request_id, store, client, bucket, key = self._prepare_s3_purge()
        original_connect = sqlite3.connect

        class CommitFailureConnection:
            def __init__(self, connection):
                self._connection = connection

            def __setattr__(self, name, value):
                if name == "_connection":
                    object.__setattr__(self, name, value)
                else:
                    setattr(self._connection, name, value)

            def commit(self):
                raise sqlite3.OperationalError("injected tenant commit failure")

            def __getattr__(self, name):
                return getattr(self._connection, name)

        def connect_with_commit_failure(database, *args, **kwargs):
            try:
                is_tenant = Path(database).resolve() == self.tenant_path.resolve()
            except (TypeError, ValueError):
                is_tenant = False
            connection = original_connect(database, *args, **kwargs)
            return CommitFailureConnection(connection) if is_tenant else connection

        with patch.dict("os.environ", {
            "COPILOT_OBJECT_STORAGE_BACKEND": "s3",
            "COPILOT_ENV": "test",
        }):
            with patch("tools.purge_approved_original_files._validate_s3_apply_authorization"):
                with patch("tools.purge_approved_original_files.sqlite3.connect", side_effect=connect_with_commit_failure):
                    result = purge_approved_requests(
                        self.tenant_path, None, self.firm_id, self.operator_id,
                        apply=True, control_database_path=self.control_path,
                        tenant_root=self.tenant_root, corpus_database_path=self.corpus_path,
                        object_store=store, quiesced=True,
                    )
        self.assertEqual(result["purged_count"], 0)
        self.assertEqual(result["results"][0]["status"], "manual_review_required")
        self.assertNotIn((bucket, key), client.objects)
        tenant = original_connect(self.tenant_path)
        try:
            request = tenant.execute(
                "SELECT status FROM original_file_deletion_requests WHERE id=?", (request_id,)
            ).fetchone()
            metadata = tenant.execute(
                "SELECT purged_at FROM original_file_objects WHERE object_id=?", (staged.object_id,)
            ).fetchone()
            self.assertEqual(request[0], "approved")
            self.assertIsNone(metadata[0])
        finally:
            tenant.close()


    def test_s3_state_machine_rejects_wrong_firm_database_binding(self):
        staged, _, store, client, bucket, key = self._prepare_s3_purge()
        wrong_firm_id, _ = self.runtime.provision_firm("Wrong Firm Purge Target")
        self.runtime.disable_firm(wrong_firm_id)
        self.runtime.close_current_thread()
        with patch.dict("os.environ", {
            "COPILOT_OBJECT_STORAGE_BACKEND": "s3",
            "COPILOT_ENV": "test",
        }):
            with patch("tools.purge_approved_original_files._validate_s3_apply_authorization"):
                with self.assertRaisesRegex(RuntimeError, "does not match the trusted catalog"):
                    purge_approved_requests(
                        self.tenant_path, None, wrong_firm_id, self.operator_id,
                        apply=True, control_database_path=self.control_path,
                        tenant_root=self.tenant_root, corpus_database_path=self.corpus_path,
                        object_store=store, quiesced=True,
                    )
        self.assertIn((bucket, key), client.objects)
        tenant = sqlite3.connect(self.tenant_path)
        try:
            request = tenant.execute(
                "SELECT status FROM original_file_deletion_requests WHERE object_id=?",
                (staged.object_id,),
            ).fetchone()
            self.assertEqual(request[0], "approved")
        finally:
            tenant.close()


if __name__ == "__main__":
    unittest.main()
