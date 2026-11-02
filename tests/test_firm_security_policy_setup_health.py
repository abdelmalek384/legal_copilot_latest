"""Per-firm MFA enforcement and onboarding setup-health reporting."""
import os
import tempfile
import unittest
from pathlib import Path

from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


class FirmSecurityPolicySetupHealthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-firm-policy-")
        self.root = Path(self.temp.name)
        self.env_names = (
            "COPILOT_DB", "COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT",
            "COPILOT_CORPUS_DB", "COPILOT_OBJECT_STORAGE_ROOT",
            "COPILOT_OBJECT_STORAGE_BACKEND", "COPILOT_ENV", "ADMIN_TOKEN",
            "MFA_ENCRYPTION_KEY", "MFA_ENFORCEMENT", "COPILOT_PUBLIC_BASE_URL",
            "COPILOT_EMAIL_SMTP_HOST", "COPILOT_EMAIL_FROM",
            "REMINDER_SMTP_HOST", "REMINDER_SMTP_SENDER",
            "REMINDER_SMTP_USERNAME", "REMINDER_SMTP_PASSWORD",
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
            "ADMIN_TOKEN": "firm-security-policy-test-admin-token",
            "MFA_ENCRYPTION_KEY": Fernet.generate_key().decode("ascii"),
            "MFA_ENFORCEMENT": "optional",
            "COPILOT_PUBLIC_BASE_URL": "https://legal.example.test",
            "COPILOT_EMAIL_SMTP_HOST": "smtp.example.test",
            "COPILOT_EMAIL_FROM": "noreply@example.test",
            "REMINDER_SMTP_HOST": "smtp.example.test",
            "REMINDER_SMTP_SENDER": "reminders@example.test",
            "REMINDER_SMTP_USERNAME": "smtp-user",
            "REMINDER_SMTP_PASSWORD": "smtp-password-test-only",
        })
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_a, _ = self.runtime.provision_firm("Policy Firm A")
        self.firm_b, _ = self.runtime.provision_firm("Policy Firm B")
        self.clients = {}
        for suffix, firm_id in (("a-admin", self.firm_a), ("b-admin", self.firm_b)):
            email = f"policy-{suffix}@example.test"
            password = f"Policy-{suffix}-password-2026!"
            self.runtime.create_initial_firm_owner(
                firm_id, f"Policy {suffix}", email, app.hash_pw(password)
            )
            self._add_client(suffix, email, password)
        self._add_lawyer("a", self.firm_a)
        self._add_lawyer("b", self.firm_b)

    def _add_client(self, key, email, password):
        client = TestClient(app.app)
        response = client.post("/login", json={"email": email, "password": password})
        self.assertEqual(response.status_code, 200, response.text)
        self.clients[key] = client

    def _add_lawyer(self, suffix, firm_id):
        email = f"policy-{suffix}-lawyer@example.test"
        password = f"Policy-{suffix}-lawyer-password-2026!"
        user_id = self.runtime.create_global_identity(
            f"Policy {suffix} Lawyer", email, app.hash_pw(password)
        )
        self.runtime.create_firm_membership(user_id, firm_id, "lawyer")
        self._add_client(f"{suffix}-lawyer", email, password)

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

    def test_setup_health_reports_configuration_without_exposing_secrets(self):
        response = self.clients["a-admin"].get("/admin/setup-health")
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertTrue(data["mail"]["identity_smtp_configured"])
        self.assertTrue(data["mail"]["reminder_smtp_configured"])
        self.assertTrue(data["public_base_url"]["configured"])
        self.assertEqual(data["public_base_url"]["value"], "https://legal.example.test")
        self.assertTrue(data["mfa_encryption_key"]["configured"])
        self.assertNotIn("MFA_ENCRYPTION_KEY", str(data))
        self.assertNotIn("smtp-password-test-only", str(data))
        self.assertEqual(self.clients["a-lawyer"].get("/admin/setup-health").status_code, 403)

    def test_mfa_policy_is_per_firm_and_can_target_admins_or_everyone(self):
        self.assertEqual(self.clients["a-admin"].get("/admin/security-policy").json(), {
            "require_mfa_for_admins": False, "require_mfa_for_everyone": False, "updated_at": None,
        })
        denied = self._mutate("a-lawyer", "put", "/admin/security-policy", json={
            "require_mfa_for_admins": True, "require_mfa_for_everyone": False,
        })
        self.assertEqual(denied.status_code, 403)

        admin_policy = self._mutate("a-admin", "put", "/admin/security-policy", json={
            "require_mfa_for_admins": True, "require_mfa_for_everyone": False,
        })
        self.assertEqual(admin_policy.status_code, 200, admin_policy.text)
        self.assertTrue(admin_policy.json()["require_mfa_for_admins"])
        self.assertTrue(self.clients["a-admin"].get("/session").json()["mfa_enrollment_required"])
        self.assertEqual(self.clients["a-admin"].get("/cases").status_code, 403)
        self.assertEqual(self.clients["a-lawyer"].get("/cases").status_code, 200)

        self.assertEqual(self.clients["b-admin"].get("/cases").status_code, 200)
        everyone_policy = self._mutate("b-admin", "put", "/admin/security-policy", json={
            "require_mfa_for_admins": False, "require_mfa_for_everyone": True,
        })
        self.assertEqual(everyone_policy.status_code, 200, everyone_policy.text)
        self.assertTrue(everyone_policy.json()["require_mfa_for_admins"])
        self.assertTrue(everyone_policy.json()["require_mfa_for_everyone"])
        self.assertTrue(self.clients["b-admin"].get("/session").json()["mfa_enrollment_required"])
        self.assertTrue(self.clients["b-lawyer"].get("/session").json()["mfa_enrollment_required"])
        self.assertEqual(self.clients["b-lawyer"].get("/cases").status_code, 403)

        control = app.control_conn()
        self.assertEqual(control.execute("SELECT COUNT(*) FROM firm_security_policy_audit").fetchone()[0], 2)


if __name__ == "__main__":
    unittest.main()
