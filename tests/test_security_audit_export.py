import csv
import io
import os
import tempfile
import unittest
from pathlib import Path

_TEMP = tempfile.TemporaryDirectory()
os.environ.update(
    COPILOT_DB=str(Path(_TEMP.name) / "audit-export-test.db"),
    ADMIN_TOKEN="audit-export-test-token-with-sufficient-length",
)
from fastapi.testclient import TestClient
import app


class SecurityAuditExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app.app)
        db = app.conn()
        db.execute("INSERT OR IGNORE INTO firms(id,name) VALUES(2,'Other firm')")
        for name, email, role, firm_id in (
            ("Firm Admin", "admin-export@example.test", "admin", 1),
            ("Firm Lawyer", "lawyer-export@example.test", "lawyer", 1),
            ("Other Admin", "other-admin-export@example.test", "admin", 2),
        ):
            db.execute(
                "INSERT INTO users(name,email,pw,role,firm_id) VALUES(?,?,?,?,?)",
                (name, email, app.hash_pw("test-password-" + name), role, firm_id),
            )
        db.commit()
        db.execute(
            "INSERT INTO security_audit_events(firm_id,user_id,event) VALUES(1,1,?)",
            ("=HYPERLINK(\"https://example.invalid\")",),
        )
        db.execute(
            "INSERT INTO security_audit_events(firm_id,user_id,event) VALUES(1,1,?)",
            ("password_changed_sessions_revoked",),
        )
        db.execute(
            "INSERT INTO security_audit_events(firm_id,user_id,event) VALUES(2,3,?)",
            ("other_firm_private_event",),
        )
        db.commit()

    def login(self, email, name):
        response = self.client.post("/login", json={
            "email": email, "password": "test-password-" + name,
        })
        self.assertEqual(response.status_code, 200, response.text)
        return dict(self.client.cookies)

    def test_admin_export_is_csv_bounded_and_no_store(self):
        self.client.cookies.clear()
        self.login("admin-export@example.test", "Firm Admin")
        response = self.client.get("/audit/security-events.csv?limit=1&offset=0")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn("text/csv", response.headers.get("content-type", ""))
        self.assertIn("attachment; filename=\"security-audit-events.csv\"",
                      response.headers.get("content-disposition", ""))
        self.assertEqual(response.headers.get("cache-control"), "no-store")
        rows = list(csv.reader(io.StringIO(response.text.lstrip("\ufeff"))))
        self.assertEqual(rows[0], ["id", "firm_id", "user_id", "event", "created_at"])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][3], "password_changed_sessions_revoked")

    def test_export_is_firm_scoped_and_neutralizes_spreadsheet_formulas(self):
        self.client.cookies.clear()
        self.login("admin-export@example.test", "Firm Admin")
        response = self.client.get("/audit/security-events.csv?limit=100")
        self.assertEqual(response.status_code, 200, response.text)
        rows = list(csv.reader(io.StringIO(response.text.lstrip("\ufeff"))))
        events = [row[3] for row in rows[1:]]
        self.assertNotIn("other_firm_private_event", events)
        self.assertIn("'=HYPERLINK(\"https://example.invalid\")", events)
        self.assertEqual(app._csv_safe_cell("  =1+1"), "'  =1+1")
        self.assertEqual(app._csv_safe_cell("\t=1+1"), "'\t=1+1")

    def test_non_admin_cannot_export_and_limits_are_validated(self):
        self.client.cookies.clear()
        self.login("lawyer-export@example.test", "Firm Lawyer")
        denied = self.client.get("/audit/security-events.csv")
        self.assertEqual(denied.status_code, 403)
        self.client.cookies.clear()
        self.login("admin-export@example.test", "Firm Admin")
        self.assertEqual(self.client.get("/audit/security-events.csv?limit=5001").status_code, 422)
        self.assertEqual(self.client.get("/audit/security-events.csv?offset=-1").status_code, 422)


if __name__ == "__main__":
    unittest.main()
