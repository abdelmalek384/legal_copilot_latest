import hashlib
import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from original_file_storage import ObjectStorageError
from s3_original_file_storage import S3PrivateObjectStore
from tools.verify_s3_original_file_roundtrip import build_acceptance_report, run_s3_roundtrip
from original_file_reconciliation import TenantDatabase
from original_file_s3_reconciliation import reconcile_s3_original_file_storage
from database_backup import _copy_s3_original_objects, _scan_s3_original_object_inventory


class FakeS3Error(RuntimeError):
    def __init__(self, code):
        super().__init__(code)
        self.response = {"Error": {"Code": code}, "ResponseMetadata": {"HTTPStatusCode": 404 if code == "NoSuchKey" else 500}}


class FakeKMSClient:
    def describe_key(self, *, KeyId):
        if KeyId not in {"alias/legal-files", "key-1234", "arn:aws:kms:us-east-1:123456789012:key/key-1234"}:
            raise RuntimeError("unknown KMS key")
        return {"KeyMetadata": {
            "KeyId": "key-1234",
            "Arn": "arn:aws:kms:us-east-1:123456789012:key/key-1234",
        }}


class FakeS3Client:
    CANONICAL_KMS_ARN = "arn:aws:kms:us-east-1:123456789012:key/key-1234"

    def __init__(self):
        self.objects = {}
        self.calls = []
        self.copy_kms_key_id = self.CANONICAL_KMS_ARN
        self.corrupt_copy_body = False
        self.versioning_status = None
        self.versioning_response = None
        self.fail_delete = False
        self.mutate_before_conditional_delete = False
        self.omit_head_etag = False

    def _read(self, bucket, key):
        try:
            return self.objects[(bucket, key)]
        except KeyError as exc:
            raise FakeS3Error("NoSuchKey") from exc

    def put_object(self, **kwargs):
        self.calls.append(("put_object", kwargs.copy()))
        key = (kwargs["Bucket"], kwargs["Key"])
        if kwargs.get("IfNoneMatch") == "*" and key in self.objects:
            raise RuntimeError("conditional create failed")
        data = kwargs["Body"]
        self.objects[key] = {
            "Body": bytes(data),
            "Metadata": dict(kwargs.get("Metadata", {})),
            "ETag": '"' + hashlib.md5(data).hexdigest() + '"',
            "ServerSideEncryption": kwargs.get("ServerSideEncryption"),
            "SSEKMSKeyId": self.CANONICAL_KMS_ARN,
        }
        return {}

    def head_object(self, **kwargs):
        value = self._read(kwargs["Bucket"], kwargs["Key"])
        result = {
            "ContentLength": len(value["Body"]),
            "Metadata": value["Metadata"],
            "ServerSideEncryption": value.get("ServerSideEncryption"),
            "SSEKMSKeyId": value.get("SSEKMSKeyId"),
        }
        if not self.omit_head_etag:
            result["ETag"] = value["ETag"]
        return result

    def copy_object(self, **kwargs):
        self.calls.append(("copy_object", kwargs.copy()))
        destination = (kwargs["Bucket"], kwargs["Key"])
        source = (kwargs["CopySource"]["Bucket"], kwargs["CopySource"]["Key"])
        if kwargs.get("IfNoneMatch") == "*" and destination in self.objects:
            raise RuntimeError("conditional copy failed")
        value = self._read(*source)
        if value["ETag"] != kwargs.get("CopySourceIfMatch"):
            raise RuntimeError("source changed")
        self.objects[destination] = {
            **value,
            "ServerSideEncryption": kwargs.get("ServerSideEncryption"),
            "SSEKMSKeyId": self.copy_kms_key_id,
        }
        if self.corrupt_copy_body:
            self.objects[destination]["Body"] = b"corrupted destination bytes"
        return {}

    def get_object(self, **kwargs):
        value = self._read(kwargs["Bucket"], kwargs["Key"])
        return {
            "Body": io.BytesIO(value["Body"]),
            "ServerSideEncryption": value.get("ServerSideEncryption"),
            "SSEKMSKeyId": value.get("SSEKMSKeyId"),
        }

    def get_bucket_versioning(self, **kwargs):
        if self.versioning_response is not None:
            return dict(self.versioning_response)
        return {"Status": self.versioning_status} if self.versioning_status else {}

    def delete_object(self, **kwargs):
        self.calls.append(("delete_object", kwargs.copy()))
        if self.fail_delete:
            raise RuntimeError("synthetic delete failure")
        key = (kwargs["Bucket"], kwargs["Key"])
        current = self.objects.get(key)
        if self.mutate_before_conditional_delete and current is not None:
            current["Body"] = b"concurrent replacement"
            current["ETag"] = '"' + hashlib.md5(current["Body"]).hexdigest() + '"'
        if "IfMatch" in kwargs and current is not None and kwargs["IfMatch"] != current["ETag"]:
            raise FakeS3Error("PreconditionFailed")
        self.objects.pop(key, None)
        return {}

    def list_objects_v2(self, **kwargs):
        keys = sorted(key for (bucket, key) in self.objects if bucket == kwargs["Bucket"] and key.startswith(kwargs["Prefix"]))
        return {"Contents": [{"Key": key} for key in keys], "IsTruncated": False}


class S3PrivateObjectStoreTests(unittest.TestCase):
    def test_acceptance_report_binds_evidence_to_non_secret_storage_target_fingerprint(self):
        from unittest.mock import patch

        configured = {
            "COPILOT_OBJECT_STORAGE_BACKEND": "s3",
            "COPILOT_S3_BUCKET": "acceptance-private-bucket",
            "COPILOT_S3_REGION": "eu-central-1",
            "COPILOT_S3_KMS_KEY_ID": "arn:aws:kms:eu-central-1:123456789012:key/example",
            "COPILOT_S3_ENDPOINT_URL": "",
        }
        with patch.dict("os.environ", configured, clear=True):
            report = build_acceptance_report()
            self.assertRegex(report["storage_config_sha256"], r"^[0-9a-f]{64}$")
            self.assertFalse(report["production_approval"])
            configured["COPILOT_S3_BUCKET"] = "different-bucket"
            with patch.dict("os.environ", configured, clear=True):
                changed = build_acceptance_report()
            self.assertNotEqual(report["storage_config_sha256"], changed["storage_config_sha256"])

    def setUp(self):
        self.client = FakeS3Client()
        self.store = S3PrivateObjectStore(
            self.client, "private-matter-files", "alias/legal-files",
            max_bytes=1024, kms_client=FakeKMSClient(),
        )

    def test_live_acceptance_roundtrip_verifies_and_cleans_up_synthetic_object(self):
        result = run_s3_roundtrip(self.store, 12, b"synthetic acceptance payload")
        self.assertTrue(result["passed"], result)
        self.assertFalse(result["cleanup_pending"])
        self.assertEqual(result["checks"][-1]["name"], "cleanup")
        self.assertEqual(self.store.object_presence(12, result["object_id"]), (False, False))

    def test_live_acceptance_reports_manual_cleanup_when_destination_kms_is_wrong(self):
        self.client.copy_kms_key_id = "arn:aws:kms:us-east-1:123456789012:key/wrong-key"
        result = run_s3_roundtrip(self.store, 12, b"synthetic acceptance payload")
        self.assertFalse(result["passed"])
        self.assertFalse(result["cleanup_pending"])
        self.assertTrue(result["object_id"])
        self.assertIn("error_type", result)
        staged_key = ("private-matter-files", f"firms/12/originals/{result['object_id']}.staged")
        final_key = ("private-matter-files", f"firms/12/originals/{result['object_id']}.blob")
        self.assertNotIn(staged_key, self.client.objects)
        self.assertNotIn(final_key, self.client.objects)

    def test_acceptance_firm_gate_rejects_orphaned_tenant_audit_data(self):
        from database_runtime import DatabaseRuntime
        from tools.verify_s3_original_file_roundtrip import verify_synthetic_firm

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime = DatabaseRuntime(
                root / "control.sqlite3", root / "tenants", root / "corpus.sqlite3"
            )
            runtime.initialize()
            firm_id, _ = runtime.provision_firm("SYNTHETIC-ACCEPTANCE-orphan-audit")
            user_id = runtime.create_initial_firm_owner(
                firm_id, "Acceptance Owner", "orphan-audit-owner@example.test", "test-hash"
            )
            context = runtime.resolve_context(user_id, firm_id)
            tenant = runtime.firm_connection(context)
            tenant.execute(
                "INSERT INTO case_deletion_audit "
                "(firm_id,case_id,actor_user_id,actor_name,case_snapshot_json,events_snapshot_json,related_counts_json) "
                "VALUES(?,?,?,?,?,?,?)",
                (firm_id, 999, user_id, "synthetic", "{}", "[]", "{}"),
            )
            tenant.commit()
            with self.assertRaisesRegex(ValueError, "no tenant matter data"):
                verify_synthetic_firm(runtime, firm_id)
            runtime.close_current_thread()

    def test_acceptance_firm_gate_requires_dedicated_empty_synthetic_tenant(self):
        from database_runtime import DatabaseRuntime
        from tools.verify_s3_original_file_roundtrip import verify_synthetic_firm

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime = DatabaseRuntime(
                root / "control.sqlite3", root / "tenants", root / "corpus.sqlite3"
            )
            runtime.initialize()
            firm_id, _ = runtime.provision_firm("SYNTHETIC-ACCEPTANCE-storage-check")
            user_id = runtime.create_initial_firm_owner(
                firm_id, "Acceptance Owner", "acceptance-owner@example.test", "test-hash"
            )
            report = verify_synthetic_firm(runtime, firm_id)
            self.assertEqual(report["firm_id"], firm_id)
            self.assertEqual(report["case_count"], 0)
            self.assertEqual(report["original_file_metadata_count"], 0)
            self.assertEqual(report["nonempty_tenant_tables"], {})

            context = runtime.resolve_context(user_id, firm_id)
            tenant = runtime.firm_connection(context)
            tenant.execute("INSERT INTO cases(title,firm_id) VALUES(?,?)", ("must block probe", firm_id))
            tenant.commit()
            with self.assertRaisesRegex(ValueError, "no cases"):
                verify_synthetic_firm(runtime, firm_id)
            runtime.close_current_thread()

    def test_stage_uses_firm_namespace_and_kms_encryption(self):
        payload = b"confidential original\x00bytes"
        staged = self.store.stage(12, payload)
        self.assertEqual(staged.sha256, hashlib.sha256(payload).hexdigest())
        self.assertEqual(staged.byte_size, len(payload))
        key = ("private-matter-files", f"firms/12/originals/{staged.object_id}.staged")
        value = self.client.objects[key]
        self.assertEqual(value["Body"], payload)
        self.assertEqual(value["ServerSideEncryption"], "aws:kms")
        self.assertEqual(value["SSEKMSKeyId"], self.client.CANONICAL_KMS_ARN)
        call = next(kwargs for name, kwargs in self.client.calls if name == "put_object")
        self.assertEqual(call["IfNoneMatch"], "*")
        self.assertEqual(call["Metadata"]["firm-id"], "12")
        self.assertEqual(self.store.object_presence(12, staged.object_id), (True, False))

    def test_stage_with_id_preserves_restored_object_id_and_refuses_overwrite(self):
        object_id = "d" * 32
        staged = self.store.stage_with_id(12, object_id, b"restored bytes")
        self.assertEqual(staged.object_id, object_id)
        with self.assertRaises(ObjectStorageError):
            self.store.stage_with_id(12, object_id, b"replacement bytes")
        self.store.finalize(12, object_id)
        with self.store.open(12, object_id) as handle:
            self.assertEqual(handle.read(), b"restored bytes")

    def test_finalize_open_and_verify(self):
        payload = b"private original bytes"
        staged = self.store.stage(12, payload)
        self.assertTrue(self.store.verify_staged(12, staged.object_id, expected_sha256=staged.sha256, expected_size=len(payload)))
        self.store.finalize(12, staged.object_id)
        self.assertEqual(self.store.object_presence(12, staged.object_id), (False, True))
        with self.store.open(12, staged.object_id) as handle:
            self.assertEqual(handle.read(), payload)
        self.assertTrue(self.store.verify(12, staged.object_id, expected_sha256=staged.sha256, expected_size=len(payload)))
        self.assertFalse(self.store.verify(12, staged.object_id, expected_sha256="0" * 64, expected_size=len(payload)))
        copy_call = next(kwargs for name, kwargs in self.client.calls if name == "copy_object")
        self.assertEqual(copy_call["ServerSideEncryption"], "aws:kms")
        self.assertEqual(copy_call["SSEKMSKeyId"], "alias/legal-files")
        self.assertEqual(copy_call["IfNoneMatch"], "*")

    def test_finalize_preserves_staged_object_when_destination_kms_key_is_wrong(self):
        staged = self.store.stage(12, b"recoverable original bytes")
        self.client.copy_kms_key_id = "arn:aws:kms:us-east-1:123456789012:key/wrong-key"

        with self.assertRaises(ObjectStorageError):
            self.store.finalize(12, staged.object_id)

        staged_key = ("private-matter-files", f"firms/12/originals/{staged.object_id}.staged")
        final_key = ("private-matter-files", f"firms/12/originals/{staged.object_id}.blob")
        self.assertIn(staged_key, self.client.objects)
        self.assertIn(final_key, self.client.objects)
        self.assertEqual(
            self.client.objects[staged_key]["Body"],
            b"recoverable original bytes",
            "staged bytes must remain available for safe retry or operator recovery",
        )
        self.assertFalse(
            any(name == "delete_object" and kwargs.get("Key") == staged_key[1]
                for name, kwargs in self.client.calls),
            "staged object must not be deleted before destination KMS verification",
        )

    def test_finalize_preserves_staged_object_when_destination_digest_mismatches(self):
        staged = self.store.stage(12, b"recoverable original bytes")
        self.client.corrupt_copy_body = True

        with self.assertRaises(ObjectStorageError):
            self.store.finalize(12, staged.object_id)

        staged_key = ("private-matter-files", f"firms/12/originals/{staged.object_id}.staged")
        self.assertIn(staged_key, self.client.objects)
        self.assertEqual(self.client.objects[staged_key]["Body"], b"recoverable original bytes")
        self.assertFalse(
            any(name == "delete_object" and kwargs.get("Key") == staged_key[1]
                for name, kwargs in self.client.calls),
            "staged object must not be deleted before destination digest verification",
        )

    def test_rejects_objects_encrypted_with_a_different_kms_key(self):
        staged = self.store.stage(12, b"confidential")
        self.store.finalize(12, staged.object_id)
        key = ("private-matter-files", f"firms/12/originals/{staged.object_id}.blob")
        self.client.objects[key]["SSEKMSKeyId"] = "arn:aws:kms:us-east-1:123456789012:key/other-key"
        with self.assertRaises(ObjectStorageError):
            self.store.open(12, staged.object_id)
        self.assertFalse(self.store.verify(
            12, staged.object_id, expected_sha256=staged.sha256,
            expected_size=staged.byte_size,
        ))
        with self.assertRaises(ObjectStorageError):
            self.store.object_presence(12, staged.object_id)

    def test_kms_alias_requires_key_resolution_client(self):
        with self.assertRaises(ValueError):
            S3PrivateObjectStore(self.client, "private-matter-files", "alias/legal-files")

    def test_rejects_unencrypted_or_non_kms_objects_on_read_and_verify(self):
        staged = self.store.stage(12, b"confidential")
        self.store.finalize(12, staged.object_id)
        key = ("private-matter-files", f"firms/12/originals/{staged.object_id}.blob")
        self.client.objects[key]["ServerSideEncryption"] = "AES256"
        with self.assertRaises(ObjectStorageError):
            self.store.open(12, staged.object_id)
        self.assertFalse(self.store.verify(
            12, staged.object_id, expected_sha256=staged.sha256,
            expected_size=staged.byte_size,
        ))
        with self.assertRaises(ObjectStorageError):
            self.store.object_presence(12, staged.object_id)

    def test_firm_namespace_and_object_id_validation(self):
        staged = self.store.stage(12, b"firm twelve")
        self.store.finalize(12, staged.object_id)
        with self.assertRaises(ObjectStorageError):
            self.store.open(13, staged.object_id)
        for value in (0, -1, True, "12"):
            with self.assertRaises(ValueError):
                self.store.stage(value, b"x")
        for value in ("../escape", "A" * 32, "f" * 31):
            with self.assertRaises(ValueError):
                self.store.open(12, value)

    def test_oversized_payload_rejected_before_remote_write(self):
        with self.assertRaises(ObjectStorageError):
            self.store.stage(12, b"x" * 1025)
        self.assertEqual(self.client.objects, {})

    def test_delete_removes_staged_and_final_objects(self):
        staged = self.store.stage(12, b"delete me")
        self.assertTrue(self.store.delete(12, staged.object_id))
        self.assertEqual(self.store.object_presence(12, staged.object_id), (False, False))
        final = self.store.stage(12, b"delete me too")
        self.store.finalize(12, final.object_id)
        self.assertTrue(self.store.delete(12, final.object_id))
        self.assertFalse(self.store.delete(12, final.object_id))

    def test_physical_purge_requires_never_versioned_bucket_and_verified_bytes(self):
        staged = self.store.stage(12, b"physical purge payload")
        self.store.finalize(12, staged.object_id)
        self.client.versioning_status = "Enabled"
        with self.assertRaisesRegex(ObjectStorageError, "never-versioned"):
            self.store.purge_unversioned(
                12, staged.object_id, expected_sha256=staged.sha256,
                expected_size=staged.byte_size,
            )
        self.assertEqual(self.store.object_presence(12, staged.object_id), (False, True))
        self.client.versioning_status = "Suspended"
        with self.assertRaisesRegex(ObjectStorageError, "versioned or suspended"):
            self.store.purge_unversioned(
                12, staged.object_id, expected_sha256=staged.sha256,
                expected_size=staged.byte_size,
            )
        self.assertEqual(self.store.object_presence(12, staged.object_id), (False, True))
        self.client.versioning_status = None
        self.client.versioning_response = {"UnexpectedState": "unknown"}
        with self.assertRaisesRegex(ObjectStorageError, "never-versioned"):
            self.store.purge_unversioned(
                12, staged.object_id, expected_sha256=staged.sha256,
                expected_size=staged.byte_size,
            )
        self.assertEqual(self.store.object_presence(12, staged.object_id), (False, True))
        self.client.versioning_response = None
        self.assertTrue(self.store.purge_unversioned(
            12, staged.object_id, expected_sha256=staged.sha256,
            expected_size=staged.byte_size,
        ))
        self.assertEqual(self.store.object_presence(12, staged.object_id), (False, False))
        purge_calls = [
            kwargs for name, kwargs in self.client.calls
            if name == "delete_object" and kwargs.get("Key") == self.store._key(12, staged.object_id, "blob")
        ]
        self.assertTrue(purge_calls)
        self.assertEqual(purge_calls[-1]["IfMatch"], '"' + hashlib.md5(b"physical purge payload").hexdigest() + '"')
        self.assertFalse(self.store.purge_unversioned(
            12, staged.object_id, expected_sha256=staged.sha256,
            expected_size=staged.byte_size,
        ))

    def test_physical_purge_uses_conditional_delete_and_preserves_concurrent_replacement(self):
        staged = self.store.stage(12, b"original immutable payload")
        self.store.finalize(12, staged.object_id)
        final_key = self.store._key(12, staged.object_id, "blob")
        self.client.mutate_before_conditional_delete = True
        with self.assertRaisesRegex(ObjectStorageError, "physical purge could not be verified"):
            self.store.purge_unversioned(
                12, staged.object_id, expected_sha256=staged.sha256,
                expected_size=staged.byte_size,
            )
        current = self.client.objects[("private-matter-files", final_key)]
        self.assertEqual(current["Body"], b"concurrent replacement")
        delete_call = [
            kwargs for name, kwargs in self.client.calls
            if name == "delete_object" and kwargs.get("Key") == final_key
        ][-1]
        self.assertEqual(delete_call["IfMatch"], '"' + hashlib.md5(b"original immutable payload").hexdigest() + '"')

    def test_physical_purge_refuses_missing_etag_before_delete(self):
        staged = self.store.stage(12, b"missing etag payload")
        self.store.finalize(12, staged.object_id)
        self.client.omit_head_etag = True
        with self.assertRaisesRegex(ObjectStorageError, "requires an object ETag"):
            self.store.purge_unversioned(
                12, staged.object_id, expected_sha256=staged.sha256,
                expected_size=staged.byte_size,
            )
        self.assertEqual(self.store.object_presence(12, staged.object_id), (False, True))
        self.assertFalse(any(name == "delete_object" and kwargs.get("Key") == self.store._key(12, staged.object_id, "blob") for name, kwargs in self.client.calls))

    def test_physical_purge_refuses_staged_or_corrupt_objects_and_preserves_bytes(self):
        staged = self.store.stage(12, b"recoverable staged payload")
        with self.assertRaisesRegex(ObjectStorageError, "staged copy exists"):
            self.store.purge_unversioned(
                12, staged.object_id, expected_sha256=staged.sha256,
                expected_size=staged.byte_size,
            )
        self.store.finalize(12, staged.object_id)
        with self.assertRaisesRegex(ObjectStorageError, "failed integrity verification"):
            self.store.purge_unversioned(
                12, staged.object_id, expected_sha256="0" * 64,
                expected_size=staged.byte_size,
            )
        self.assertEqual(self.store.object_presence(12, staged.object_id), (False, True))
        self.client.fail_delete = True
        with self.assertRaisesRegex(ObjectStorageError, "physical purge could not be verified"):
            self.store.purge_unversioned(
                12, staged.object_id, expected_sha256=staged.sha256,
                expected_size=staged.byte_size,
            )
        self.assertEqual(self.store.object_presence(12, staged.object_id), (False, True))

    def test_production_s3_purge_cli_fails_closed_without_complete_acceptance_manifest(self):
        import contextlib
        import io
        import sys
        from unittest.mock import patch
        from tools.purge_approved_s3_original_files import main

        environment = {
            "COPILOT_ENV": "production",
            "COPILOT_OBJECT_STORAGE_BACKEND": "s3",
            "COPILOT_S3_BUCKET": "private-matter-files",
            "COPILOT_S3_REGION": "eu-central-1",
            "COPILOT_S3_KMS_KEY_ID": "alias/legal-files",
            "COPILOT_S3_ENDPOINT_URL": "",
            "COPILOT_DATABASE_ACCEPTANCE_FILE": "/nonexistent/acceptance.json",
        }
        output = io.StringIO()
        with patch.dict("os.environ", environment, clear=True):
            with patch.object(sys, "argv", ["purge-s3", "--firm-id", "12", "--operator-user-id", "7"]):
                with contextlib.redirect_stdout(output):
                    self.assertEqual(main(), 2)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["decision"], "blocked")
        self.assertEqual(payload["reason"], "database_release_acceptance_incomplete")
        self.assertEqual(payload["mutations_performed"], 0)

    def test_inventory_lists_only_keys_in_originals_namespace(self):
        one = self.store.stage(12, b"one")
        self.store.finalize(12, one.object_id)
        other = self.store.stage(13, b"other")
        keys = self.store.list_object_keys()
        self.assertIn(f"firms/12/originals/{one.object_id}.blob", keys)
        self.assertIn(f"firms/13/originals/{other.object_id}.staged", keys)
        self.assertTrue(all(key.startswith("firms/") for key in keys))

    def test_s3_reconciliation_checks_metadata_integrity_and_orphans_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "firm.sqlite3"
            db = sqlite3.connect(path)
            db.executescript("""
                CREATE TABLE tenant_database_binding(singleton INTEGER PRIMARY KEY, firm_id INTEGER NOT NULL);
                CREATE TABLE original_file_objects(
                    object_id TEXT PRIMARY KEY, firm_id INTEGER NOT NULL, storage_backend TEXT NOT NULL,
                    sha256 TEXT NOT NULL, byte_size INTEGER NOT NULL, state TEXT NOT NULL, purged_at TEXT
                );
                INSERT INTO tenant_database_binding(singleton,firm_id) VALUES(1,12);
            """)
            payload = b"verified object"
            staged = self.store.stage(12, payload)
            self.store.finalize(12, staged.object_id)
            db.execute(
                "INSERT INTO original_file_objects VALUES(?,?,?,?,?,'ready',NULL)",
                (staged.object_id, 12, "s3", staged.sha256, staged.byte_size),
            )
            db.commit()
            db.close()

            report = reconcile_s3_original_file_storage(
                self.store, [TenantDatabase(firm_id=12, path=path)]
            )
            self.assertTrue(report.clean, report.findings)
            self.assertEqual(report.checked_metadata_rows, 1)
            self.assertEqual(report.checked_objects, 1)

    def test_s3_reconciliation_reports_missing_object(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "firm.sqlite3"
            db = sqlite3.connect(path)
            db.executescript("""
                CREATE TABLE tenant_database_binding(singleton INTEGER PRIMARY KEY, firm_id INTEGER NOT NULL);
                CREATE TABLE original_file_objects(
                    object_id TEXT PRIMARY KEY, firm_id INTEGER NOT NULL, storage_backend TEXT NOT NULL,
                    sha256 TEXT NOT NULL, byte_size INTEGER NOT NULL, state TEXT NOT NULL, purged_at TEXT
                );
                INSERT INTO tenant_database_binding(singleton,firm_id) VALUES(1,12);
            """)
            db.execute(
                "INSERT INTO original_file_objects VALUES(?,?,?,?,?,'ready',NULL)",
                ("a" * 32, 12, "s3", hashlib.sha256(b"missing").hexdigest(), 7),
            )
            db.commit()
            db.close()

            report = reconcile_s3_original_file_storage(
                self.store, [TenantDatabase(firm_id=12, path=path)]
            )
            self.assertIn("missing_object", {item.code for item in report.findings})

    def test_encrypted_backup_staging_copies_verified_s3_originals(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "tenant.sqlite3"
            payload_dir = root / "payload"
            payload_dir.mkdir()
            db = sqlite3.connect(path)
            db.executescript("""
                CREATE TABLE original_file_objects(
                    object_id TEXT PRIMARY KEY, firm_id INTEGER NOT NULL, storage_backend TEXT NOT NULL,
                    sha256 TEXT NOT NULL, byte_size INTEGER NOT NULL, state TEXT NOT NULL, purged_at TEXT
                );
            """)
            payload = b"backup source bytes"
            staged = self.store.stage(12, payload)
            self.store.finalize(12, staged.object_id)
            db.execute(
                "INSERT INTO original_file_objects VALUES(?,?,?,?,?,'ready',NULL)",
                (staged.object_id, 12, "s3", staged.sha256, staged.byte_size),
            )
            db.commit()
            db.close()

            expected = _copy_s3_original_objects(path, 12, self.store, payload_dir)
            backup_copy = payload_dir / "objects" / "firm-12" / f"{staged.object_id}.blob"
            self.assertEqual(expected, {f"firm-12/{staged.object_id}.blob"})
            self.assertEqual(backup_copy.read_bytes(), payload)
            self.assertEqual(_scan_s3_original_object_inventory(self.store), expected)

    def test_missing_kms_configuration_is_rejected(self):
        with self.assertRaises(ValueError):
            S3PrivateObjectStore(self.client, "private-matter-files", "")


if __name__ == "__main__":
    unittest.main()
