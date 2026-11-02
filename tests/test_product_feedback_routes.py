"""Firm-private product feedback submission, review and audit coverage."""
import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


class ProductFeedbackRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-feedback-")
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
            "ADMIN_TOKEN": "product-feedback-test-admin-token",
        })
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Feedback Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Feedback Firm B")
        self.clients = {}
        for suffix, firm_id, role in (
            ("a-admin", self.firm_a, "admin"),
            ("b-admin", self.firm_b, "admin"),
            ("a-lawyer", self.firm_a, "lawyer"),
            ("a-lawyer-other", self.firm_a, "lawyer"),
        ):
            email = f"feedback-{suffix}@example.test"
            password = f"Feedback-{suffix}-password-2026!"
            if role == "admin":
                self.runtime.create_initial_firm_owner(
                    firm_id, f"Feedback {suffix}", email, app.hash_pw(password)
                )
            else:
                user_id = self.runtime.create_global_identity(
                    f"Feedback {suffix}", email, app.hash_pw(password)
                )
                self.runtime.create_firm_membership(user_id, firm_id, role)
            client = TestClient(app.app)
            response = client.post("/login", json={"email": email, "password": password})
            self.assertEqual(response.status_code, 200, response.text)
            self.clients[suffix] = client

    def tearDown(self):
        for client in self.clients.values():
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

    def _mutate(self, key, method, url, **kwargs):
        client = self.clients[key]
        headers = dict(kwargs.pop("headers", {}) or {})
        headers["X-CSRF-Token"] = client.cookies.get("lc_csrf", "")
        return getattr(client, method)(url, headers=headers, **kwargs)

    def test_feedback_submission_is_private_and_reviewed_with_immutable_audit(self):
        submitted = self._mutate("a-lawyer", "post", "/feedback", json={
            "category": "bug",
            "title": "Deadline calendar does not refresh",
            "message": "The calendar remains stale after I save a new deadline.",
            "page_path": "/calendar",
        })
        self.assertEqual(submitted.status_code, 200, submitted.text)
        payload = submitted.json()
        self.assertEqual(payload["privacy"], "firm_private")
        self.assertEqual(payload["training_use"], "none")
        feedback_id = payload["id"]

        mine = self.clients["a-lawyer"].get("/feedback/mine")
        self.assertEqual(mine.status_code, 200, mine.text)
        self.assertEqual(mine.json()[0]["id"], feedback_id)
        self.assertEqual(self.clients["a-admin"].get("/admin/feedback").json()[0]["id"], feedback_id)
        self.assertEqual(self.clients["a-lawyer-other"].get("/feedback/mine").json(), [])
        self.assertEqual(self.clients["b-admin"].get("/admin/feedback").json(), [])
        self.assertEqual(self.clients["b-admin"].get("/feedback/mine").json(), [])
        self.assertEqual(self.clients["a-lawyer"].get("/admin/feedback").status_code, 403)

        cross_firm = self._mutate("b-admin", "post",
            f"/admin/feedback/{feedback_id}/review",
            json={"status": "planned", "response": "Not your firm's feedback."})
        self.assertEqual(cross_firm.status_code, 404)

        reviewed = self._mutate("a-admin", "post",
            f"/admin/feedback/{feedback_id}/review",
            json={"status": "planned", "response": "Added to the product backlog."})
        self.assertEqual(reviewed.status_code, 200, reviewed.text)
        self.assertEqual(self.clients["a-lawyer"].get("/feedback/mine").json()[0]["status"], "planned")
        self.assertEqual(self.clients["a-lawyer"].get("/feedback/mine").json()[0]["response"],
                         "Added to the product backlog.")
        duplicate = self._mutate("a-admin", "post",
            f"/admin/feedback/{feedback_id}/review",
            json={"status": "acknowledged", "response": "Duplicate review."})
        self.assertEqual(duplicate.status_code, 409)

        tenant = self.runtime._tenant_router.connection_for_firm(self.firm_a)
        self.assertEqual(tenant.execute(
            "SELECT COUNT(*) FROM product_feedback_events WHERE feedback_id=?", (feedback_id,)
        ).fetchone()[0], 2)
        with self.assertRaisesRegex(Exception, "immutable"):
            tenant.execute(
                "UPDATE product_feedback_events SET detail_json='{}' WHERE feedback_id=?",
                (feedback_id,),
            )

    def test_feedback_validation_rejects_short_or_unknown_values(self):
        short = self._mutate("a-lawyer", "post", "/feedback", json={
            "category": "bug", "title": "x", "message": "short",
        })
        self.assertEqual(short.status_code, 422)
        invalid = self._mutate("a-lawyer", "post", "/feedback", json={
            "category": "training", "title": "Useful idea", "message": "Please add this workflow.",
        })
        self.assertEqual(invalid.status_code, 422)
        self.assertEqual(self.clients["a-admin"].get("/admin/feedback").json(), [])


if __name__ == "__main__":
    unittest.main()
