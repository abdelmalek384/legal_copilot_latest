"""End-to-end recovery drill acceptance tests using disposable tenant databases."""
import tempfile
import unittest
from pathlib import Path

from cryptography.fernet import Fernet

from database_backup import create_backup_bundle
from database_runtime import DatabaseRuntime
from tools.run_database_recovery_drill import run_recovery_drill


class DatabaseRecoveryDrillTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.runtime = DatabaseRuntime(
            self.root / "source" / "control.sqlite3",
            self.root / "source" / "tenants",
            self.root / "source" / "corpus.sqlite3",
        )
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Recovery Drill A")
        self.firm_b, _ = self.runtime.provision_firm("Recovery Drill B")
        self.user_a = self.runtime.create_initial_firm_owner(
            self.firm_a, "Owner A", "owner-a@example.test", "test-password-hash"
        )
        self.user_b = self.runtime.create_initial_firm_owner(
            self.firm_b, "Owner B", "owner-b@example.test", "test-password-hash"
        )
        self.suspended_user = self.runtime.create_global_identity(
            "Suspended Member", "suspended@example.test", "test-password-hash"
        )
        self.runtime.create_firm_membership(self.suspended_user, self.firm_a, "lawyer")
        control = self.runtime.control_connection()
        control.execute(
            "UPDATE firm_memberships SET status='suspended' WHERE user_id=? AND firm_id=?",
            (self.suspended_user, self.firm_a),
        )
        control.commit()
        self.object_root = self.root / "objects"
        self.object_root.mkdir()
        for firm_id in (self.firm_a, self.firm_b):
            (self.object_root / f"firm-{firm_id}").mkdir()
        self.backup_dir = self.root / "backups"
        self.backup_dir.mkdir()
        self.cipher = Fernet(Fernet.generate_key())
        self.bundle = create_backup_bundle(
            self.runtime,
            self.cipher,
            self.backup_dir,
            quiesced=True,
            object_storage_root=self.object_root,
        )
        self.temp_parent = self.root / "recovery-temp"
        self.temp_parent.mkdir()

    def tearDown(self):
        self.runtime.close_current_thread()
        self.temp.cleanup()

    def test_recovery_drill_checks_profiles_routing_and_membership_denials(self):
        report = run_recovery_drill(self.bundle, self.cipher, self.temp_parent)
        self.assertTrue(report["verified"], report["findings"])
        self.assertEqual(report["database_count"], 4)
        self.assertEqual(report["active_firm_routing_checks"], 2)
        self.assertEqual(report["object_file_count"], 0)
        self.assertFalse(report["plaintext_retained"])
        self.assertEqual(report["findings"], [])
        self.assertEqual(list(self.temp_parent.iterdir()), [])

    def test_recovery_drill_restores_and_reconciles_real_firm_original_object(self):
        import hashlib

        import app
        from original_file_storage import LocalPrivateObjectStore

        context = self.runtime.resolve_context(self.user_a, self.firm_a)
        firm_db = self.runtime.firm_connection(context)
        case_id = firm_db.execute(
            "INSERT INTO cases(title,firm_id) VALUES('Recovery Object Matter',?)",
            (self.firm_a,),
        ).lastrowid
        payload = b"recovery drill original evidence bytes"
        _, document_id = app.save_doc(
            firm_db,
            {"id": self.user_a, "firm_id": self.firm_a, "name": "Recovery Owner"},
            case_id,
            "recovery-original.txt",
            "Extracted text for recovery fixture",
            content_hash=hashlib.sha256(payload).hexdigest(),
            content_type="text/plain",
            byte_size=len(payload),
        )
        store = LocalPrivateObjectStore(self.object_root)
        staged = store.stage(self.firm_a, payload)
        store.finalize(self.firm_a, staged.object_id)
        firm_db.execute(
            "INSERT INTO original_file_objects("
            "object_id,document_id,firm_id,storage_backend,sha256,byte_size,content_type,state"
            ") VALUES(?,?,?,'local',?,?,'text/plain','ready')",
            (
                staged.object_id, document_id, self.firm_a,
                staged.sha256, staged.byte_size,
            ),
        )
        firm_db.commit()

        bundle = create_backup_bundle(
            self.runtime,
            self.cipher,
            self.backup_dir,
            quiesced=True,
            object_storage_root=self.object_root,
        )
        report = run_recovery_drill(bundle, self.cipher, self.temp_parent)

        self.assertTrue(report["verified"], report["findings"])
        self.assertEqual(report["object_file_count"], 1)
        self.assertEqual(report["database_count"], 4)
        self.assertFalse(report["plaintext_retained"])
        self.assertEqual(list(self.temp_parent.iterdir()), [])

    def test_recovery_drill_fails_closed_when_an_active_firm_has_no_active_membership(self):
        control = self.runtime.control_connection()
        control.execute(
            "UPDATE firm_memberships SET status='suspended' WHERE user_id=? AND firm_id=?",
            (self.user_b, self.firm_b),
        )
        control.commit()
        # Rebuild the bundle from the changed, intentionally invalid operational state.
        bundle = create_backup_bundle(
            self.runtime,
            self.cipher,
            self.backup_dir,
            quiesced=True,
            object_storage_root=self.object_root,
        )
        report = run_recovery_drill(bundle, self.cipher, self.temp_parent)
        self.assertFalse(report["verified"])
        self.assertIn(
            {"scope": f"firm:{self.firm_b}", "code": "active_firm_has_no_active_membership"},
            report["findings"],
        )
        self.assertFalse(report["plaintext_retained"])
        self.assertEqual(list(self.temp_parent.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
