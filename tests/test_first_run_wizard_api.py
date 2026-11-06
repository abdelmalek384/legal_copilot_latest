"""First-run setup, profile isolation, health explanations, and fake SMTP delivery."""
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


class FirstRunWizardApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-first-run-")
        self.root = Path(self.temp.name)
        self.env_names = (
            "COPILOT_DB", "COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT",
            "COPILOT_CORPUS_DB", "COPILOT_OBJECT_STORAGE_ROOT",
            "COPILOT_OBJECT_STORAGE_BACKEND", "COPILOT_ENV", "ADMIN_TOKEN",
            "COPILOT_EMAIL_SMTP_HOST", "COPILOT_EMAIL_FROM", "COPILOT_EMAIL_SMTP_PORT",
            "COPILOT_EMAIL_SMTP_SECURITY", "COPILOT_EMAIL_SMTP_USERNAME", "COPILOT_EMAIL_SMTP_PASSWORD",
            "REMINDER_SMTP_HOST", "REMINDER_SMTP_SENDER", "REMINDER_SMTP_PORT",
            "REMINDER_SMTP_SECURITY", "REMINDER_SMTP_USERNAME", "REMINDER_SMTP_PASSWORD",
            "COPILOT_PUBLIC_ORIGIN", "MFA_ENCRYPTION_KEY", "MFA_ENFORCEMENT", "BACKUP_KEY",
        )
        self.old_env = {name: os.environ.get(name) for name in self.env_names}
        for name in self.env_names:
            os.environ.pop(name, None)
        os.environ.update({
            "COPILOT_CONTROL_DB": str(self.root / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(self.root / "tenants"),
            "COPILOT_CORPUS_DB": str(self.root / "corpus.sqlite3"),
            "COPILOT_OBJECT_STORAGE_ROOT": str(self.root / "objects"),
            "COPILOT_OBJECT_STORAGE_BACKEND": "local",
            "COPILOT_ENV": "development",
            "ADMIN_TOKEN": "first-run-test-admin-token-long-enough",
        })
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("مكتب ألف")
        self.firm_b, _ = self.runtime.provision_firm("مكتب باء")
        self.clients = {}
        self.user_ids = {}
        for key, firm_id in (("a", self.firm_a), ("b", self.firm_b)):
            email = f"first-run-{key}@example.test"
            password = f"FirstRun-{key}-Strong-Password-2026!"
            self.runtime.create_initial_firm_owner(
                firm_id, f"مدير {key}", email, app.hash_pw(password)
            )
            user_id = int(self.runtime.control_connection().execute(
                "SELECT id FROM users WHERE email_normalized=?", (email,)
            ).fetchone()["id"])
            self.user_ids[key] = user_id
            client = TestClient(app.app)
            login = client.post("/login", json={"email": email, "password": password})
            self.assertEqual(login.status_code, 200, login.text)
            self.clients[key] = client

    def tearDown(self):
        for client in self.clients.values():
            client.close()
        if app._database_runtime is not None:
            try:
                app._database_runtime.close_current_thread()
            except Exception:
                pass
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

    def test_profile_and_first_run_are_scoped_to_the_active_firm(self):
        initial = self.clients["a"].get("/setup/first-run")
        self.assertEqual(initial.status_code, 200, initial.text)
        self.assertEqual(initial.json()["total"], 6)
        self.assertEqual(initial.json()["completed"], 0)
        self.assertIsInstance(initial.json()["onboarding_started_at"], int)
        self.assertIsNone(initial.json()["onboarding_completed_at"])
        self.assertIsNone(initial.json()["onboarding_completion_seconds"])
        updated = self.clients["a"].put("/firm/profile", json={
            "name": "مكتب ألف للمحاماة", "phone": "+20 100 123 4567", "address": "القاهرة — بيانات تجريبية",
        }, headers={"X-CSRF-Token": self.clients["a"].cookies.get("lc_csrf")})
        self.assertEqual(updated.status_code, 200, updated.text)
        self.assertEqual(updated.json()["name"], "مكتب ألف للمحاماة")
        profile_b = self.clients["b"].get("/firm/profile")
        self.assertEqual(profile_b.status_code, 200, profile_b.text)
        self.assertEqual(profile_b.json()["name"], "مكتب باء")
        self.assertNotIn("مكتب ألف للمحاماة", profile_b.text)
        checklist = self.clients["a"].get("/setup/first-run").json()
        self.assertTrue(checklist["checklist"][0]["done"])
        self.assertFalse(checklist["checklist"][1]["done"])
        self.assertIsNone(checklist["onboarding_completed_at"])
        self.assertIsNone(checklist["onboarding_completion_seconds"])
        context = self.runtime.resolve_context(self.user_ids["a"], self.firm_a)
        tenant = self.runtime.firm_connection(context)
        case_id = tenant.execute(
            "INSERT INTO cases(title,client,stage,created_by,firm_id) VALUES(?,?,?,?,?)",
            ("قضية تجريبية", "عميل افتراضي", "تجهيز", self.user_ids["a"], self.firm_a),
        ).lastrowid
        tenant.execute(
            "INSERT INTO deadlines(case_id,title,due,created_by) VALUES(?,?,?,?)",
            (case_id, "موعد تجريبي", "2026-12-01", self.user_ids["a"]),
        )
        tenant.commit()
        checklist = self.clients["a"].get("/setup/first-run").json()
        self.assertTrue(checklist["checklist"][3]["done"])
        self.assertTrue(checklist["checklist"][4]["done"])
        self.assertEqual(checklist["first_case_id"], case_id)

    def test_onboarding_duration_is_recorded_once_when_all_steps_complete(self):
        initial = self.clients["a"].get("/setup/first-run")
        self.assertEqual(initial.status_code, 200, initial.text)
        started_at = initial.json()["onboarding_started_at"]
        control = self.runtime.control_connection()
        now = int(datetime.now(timezone.utc).timestamp())
        profile = self.clients["a"].put(
            "/firm/profile",
            json={"name":"مكتب ألف للمحاماة","phone":"+20 100 123 4567","address":"بيانات تجريبية"},
            headers={"X-CSRF-Token":self.clients["a"].cookies.get("lc_csrf")},
        )
        self.assertEqual(profile.status_code, 200, profile.text)
        control.execute(
            "INSERT INTO identity_invitations(firm_id,email_normalized,email_display,invited_role,token_hash,"
            "invited_by_user_id,created_at,expires_at,status,updated_at) "
            "VALUES(?,?,?,?,?,?,?,?, 'pending',?)",
            (self.firm_a,"colleague-a@example.test","colleague-a@example.test","lawyer",
             "a"*64,self.user_ids["a"],now,now+3600,now),
        )
        control.execute(
            "INSERT INTO firm_setup_events(firm_id,actor_user_id,event_type,provider_status) "
            "VALUES(?,?,'test_reminder_accepted','accepted_by_smtp')",
            (self.firm_a,self.user_ids["a"]),
        )
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name,granted_by_user_id) "
            "VALUES(?,'platform_admin',?)",
            (self.user_ids["a"],self.user_ids["a"]),
        )
        control.commit()
        context = self.runtime.resolve_context(self.user_ids["a"], self.firm_a)
        tenant = self.runtime.firm_connection(context)
        case_id = tenant.execute(
            "INSERT INTO cases(title,client,stage,created_by,firm_id) VALUES(?,?,?,?,?)",
            ("Matter for onboarding", "Synthetic Client", "open", self.user_ids["a"], self.firm_a),
        ).lastrowid
        tenant.execute(
            "INSERT INTO deadlines(case_id,title,due,created_by) VALUES(?,?,?,?)",
            (case_id,"First hearing","2026-12-01",self.user_ids["a"]),
        )
        tenant.commit()
        with patch("app._mfa_is_enabled", return_value=True):
            completed = self.clients["a"].get("/setup/first-run")
            self.assertEqual(completed.status_code, 200, completed.text)
            self.assertEqual(completed.json()["completed"], 6)
            self.assertIsInstance(completed.json()["onboarding_completed_at"], int)
            self.assertGreaterEqual(completed.json()["onboarding_completion_seconds"], 0)
            repeated = self.clients["a"].get("/setup/first-run")
        self.assertEqual(repeated.json()["onboarding_started_at"], started_at)
        self.assertEqual(repeated.json()["onboarding_completed_at"], completed.json()["onboarding_completed_at"])
        self.assertEqual(repeated.json()["onboarding_completion_seconds"], completed.json()["onboarding_completion_seconds"])
        platform = self.clients["a"].get("/platform/pilot-metrics")
        self.assertEqual(platform.status_code, 200, platform.text)
        measured = next(row for row in platform.json()["onboarding"] if row["firm_id"] == self.firm_a)
        self.assertEqual(measured["completion_seconds"], completed.json()["onboarding_completion_seconds"])
        self.assertIsNone(next(row for row in platform.json()["onboarding"] if row["firm_id"] == self.firm_b)["started_at"])
        self.assertEqual(self.clients["b"].get("/platform/pilot-metrics").status_code, 403)

    def test_setup_health_explains_missing_configuration_without_exposing_secrets(self):
        response = self.clients["a"].get("/setup/health")
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        checks = {item["id"]: item for item in payload["checks"]}
        self.assertFalse(checks["reminder_smtp"]["ok"])
        self.assertFalse(checks["public_origin"]["ok"])
        self.assertFalse(checks["mfa_key"]["ok"])
        self.assertTrue(checks["mfa_key"]["message_ar"])
        self.assertNotIn(os.environ["ADMIN_TOKEN"], response.text)
        self.assertNotIn("MFA_ENCRYPTION_KEY=", response.text)
        blocked = self.clients["a"].post(
            "/setup/test-reminder",
            headers={"X-CSRF-Token": self.clients["a"].cookies.get("lc_csrf")},
        )
        self.assertEqual(blocked.status_code, 200, blocked.text)
        self.assertEqual(blocked.json()["status"], "blocked")

    def test_test_reminder_uses_fake_smtp_and_records_only_acceptance_metadata(self):
        os.environ.update({
            "REMINDER_SMTP_HOST": "smtp.example.test",
            "REMINDER_SMTP_SENDER": "reminders@example.test",
            "REMINDER_SMTP_USERNAME": "synthetic-user",
            "REMINDER_SMTP_PASSWORD": "synthetic-password",
            "COPILOT_PUBLIC_ORIGIN": "https://app.example.test",
            "MFA_ENCRYPTION_KEY": Fernet.generate_key().decode("ascii"),
        })
        with patch("tools.reminder_email._smtp_send") as fake_send:
            response = self.clients["a"].post(
                "/setup/test-reminder",
                headers={"X-CSRF-Token": self.clients["a"].cookies.get("lc_csrf")},
            )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["status"], "accepted_by_smtp")
        fake_send.assert_called_once()
        count = self.runtime.control_connection().execute(
            "SELECT COUNT(*) FROM firm_setup_events WHERE firm_id=? AND event_type='test_reminder_accepted'",
            (self.firm_a,),
        ).fetchone()[0]
        self.assertEqual(count, 1)
        self.assertEqual(
            self.runtime.control_connection().execute(
                "SELECT COUNT(*) FROM firm_setup_events WHERE firm_id=?", (self.firm_b,)
            ).fetchone()[0],
            0,
        )


if __name__ == "__main__":
    unittest.main()
