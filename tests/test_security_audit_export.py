"""Security audit CSV export tests on isolated firm database profiles."""
import csv
import io
import os
import tempfile
import unittest
from pathlib import Path

_TEMP = tempfile.TemporaryDirectory(prefix="legal-copilot-audit-export-")
_ENV_NAMES = (
    "COPILOT_DB", "COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT",
    "COPILOT_CORPUS_DB", "COPILOT_ENV", "ADMIN_TOKEN",
)
_OLD_ENV = {name: os.environ.get(name) for name in _ENV_NAMES}
os.environ.pop("COPILOT_DB", None)
os.environ.update(
    COPILOT_ENV="development",
    COPILOT_CONTROL_DB=str(Path(_TEMP.name) / "control.sqlite3"),
    COPILOT_TENANT_DB_ROOT=str(Path(_TEMP.name) / "tenants"),
    COPILOT_CORPUS_DB=str(Path(_TEMP.name) / "corpus.sqlite3"),
    ADMIN_TOKEN="audit-export-test-token-with-sufficient-length",
)
from fastapi.testclient import TestClient
import app


class SecurityAuditExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import importlib
        cls.app = importlib.reload(app)
        cls.runtime = cls.app.get_database_runtime()
        cls.runtime.initialize()
        cls.firm_a, _ = cls.runtime.provision_firm("Audit export Firm A")
        cls.firm_b, _ = cls.runtime.provision_firm("Audit export Firm B")
        cls.admin_password = "audit-export-admin-password-2026!"
        cls.other_password = "audit-export-other-password-2026!"
        cls.lawyer_password = "audit-export-lawyer-password-2026!"
        cls.admin_id = cls.runtime.create_initial_firm_owner(
            cls.firm_a, "Firm Admin", "admin-export@example.test",
            cls.app.hash_pw(cls.admin_password),
        )
        cls.other_admin_id = cls.runtime.create_initial_firm_owner(
            cls.firm_b, "Other Admin", "other-admin-export@example.test",
            cls.app.hash_pw(cls.other_password),
        )
        cls.lawyer_id = cls.runtime.create_global_identity(
            "Firm Lawyer", "lawyer-export@example.test", cls.app.hash_pw(cls.lawyer_password)
        )
        cls.runtime.create_firm_membership(cls.lawyer_id, cls.firm_a, "lawyer")

        firm_a_context = cls.runtime.resolve_context(cls.admin_id, cls.firm_a)
        db_a = cls.runtime.firm_connection(firm_a_context)
        db_a.execute(
            "INSERT INTO security_audit_events(firm_id,user_id,event) VALUES(?,?,?)",
            (cls.firm_a, cls.admin_id, '=HYPERLINK("https://example.invalid")'),
        )
        db_a.execute(
            "INSERT INTO security_audit_events(firm_id,user_id,event) VALUES(?,?,?)",
            (cls.firm_a, cls.admin_id, "password_changed_sessions_revoked"),
        )
        db_a.commit()

        firm_b_context = cls.runtime.resolve_context(cls.other_admin_id, cls.firm_b)
        db_b = cls.runtime.firm_connection(firm_b_context)
        db_b.execute(
            "INSERT INTO security_audit_events(firm_id,user_id,event) VALUES(?,?,?)",
            (cls.firm_b, cls.other_admin_id, "other_firm_private_event"),
        )
        db_b.commit()
        cls.client = TestClient(cls.app.app)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.client.close()
        finally:
            cls.runtime.close_current_thread()
            cls.app._database_runtime = None
            for name, value in _OLD_ENV.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value
            _TEMP.cleanup()

    def login(self, email, password):
        response = self.client.post("/login", json={"email": email, "password": password})
        self.assertEqual(response.status_code, 200, response.text)
        return dict(self.client.cookies)

    def test_admin_export_is_csv_bounded_and_no_store(self):
        self.client.cookies.clear()
        self.login("admin-export@example.test", self.admin_password)
        response = self.client.get("/audit/security-events.csv?limit=1&offset=0")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn("text/csv", response.headers.get("content-type", ""))
        self.assertIn(
            'attachment; filename="security-audit-events.csv"',
            response.headers.get("content-disposition", ""),
        )
        self.assertEqual(response.headers.get("cache-control"), "no-store")
        rows = list(csv.reader(io.StringIO(response.text.lstrip("\\ufeff"))))
        self.assertEqual(rows[0], ["id", "firm_id", "user_id", "event", "created_at"])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][3], "password_changed_sessions_revoked")

    def test_export_is_firm_scoped_and_neutralizes_spreadsheet_formulas(self):
        self.client.cookies.clear()
        self.login("admin-export@example.test", self.admin_password)
        response = self.client.get("/audit/security-events.csv?limit=100")
        self.assertEqual(response.status_code, 200, response.text)
        rows = list(csv.reader(io.StringIO(response.text.lstrip("\\ufeff"))))
        events = [row[3] for row in rows[1:]]
        self.assertNotIn("other_firm_private_event", events)
        self.assertIn(''=HYPERLINK("https://example.invalid")', events)
        self.assertEqual(self.app._csv_safe_cell("  =1+1"), "'  =1+1")
        self.assertEqual(self.app._csv_safe_cell("\\t=1+1"), "'\\t=1+1")

    def test_non_admin_cannot_export_and_limits_are_validated(self):
        self.client.cookies.clear()
        self.login("lawyer-export@example.test", self.lawyer_password)
        denied = self.client.get("/audit/security-events.csv")
        self.assertEqual(denied.status_code, 403)
        self.client.cookies.clear()
        self.login("admin-export@example.test", self.admin_password)
        self.assertEqual(self.client.get("/audit/security-events.csv?limit=5001").status_code, 422)
        self.assertEqual(self.client.get("/audit/security-events.csv?offset=-1").status_code, 422)


if __name__ == "__main__":
    unittest.main()
