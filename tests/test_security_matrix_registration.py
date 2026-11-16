"""Keep focused security regression modules wired into the explicit Tests workflow."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
MATRIX = (ROOT / "scripts" / "security_regression_check.sh").read_text(encoding="utf-8")

WORKFLOW_MODULES = set(re.findall(r"tests/(test_[A-Za-z0-9_]+\\.py)", WORKFLOW))
MATRIX_MODULES = re.findall(r"^\\s+(test_[A-Za-z0-9_]+\\.py)\\s*$", MATRIX, re.MULTILINE)


class SecurityMatrixRegistrationTests(unittest.TestCase):
    def test_every_security_matrix_module_is_in_tests_workflow(self):
        self.assertEqual(
            sorted(set(MATRIX_MODULES) - WORKFLOW_MODULES),
            [],
            "Every focused security regression must have an explicit Tests workflow step.",
        )

    def test_security_matrix_has_no_duplicate_modules(self):
        self.assertEqual(len(MATRIX_MODULES), len(set(MATRIX_MODULES)))

    def test_every_security_matrix_module_exists(self):
        missing = [name for name in MATRIX_MODULES if not (ROOT / "tests" / name).is_file()]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
