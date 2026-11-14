from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DependencyLockWorkflowContractTests(unittest.TestCase):
    def test_resolver_is_read_only_and_toolchain_is_pinned(self):
        workflow = (ROOT / ".github" / "workflows" / "resolve-deployment-lock.yml").read_text(encoding="utf-8")
        self.assertIn("contents: read", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("pip==26.2.2", workflow)
        self.assertIn("pip-tools==7.6.2", workflow)
        self.assertIn("pip-audit==2.10.1", workflow)

    def test_lock_requires_hashes_and_is_audited_before_artifact_upload(self):
        workflow = (ROOT / ".github" / "workflows" / "resolve-deployment-lock.yml").read_text(encoding="utf-8")
        self.assertIn("--generate-hashes", workflow)
        self.assertIn("--require-hashes", workflow)
        self.assertIn("pip-audit --strict --progress-spinner off -r requirements-py312.lock", workflow)
        self.assertIn("name: requirements-py312-lock", workflow)
        self.assertLess(
            workflow.index("Audit the exact hash-locked dependency set"),
            workflow.index("Upload resolved deployment lock"),
        )

    def test_local_developer_entrypoints_use_hash_locked_python_312_dependencies(self):
        entrypoints = (
            ROOT / "README.md",
            ROOT / "docs" / "collection_pipeline.md",
            ROOT / "start_mac.command",
            ROOT / "start_windows.bat",
        )
        for path in entrypoints:
            with self.subTest(path=path.name):
                content = path.read_text(encoding="utf-8")
                self.assertIn("--require-hashes -r requirements-py312.lock", content)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("python -m pip install -r requirements.txt", readme)
        collection = (ROOT / "docs" / "collection_pipeline.md").read_text(encoding="utf-8")
        self.assertIn("Python 3.12", collection)
        self.assertNotIn("Python 3.11+", collection)

    def test_dependency_audit_prefers_lock_when_checked_in(self):
        workflow = (ROOT / ".github" / "workflows" / "dependency-audit.yml").read_text(encoding="utf-8")
        self.assertIn("if [ -f requirements-py312.lock ]", workflow)
        self.assertIn("pip-audit --strict --progress-spinner off -r requirements-py312.lock", workflow)
        self.assertIn("pip-audit --strict --progress-spinner off -r requirements.txt", workflow)


if __name__ == "__main__":
    unittest.main()
