"""Arabic document skeletons are case-scoped and contain headings only."""
import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


class DocumentSkeletonRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-skeletons-")
        self.root = Path(self.temp.name)
        self.env_names = (
            "COPILOT_DB", "COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT",
            "COPILOT_CORPUS_DB", "COPILOT_OBJECT_STORAGE_ROOT",
            "COPILOT_OBJECT_STORAGE_BACKEND", "COPILOT_ENV", "ADMIN_TOKEN",
        )
        self.old_env = {name: os.environ.get(name) for name in self.env_names}
        os.environ.pop("COPILOT_DB", None)
        os.environ.update({
            "COPILOT_CONTROL_DB": str(self.root / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(self.root / "tenants"),
            "COPILOT_CORPUS_DB": str(self.root / "corpus.sqlite3"),
            "COPILOT_OBJECT_STORAGE_ROOT": str(self.root / "objects"),
            "COPILOT_OBJECT_STORAGE_BACKEND": "local",
            "COPILOT_ENV": "development",
            "ADMIN_TOKEN": "skeleton-route-test-admin-token",
        })
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Skeleton Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Skeleton Firm B")
        self._owner(self.firm_a, "skeleton-a@example.test", "Skeleton-A-owner-password-2026!")
        self._owner(self.firm_b, "skeleton-b@example.test", "Skeleton-B-owner-password-2026!")
        self.client_a = TestClient(app.app)
        self.client_b = TestClient(app.app)
        self._login(self.client_a, "skeleton-a@example.test", "Skeleton-A-owner-password-2026!")
        self._login(self.client_b, "skeleton-b@example.test", "Skeleton-B-owner-password-2026!")
        created = self._mutate(self.client_a, "post", "/cases", json={
            "title": "Matter title", "client": "Client One", "case_number": "123",
            "case_year": "2026", "court": "محكمة القاهرة", "circuit": "الدائرة المدنية",
            "opposing_party": "Opposing Party",
        })
        self.assertEqual(created.status_code, 200, created.text)
        self.case_id = created.json()["id"]
        lawyer_password = "Skeleton-lawyer-password-2026!"
        lawyer_id = self.runtime.create_global_identity(
            "Skeleton Lawyer", "skeleton-lawyer@example.test", app.hash_pw(lawyer_password)
        )
        self.runtime.create_firm_membership(lawyer_id, self.firm_a, "lawyer")
        self.client_nonmember = TestClient(app.app)
        self._login(self.client_nonmember, "skeleton-lawyer@example.test", lawyer_password)

    def _owner(self, firm_id, email, password):
        self.runtime.create_initial_firm_owner(firm_id, email.split("@")[0], email, app.hash_pw(password))

    def tearDown(self):
        for client in (self.client_a, self.client_b, self.client_nonmember):
            client.close()
        try:
            self.runtime.close_current_thread()
        except Exception:
            pass
        app._database_runtime = None
        for name, value in self.old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        self.temp.cleanup()

    def _login(self, client, email, password):
        response = client.post("/login", json={"email": email, "password": password})
        self.assertEqual(response.status_code, 200, response.text)

    def _mutate(self, client, method, url, **kwargs):
        headers = dict(kwargs.pop("headers", {}) or {})
        headers["X-CSRF-Token"] = client.cookies.get("lc_csrf", "")
        return getattr(client, method)(url, headers=headers, **kwargs)

    def test_skeletons_fill_case_fields_and_are_explicitly_drafts(self):
        memo = self.client_a.get(f"/cases/{self.case_id}/draft-skeleton?document_type=memo")
        self.assertEqual(memo.status_code, 200, memo.text)
        data = memo.json()
        self.assertTrue(data["draft"])
        self.assertTrue(data["lawyer_review_required"])
        self.assertFalse(data["contains_legal_advice"])
        self.assertIn("Client One", data["skeleton_text"])
        self.assertIn("123", data["skeleton_text"])
        self.assertIn("2026", data["skeleton_text"])
        self.assertIn("مسودة — يجب مراجعتها بواسطة محامٍ", data["skeleton_text"])

        pleading = self.client_a.get(f"/cases/{self.case_id}/draft-skeleton?document_type=pleading")
        self.assertEqual(pleading.status_code, 200, pleading.text)
        self.assertIn("محكمة القاهرة", pleading.json()["skeleton_text"])
        self.assertIn("Opposing Party", pleading.json()["skeleton_text"])
        self.assertEqual(self.client_a.get(
            f"/cases/{self.case_id}/draft-skeleton?document_type=unknown"
        ).status_code, 422)

    def test_firm_b_and_same_firm_nonmember_cannot_read_case_skeleton(self):
        self.assertEqual(self.client_b.get(
            f"/cases/{self.case_id}/draft-skeleton"
        ).status_code, 404)
        self.assertEqual(self.client_nonmember.get(
            f"/cases/{self.case_id}/draft-skeleton"
        ).status_code, 404)


if __name__ == "__main__":
    unittest.main()
