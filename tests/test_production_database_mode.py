import json
import os
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tools.database_release_acceptance import original_storage_config_fingerprint


class ProductionDatabaseModeTests(unittest.TestCase):
    @staticmethod
    def _storage_config():
        return {
            "COPILOT_OBJECT_STORAGE_BACKEND": "s3",
            "COPILOT_S3_BUCKET": "acceptance-test-bucket",
            "COPILOT_S3_REGION": "us-east-1",
            "COPILOT_S3_KMS_KEY_ID": "test-kms-key",
            "COPILOT_S3_ENDPOINT_URL": "",
            "COPILOT_S3_RECOVERY_BUCKET": "acceptance-recovery-test-bucket",
            "COPILOT_S3_RECOVERY_REGION": "us-east-1",
            "COPILOT_S3_RECOVERY_KMS_KEY_ID": "test-recovery-kms-key",
            "COPILOT_S3_RECOVERY_ENDPOINT_URL": "",
        }

    def _write_acceptance_manifest(self, path):
        stamp = datetime.now(timezone.utc).isoformat()
        manifest = {
            "schema_version": 1,
            "gates": {
                "original_file_storage": {
                    "status": "passed", "evidence_ref": "synthetic-test-evidence",
                    "verified_at": stamp, "verified_by": "test-operator",
                    "storage_config_sha256": original_storage_config_fingerprint(self._storage_config()),
                },

                "purge_writer_quiescence": {
                    "status": "passed", "evidence_ref": "synthetic-test-evidence",
                    "verified_at": stamp, "verified_by": "test-operator",
                    "witnessed_by": "independent-test-witness",
                    "storage_config_sha256": original_storage_config_fingerprint(self._storage_config()),
                    "verified_scenarios": [
                        "upload_finalize_workers_drained",
                        "non_purge_principals_denied_put_object",
                        "purge_role_denied_put_object",
                        "bucket_policy_and_iam_changes_frozen",
                        "cloudtrail_negative_tests_retained",
                    ],
                },\n                "backup_restore_rollback": {
                    "status": "passed", "evidence_ref": "synthetic-test-evidence",
                    "verified_at": stamp, "verified_by": "test-operator",
                    "witnessed_by": "independent-test-witness",
                    "verified_scenarios": [
                        "staging_restore", "rollback", "staged_upload_recovery", "deletion_recovery",
                    ],
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
            env.update(self._storage_config())
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
            # Production runtime is attach-only: provision empty synthetic profiles
            # through the development bootstrap path before testing production startup.
            bootstrap_env = dict(env)
            bootstrap_env["COPILOT_ENV"] = "development"
            bootstrap = subprocess.run(
                [
                    sys.executable, "-c",
                    "from database_runtime import DatabaseRuntime; "
                    "runtime = DatabaseRuntime.from_env(); runtime.initialize()",
                ],
                env=bootstrap_env, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(bootstrap.returncode, 0, bootstrap.stderr)
            tenant_root = Path(env["COPILOT_TENANT_DB_ROOT"])
            if os.name == "posix":
                os.chmod(tenant_root, 0o700)
            result = subprocess.run(
                [
                    sys.executable, "-c",
                    "from fastapi.testclient import TestClient; import app; "
                    "from database_runtime import DatabaseRuntime; "
                    "runtime = DatabaseRuntime.from_env(); runtime.initialize(); "
                    "client = TestClient(app.app); client.__enter__(); client.__exit__(None, None, None)",
                ],
                env=env, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_production_startup_rejects_acceptance_for_changed_storage_target(self):
        from cryptography.fernet import Fernet
        with __import__("tempfile").TemporaryDirectory() as temp:
            env = os.environ.copy()
            env.pop("COPILOT_DB", None)
            acceptance_path = self._write_acceptance_manifest(Path(temp) / "database-acceptance.json")
            env["COPILOT_DATABASE_ACCEPTANCE_FILE"] = str(acceptance_path)
            env.update(self._storage_config())
            # Evidence was recorded for the fixture bucket; production is now pointed
            # at a different bucket and must reject that stale acceptance.
            env["COPILOT_S3_BUCKET"] = "changed-after-acceptance"
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
            bootstrap_env = dict(env)
            bootstrap_env["COPILOT_ENV"] = "development"
            bootstrap = subprocess.run(
                [
                    sys.executable, "-c",
                    "from database_runtime import DatabaseRuntime; "
                    "runtime = DatabaseRuntime.from_env(); runtime.initialize()",
                ],
                env=bootstrap_env, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(bootstrap.returncode, 0, bootstrap.stderr)
            tenant_root = Path(env["COPILOT_TENANT_DB_ROOT"])
            if os.name == "posix":
                os.chmod(tenant_root, 0o700)
            result = subprocess.run(
                [
                    sys.executable, "-c",
                    "from fastapi.testclient import TestClient; import app; "
                    "from database_runtime import DatabaseRuntime; "
                    "runtime = DatabaseRuntime.from_env(); runtime.initialize(); "
                    "client = TestClient(app.app); client.__enter__(); client.__exit__(None, None, None)",
                ],
                env=env, capture_output=True, text=True, timeout=60,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "complete accepted database operational evidence manifest",
                result.stderr,
            )

    def test_production_startup_refuses_unprovisioned_database_profiles(self):
        with __import__("tempfile").TemporaryDirectory() as temp:
            acceptance_path = self._write_acceptance_manifest(
                Path(temp) / "database-acceptance.json"
            )
            env = os.environ.copy()
            for key in ("COPILOT_DB",):
                env.pop(key, None)
            env.update(self._storage_config())
            env.update({
                "COPILOT_ENV": "production",
                "COPILOT_DATABASE_ACCEPTANCE_FILE": str(acceptance_path),
                "COPILOT_CONTROL_DB": os.path.join(temp, "missing-control.sqlite3"),
                "COPILOT_TENANT_DB_ROOT": os.path.join(temp, "missing-tenants"),
                "COPILOT_CORPUS_DB": os.path.join(temp, "missing-corpus.sqlite3"),
                "COPILOT_ALLOWED_HOSTS": "legal.example.test",
                "COPILOT_SECURE_COOKIES": "1",
                "COPILOT_PUBLIC_ORIGIN": "https://legal.example.test",
                "ADMIN_TOKEN": "A" * 48,
            })
            from cryptography.fernet import Fernet
            env["BACKUP_KEY"] = Fernet.generate_key().decode("ascii")
            result = subprocess.run(
                [
                    sys.executable, "-c",
                    "from fastapi.testclient import TestClient; import app; "
                    "client = TestClient(app.app); client.__enter__()",
                ],
                env=env, capture_output=True, text=True, timeout=60,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "Production database profiles must be provisioned and validated before application startup",
            result.stderr,
        )

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

    def test_shared_database_compatibility_is_rejected_in_every_environment(self):
        for environment in ("", "development", "dev", "test", "staging", "production"):
            with self.subTest(environment=environment), __import__("tempfile").TemporaryDirectory() as temp:
                env = os.environ.copy()
                for key in ("COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB"):
                    env.pop(key, None)
                if environment:
                    env["COPILOT_ENV"] = environment
                else:
                    env.pop("COPILOT_ENV", None)
                env["COPILOT_DB"] = os.path.join(temp, "shared.sqlite3")
                result = subprocess.run(
                    [sys.executable, "-c", "import app; app.conn()"],
                    env=env, capture_output=True, text=True, timeout=30,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("COPILOT_DB is no longer supported", result.stderr)

    def test_legacy_connection_helper_fails_closed_even_when_called_directly(self):
        env = os.environ.copy()
        env.pop("COPILOT_DB", None)
        env["COPILOT_ENV"] = "development"
        for key in ("COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB"):
            env.pop(key, None)
        result = subprocess.run(
            [sys.executable, "-c", "import app; app._legacy_conn()"],
            env=env, capture_output=True, text=True, timeout=30,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("shared COPILOT_DB database runtime is retired", result.stderr)


if __name__ == "__main__":
    unittest.main()
