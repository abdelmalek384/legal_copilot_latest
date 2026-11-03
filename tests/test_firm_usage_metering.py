"""Firm usage metering is private, append-only and records no matter content."""
import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


class FirmUsageMeteringRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-usage-")
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
            "ADMIN_TOKEN": "usage-metering-test-admin-token",
        })
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Usage Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Usage Firm B")
        self.clients = {}
        self.user_ids = {}
        for suffix, firm_id in (("a", self.firm_a), ("b", self.firm_b)):
            email = f"usage-{suffix}@example.test"
            password = f"Usage-{suffix}-password-2026!"
            self.runtime.create_initial_firm_owner(
                firm_id, f"Usage Admin {suffix}", email, app.hash_pw(password)
            )
            self.user_ids[suffix] = int(app.control_conn().execute(
                "SELECT id FROM users WHERE email_normalized=?", (email,)
            ).fetchone()["id"])
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

    def test_successful_research_is_metered_and_usage_is_firm_private(self):
        response = self._mutate("a", "post", "/search", json={
            "q": "ما هي مدة الإخطار في قانون العمل؟",
            "scope": "verified_corpus",
        })
        self.assertEqual(response.status_code, 200, response.text)

        billing_a = self.clients["a"].get("/billing")
        billing_b = self.clients["b"].get("/billing")
        self.assertEqual(billing_a.status_code, 200, billing_a.text)
        self.assertEqual(billing_b.status_code, 200, billing_b.text)
        usage_a = billing_a.json()["usage"]["month_to_date"]
        usage_b = billing_b.json()["usage"]["month_to_date"]
        self.assertEqual(usage_a["research_query"]["events"], 1)
        self.assertEqual(usage_a["research_query"]["units"], 1)
        self.assertEqual(usage_b, {})

        control = app.control_conn()
        rows = control.execute(
            "SELECT firm_id,user_id,event_type,units FROM firm_usage_events"
        ).fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(dict(rows[0]), {
            "firm_id": self.firm_a, "user_id": self.user_ids["a"],
            "event_type": "research_query", "units": 1,
        })
        columns = {row["name"] for row in control.execute(
            "PRAGMA table_info(firm_usage_events)"
        ).fetchall()}
        self.assertNotIn("query", columns)
        self.assertNotIn("case_id", columns)
        self.assertNotIn("content", columns)

    def test_usage_events_are_append_only_and_reject_unknown_categories(self):
        control = app.control_conn()
        app._record_firm_usage(control, self.firm_a, self.user_ids["a"], "document_upload")
        event_id = control.execute("SELECT id FROM firm_usage_events").fetchone()["id"]
        with self.assertRaisesRegex(Exception, "immutable"):
            control.execute("UPDATE firm_usage_events SET units=99 WHERE id=?", (event_id,))
        with self.assertRaisesRegex(Exception, "immutable"):
            control.execute("DELETE FROM firm_usage_events WHERE id=?", (event_id,))
        with self.assertRaises(ValueError):
            app._record_firm_usage(control, self.firm_a, self.user_ids["a"], "case_contents")
        self.assertEqual(control.execute(
            "SELECT COUNT(*) FROM firm_usage_events"
        ).fetchone()[0], 1)



    def test_platform_pilot_metrics_are_aggregate_only_and_platform_admin_only(self):
        control = app.control_conn()
        # The successful sign-in during setUp contributes one active-user sign-in.
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,'platform_admin')",
            (self.user_ids["a"],),
        )
        control.commit()
        for metric in (
            "cases_created", "deadlines_created", "answers_requested",
            "invoices_issued", "corrections_submitted",
        ):
            app._record_pilot_metric(control, self.firm_a, metric)

        schema_columns = {
            row["name"] for row in control.execute(
                "PRAGMA table_info(firm_weekly_pilot_metrics)"
            ).fetchall()
        }
        self.assertEqual(
            schema_columns,
            {"firm_id", "week_start", "metric", "count", "updated_at"},
        )
        self.assertEqual(
            control.execute(
                "SELECT COUNT(*) FROM firm_weekly_pilot_metrics WHERE firm_id=?",
                (self.firm_a,),
            ).fetchone()[0],
            6,
        )

        visible = self.clients["a"].get("/platform/pilot-metrics?weeks=4")
        self.assertEqual(visible.status_code, 200, visible.text)
        payload = visible.json()
        self.assertEqual(set(payload["metrics"]), set(app._PILOT_METRICS))
        self.assertIn("not distinct people", payload["active_users_definition"])
        firm_a_rows = [row for row in payload["items"] if row["firm_id"] == self.firm_a]
        firm_b_rows = [row for row in payload["items"] if row["firm_id"] == self.firm_b]
        self.assertEqual(len(firm_a_rows), 4)
        self.assertEqual(len(firm_b_rows), 4)
        current_week = app._pilot_week_start(int(__import__("time").time()))
        firm_a_current = next(row for row in firm_a_rows if row["week_start"] == current_week)
        for metric in app._PILOT_METRICS:
            self.assertEqual(firm_a_current[metric], 1, metric)
        self.assertEqual(sum(row["active_users"] for row in firm_b_rows), 0)
        self.assertNotIn("user_id", str(payload))
        self.assertNotIn("case_id", str(payload))
        self.assertNotIn("content", str(payload))

        exported = self.clients["a"].get("/platform/pilot-metrics.csv?weeks=4")
        self.assertEqual(exported.status_code, 200, exported.text)
        self.assertIn("cases_created", exported.text)
        self.assertNotIn("user_id", exported.text)
        self.assertNotIn("case_id", exported.text)

        # A normal firm administrator, even in a different firm, cannot inspect
        # the platform-wide operator view or its CSV export.
        denied_json = self.clients["b"].get("/platform/pilot-metrics?weeks=4")
        denied_csv = self.clients["b"].get("/platform/pilot-metrics.csv?weeks=4")
        self.assertEqual(denied_json.status_code, 403)
        self.assertEqual(denied_csv.status_code, 403)

if __name__ == "__main__":
    unittest.main()
