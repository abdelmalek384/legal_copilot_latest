"""Keep focused security regression modules wired into the explicit Tests workflow."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
MATRIX = (ROOT / "scripts" / "security_regression_check.sh").read_text(encoding="utf-8")

WORKFLOW_MODULES = set(re.findall(r"tests/(test_[A-Za-z0-9_]+\.py)", WORKFLOW))
MATRIX_MODULES = re.findall(r"^\s+(test_[A-Za-z0-9_]+\.py)\s*$", MATRIX, re.MULTILINE)


REQUIRED_SECURITY_MODULES = {
    "test_mfa_primitives.py", "test_mfa_break_glass_cli.py",
    "test_platform_admin_bootstrap_cli.py", "test_tenant_context.py",
    "test_tenant_context_transaction_boundary.py", "test_tenant_database_preflight.py",
    "test_tenant_fleet_migration.py", "test_tenant_ownership_preflight.py",
    "test_tenant_write_failure_diagnostics.py", "test_s3_storage_preflight.py",
    "test_s3_recovery_archive_preflight.py", "test_document_classifications.py",
    "test_document_intelligence.py", "test_document_review_workflow.py",
    "test_invoice_schema_migration.py", "test_security_audit_export.py",
}


class SecurityMatrixRegistrationTests(unittest.TestCase):
    def test_every_security_matrix_module_is_in_tests_workflow(self):
        self.assertEqual(
            sorted(set(MATRIX_MODULES) - WORKFLOW_MODULES),
            [],
            "Every focused security regression must have an explicit Tests workflow step.",
        )

    def test_mandatory_high_risk_modules_remain_in_security_matrix(self):
        self.assertEqual(sorted(REQUIRED_SECURITY_MODULES - set(MATRIX_MODULES)), [])

    def test_security_matrix_has_no_duplicate_modules(self):
        self.assertEqual(len(MATRIX_MODULES), len(set(MATRIX_MODULES)))

    def test_every_security_matrix_module_exists(self):
        missing = [name for name in MATRIX_MODULES if not (ROOT / "tests" / name).is_file()]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
