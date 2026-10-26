import os
import subprocess
import sys
import unittest


class ProductionDatabaseModeTests(unittest.TestCase):
    def test_app_refuses_legacy_shared_database_in_production(self):
        env = os.environ.copy()
        for key in ("COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB"):
            env.pop(key, None)
        env["COPILOT_ENV"] = "production"
        env["COPILOT_DB"] = "/tmp/legacy-shared.sqlite3"
        result = subprocess.run(
            [sys.executable, "-c", "import app"],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Production requires explicit separate database paths", result.stderr)


if __name__ == "__main__":
    unittest.main()
