import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


class SeparateRuntimeSecurityAuditReadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env_names = (
            "COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB",
            "COPILOT_DB", "COPILOT_OBJECT_STORAGE_ROOT", "COPILOT_OBJECT_STORAGE_BACKEND",
            "COPILOT_ENV", "ADMIN_TOKEN",
        )
        self.old_env = {name: os.environ.get(name) for name in self.env_names}
        os.environ.pop("COPILOT_DB", None)
        os.environ["COPILOT_CONTROL_DB"] = str(self.root / "control.sqlite3")
        os.environ["COPILOT_TENANT_DB_ROOT"] = str(self.root / "tenants")
        os.environ["COPILOT_CORPUS_DB"] = str(self.root / "corpus.sqlite3")
        os.environ["COPILOT_OBJECT_STORAGE_ROOT"] = str(self.root / "objects")
        os.environ["COPILOT_OBJECT_STORAGE_BACKEND"] = "local"
        os.environ["COPILOT_ENV"] = "development"
        os.environ["ADMIN_TOKEN"] = "separate-runtime-audit-test-token-2026"
        app._database_runtime = None

        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Audit Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Audit Firm B")
        self.password = "SeparateRuntimeAuditPassphrase-2026!"
        self.owner_a = self.runtime.create_initial_firm_owner(
            self.firm_a, "Audit Owner A", "audit-owner-a@example.test",
            app.hash_pw(self.password),
        )
        self.owner_b = self.runtime.create_initial_firm_owner(
            self.firm_b, "Audit Owner B", "audit-owner-b@example.test",
            app.hash_pw(self.password),
        )
        self.client_a = TestClient(app.app)
        self.client_b = TestClient(app.app)

    def tearDown(self):
        self.client_a.close()
        self.client_b.close()
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

    def _login(self, client, email):
        response = client.post("/login", json={"email": email, "password": self.password})
        self.assertEqual(response.status_code, 200, response.text)
        return response

    def test_case_detail_read_audit_is_persisted_and_firm_scoped(self):
        self._login(self.client_a, "audit-owner-a@example.test")
        csrf_a = self.client_a.cookies.get("lc_csrf") or ""
        created = self.client_a.post(
            "/cases", json={"title": "Audited Separate Runtime Matter"},
            headers={"X-CSRF-Token": csrf_a},
        )
        self.assertEqual(created.status_code, 200, created.text)
        case_id = created.json()["id"]

        detail = self.client_a.get(f"/cases/{case_id}")
        self.assertEqual(detail.status_code, 200, detail.text)

        context_a = self.runtime.resolve_context(self.owner_a, self.firm_a)
        firm_db_a = self.runtime.firm_connection(context_a)
        rows = firm_db_a.execute(
            "SELECT id,firm_id,user_id,event,created_at FROM security_audit_events "
            "WHERE event=?",
            (f"case_read:{case_id}",),
        ).fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(
            (rows[0]["firm_id"], rows[0]["user_id"], rows[0]["event"]),
            (self.firm_a, self.owner_a, f"case_read:{case_id}"),
        )
        self.assertEqual(
            set(rows[0].keys()), {"id", "firm_id", "user_id", "event", "created_at"}
        )

        audit_a = self.client_a.get("/audit/security-events?limit=100")
        self.assertEqual(audit_a.status_code, 200, audit_a.text)
        self.assertTrue(any(
            item["event"] == f"case_read:{case_id}" and item["user_id"] == self.owner_a
            for item in audit_a.json()["items"]
        ))

        self._login(self.client_b, "audit-owner-b@example.test")
        audit_b = self.client_b.get("/audit/security-events?limit=100")
        self.assertEqual(audit_b.status_code, 200, audit_b.text)
        self.assertFalse(any(
            item["event"] == f"case_read:{case_id}"
            for item in audit_b.json()["items"]
        ))


if __name__ == "__main__":
    unittest.main()
