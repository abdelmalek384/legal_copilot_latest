"""Keep the manual release gate runnable and explicit when hosted CI is unavailable."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RELEASE_CHECK = (ROOT / "scripts" / "local_release_check.sh").read_text(encoding="utf-8")


class ManualReleaseGateContractTests(unittest.TestCase):
    def test_gate_runs_full_python_and_security_suites(self):
        self.assertIn('run_check "Full CI-invoked Python test suite" python tools/run_local_test_suite.py', RELEASE_CHECK)
        self.assertIn('run_check "Focused security regression matrix" bash scripts/security_regression_check.sh', RELEASE_CHECK)

    def test_frontend_syntax_check_is_part_of_manual_gate(self):
        self.assertIn('run_check "Frontend inline JavaScript syntax"', RELEASE_CHECK)
        self.assertIn('node --check "$tmpfile"', RELEASE_CHECK)
        self.assertIn('Node.js is not installed; the frontend syntax check was not run', RELEASE_CHECK)

    def test_frontend_check_uses_portable_temporary_directory(self):
        self.assertIn('tmpdir=$(mktemp -d)', RELEASE_CHECK)
        self.assertNotIn('mktemp --suffix', RELEASE_CHECK)


if __name__ == "__main__":
    unittest.main()
