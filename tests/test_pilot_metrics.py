"""Platform-only weekly pilot metrics expose counts, never matter content."""
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


class PilotMetricsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-pilot-metrics-")
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
            "ADMIN_TOKEN": "pilot-metrics-test-admin-token",
        })
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Pilot Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Pilot Firm B")
        self.clients = {}
        self.user_ids = {}
        for suffix, firm_id in (("a", self.firm_a), ("b", self.firm_b)):
            email = f"pilot-{suffix}@example.test"
            password = f"Pilot-{suffix}-password-2026!"
            self.runtime.create_initial_firm_owner(
                firm_id, f"Pilot Admin {suffix}", email, app.hash_pw(password)
            )
            user_id = int(app.control_conn().execute(
                "SELECT id FROM users WHERE email_normalized=?", (email,)
            ).fetchone()["id"])
            self.user_ids[suffix] = user_id
            client = TestClient(app.app)
            response = client.post("/login", json={"email": email, "password": password})
            self.assertEqual(response.status_code, 200, response.text)
            self.clients[suffix] = client
            active = client.get("/session")
            self.assertEqual(active.status_code, 200, active.text)
        control = app.control_conn()
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name,granted_by_user_id) VALUES(?,'platform_admin',?)",
            (self.user_ids["a"], self.user_ids["a"]),
        )
        control.commit()

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

    def test_platform_metrics_are_weekly_counts_and_firm_users_cannot_view_them(self):
        now = int(datetime(2026, 11, 3, 12, tzinfo=timezone.utc).timestamp())
        control = app.control_conn()
        app._record_pilot_metric(control, self.firm_a, self.user_ids["a"], "case_created", now)
        app._record_pilot_metric(control, self.firm_a, self.user_ids["a"], "deadline_created", now)
        app._record_pilot_metric(control, self.firm_a, self.user_ids["a"], "answer_requested", now)
        app._record_pilot_metric(control, self.firm_b, self.user_ids["b"], "invoice_issued", now)
        platform_response = self.clients["a"].get("/platform/pilot-metrics?weeks=4")
        self.assertEqual(platform_response.status_code, 200, platform_response.text)
        rows = platform_response.json()["metrics"]
        by_firm = {row["firm_id"]: row for row in rows}
        self.assertEqual(set(by_firm), {self.firm_a, self.firm_b})
        self.assertEqual(by_firm[self.firm_a]["active_users"], 1)
        self.assertEqual(by_firm[self.firm_a]["cases_created"], 1)
        self.assertEqual(by_firm[self.firm_a]["deadlines_created"], 1)
        self.assertEqual(by_firm[self.firm_a]["answers_requested"], 1)
        self.assertEqual(by_firm[self.firm_a]["invoices_issued"], 0)
        self.assertEqual(by_firm[self.firm_a]["corrections_submitted"], 0)
        self.assertEqual(by_firm[self.firm_b]["active_users"], 1)
        self.assertEqual(by_firm[self.firm_b]["invoices_issued"], 1)
        denied = self.clients["b"].get("/platform/pilot-metrics")
        self.assertEqual(denied.status_code, 403, denied.text)

    def test_csv_export_is_platform_only_and_contains_aggregate_columns(self):
        now = int(datetime(2026, 11, 3, 12, tzinfo=timezone.utc).timestamp())
        app._record_pilot_metric(app.control_conn(), self.firm_a, self.user_ids["a"], "correction_submitted", now)
        response = self.clients["a"].get("/platform/pilot-metrics/export.csv?weeks=4")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn("text/csv", response.headers.get("content-type", ""))
        self.assertIn("corrections_submitted", response.text)
        self.assertIn("Pilot Firm A", response.text)
        self.assertNotIn("correction_note", response.text)
        denied = self.clients["b"].get("/platform/pilot-metrics/export.csv")
        self.assertEqual(denied.status_code, 403, denied.text)

    def test_metric_ledger_rejects_content_categories_and_mutations(self):
        control = app.control_conn()
        with self.assertRaises(ValueError):
            app._record_pilot_metric(control, self.firm_a, self.user_ids["a"], "case_contents")
        app._record_pilot_metric(control, self.firm_a, self.user_ids["a"], "case_created")
        row_id = control.execute("SELECT id FROM pilot_metrics_events").fetchone()["id"]
        with self.assertRaisesRegex(Exception, "immutable"):
            control.execute("UPDATE pilot_metrics_events SET metric='invoice_issued' WHERE id=?", (row_id,))
        with self.assertRaisesRegex(Exception, "immutable"):
            control.execute("DELETE FROM pilot_metrics_events WHERE id=?", (row_id,))
        columns = {row["name"] for row in control.execute("PRAGMA table_info(pilot_metrics_events)")}
        self.assertEqual(columns, {"id", "firm_id", "user_id", "metric", "week_start", "occurred_at"})


if __name__ == "__main__":
    unittest.main()
