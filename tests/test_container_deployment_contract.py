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
