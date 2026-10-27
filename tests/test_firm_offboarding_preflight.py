import hashlib
import tempfile
import unittest
from pathlib import Path

import app
from database_runtime import DatabaseRuntime
from original_file_storage import LocalPrivateObjectStore
from tools.firm_offboarding_preflight import inspect_firm_offboarding


class FirmOffboardingPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.control = self.root / "control.sqlite3"
        self.tenants = self.root / "tenants"
        self.corpus = self.root / "corpus.sqlite3"
        self.objects = self.root / "objects"
        self.objects.mkdir()
        self.runtime = DatabaseRuntime(self.control, self.tenants, self.corpus)
        self.runtime.initialize()
        self.firm_id, _ = self.runtime.provision_firm("Offboarding Preflight Firm")
        self.user_id = self.runtime.create_initial_firm_owner(
            self.firm_id, "Offboarding Owner", "offboarding-owner@example.test", "test-password-hash"
        )

    def tearDown(self):
        try:
            self.runtime.close_current_thread()
        except Exception:
            pass
        self.temp.cleanup()

    def _disable_and_revoke_membership(self):
        self.runtime.disable_firm(self.firm_id)
        control = self.runtime.control_connection()
        control.execute(
            "UPDATE firm_memberships SET status='suspended',updated_at=datetime('now') "
            "WHERE firm_id=?",
            (self.firm_id,),
        )
        control.commit()
        self.runtime.close_current_thread()

    def _inspect(self):
        return inspect_firm_offboarding(
            self.control, self.tenants, self.corpus, self.objects, self.firm_id
        )

    def test_clear_preflight_requires_disabled_firm_and_revoked_membership(self):
        self._disable_and_revoke_membership()

        report = self._inspect()

        self.assertTrue(report["purge_preflight_clear"], report["findings"])
        self.assertEqual(report["firm_status"], "disabled")
        self.assertEqual(report["catalog_status"], "disabled")
        self.assertEqual(report["active_memberships"], 0)
        self.assertEqual(report["mutations_performed"], 0)

    def test_active_membership_blocks_purge_preflight(self):
        self.runtime.disable_firm(self.firm_id)
        self.runtime.close_current_thread()

        report = self._inspect()

        self.assertFalse(report["purge_preflight_clear"])
        self.assertIn("active_memberships_remain", {item["code"] for item in report["findings"]})

    def test_active_legal_hold_blocks_purge_preflight(self):
        context = self.runtime.resolve_context(self.user_id, self.firm_id)
        firm_db = self.runtime.firm_connection(context)
        case_id = firm_db.execute(
            "INSERT INTO cases(title,firm_id) VALUES('Held Matter',?)", (self.firm_id,)
        ).lastrowid
        original = b"preserve this original evidence"
        _, document_id = app.save_doc(
            firm_db,
            {"id": self.user_id, "firm_id": self.firm_id, "name": "Offboarding Owner"},
            case_id,
            "held-original.txt",
            "Synthetic extracted evidence text",
            content_hash=hashlib.sha256(original).hexdigest(),
            content_type="text/plain",
            byte_size=len(original),
        )
        store = LocalPrivateObjectStore(self.objects)
        staged = store.stage(self.firm_id, original)
        store.finalize(self.firm_id, staged.object_id)
        firm_db.execute(
            "INSERT INTO original_file_objects("
            "object_id,document_id,firm_id,storage_backend,sha256,byte_size,content_type,state,"
            "legal_hold,hold_reason,hold_set_by,hold_set_at"
            ") VALUES(?,?,?,'local',?,?,?,'ready',1,?,?,datetime('now'))",
            (
                staged.object_id, document_id, self.firm_id, staged.sha256, staged.byte_size,
                "text/plain", self.user_id, "Preserve pending matter",
            ),
        )
        firm_db.commit()
        self._disable_and_revoke_membership()

        report = self._inspect()

        self.assertFalse(report["purge_preflight_clear"])
        self.assertEqual(report["active_legal_hold_count"], 1)
        self.assertIn("active_legal_holds_remain", {item["code"] for item in report["findings"]})
        self.assertEqual(report["mutations_performed"], 0)


if __name__ == "__main__":
    unittest.main()
