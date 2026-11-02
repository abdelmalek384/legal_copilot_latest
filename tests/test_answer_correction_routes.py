"""Correction suggestions are private to a firm's tenant and never training data by default."""
import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


class AnswerCorrectionRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-corrections-")
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
            "ADMIN_TOKEN": "answer-correction-test-admin-token",
        })
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Correction Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Correction Firm B")
        self.password_a = "Correction-owner-A-password-2026!"
        self.password_b = "Correction-owner-B-password-2026!"
        self.runtime.create_initial_firm_owner(
            self.firm_a, "Correction Owner A", "correction-a@example.test", app.hash_pw(self.password_a)
        )
        self.runtime.create_initial_firm_owner(
            self.firm_b, "Correction Owner B", "correction-b@example.test", app.hash_pw(self.password_b)
        )
        self.client_a = TestClient(app.app)
        self.client_b = TestClient(app.app)
        self._login(self.client_a, "correction-a@example.test", self.password_a, self.firm_a)
        self._login(self.client_b, "correction-b@example.test", self.password_b, self.firm_b)
        created = self._mutate(self.client_a, "post", "/cases", json={
            "title": "Correction test matter", "client": "Client A",
        })
        self.assertEqual(created.status_code, 200, created.text)
        self.case_id = created.json()["id"]
        lawyer_password = "Correction-lawyer-password-2026!"
        lawyer_id = self.runtime.create_global_identity(
            "Correction Lawyer", "correction-lawyer@example.test", app.hash_pw(lawyer_password)
        )
        self.runtime.create_firm_membership(lawyer_id, self.firm_a, "lawyer")
        self.client_lawyer = TestClient(app.app)
        self._login(self.client_lawyer, "correction-lawyer@example.test", lawyer_password, self.firm_a)

    def tearDown(self):
        for client in (self.client_a, self.client_b, self.client_lawyer):
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

    def _login(self, client, email, password, firm_id):
        response = client.post("/login", json={"email": email, "password": password})
        self.assertEqual(response.status_code, 200, response.text)
        if response.json()["firm_id"] != firm_id:
            switched = client.post("/session/firm", json={"firm_id": firm_id},
                headers={"X-CSRF-Token": client.cookies.get("lc_csrf", "")})
            self.assertEqual(switched.status_code, 200, switched.text)

    def _mutate(self, client, method, url, **kwargs):
        headers = dict(kwargs.pop("headers", {}) or {})
        headers["X-CSRF-Token"] = client.cookies.get("lc_csrf", "")
        return getattr(client, method)(url, headers=headers, **kwargs)

    def test_correction_submission_review_and_training_default(self):
        submitted = self._mutate(self.client_a, "post", "/answers/corrections", json={
            "case_id": self.case_id, "answer_id": "ans_test_123",
            "question": "What is the procedural deadline?",
            "answer_excerpt": "The answer excerpt shown to the lawyer.",
            "correction_note": "Please re-check the cited source date.",
        })
        self.assertEqual(submitted.status_code, 200, submitted.text)
        self.assertEqual(submitted.json()["training_use"], "none")
        suggestion_id = submitted.json()["id"]

        queue = self.client_a.get("/admin/corrections")
        self.assertEqual(queue.status_code, 200, queue.text)
        self.assertEqual(queue.json()[0]["id"], suggestion_id)
        self.assertEqual(queue.json()[0]["training_use"], "none")
        self.assertEqual(self.client_a.get("/corrections").json()[0]["status"], "pending")

        self.assertEqual(self.client_b.get("/admin/corrections").json(), [])
        self.assertEqual(self.client_b.get("/corrections").json(), [])
        self.assertEqual(self.client_lawyer.get("/admin/corrections").status_code, 403)
        cross_firm = self._mutate(self.client_b, "post",
            f"/admin/corrections/{suggestion_id}/review", json={"status": "accepted"})
        self.assertEqual(cross_firm.status_code, 404)

        reviewed = self._mutate(self.client_a, "post",
            f"/admin/corrections/{suggestion_id}/review",
            json={"status": "accepted", "review_note": "Reviewed internally."})
        self.assertEqual(reviewed.status_code, 200, reviewed.text)
        self.assertEqual(self.client_a.get("/corrections").json()[0]["status"], "accepted")
        tenant = self.runtime._tenant_router.connection_for_firm(self.firm_a)
        self.assertEqual(tenant.execute(
            "SELECT COUNT(*) FROM answer_correction_events WHERE suggestion_id=?", (suggestion_id,)
        ).fetchone()[0], 2)

    def test_non_case_member_cannot_attach_correction_to_case(self):
        denied = self._mutate(self.client_lawyer, "post", "/answers/corrections", json={
            "case_id": self.case_id, "answer_excerpt": "Matter answer",
            "correction_note": "Attempt to attach to an inaccessible case.",
        })
        self.assertEqual(denied.status_code, 404)
        self.assertEqual(self.client_a.get("/admin/corrections").json(), [])


if __name__ == "__main__":
    unittest.main()
