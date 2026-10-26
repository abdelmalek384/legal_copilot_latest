import io
import json
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


if __name__ == "__main__":
    unittest.main()
