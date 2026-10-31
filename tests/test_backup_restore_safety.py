"""The old single-file backup/restore CLI must fail closed.

Real backup and recovery coverage lives in tests/test_database_backup_bundle.py.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANAGE = ROOT / "manage.py"


class SingleFileBackupRestoreDisabledTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env = os.environ.copy()
        self.env["COPILOT_ENV"] = "development"
        # Exercise the retired CLI subcommands directly; COPILOT_DB is independently
        # rejected by the application import guard and is covered in the runtime tests.
        self.env.pop("COPILOT_DB", None)
        self.env["PYTHONPATH"] = str(ROOT)
        for name in ("COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB"):
            self.env.pop(name, None)

    def tearDown(self):
        self.temp.cleanup()

    def run_manage(self, *args):
        return subprocess.run(
            [sys.executable, str(MANAGE), *args],
            cwd=ROOT,
            env=self.env,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )

    def test_single_file_backup_fails_closed_before_creating_output(self):
        backup_dir = self.root / "backups"
        result = self.run_manage("backup", str(backup_dir), "--keep", "2")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Single-file backups are disabled", result.stderr)
        self.assertIn("backup-tenancy", result.stderr)
        self.assertFalse(backup_dir.exists())

    def test_single_file_restore_fails_closed_without_replacing_destination(self):
        source = self.root / "legacy-backup.db.enc"
        source.write_bytes(b"not used by the disabled single-file restore path")
        destination = self.root / "existing.sqlite3"
        original = b"destination must remain unchanged"
        destination.write_bytes(original)
        result = self.run_manage("restore", str(source), str(destination))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Single-file restores are disabled", result.stderr)
        self.assertIn("restore-tenancy", result.stderr)
        self.assertEqual(destination.read_bytes(), original)
        self.assertFalse(list(self.root.glob(".restore-*.tmp")))


if __name__ == "__main__":
    unittest.main()
