"""Per-user reminder preferences stay isolated in each firm's tenant database."""
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
            ADMIN_TOKEN="reminder-preferences-test-admin-token",
        )
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Reminder Preferences A")
        self.firm_b, _ = self.runtime.provision_firm("Reminder Preferences B")
        self.password = "Reminder-preferences-test-password-2026!"
        self.runtime.create_initial_firm_owner(
            self.firm_a, "Shared Reminder Owner", "reminder-owner@example.test",
            app.hash_pw(self.password),
        )
        user = self.runtime.control_connection().execute(
            "SELECT id FROM users WHERE email_canonical=?",
            ("reminder-owner@example.test",),
        ).fetchone()
        self.user_id = int(user["id"])
        self.runtime.create_firm_membership(self.user_id, self.firm_b, "lawyer")
        self.client = TestClient(app.app)
        login = self.client.post(
            "/login", json={"email": "reminder-owner@example.test", "password": self.password}
        )
        self.assertEqual(login.status_code, 200, login.text)

    def tearDown(self):
        self.client.close()
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

    def _mutate(self, method, url, **kwargs):
        headers = dict(kwargs.pop("headers", {}) or {})
        headers["X-CSRF-Token"] = self.client.cookies.get("lc_csrf", "")
        return getattr(self.client, method)(url, headers=headers, **kwargs)

    def test_preferences_default_and_persist_for_current_user(self):
        initial = self.client.get("/reminder-preferences")
        self.assertEqual(initial.status_code, 200, initial.text)
        self.assertTrue(all(initial.json().values()))
        payload = {
            "email_enabled": True, "deadline_7_days": True, "deadline_3_days": False,
            "deadline_1_day": True, "deadline_day_of": False, "deadline_overdue": False,
            "session_day_of": True, "task_reminders": False,
        }
        saved = self._mutate("put", "/reminder-preferences", json=payload)
        self.assertEqual(saved.status_code, 200, saved.text)
        self.assertEqual({k: v for k, v in saved.json().items() if k != "ok"}, payload)
        self.assertEqual(self.client.get("/reminder-preferences").json(), payload)

    def test_same_identity_sees_separate_preferences_in_each_firm_database(self):
        a_preferences = {
            "email_enabled": True, "deadline_7_days": False, "deadline_3_days": True,
            "deadline_1_day": False, "deadline_day_of": True, "deadline_overdue": False,
            "session_day_of": True, "task_reminders": False,
        }
        saved_a = self._mutate("put", "/reminder-preferences", json=a_preferences)
        self.assertEqual(saved_a.status_code, 200, saved_a.text)

        switched = self._mutate("post", "/session/firm", json={"firm_id": self.firm_b})
        self.assertEqual(switched.status_code, 200, switched.text)
        prefs_b = self.client.get("/reminder-preferences")
        self.assertEqual(prefs_b.status_code, 200, prefs_b.text)
        self.assertTrue(all(prefs_b.json().values()), "firm B must not inherit firm A preferences")

        b_preferences = dict(a_preferences)
        b_preferences["email_enabled"] = False
        saved_b = self._mutate("put", "/reminder-preferences", json=b_preferences)
        self.assertEqual(saved_b.status_code, 200, saved_b.text)

        switched_back = self._mutate("post", "/session/firm", json={"firm_id": self.firm_a})
        self.assertEqual(switched_back.status_code, 200, switched_back.text)
        self.assertEqual(self.client.get("/reminder-preferences").json(), a_preferences)


if __name__ == "__main__":
    unittest.main()
