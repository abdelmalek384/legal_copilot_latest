"""Regression test for gaps in the recorded migration history."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from db_migrations import MigrationError, apply_migrations


class MigrationHistoryOrderingTests(unittest.TestCase):
    def test_rejects_recorded_history_with_a_missing_middle_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            migrations = Path(tmp)
            for version in (1, 2, 3):
                (migrations / f"{version:04d}_step_{version}.sql").write_text(
                    f"CREATE TABLE step_{version}(id INTEGER);", encoding="utf-8"
                )

            db = sqlite3.connect(":memory:")
            try:
                self.assertEqual(apply_migrations(db, migrations), [1, 2, 3])
                db.execute("DELETE FROM schema_migrations WHERE version=2")
                db.commit()

                with self.assertRaisesRegex(MigrationError, "ordered prefix"):
                    apply_migrations(db, migrations)
            finally:
                db.close()


if __name__ == "__main__":
    unittest.main()
