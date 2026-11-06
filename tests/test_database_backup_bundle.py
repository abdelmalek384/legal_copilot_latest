import io
import json
import sqlite3
import tempfile
import unittest
import zipfile
from pathlib import Path

from cryptography.fernet import Fernet

from database_backup import (
    DatabaseBundleError,
    create_backup_bundle,
    restore_backup_bundle,
)
from database_runtime import DatabaseRuntime


class DatabaseBackupBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.runtime = DatabaseRuntime(
            self.root / "source" / "control.sqlite3",
            self.root / "source" / "tenants",
            self.root / "source" / "corpus.sqlite3",
        )
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Backup Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Backup Firm B")
        self.user_id = self.runtime.create_initial_firm_owner(
            self.firm_a, "Backup Owner", "backup-owner@example.test", "test-password-hash"
        )
        self.runtime.create_firm_membership(self.user_id, self.firm_b, "lawyer")
        context = self.runtime.resolve_context(self.user_id, self.firm_a)
        firm_db = self.runtime.firm_connection(context)
        firm_db.execute(
            "INSERT INTO cases(title,firm_id) VALUES('Snapshot Matter',?)", (self.firm_a,)
        )
        firm_db.commit()
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.backup_dir = self.root / "backups"
        self.backup_dir.mkdir()

    def tearDown(self):
        try:
            self.runtime.close_current_thread()
        except Exception:
            pass
        self.temp.cleanup()

    def test_encrypted_bundle_restores_control_corpus_and_each_firm(self):
        with self.assertRaises(DatabaseBundleError):
            create_backup_bundle(self.runtime, self.cipher, self.backup_dir)

        bundle = create_backup_bundle(
            self.runtime, self.cipher, self.backup_dir, keep=3, quiesced=True
        )
        self.assertTrue(bundle.is_file())
        self.assertFalse(bundle.read_bytes().startswith(b"PK"))

        target = self.root / "restored"
        restored = restore_backup_bundle(bundle, self.cipher, target)
        self.assertEqual(restored["root"], target)
        self.assertTrue(restored["control_plane"].is_file())
        self.assertTrue(restored["legal_corpus"].is_file())

        # Restore itself, before runtime initialization, must establish the
        # concurrency mode expected by the application for every database.
        restored_databases = [
            restored["control_plane"],
            restored["legal_corpus"],
            *sorted(restored["tenant_root"].glob("tenant-*.sqlite3")),
        ]
        self.assertGreaterEqual(len(restored_databases), 4)
        for database_path in restored_databases:
            connection = sqlite3.connect(database_path)
            try:
                journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
                self.assertEqual(str(journal_mode).lower(), "wal", database_path.name)
            finally:
                connection.close()

        restored_runtime = DatabaseRuntime(
            restored["control_plane"], restored["tenant_root"], restored["legal_corpus"]
        )
        restored_runtime.initialize()
        context_a = restored_runtime.resolve_context(self.user_id, self.firm_a)
        context_b = restored_runtime.resolve_context(self.user_id, self.firm_b)
        db_a = restored_runtime.firm_connection(context_a)
        db_b = restored_runtime.firm_connection(context_b)
        self.assertEqual(
            db_a.execute("SELECT title FROM cases").fetchone()[0], "Snapshot Matter"
        )
        self.assertEqual(db_b.execute("SELECT COUNT(*) FROM cases").fetchone()[0], 0)
        self.assertEqual(
            restored_runtime.legal_corpus_connection()
            .execute("SELECT profile FROM database_profile").fetchone()[0],
            "legal_corpus",
        )
        restored_runtime.close_current_thread()

    def test_original_objects_restore_with_tenant_metadata_and_verified_bytes(self):
        import hashlib
        import app
        from original_file_storage import LocalPrivateObjectStore

        context = self.runtime.resolve_context(self.user_id, self.firm_a)
        firm_db = self.runtime.firm_connection(context)
        case_id = firm_db.execute(
            "SELECT id FROM cases WHERE title='Snapshot Matter'"
        ).fetchone()[0]
        original = b"synthetic confidential original evidence bytes"
        _, document_id = app.save_doc(
            firm_db,
            {"id": self.user_id, "firm_id": self.firm_a, "name": "Backup Owner"},
            case_id,
            "original-evidence.txt",
            "Extracted evidence text retained separately from original bytes.",
            content_hash=hashlib.sha256(original).hexdigest(),
            content_type="text/plain",
            byte_size=len(original),
        )

        object_root = self.root / "source" / "objects"
        store = LocalPrivateObjectStore(object_root)
        staged = store.stage(self.firm_a, original)
        store.finalize(self.firm_a, staged.object_id)
        firm_db.execute(
            "INSERT INTO original_file_objects(object_id,document_id,firm_id,storage_backend,sha256,byte_size,content_type,state) "
            "VALUES(?,?,?,'local',?,?,?,'ready')",
            (staged.object_id, document_id, self.firm_a, staged.sha256, staged.byte_size, "text/plain"),
        )
        firm_db.commit()

        bundle = create_backup_bundle(
            self.runtime, self.cipher, self.backup_dir, quiesced=True
        )
        restored = restore_backup_bundle(bundle, self.cipher, self.root / "restored-with-objects")
        restored_object = (
            restored["object_storage"] / f"firm-{self.firm_a}" / f"{staged.object_id}.blob"
        )
        self.assertTrue(restored_object.is_file())
        self.assertEqual(restored_object.read_bytes(), original)

        from tools.run_database_recovery_drill import run_recovery_drill
        drill = run_recovery_drill(bundle, self.cipher, self.root)
        self.assertTrue(drill["verified"], drill["findings"])
        self.assertEqual(drill["object_file_count"], 1)
        self.assertEqual(drill["active_firm_routing_checks"], 2)

        restored_runtime = DatabaseRuntime(
            restored["control_plane"], restored["tenant_root"], restored["legal_corpus"]
        )
        restored_runtime.initialize()
        restored_context = restored_runtime.resolve_context(self.user_id, self.firm_a)
        restored_db = restored_runtime.firm_connection(restored_context)
        metadata = restored_db.execute(
            "SELECT state,sha256,byte_size FROM original_file_objects WHERE object_id=?",
            (staged.object_id,),
        ).fetchone()
        self.assertEqual(metadata["state"], "ready")
        self.assertEqual(metadata["sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(metadata["byte_size"], len(original))
        restored_runtime.close_current_thread()

    def test_recovery_drill_restores_and_exercises_active_firm_routing(self):
        from tools.run_database_recovery_drill import run_recovery_drill

        bundle = create_backup_bundle(
            self.runtime, self.cipher, self.backup_dir, quiesced=True
        )
        report = run_recovery_drill(bundle, self.cipher, self.root)

        self.assertTrue(report["verified"], report["findings"])
        self.assertGreaterEqual(report["database_count"], 4)
        self.assertEqual(report["active_firm_routing_checks"], 2)
        self.assertFalse(report["plaintext_retained"])

    def test_restore_refuses_existing_target_and_wrong_encryption_key(self):
        bundle = create_backup_bundle(
            self.runtime, self.cipher, self.backup_dir, quiesced=True
        )
        existing = self.root / "existing"
        existing.mkdir()
        marker = existing / "keep.txt"
        marker.write_text("preserve", encoding="utf-8")
        with self.assertRaises(DatabaseBundleError):
            restore_backup_bundle(bundle, self.cipher, existing)
        self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")
        with self.assertRaises(DatabaseBundleError):
            restore_backup_bundle(bundle, Fernet(Fernet.generate_key()), self.root / "wrong-key")

    def test_restore_rejects_symlinked_backup_input(self):
        bundle = self.backup_dir / "linked-backup.enc"
        target = self.backup_dir / "target.enc"
        target.write_bytes(self.cipher.encrypt(b"not a real bundle"))
        bundle.symlink_to(target)
        with self.assertRaisesRegex(DatabaseBundleError, "must not be a symlink"):
            restore_backup_bundle(bundle, self.cipher, self.root / "linked-restore")
        self.assertFalse((self.root / "linked-restore").exists())

    def test_restore_rejects_fifo_backup_input_without_blocking(self):
        import os

        if not hasattr(os, "mkfifo") or os.name != "posix":
            self.skipTest("FIFO behavior is POSIX-specific")
        fifo = self.backup_dir / "waiting-backup.enc"
        os.mkfifo(fifo)
        with self.assertRaisesRegex(DatabaseBundleError, "must be a regular file"):
            restore_backup_bundle(fifo, self.cipher, self.root / "fifo-restore")
        self.assertFalse((self.root / "fifo-restore").exists())

    def test_restore_rejects_oversized_encrypted_input_before_reading(self):
        from unittest.mock import patch
        import database_backup

        bundle = self.backup_dir / "oversized-backup.enc"
        bundle.write_bytes(b"x" * 17)
        with patch.object(database_backup, "_MAX_ENCRYPTED_BUNDLE_BYTES", 16):
            with self.assertRaisesRegex(DatabaseBundleError, "size limit"):
                restore_backup_bundle(bundle, self.cipher, self.root / "oversized-restore")
        self.assertFalse((self.root / "oversized-restore").exists())

    def test_restore_rejects_checksum_tampering_even_with_valid_encryption(self):
        bundle = create_backup_bundle(
            self.runtime, self.cipher, self.backup_dir, quiesced=True
        )
        plaintext = self.cipher.decrypt(bundle.read_bytes())
        with zipfile.ZipFile(io.BytesIO(plaintext), "r") as archive:
            members = {name: archive.read(name) for name in archive.namelist()}
        tenant_path = next(name for name in members if name.startswith("tenants/"))
        members[tenant_path] += b"tampered"
        changed = io.BytesIO()
        with zipfile.ZipFile(changed, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in members.items():
                archive.writestr(name, data)
        tampered_bundle = self.backup_dir / "tampered.dbbundle.enc"
        tampered_bundle.write_bytes(self.cipher.encrypt(changed.getvalue()))
        with self.assertRaises(DatabaseBundleError):
            restore_backup_bundle(
                tampered_bundle, self.cipher, self.root / "tampered-restore"
            )

    def test_real_bundle_roundtrips_through_versioned_s3_archive_before_isolated_restore(self):
        import hashlib
        from database_backup import verify_backup_bundle
        from database_backup_archive import (
            upload_encrypted_bundle,
            download_encrypted_bundle_version,
        )

        class FakeS3:
            def __init__(self):
                self.items = {}
                self.version = "integration-version-001"

            def get_bucket_versioning(self, **kwargs):
                return {"Status": "Enabled"}

            def put_object(self, **kwargs):
                data = kwargs["Body"].read()
                self.items[(kwargs["Bucket"], kwargs["Key"], self.version)] = {
                    "data": data,
                    "metadata": kwargs["Metadata"],
                    "encryption": kwargs["ServerSideEncryption"],
                    "kms": kwargs["SSEKMSKeyId"],
                }
                return {"VersionId": self.version}

            def head_object(self, **kwargs):
                item = self.items[(kwargs["Bucket"], kwargs["Key"], kwargs["VersionId"])]
                return {
                    "VersionId": kwargs["VersionId"],
                    "ServerSideEncryption": item["encryption"],
                    "SSEKMSKeyId": item["kms"],
                    "ContentLength": len(item["data"]),
                    "Metadata": item["metadata"],
                }

            def get_object(self, **kwargs):
                import io
                item = self.items[(kwargs["Bucket"], kwargs["Key"], kwargs["VersionId"])]
                return {"VersionId": kwargs["VersionId"], "Body": io.BytesIO(item["data"])}

        class FakeKMS:
            def describe_key(self, **kwargs):
                return {"KeyMetadata": {
                    "Arn": "arn:aws:kms:eu-west-1:123456789012:key/integration-archive-key",
                    "KeyState": "Enabled",
                    "KeyUsage": "ENCRYPT_DECRYPT",
                    "KeySpec": "SYMMETRIC_DEFAULT",
                    "KeyManager": "CUSTOMER",
                }}

        bundle = create_backup_bundle(
            self.runtime, self.cipher, self.backup_dir, quiesced=True
        )
        s3 = FakeS3()
        kms = FakeKMS()
        config = {
            "bucket": "isolated-recovery-archive",
            "kms_key_id": "alias/integration-archive-key",
        }
        locator = upload_encrypted_bundle(s3, kms, bundle, **config)
        self.assertEqual(locator["version_id"], s3.version)
        self.assertEqual(locator["sha256"], hashlib.sha256(bundle.read_bytes()).hexdigest())

        downloaded = download_encrypted_bundle_version(
            s3, kms, locator, self.root / "archive-roundtrip.enc", **config
        )
        self.assertEqual(downloaded.read_bytes(), bundle.read_bytes())
        report = verify_backup_bundle(downloaded, self.cipher)
        self.assertTrue(report["verified"])
        self.assertEqual(report["tenant_database_count"], 2)

        restored = restore_backup_bundle(
            downloaded, self.cipher, self.root / "archive-isolated-restore"
        )
        self.assertTrue(restored["control_plane"].is_file())
        restored_runtime = DatabaseRuntime(
            restored["control_plane"], restored["tenant_root"], restored["legal_corpus"]
        )
        try:
            restored_runtime.initialize()
            context = restored_runtime.resolve_context(self.user_id, self.firm_a)
            database = restored_runtime.firm_connection(context)
            self.assertEqual(
                database.execute("SELECT title FROM cases").fetchone()[0],
                "Snapshot Matter",
            )
            self.assertEqual(
                restored_runtime.legal_corpus_connection()
                .execute("SELECT profile FROM database_profile").fetchone()[0],
                "legal_corpus",
            )
        finally:
            restored_runtime.close_current_thread()

    def test_verify_bundle_validates_all_profiles_without_retaining_plaintext(self):
        from database_backup import verify_backup_bundle
        bundle = create_backup_bundle(self.runtime, self.cipher, self.backup_dir, quiesced=True)
        result = verify_backup_bundle(bundle, self.cipher)
        self.assertTrue(result["verified"])
        self.assertEqual(result["format_version"], 2)
        self.assertEqual(result["tenant_database_count"], 2)
        self.assertEqual(result["original_object_count"], 0)
        self.assertTrue(result["original_objects_verified"])
        self.assertFalse(result["plaintext_retained"])
        self.assertIn("not guaranteed secure erasure", result["warning"])

    def test_verify_bundle_rejects_wrong_key_without_persistent_restore(self):
        from database_backup import verify_backup_bundle
        bundle = create_backup_bundle(self.runtime, self.cipher, self.backup_dir, quiesced=True)
        before = {p.name for p in self.root.iterdir()}
        with self.assertRaises(DatabaseBundleError):
            verify_backup_bundle(bundle, Fernet(Fernet.generate_key()))
        self.assertEqual({p.name for p in self.root.iterdir()}, before)

    def test_backup_rejects_tenant_root_as_output_directory(self):
        with self.assertRaises(DatabaseBundleError):
            create_backup_bundle(
                self.runtime, self.cipher, self.runtime.paths.tenant_root, quiesced=True
            )


    def test_backup_rejects_unreferenced_tenant_database_files(self):
        rogue = self.runtime.paths.tenant_root / "tenant-999-0123456789abcdef0123456789abcdef.sqlite3"
        rogue.write_bytes(b"unreferenced tenant data")

        with self.assertRaisesRegex(DatabaseBundleError, "unreferenced database files"):
            create_backup_bundle(
                self.runtime, self.cipher, self.backup_dir, quiesced=True
            )

        self.assertEqual(list(self.backup_dir.glob("tenancy-*.dbbundle.enc")), [])

    def test_backup_rejects_cataloged_tenant_database_replaced_by_symlink(self):
        control = self.runtime.control_connection()
        row = control.execute(
            "SELECT database_file FROM tenant_database_catalog WHERE firm_id=?",
            (self.firm_a,),
        ).fetchone()
        self.assertIsNotNone(row)
        firm_a_path = self.runtime.paths.tenant_root / row["database_file"]
        firm_b_path = next(
            path for path in self.runtime.paths.tenant_root.glob("tenant-*.sqlite3")
            if path != firm_a_path
        )

        self.runtime.close_current_thread()
        firm_a_path.unlink()
        try:
            firm_a_path.symlink_to(firm_b_path)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlink creation is unavailable: {exc}")

        with self.assertRaisesRegex(DatabaseBundleError, "missing or is a symlink"):
            create_backup_bundle(
                self.runtime, self.cipher, self.backup_dir, quiesced=True
            )

        self.assertEqual(list(self.backup_dir.glob("tenancy-*.dbbundle.enc")), [])


    def test_restore_preserves_disabled_firm_and_suspended_membership(self):
        from tenant_context import FirmContextError

        control = self.runtime.control_connection()
        control.execute(
            "UPDATE firm_memberships SET status='suspended' "
            "WHERE user_id=? AND firm_id=?",
            (self.user_id, self.firm_b),
        )
        control.commit()
        self.assertTrue(self.runtime.disable_firm(self.firm_b))

        # Also retain an independently suspended membership in an otherwise
        # active firm, so denial is not explained only by the disabled tenant.
        suspended_user_id = self.runtime.create_global_identity(
            "Suspended Member", "suspended-member@example.test", "test-password-hash"
        )
        self.runtime.create_firm_membership(suspended_user_id, self.firm_a, "lawyer")
        control.execute(
            "UPDATE firm_memberships SET status='suspended' "
            "WHERE user_id=? AND firm_id=?",
            (suspended_user_id, self.firm_a),
        )
        control.commit()

        bundle = create_backup_bundle(
            self.runtime, self.cipher, self.backup_dir, quiesced=True
        )
        target = self.root / "lifecycle-restore"
        restored = restore_backup_bundle(bundle, self.cipher, target)
        restored_runtime = DatabaseRuntime(
            restored["control_plane"], restored["tenant_root"], restored["legal_corpus"]
        )
        try:
            restored_runtime.initialize()
            restored_control = restored_runtime.control_connection()
            firm = restored_control.execute(
                "SELECT status FROM firms WHERE id=?", (self.firm_b,)
            ).fetchone()
            catalog = restored_control.execute(
                "SELECT status,database_file FROM tenant_database_catalog WHERE firm_id=?",
                (self.firm_b,),
            ).fetchone()
            membership = restored_control.execute(
                "SELECT status FROM firm_memberships WHERE user_id=? AND firm_id=?",
                (self.user_id, self.firm_b),
            ).fetchone()

            self.assertEqual(firm["status"], "disabled")
            self.assertEqual(catalog["status"], "disabled")
            self.assertEqual(membership["status"], "suspended")
            self.assertTrue((restored["tenant_root"] / catalog["database_file"]).is_file())

            # Recovery must preserve denial state, not reactivate a tenant or membership.
            with self.assertRaises(FirmContextError):
                restored_runtime.resolve_context(self.user_id, self.firm_b)
            with self.assertRaises(FirmContextError):
                restored_runtime.resolve_context(suspended_user_id, self.firm_a)

            restored_suspension = restored_control.execute(
                "SELECT status FROM firm_memberships WHERE user_id=? AND firm_id=?",
                (suspended_user_id, self.firm_a),
            ).fetchone()
            self.assertEqual(restored_suspension["status"], "suspended")

            context_a = restored_runtime.resolve_context(self.user_id, self.firm_a)
            db_a = restored_runtime.firm_connection(context_a)
            self.assertEqual(
                db_a.execute("SELECT title FROM cases").fetchone()[0], "Snapshot Matter"
            )
        finally:
            restored_runtime.close_current_thread()


if __name__ == "__main__":
    unittest.main()
