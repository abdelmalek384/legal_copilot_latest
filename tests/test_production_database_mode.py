import os
import subprocess
import sys
import unittest


class ProductionDatabaseModeTests(unittest.TestCase):
    def test_production_startup_requires_host_cookie_origin_admin_and_backup_settings(self):
        env = os.environ.copy()
        env.pop("COPILOT_DB", None)
        env.update({
            "COPILOT_ENV": "production",
            "COPILOT_CONTROL_DB": "/tmp/legal-copilot-control.sqlite3",
            "COPILOT_TENANT_DB_ROOT": "/tmp/legal-copilot-tenants",
            "COPILOT_CORPUS_DB": "/tmp/legal-copilot-corpus.sqlite3",
        })
        result = subprocess.run(
            [sys.executable, "-c", "import app"],
            env=env, capture_output=True, text=True, timeout=30,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("COPILOT_ALLOWED_HOSTS is required in production", result.stderr)
        self.assertIn("COPILOT_SECURE_COOKIES=1 is required in production", result.stderr)
        self.assertIn("BACKUP_KEY must be a valid Fernet key", result.stderr)

    def test_production_startup_accepts_explicit_hardened_configuration(self):
        from cryptography.fernet import Fernet
        with __import__("tempfile").TemporaryDirectory() as temp:
            env = os.environ.copy()
            env.pop("COPILOT_DB", None)
            env.update({
                "COPILOT_ENV": "production",
                "COPILOT_CONTROL_DB": os.path.join(temp, "control.sqlite3"),
                "COPILOT_TENANT_DB_ROOT": os.path.join(temp, "tenants"),
                "COPILOT_CORPUS_DB": os.path.join(temp, "corpus.sqlite3"),
                "COPILOT_ALLOWED_HOSTS": "legal.example.test",
                "COPILOT_SECURE_COOKIES": "1",
                "COPILOT_PUBLIC_ORIGIN": "https://legal.example.test",
                "ADMIN_TOKEN": "A" * 48,
                "BACKUP_KEY": Fernet.generate_key().decode("ascii"),
            })
            result = subprocess.run(
                [sys.executable, "-c", "import app"],
                env=env, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_app_refuses_legacy_shared_database_in_production(self):
        env = os.environ.copy()
        for key in ("COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB"):
            env.pop(key, None)
        env["COPILOT_ENV"] = "production"
        env["COPILOT_DB"] = "/tmp/legacy-shared.sqlite3"
        result = subprocess.run(
            [sys.executable, "-c", "import app"],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Production requires explicit separate database paths", result.stderr)


if __name__ == "__main__":
    unittest.main()
