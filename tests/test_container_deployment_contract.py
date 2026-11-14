from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ContainerDeploymentContractTests(unittest.TestCase):
    def test_image_uses_hash_locked_dependencies_and_non_root_runtime(self):
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("requirements-py312.lock", dockerfile)
        self.assertIn("--require-hashes", dockerfile)
        self.assertIn("USER 10001:10001", dockerfile)
        self.assertIn("--no-proxy-headers", dockerfile)
        self.assertIn("HEALTHCHECK", dockerfile)
        self.assertIn("--workers", dockerfile)

    def test_compose_has_no_published_port_and_hardens_runtime(self):
        compose = (ROOT / "compose.production.yaml").read_text(encoding="utf-8")
        self.assertNotIn("\n    ports:", compose)
        for setting in (
            "read_only: true",
            'user: "10001:10001"',
            "cap_drop:",
            "no-new-privileges:true",
            "create_host_path: false",
            "database-acceptance.json",
            "legal-copilot-proxy",
        ):
            self.assertIn(setting, compose)

    def test_secret_material_is_excluded_from_build_context(self):
        ignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
        self.assertIn("secrets/", ignore)
        self.assertIn(".env", ignore)
        self.assertIn(".env.*", ignore)
        example = (ROOT / ".env.production.example").read_text(encoding="utf-8")
        self.assertIn("ADMIN_TOKEN=PLACEHOLDER_SET_IN_SECRET_MANAGER", example)
        for required_setting in (
            "COPILOT_ALLOWED_HOSTS=",
            "COPILOT_TRUSTED_PROXIES=",
            "COPILOT_PUBLIC_ORIGIN=",
            "BACKUP_KEY=",
            "MFA_ENCRYPTION_KEY=",
            "COPILOT_S3_BUCKET=",
            "COPILOT_S3_REGION=",
            "COPILOT_S3_KMS_KEY_ID=",
            "COPILOT_S3_RECOVERY_BUCKET=",
            "COPILOT_S3_RECOVERY_REGION=",
            "COPILOT_S3_RECOVERY_KMS_KEY_ID=",
            "COPILOT_EMAIL_SMTP_HOST=",
            "COPILOT_EMAIL_FROM=",
        ):
            self.assertIn(required_setting, example)
        self.assertNotIn("AKIA", example)
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for private_path in ("runtime-data/", "secrets/", "backups/"):
            self.assertIn(private_path, gitignore)

    def test_ci_builds_both_supported_container_architectures(self):
        workflow = (ROOT / ".github" / "workflows" / "container-image.yml").read_text(encoding="utf-8")
        self.assertIn("linux/amd64", workflow)
        self.assertIn("linux/arm64", workflow)
        self.assertIn("push: false", workflow)
        self.assertIn("docker compose --env-file .env.production -f compose.production.yaml config --quiet", workflow)
        self.assertIn("contents: read", workflow)

    def test_windows_launcher_uses_exact_python_minor_and_hash_locked_dependencies(self):
        launcher = (ROOT / "start_windows.bat").read_text(encoding="utf-8")
        self.assertIn("sys.version_info[:2] == (3, 12)", launcher)
        self.assertIn("python -m pip install --require-hashes -r requirements-py312.lock", launcher)
        self.assertNotIn("python -m pip install -r requirements.txt", launcher)

    def test_local_release_check_includes_security_and_safe_compose_validation(self):
        checker = (ROOT / "scripts" / "local_release_check.sh").read_text(encoding="utf-8")
        self.assertIn("sys.version_info[:2] == (3, 12)", checker)
        self.assertIn('details+=("requires Python 3.12")', checker)
        self.assertIn('run_check "Focused security regression matrix" bash scripts/security_regression_check.sh', checker)
        self.assertIn('run_check "Placeholder-only production Compose validation"', checker)
        self.assertIn('test ! -e .env.production', checker)
        self.assertIn('sed "s|      - .env.production|      - $tmpdir/.env.production|"', checker)
        self.assertIn('docker compose --project-directory "$PWD" --env-file "$tmpdir/.env.production"', checker)
        self.assertIn('-f "$tmpdir/compose.production.yaml" config --quiet', checker)
        self.assertNotIn("docker compose up", checker)

    def test_local_release_check_audits_lock_drift_and_dependency_vulnerabilities(self):
        checker = (ROOT / "scripts" / "local_release_check.sh").read_text(encoding="utf-8")
        self.assertIn("pip-compile --resolver=backtracking --generate-hashes", checker)
        self.assertIn('diff -u requirements-py312.lock "$tmpdir/requirements-py312.lock"', checker)
        self.assertIn("pip-audit --strict --progress-spinner off -r requirements-py312.lock", checker)
        self.assertIn('details+=("pip-compile is not installed")', checker)
        self.assertIn('details+=("pip-audit is not installed")', checker)

    def test_focused_security_matrix_includes_backup_restore_and_recovery(self):
        matrix = (ROOT / "scripts" / "security_regression_check.sh").read_text(encoding="utf-8")
        self.assertIn("test_database_backup_bundle.py", matrix)
        self.assertIn("test_database_recovery_drill.py", matrix)

    def test_local_release_check_runs_isolated_encrypted_recovery_drill(self):
        checker = (ROOT / "scripts" / "local_release_check.sh").read_text(encoding="utf-8")
        self.assertIn(
            'run_check "Encrypted multi-tenant backup/restore recovery drill" python tests/test_database_recovery_drill.py',
            checker,
        )
        drill = (ROOT / "tests" / "test_database_recovery_drill.py").read_text(encoding="utf-8")
        self.assertIn("run_recovery_drill", drill)
        self.assertIn("plaintext_retained", drill)

    def test_image_python_version_matches_ci_and_dependabot_blocks_unverified_minor_major(self):
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("FROM python:3.12-slim-bookworm", dockerfile)
        self.assertNotIn("FROM python:3.15-slim-bookworm", dockerfile)
        dependabot = (ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
        docker_section = dependabot.split("package-ecosystem: docker", 1)[1]
        self.assertIn('dependency-name: "python"', docker_section)
        self.assertIn('"version-update:semver-major"', docker_section)
        self.assertIn('"version-update:semver-minor"', docker_section)

    def test_dependabot_tracks_docker_base_image_updates(self):
        dependabot = (ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
        self.assertIn("package-ecosystem: docker", dependabot)
        docs = (ROOT / "docs" / "container_deployment.md").read_text(encoding="utf-8")
        self.assertIn("one application replica", docs)
        self.assertIn("liveness only", docs)
        self.assertIn("tools/deployment_preflight.py --strict --require-separate", docs)
        self.assertIn("tools/production_release_gate.py", docs)
        self.assertIn("witnessed", docs)
        self.assertIn("proxy_set_header X-Forwarded-For $remote_addr;", docs)
        checklist = (ROOT / "docs" / "production_deployment_checklist.md").read_text(encoding="utf-8")
        self.assertIn("COPILOT_TRUSTED_PROXIES` to your proxy address", checklist)


if __name__ == "__main__":
    unittest.main()
