from pathlib import Path
import re
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
        self.assertIn("python -m pip_audit --require-hashes --strict --progress-spinner off -r requirements-py312.lock", workflow)
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
        self.assertIn("python -m pip_audit --require-hashes --strict --progress-spinner off -r requirements-py312.lock", workflow)
        self.assertIn("python -m pip_audit --strict --progress-spinner off -r requirements.txt", workflow)

    def test_every_direct_requirement_is_satisfied_by_the_hash_locked_set(self):
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        lock = (ROOT / "requirements-py312.lock").read_text(encoding="utf-8")

        def normalize(name):
            return re.sub(r"[-_.]+", "-", name).lower()

        def version(value):
            return tuple(int(part) for part in value.split("."))

        locked = {
            normalize(match.group(1)): match.group(2)
            for match in re.finditer(
                r"(?m)^([A-Za-z0-9_.-]+)==([0-9]+(?:\.[0-9]+)+)", lock
            )
        }
        checked = 0
        for raw in requirements.splitlines():
            requirement = raw.strip()
            if not requirement or requirement.startswith("#"):
                continue
            match = re.fullmatch(r"([A-Za-z0-9_.-]+)(.*)", requirement)
            self.assertIsNotNone(match, f"Unsupported direct requirement: {requirement}")
            name, specifier = normalize(match.group(1)), match.group(2)
            pinned = locked.get(name)
            self.assertIsNotNone(pinned, f"{name} is missing from the deployment lock")

            exact = re.fullmatch(r"==([0-9]+(?:\.[0-9]+)+)", specifier)
            bounded = re.fullmatch(
                r">=([0-9]+(?:\.[0-9]+)+),<([0-9]+(?:\.[0-9]+)*)", specifier
            )
            if exact:
                self.assertEqual(pinned, exact.group(1), f"{name} pin drift")
            else:
                self.assertIsNotNone(bounded, f"Unsupported specifier for {name}: {specifier}")
                self.assertGreaterEqual(version(pinned), version(bounded.group(1)), name)
                self.assertLess(version(pinned), version(bounded.group(2)), name)
            checked += 1

        self.assertGreater(checked, 0)
        self.assertEqual(locked["boto3"], locked["botocore"])

    def test_local_release_gate_runs_one_dependency_audit_with_safe_fallback(self):
        script = (ROOT / "scripts" / "local_release_check.sh").read_text(encoding="utf-8")
        self.assertEqual(
            script.count("if [[ \"$python312_available\" -eq 1 ]] && python -c 'import pip_audit'"),
            1,
        )
        self.assertIn('if [[ -f requirements-py312.lock ]]; then', script)
        self.assertIn('run_check "Hash-locked dependency vulnerability audit"', script)
        self.assertIn('run_check "Dependency vulnerability audit (requirements fallback)"', script)
        self.assertIn("python -m piptools compile", script)
        self.assertNotIn("pip-compile --resolver", script)
        self.assertIn("python -m pip_audit --require-hashes", script)
        self.assertIn('if [[ "$python312_available" -eq 1 ]]; then\n  run_check "Strict deployment preflight"', script)
        self.assertIn("Python 3.12 is required for the supported deployment preflight", script)


if __name__ == "__main__":
    unittest.main()
