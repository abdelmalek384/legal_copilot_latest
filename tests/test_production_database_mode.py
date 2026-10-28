import json
import os
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


class ProductionDatabaseModeTests(unittest.TestCase):
    def _write_acceptance_manifest(self, path):
        stamp = datetime.now(timezone.utc).isoformat()
        manifest = {
            "schema_version": 1,
            "gates": {
                "original_file_storage": {
                    "status": "passed", "evidence_ref": "synthetic-test-evidence",
                    "verified_at": stamp, "verified_by": "test-operator",
                },
                "backup_restore_rollback": {
                    "status": "passed", "evidence_ref": "synthetic-test-evidence",
                    "verified_at": stamp, "verified_by": "test-operator",
                    "witnessed_by": "independent-test-witness",
                },
                "retention_export_deletion_policy": {
                    "status": "passed", "evidence_ref": "synthetic-test-evidence",
                    "approved_at": stamp, "approved_by": "test-policy-owner",
                },
                "production_identity_email": {
                    "status": "passed", "evidence_ref": "synthetic-test-evidence",
                    "verified_at": stamp, "verified_by": "test-operator",
                },
                "privileged_recovery_bootstrap": {
                    "status": "passed", "evidence_ref": "synthetic-test-evidence",
                    "verified_at": stamp, "verified_by": "test-operator",
                    "witnessed_by": "independent-test-witness",
                },
                "independent_security_review": {
                    "status": "passed", "evidence_ref": "synthetic-test-evidence",
                    "reviewed_at": stamp, "reviewer": "independent-security-reviewer",
                    "unresolved_critical_high": 0,
                },
            },
        }
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path

    def test_production_startup_requires_host_cookie_origin_admin_and_backup_settings(self):
        env = os.environ.copy()
        env.pop("COPILOT_DB", None)
        env.pop("COPILOT_DATABASE_ACCEPTANCE_FILE", None)
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
        self.assertIn("COPILOT_DATABASE_ACCEPTANCE_FILE must reference a complete accepted database operational evidence manifest", result.stderr)

    def test_production_startup_accepts_explicit_hardened_configuration(self):
        from cryptography.fernet import Fernet
        with __import__("tempfile").TemporaryDirectory() as temp:
            env = os.environ.copy()
            env.pop("COPILOT_DB", None)
            acceptance_path = self._write_acceptance_manifest(Path(temp) / "database-acceptance.json")
            env["COPILOT_DATABASE_ACCEPTANCE_FILE"] = str(acceptance_path)
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
                [
                    sys.executable, "-c",
                    "from fastapi.testclient import TestClient; import app; "
                    "client = TestClient(app.app); client.__enter__(); client.__exit__(None, None, None)",
                ],
                env=env, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_profile_initialization_failure_blocks_asgi_startup(self):
        with __import__("tempfile").TemporaryDirectory() as temp:
            control_directory = Path(temp) / "control-is-a-directory.sqlite3"
            control_directory.mkdir()
            env = os.environ.copy()
            for key in ("COPILOT_DB", "COPILOT_DATABASE_ACCEPTANCE_FILE"):
                env.pop(key, None)
            env.update({
                "COPILOT_ENV": "development",
                "COPILOT_CONTROL_DB": str(control_directory),
                "COPILOT_TENANT_DB_ROOT": os.path.join(temp, "tenants"),
                "COPILOT_CORPUS_DB": os.path.join(temp, "corpus.sqlite3"),
            })
            result = subprocess.run(
                [
                    sys.executable, "-c",
                    "from fastapi.testclient import TestClient; import app; "
                    "client = TestClient(app.app); client.__enter__()",
                ],
                env=env, capture_output=True, text=True, timeout=60,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Database runtime initialization failed; refusing to start", result.stderr)

    def test_production_startup_blocks_missing_acceptance_even_with_other_settings_valid(self):
        from cryptography.fernet import Fernet
        with __import__("tempfile").TemporaryDirectory() as temp:
            env = os.environ.copy()
            for key in ("COPILOT_DB", "COPILOT_DATABASE_ACCEPTANCE_FILE"):
                env.pop(key, None)
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
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "COPILOT_DATABASE_ACCEPTANCE_FILE must reference a complete accepted database operational evidence manifest",
            result.stderr,
        )

    def test_shared_database_compatibility_requires_explicit_development_mode(self):
        with __import__("tempfile").TemporaryDirectory() as temp:
            env = os.environ.copy()
            env.pop("COPILOT_ENV", None)
            for key in ("COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB"):
                env.pop(key, None)
            env["COPILOT_DB"] = os.path.join(temp, "shared.sqlite3")
            result = subprocess.run(
                [sys.executable, "-c", "import app; app.conn()"],
                env=env, capture_output=True, text=True, timeout=30,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("COPILOT_DB is restricted to explicit development/test mode", result.stderr)

    def test_shared_database_compatibility_is_explicitly_available_in_development(self):
        with __import__("tempfile").TemporaryDirectory() as temp:
            env = os.environ.copy()
            for key in ("COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB"):
                env.pop(key, None)
            env["COPILOT_ENV"] = "development"
            env["COPILOT_DB"] = os.path.join(temp, "shared.sqlite3")
            result = subprocess.run(
                [sys.executable, "-c", "import app; app.conn().close()"],
                env=env, capture_output=True, text=True, timeout=30,
            )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_app_refuses_legacy_shared_database_in_production(self):
        env = os.environ.copy()
        for key in ("COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB"):
            env.pop(key, None)
        env["COPILOT_ENV"] = "production"
        env.pop("COPILOT_DATABASE_ACCEPTANCE_FILE", None)
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
