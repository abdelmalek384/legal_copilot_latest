import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "deployment_preflight.py"
SPEC = importlib.util.spec_from_file_location("deployment_preflight", MODULE_PATH)
preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preflight)


class DeploymentPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.db_path = Path(self.tempdir.name) / "production.db"
        self.env = {
            "ADMIN_TOKEN": "a" * 40,
            "MIN_SCORE": "0.3",
            "COPILOT_DB": str(self.db_path),
        }

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

    def test_warns_that_shared_database_is_not_ready_for_multi_firm_confidential_data(self):
        _, warnings, errors = preflight.inspect_environment(self.env)
        self.assertTrue(any("one shared COPILOT_DB" in item for item in warnings))
        self.assertTrue(any("unrelated firms' confidential matters" in item for item in warnings))
        self.assertEqual(errors, [])

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

    def test_warns_on_relative_database_path(self):
        _, warnings, errors = preflight.inspect_environment(dict(self.env, COPILOT_DB="relative.db"))
        self.assertTrue(any("relative" in item for item in warnings))
        self.assertEqual(errors, [])

    def test_rejects_symlinked_database_path_without_following_target(self):
        target = Path(self.tempdir.name) / "real-production.db"
        target.write_text("test", encoding="utf-8")
        self.db_path.symlink_to(target)
        passed, warnings, errors = preflight.inspect_environment(self.env)
        self.assertTrue(any("must not be a symbolic link" in item for item in errors))
        self.assertFalse(any("existing COPILOT_DB file is readable" in item for item in passed))
        self.assertFalse(any("does not exist yet" in item for item in warnings))

    def test_existing_database_must_be_readable_and_writable(self):
        self.db_path.write_text("test", encoding="utf-8")
        passed, warnings, errors = preflight.inspect_environment(self.env)
        self.assertTrue(any("existing COPILOT_DB" in item for item in passed))
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
