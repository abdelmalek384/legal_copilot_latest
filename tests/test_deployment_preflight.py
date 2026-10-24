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

    def test_valid_config_and_missing_db_is_warning_only(self):
        passed, warnings, errors = preflight.inspect_environment(self.env)
        self.assertTrue(any("ADMIN_TOKEN" in item for item in passed))
        self.assertTrue(any("does not exist yet" in item for item in warnings))
        self.assertEqual(errors, [])
        self.assertFalse(self.db_path.exists())

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

    def test_existing_database_must_be_readable_and_writable(self):
        self.db_path.write_text("test", encoding="utf-8")
        passed, warnings, errors = preflight.inspect_environment(self.env)
        self.assertTrue(any("existing COPILOT_DB" in item for item in passed))
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
