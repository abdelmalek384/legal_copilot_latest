"""Tenant-local per-user reminder preference API tests."""
import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


class ReminderPreferencesRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-reminder-prefs-")
        self.root = Path(self.temp.name)
        self.env_names = (
            "COPILOT_DB", "COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT",
            "COPILOT_CORPUS_DB", "COPILOT_OBJECT_STORAGE_ROOT",
            "COPILOT_OBJECT_STORAGE_BACKEND", "COPILOT_ENV", "ADMIN_TOKEN",
        )
        self.old_env = {name: os.environ.get(name) for name in self.env_names}
        os.environ.pop("COPILOT_DB", None)
        os.environ.update(
            COPILOT_CONTROL_DB=str(self.root / "control.sqlite3"),
            COPILOT_TENANT_DB_ROOT=str(self.root / "tenants"),
            COPILOT_CORPUS_DB=str(self.root / "corpus.sqlite3"),
            COPILOT_OBJECT_STORAGE_ROOT=str(self.root / "objects"),
            COPILOT_OBJECT_STORAGE_BACKEND="local",
            COPILOT_ENV="development",
            ADMIN_TOKEN="reminder-prefs-test-admin-token-long-enough",
        )
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Reminder Preferences A")
        self.firm_b, _ = self.runtime.provision_firm("Reminder Preferences B")
        self.password = "Reminder-prefs-test-password-2026!"
        self.runtime.create_initial_firm_owner(
            self.firm_a, "Reminder Owner A", "reminder-owner-a@example.test",
            app.hash_pw(self.password),
        )
        self.runtime.create_initial_firm_owner(
            self.firm_b, "Reminder Owner B", "reminder-owner-b@example.test",
            app.hash_pw(self.password),
        )
        self.client_a = TestClient(app.app)
        self.client_b = TestClient(app.app)
        for client, email in (
            (self.client_a, "reminder-owner-a@example.test"),
            (self.client_b, "reminder-owner-b@example.test"),
        ):
            response = client.post("/login", json={"email": email, "password": self.password})
            self.assertEqual(response.status_code, 200, response.text)

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

    @staticmethod
    def mutate(client, method, url, **kwargs):
        headers = dict(kwargs.pop("headers", {}) or {})
        headers["X-CSRF-Token"] = client.cookies.get("lc_csrf", "")
        return getattr(client, method)(url, headers=headers, **kwargs)

    def test_get_returns_safe_defaults_without_creating_rows(self):
        response = self.client_a.get("/reminder-preferences")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(set(response.json()), {
            "email_enabled", "deadline_7_days", "deadline_3_days", "deadline_1_day",
            "deadline_day_of", "deadline_overdue", "session_day_of", "task_reminders",
        })
        self.assertTrue(all(response.json().values()))
        tenant = self.runtime._tenant_router.connection_for_firm(self.firm_a)
        self.assertEqual(tenant.execute("SELECT COUNT(*) FROM reminder_preferences").fetchone()[0], 0)

    def test_user_can_update_and_read_back_all_preferences(self):
        payload = {
            "email_enabled": True,
            "deadline_7_days": False,
            "deadline_3_days": True,
            "deadline_1_day": False,
            "deadline_day_of": True,
            "deadline_overdue": False,
            "session_day_of": False,
            "task_reminders": True,
        }
        saved = self.mutate(self.client_a, "put", "/reminder-preferences", json=payload)
        self.assertEqual(saved.status_code, 200, saved.text)
        self.assertTrue(saved.json()["ok"])
        self.assertEqual({key: saved.json()[key] for key in payload}, payload)
        read_back = self.client_a.get("/reminder-preferences")
        self.assertEqual({key: read_back.json()[key] for key in payload}, payload)

    def test_preferences_are_isolated_between_firms(self):
        payload = {
            "email_enabled": False,
            "deadline_7_days": False,
            "deadline_3_days": False,
            "deadline_1_day": False,
            "deadline_day_of": False,
            "deadline_overdue": False,
            "session_day_of": False,
            "task_reminders": False,
        }
        saved = self.mutate(self.client_a, "put", "/reminder-preferences", json=payload)
        self.assertEqual(saved.status_code, 200, saved.text)
        other_firm = self.client_b.get("/reminder-preferences")
        self.assertEqual(other_firm.status_code, 200, other_firm.text)
        self.assertTrue(all(other_firm.json().values()))
        tenant_a = self.runtime._tenant_router.connection_for_firm(self.firm_a)
        tenant_b = self.runtime._tenant_router.connection_for_firm(self.firm_b)
        self.assertEqual(tenant_a.execute("SELECT COUNT(*) FROM reminder_preferences").fetchone()[0], 1)
        self.assertEqual(tenant_b.execute("SELECT COUNT(*) FROM reminder_preferences").fetchone()[0], 0)

    def test_invalid_payload_is_rejected(self):
        response = self.mutate(
            self.client_a, "put", "/reminder-preferences",
            json={"deadline_7_days": "not-a-boolean"},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
