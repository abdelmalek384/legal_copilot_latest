from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "backup_restore_drill.sh"


class BackupRestoreDrillPathTests(unittest.TestCase):
    def run_drill(self, backup_dir: Path, restore_parent: Path) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update({"BACKUP_KEY": "synthetic-test-key", "COPILOT_ENV": "development"})
        return subprocess.run(
            ["bash", str(SCRIPT), str(backup_dir), str(restore_parent), "restore-test"],
            cwd=ROOT,
            env=env,
            input="",
            text=True,
            capture_output=True,
            check=False,
        )

    def test_rejects_restore_parent_nested_inside_backup_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            backup = root / "backup-tree"
            restore_parent = backup / "recovery"
            restore_parent.mkdir(parents=True)
            result = self.run_drill(backup, restore_parent)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("must not overlap", result.stderr)

    def test_rejects_filesystem_root_as_either_backup_or_restore_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            ordinary = Path(temporary)
            for backup, restore_parent in (
                (Path("/"), ordinary),
                (ordinary, Path("/")),
            ):
                with self.subTest(backup=backup, restore_parent=restore_parent):
                    result = self.run_drill(backup, restore_parent)
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertIn("must not be filesystem roots", result.stderr)

    def test_rejects_backup_directory_nested_inside_restore_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            restore_parent = root / "recovery-tree"
            backup = restore_parent / "backups"
            backup.mkdir(parents=True)
            result = self.run_drill(backup, restore_parent)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("must not overlap", result.stderr)


if __name__ == "__main__":
    unittest.main()
