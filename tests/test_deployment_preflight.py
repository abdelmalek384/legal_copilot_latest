import importlib.util
import os
import io
from contextlib import redirect_stdout
from unittest.mock import patch
import tempfile
import unittest
from pathlib import Path
from cryptography.fernet import Fernet

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "deployment_preflight.py"
SPEC = importlib.util.spec_from_file_location("deployment_preflight", MODULE_PATH)
preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preflight)


class DeploymentPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        root = Path(self.tempdir.name)
        self.db_path = root / "control.sqlite3"
        self.corpus_path = root / "corpus.sqlite3"
        self.tenant_root = root / "tenants"
        self.tenant_root.mkdir()
        (root / "control").mkdir()
        (root / "corpus").mkdir()
        if os.name == "posix":
            os.chmod(self.tenant_root, 0o700)
        self.db_path = root / "control" / "control.sqlite3"
        self.corpus_path = root / "corpus" / "corpus.sqlite3"
        self.env = {
            "ADMIN_TOKEN": "a" * 40,
            "MIN_SCORE": "0.3",
            "COPILOT_CONTROL_DB": str(self.db_path),
            "COPILOT_TENANT_DB_ROOT": str(self.tenant_root),
            "COPILOT_CORPUS_DB": str(self.corpus_path),
        }

    def test_allowed_hosts_preflight_requires_explicit_hostnames_not_urls_or_wildcard_all(self):
        for value in ("legal.example.com,*.example.org", "127.0.0.1", "[::1]"):
            with self.subTest(value=value):
                _, _, errors = preflight.inspect_environment(dict(self.env, COPILOT_ALLOWED_HOSTS=value))
                self.assertFalse(any("COPILOT_ALLOWED_HOSTS must be" in item for item in errors))
        for value in ("*", "https://legal.example.com", "legal.example.com/path", "*.127.0.0.1"):
            with self.subTest(value=value):
                _, _, errors = preflight.inspect_environment(dict(self.env, COPILOT_ALLOWED_HOSTS=value))
                self.assertTrue(any("COPILOT_ALLOWED_HOSTS must be" in item for item in errors))

    def test_production_requires_explicit_host_allowlist(self):
        production = dict(self.env, COPILOT_ENV="production")
        _, _, errors = preflight.inspect_environment(production)
        self.assertTrue(any("COPILOT_ALLOWED_HOSTS is required in production" in item for item in errors))

        configured = dict(production, COPILOT_ALLOWED_HOSTS="legal.example.com,*.example.org")
        _, _, errors = preflight.inspect_environment(configured)
        self.assertFalse(any("COPILOT_ALLOWED_HOSTS" in item for item in errors))

    def test_public_origin_must_be_a_bare_https_origin(self):
        valid = dict(self.env, COPILOT_PUBLIC_ORIGIN="https://legal.example.com")
        _, _, errors = preflight.inspect_environment(valid)
        self.assertFalse(any("COPILOT_PUBLIC_ORIGIN" in item for item in errors))
        for origin in ("http://legal.example.com", "https://user:pass@legal.example.com", "https://legal.example.com/path", "https://legal.example.com?x=1"):
            with self.subTest(origin=origin):
                _, _, errors = preflight.inspect_environment(dict(self.env, COPILOT_PUBLIC_ORIGIN=origin))
                self.assertTrue(any("COPILOT_PUBLIC_ORIGIN must be an HTTPS origin" in item for item in errors))

    def test_llm_url_must_use_https_or_loopback_http(self):
        for url in ("https://llm.example.com/v1/chat/completions", "http://127.0.0.1:11434/v1", "http://localhost:11434/v1"):
            with self.subTest(url=url):
                _, _, errors = preflight.inspect_environment(dict(self.env, LLM_URL=url))
                self.assertFalse(any("LLM_URL must use HTTPS" in item for item in errors))
        for url in ("http://llm.example.com/v1", "http://192.168.1.10/v1", "https://user:pass@llm.example.com/v1", "https://llm.example.com/v1?key=x"):
            with self.subTest(url=url):
                _, _, errors = preflight.inspect_environment(dict(self.env, LLM_URL=url))
                self.assertTrue(any("LLM_URL must use HTTPS" in item for item in errors))

    def test_rejects_unlinked_legacy_law_search_override(self):
        _, _, errors = preflight.inspect_environment(dict(self.env, ALLOW_UNLINKED_LEGACY_LAW_SEARCH="1"))
        self.assertTrue(any("ALLOW_UNLINKED_LEGACY_LAW_SEARCH" in item for item in errors))

    def test_default_legacy_law_search_override_is_safe(self):
        passed, _, errors = preflight.inspect_environment(self.env)
        self.assertTrue(any("legacy-law search override is disabled" in item for item in passed))
        self.assertEqual(errors, [])

    def test_valid_config_and_missing_db_is_warning_only(self):
        passed, warnings, errors = preflight.inspect_environment(self.env)
        self.assertTrue(any("ADMIN_TOKEN" in item for item in passed))
        self.assertTrue(any("does not exist yet" in item for item in warnings))
        self.assertEqual(errors, [])
        self.assertFalse(self.db_path.exists())

    def test_shared_database_setting_is_rejected_in_every_environment(self):
        _, warnings, errors = preflight.inspect_environment(
            dict(self.env, COPILOT_DB=str(Path(self.tempdir.name) / "legacy.sqlite3"))
        )
        self.assertTrue(any("COPILOT_DB is retired" in item for item in errors))
        self.assertFalse(any("one shared COPILOT_DB" in item for item in warnings))

    def test_strict_release_gate_fails_on_unaccepted_missing_profile_databases(self):
        output = io.StringIO()
        with patch.dict(os.environ, self.env, clear=True), redirect_stdout(output):
            result = preflight.main(["--strict"])
        self.assertEqual(result, 1)
        self.assertIn("does not exist yet", output.getvalue())
        self.assertIn("Preflight failed", output.getvalue())
        self.assertFalse(self.db_path.exists())

    def test_release_gate_rejects_legacy_only_database_configuration(self):
        legacy_only = {
            "ADMIN_TOKEN": "a" * 40,
            "MIN_SCORE": "0.3",
            "COPILOT_DB": str(Path(self.tempdir.name) / "legacy.sqlite3"),
        }
        passed, warnings, errors = preflight.inspect_environment(legacy_only, require_separate=True)
        self.assertTrue(any("All three profile-separated database paths are required" in item for item in errors))
        self.assertTrue(any("COPILOT_DB is retired" in item for item in errors))

    def test_production_requires_separate_paths_secure_origin_hosts_and_valid_backup_key(self):
        env = dict(self.env)
        env.pop("COPILOT_DB", None)
        env.update({
            "COPILOT_ENV": "production",
            "COPILOT_CONTROL_DB": str(Path(self.tempdir.name) / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(Path(self.tempdir.name) / "tenants"),
            "COPILOT_CORPUS_DB": str(Path(self.tempdir.name) / "corpus.sqlite3"),
            "COPILOT_ALLOWED_HOSTS": "legal.example.test",
            "COPILOT_SECURE_COOKIES": "1",
            "COPILOT_PUBLIC_ORIGIN": "https://legal.example.test",
            "COPILOT_EMAIL_SMTP_HOST": "smtp.example.test",
            "COPILOT_EMAIL_FROM": "noreply@example.test",
            "COPILOT_EMAIL_SMTP_PORT": "587",
            "COPILOT_EMAIL_SMTP_SECURITY": "starttls",
            "COPILOT_EMAIL_SMTP_USERNAME": "smtp-user",
            "COPILOT_EMAIL_SMTP_PASSWORD": "smtp-password",
            "BACKUP_KEY": "not-a-valid-fernet-key",
            "MFA_ENFORCEMENT": "admins_required",
            "MFA_ENCRYPTION_KEY": Fernet.generate_key().decode(),
        })
        _, _, errors = preflight.inspect_environment(env)
        self.assertTrue(any("BACKUP_KEY must be a valid Fernet key" in item for item in errors))
        env["BACKUP_KEY"] = Fernet.generate_key().decode()
        env["MFA_ENCRYPTION_KEY"] = Fernet.generate_key().decode()
        _, _, errors = preflight.inspect_environment(env)
        self.assertTrue(any(
            "COPILOT_OBJECT_STORAGE_BACKEND=s3" in item
            for item in errors
        ))
        self.assertFalse(any("COPILOT_EMAIL_" in item for item in errors), errors)

    def test_production_requires_complete_encrypted_identity_email_configuration(self):
        root = Path(self.tempdir.name)
        env = dict(self.env)
        env.pop("COPILOT_DB", None)
        env.update({
            "COPILOT_ENV": "production",
            "COPILOT_CONTROL_DB": str(root / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(root / "tenants"),
            "COPILOT_CORPUS_DB": str(root / "corpus.sqlite3"),
            "COPILOT_ALLOWED_HOSTS": "legal.example.test",
            "COPILOT_SECURE_COOKIES": "1",
            "COPILOT_PUBLIC_ORIGIN": "https://legal.example.test",
            "COPILOT_EMAIL_SMTP_HOST": "smtp.example.test",
            "COPILOT_EMAIL_FROM": "noreply@example.test",
            "COPILOT_EMAIL_SMTP_PORT": "587",
            "COPILOT_EMAIL_SMTP_SECURITY": "starttls",
            "COPILOT_EMAIL_SMTP_USERNAME": "smtp-user",
            "COPILOT_EMAIL_SMTP_PASSWORD": "smtp-password",
            "BACKUP_KEY": Fernet.generate_key().decode(),
            "MFA_ENFORCEMENT": "admins_required",
            "MFA_ENCRYPTION_KEY": Fernet.generate_key().decode(),
            "COPILOT_OBJECT_STORAGE_BACKEND": "s3",
        })
        for key in ("COPILOT_EMAIL_SMTP_HOST", "COPILOT_EMAIL_FROM", "COPILOT_EMAIL_SMTP_PORT", "COPILOT_EMAIL_SMTP_SECURITY", "COPILOT_EMAIL_SMTP_USERNAME", "COPILOT_EMAIL_SMTP_PASSWORD"):
            env.pop(key, None)
        _, _, errors = preflight.inspect_environment(env)
        self.assertTrue(any("COPILOT_EMAIL_SMTP_HOST" in item for item in errors))
        self.assertTrue(any("COPILOT_EMAIL_FROM" in item for item in errors))

        env.update({
            "COPILOT_EMAIL_SMTP_HOST": "smtp.example.test",
            "COPILOT_EMAIL_FROM": "noreply@example.test",
            "COPILOT_EMAIL_SMTP_PORT": "587",
            "COPILOT_EMAIL_SMTP_SECURITY": "starttls",
            "COPILOT_EMAIL_SMTP_USERNAME": "smtp-user",
            "COPILOT_EMAIL_SMTP_PASSWORD": "smtp-password",
        })
        _, _, errors = preflight.inspect_environment(env)
        self.assertFalse(any("COPILOT_EMAIL_" in item for item in errors), errors)

        for overrides in (
            {"COPILOT_EMAIL_SMTP_SECURITY": "plain"},
            {"COPILOT_EMAIL_SMTP_PORT": "70000"},
            {"COPILOT_EMAIL_SMTP_PORT": "not-a-port"},
            {"COPILOT_EMAIL_SMTP_PASSWORD": ""},
        ):
            with self.subTest(overrides=overrides):
                invalid = dict(env, **overrides)
                _, _, errors = preflight.inspect_environment(invalid)
                self.assertTrue(any("COPILOT_EMAIL_" in item for item in errors), errors)

    def test_production_requires_host_and_secure_cookie_settings(self):
        env = dict(self.env)
        env.pop("COPILOT_DB", None)
        env.update({
            "COPILOT_ENV": "production",
            "COPILOT_CONTROL_DB": str(Path(self.tempdir.name) / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(Path(self.tempdir.name) / "tenants"),
            "COPILOT_CORPUS_DB": str(Path(self.tempdir.name) / "corpus.sqlite3"),
            "BACKUP_KEY": __import__("cryptography.fernet", fromlist=["Fernet"]).Fernet.generate_key().decode(),
        })
        _, _, errors = preflight.inspect_environment(env)
        self.assertTrue(any("COPILOT_ALLOWED_HOSTS is required in production" in item for item in errors))
        self.assertTrue(any("COPILOT_SECURE_COOKIES=1 is required in production" in item for item in errors))
        self.assertTrue(any("COPILOT_PUBLIC_ORIGIN must be set" in item for item in errors))

    def test_unimplemented_backend_name_cannot_bypass_production_storage_gate(self):
        root = Path(self.tempdir.name)
        tenant_root = root / "tenants"
        tenant_root.mkdir()
        if os.name == "posix":
            os.chmod(tenant_root, 0o700)
        (root / "control").mkdir()
        (root / "corpus").mkdir()
        base = {
            "ADMIN_TOKEN": "a" * 40,
            "MIN_SCORE": "0.3",
            "COPILOT_ENV": "production",
            "COPILOT_CONTROL_DB": str(root / "control" / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(tenant_root),
            "COPILOT_CORPUS_DB": str(root / "corpus" / "corpus.sqlite3"),
            "COPILOT_ALLOWED_HOSTS": "legal.example.test",
            "COPILOT_SECURE_COOKIES": "1",
            "COPILOT_PUBLIC_ORIGIN": "https://legal.example.test",
            "COPILOT_EMAIL_SMTP_HOST": "smtp.example.test",
            "COPILOT_EMAIL_FROM": "noreply@example.test",
            "COPILOT_EMAIL_SMTP_PORT": "587",
            "COPILOT_EMAIL_SMTP_SECURITY": "starttls",
            "COPILOT_EMAIL_SMTP_USERNAME": "smtp-user",
            "COPILOT_EMAIL_SMTP_PASSWORD": "smtp-password",
            "BACKUP_KEY": Fernet.generate_key().decode(),
            "MFA_ENFORCEMENT": "admins_required",
            "MFA_ENCRYPTION_KEY": Fernet.generate_key().decode(),
        }
        for backend in ("local", "s3_kms", "unknown"):
            with self.subTest(backend=backend):
                _, _, errors = preflight.inspect_environment(
                    dict(base, COPILOT_OBJECT_STORAGE_BACKEND=backend)
                )
                self.assertTrue(any(
                    "COPILOT_OBJECT_STORAGE_BACKEND=s3" in item
                    for item in errors
                ))

    def test_release_preflight_blocks_until_production_object_storage_is_verified(self):
        root = Path(self.tempdir.name)
        tenant_root = root / "tenants"
        tenant_root.mkdir()
        if os.name == "posix":
            os.chmod(tenant_root, 0o700)
        (root / "control").mkdir()
        (root / "corpus").mkdir()
        env = {
            "ADMIN_TOKEN": "a" * 40,
            "MIN_SCORE": "0.3",
            "COPILOT_CONTROL_DB": str(root / "control" / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(tenant_root),
            "COPILOT_CORPUS_DB": str(root / "corpus" / "corpus.sqlite3"),
        }
        _, _, errors = preflight.inspect_environment(env, require_separate=True)
        self.assertTrue(any(
            "COPILOT_OBJECT_STORAGE_BACKEND=s3" in item
            for item in errors
        ))

    def test_production_s3_backend_requires_bucket_region_and_key_configuration(self):
        root = Path(self.tempdir.name)
        tenant_root = root / "tenants-s3"
        tenant_root.mkdir()
        if os.name == "posix":
            os.chmod(tenant_root, 0o700)
        (root / "control-s3").mkdir()
        (root / "corpus-s3").mkdir()
        env = {
            "ADMIN_TOKEN": "a" * 40,
            "MIN_SCORE": "0.3",
            "COPILOT_ENV": "production",
            "COPILOT_OBJECT_STORAGE_BACKEND": "s3",
            "COPILOT_CONTROL_DB": str(root / "control-s3" / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(tenant_root),
            "COPILOT_CORPUS_DB": str(root / "corpus-s3" / "corpus.sqlite3"),
            "COPILOT_ALLOWED_HOSTS": "legal.example.test",
            "COPILOT_SECURE_COOKIES": "1",
            "COPILOT_PUBLIC_ORIGIN": "https://legal.example.test",
            "COPILOT_EMAIL_SMTP_HOST": "smtp.example.test",
            "COPILOT_EMAIL_FROM": "noreply@example.test",
            "COPILOT_EMAIL_SMTP_PORT": "587",
            "COPILOT_EMAIL_SMTP_SECURITY": "starttls",
            "COPILOT_EMAIL_SMTP_USERNAME": "smtp-user",
            "COPILOT_EMAIL_SMTP_PASSWORD": "smtp-password",
            "BACKUP_KEY": Fernet.generate_key().decode(),
            "MFA_ENFORCEMENT": "admins_required",
            "MFA_ENCRYPTION_KEY": Fernet.generate_key().decode(),
        }
        _, _, errors = preflight.inspect_environment(env)
        self.assertTrue(any("S3/KMS production configuration is incomplete" in item for item in errors))

        env.update({
            "COPILOT_S3_BUCKET": "private-originals-test",
            "COPILOT_S3_REGION": "us-east-1",
            "COPILOT_S3_KMS_KEY_ID": "arn:aws:kms:us-east-1:123456789012:key/test-key",
        })
        passed, _, errors = preflight.inspect_environment(env)
        self.assertFalse(any("S3/KMS production configuration is incomplete" in item for item in errors))
        self.assertTrue(any("live provider acceptance remains a separate mandatory gate" in item for item in passed))

    def test_accepts_complete_separate_database_path_configuration_without_shared_warning(self):
        root = Path(self.tempdir.name)
        tenant_root = root / "tenants"
        tenant_root.mkdir()
        if os.name == "posix":
            os.chmod(tenant_root, 0o700)
        env = {
            "ADMIN_TOKEN": "a" * 40,
            "MIN_SCORE": "0.3",
            "COPILOT_CONTROL_DB": str(root / "control" / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(tenant_root),
            "COPILOT_CORPUS_DB": str(root / "corpus" / "corpus.sqlite3"),
        }
        (root / "control").mkdir()
        (root / "corpus").mkdir()
        passed, warnings, errors = preflight.inspect_environment(env)
        self.assertTrue(any("Separate control-plane" in item for item in passed))
        self.assertFalse(any("one shared COPILOT_DB" in item for item in warnings))
        self.assertFalse(any("shared COPILOT_DB" in item for item in warnings))
        self.assertEqual(errors, [])
        self.assertFalse((root / "control" / "control.sqlite3").exists())
        self.assertFalse((root / "corpus" / "corpus.sqlite3").exists())

    def test_rejects_legacy_database_path_when_separate_paths_are_configured(self):
        root = Path(self.tempdir.name)
        tenant_root = root / "tenants"
        tenant_root.mkdir()
        if os.name == "posix":
            os.chmod(tenant_root, 0o700)
        (root / "control").mkdir()
        (root / "corpus").mkdir()
        env = {
            "ADMIN_TOKEN": "a" * 40,
            "MIN_SCORE": "0.3",
            "COPILOT_CONTROL_DB": str(root / "control" / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(tenant_root),
            "COPILOT_CORPUS_DB": str(root / "corpus" / "corpus.sqlite3"),
            "COPILOT_DB": str(root / "legacy.sqlite3"),
        }
        _, _, errors = preflight.inspect_environment(env)
        self.assertTrue(any("COPILOT_DB is retired" in item for item in errors))

    def test_rejects_partial_separate_database_configuration(self):
        env = dict(self.env)
        env.pop("COPILOT_TENANT_DB_ROOT")
        env.pop("COPILOT_CORPUS_DB")
        env["COPILOT_CONTROL_DB"] = str(Path(self.tempdir.name) / "control.sqlite3")
        _, _, errors = preflight.inspect_environment(env)
        self.assertTrue(any("requires all three paths" in item for item in errors))

    def test_rejects_shared_control_and_corpus_database_path(self):
        root = Path(self.tempdir.name)
        (root / "tenants").mkdir()
        shared = root / "shared.sqlite3"
        env = {
            "ADMIN_TOKEN": "a" * 40,
            "MIN_SCORE": "0.3",
            "COPILOT_CONTROL_DB": str(shared),
            "COPILOT_TENANT_DB_ROOT": str(root / "tenants"),
            "COPILOT_CORPUS_DB": str(shared),
        }
        _, _, errors = preflight.inspect_environment(env)
        self.assertTrue(any("must be different" in item for item in errors))

    def test_rejects_short_or_placeholder_admin_token(self):
        for token in ("short", "test-token-" + "x" * 30):
            with self.subTest(token_length=len(token)):
                env = dict(self.env, ADMIN_TOKEN=token)
                _, _, errors = preflight.inspect_environment(env)
                self.assertTrue(any("ADMIN_TOKEN" in item for item in errors))

    def test_rejects_nonfinite_or_out_of_range_min_score(self):
        for score in ("nan", "inf", "-0.1", "1.1", "not-a-number"):
            with self.subTest(score=score):
                _, _, errors = preflight.inspect_environment(dict(self.env, MIN_SCORE=score))
                self.assertTrue(any("MIN_SCORE" in item for item in errors))

    def test_rejects_relative_legacy_database_setting(self):
        _, warnings, errors = preflight.inspect_environment(dict(self.env, COPILOT_DB="relative.db"))
        self.assertTrue(any("COPILOT_DB is retired" in item for item in errors))
        self.assertFalse(any("relative" in item for item in warnings))

    def test_rejects_symlinked_database_path_without_following_target(self):
        target = Path(self.tempdir.name) / "real-production.db"
        target.write_text("test", encoding="utf-8")
        self.db_path.symlink_to(target)
        passed, warnings, errors = preflight.inspect_environment(self.env)
        self.assertTrue(any("must not be a symbolic link" in item for item in errors))
        self.assertFalse(any("existing COPILOT_CONTROL_DB file is readable" in item for item in passed))
        self.assertFalse(any("COPILOT_CONTROL_DB does not exist yet" in item for item in warnings))

    @unittest.skipUnless(os.name == "posix", "POSIX file permission bits are required")
    def test_rejects_world_readable_sqlite_wal_sidecar(self):
        sidecar = Path(str(self.db_path) + "-wal")
        sidecar.write_text("synthetic sidecar", encoding="utf-8")
        os.chmod(sidecar, 0o644)
        _, _, errors = preflight.inspect_environment(self.env)
        self.assertTrue(any("SQLite sidecar" in item and "allow group/other access" in item for item in errors))

    @unittest.skipUnless(os.name == "posix", "POSIX file permission bits are required")
    def test_rejects_symlinked_sqlite_sidecar(self):
        target = Path(self.tempdir.name) / "external-wal"
        target.write_text("synthetic sidecar", encoding="utf-8")
        Path(str(self.db_path) + "-wal").symlink_to(target)
        _, _, errors = preflight.inspect_environment(self.env)
        self.assertTrue(any("SQLite sidecar" in item and "symbolic link" in item for item in errors))

    @unittest.skipUnless(os.name == "posix", "POSIX named pipes are required")
    def test_rejects_fifo_sqlite_sidecar(self):
        sidecar = Path(str(self.db_path) + "-wal")
        os.mkfifo(sidecar)
        _, _, errors = preflight.inspect_environment(self.env)
        self.assertTrue(any("SQLite sidecar" in item and "not a regular file" in item for item in errors))

    def test_existing_database_must_be_readable_and_writable(self):
        self.db_path.write_text("test", encoding="utf-8")
        passed, warnings, errors = preflight.inspect_environment(self.env)
        self.assertTrue(any("COPILOT_CONTROL_DB exists and is readable/writable" in item for item in passed))
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
