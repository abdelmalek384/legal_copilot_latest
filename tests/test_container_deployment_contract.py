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
        for placeholder in (
            "REPLACE_WITH_RANDOM_SECRET",
            "REPLACE_WITH_FERNET_BACKUP_KEY",
            "REPLACE_WITH_DIFFERENT_FERNET_MFA_KEY",
            "REPLACE_WITH_PRIVATE_BUCKET",
        ):
            self.assertIn(placeholder, example)
        self.assertNotIn("AKIA", example)

    def test_ci_builds_both_supported_container_architectures(self):
        workflow = (ROOT / ".github" / "workflows" / "container-image.yml").read_text(encoding="utf-8")
        self.assertIn("linux/amd64", workflow)
        self.assertIn("linux/arm64", workflow)
        self.assertIn("push: false", workflow)
        self.assertIn("docker compose --env-file .env.production -f compose.production.yaml config --quiet", workflow)
        self.assertIn("contents: read", workflow)

    def test_dependabot_tracks_docker_base_image_updates(self):
        dependabot = (ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
        self.assertIn("package-ecosystem: docker", dependabot)
        docs = (ROOT / "docs" / "container_deployment.md").read_text(encoding="utf-8")
        self.assertIn("one application replica", docs)
        self.assertIn("liveness only", docs)
        self.assertIn("tools/deployment_preflight.py --strict --require-separate", docs)
        self.assertIn("tools/production_release_gate.py", docs)
        self.assertIn("witnessed", docs)


if __name__ == "__main__":
    unittest.main()
