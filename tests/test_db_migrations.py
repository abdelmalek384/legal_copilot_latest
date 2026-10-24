"""Tests for versioned SQLite migration execution."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from db_migrations import MigrationError, apply_migrations


class DatabaseMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def write(self, name, sql):
        (self.path / name).write_text(sql, encoding="utf-8")

    def test_applies_in_version_order_and_is_idempotent(self):
        self.write("0002_add_value.sql", "ALTER TABLE sample ADD COLUMN value TEXT;")
        self.write("0001_create_sample.sql", "CREATE TABLE sample (id INTEGER PRIMARY KEY);")
        self.assertEqual(apply_migrations(self.db, self.path), [1, 2])
        self.assertEqual(apply_migrations(self.db, self.path), [])
        columns = [row["name"] for row in self.db.execute("PRAGMA table_info(sample)")]
        self.assertEqual(columns, ["id", "value"])
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0], 2)

    def test_failed_migration_rolls_back_schema_and_ledger(self):
        self.write("0001_atomic.sql", """
            CREATE TABLE should_rollback (id INTEGER);
            INSERT INTO missing_table VALUES (1);
        """)
        with self.assertRaises(sqlite3.OperationalError):
            apply_migrations(self.db, self.path)
        self.assertIsNone(self.db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='should_rollback'"
        ).fetchone())
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0], 0)

    def test_checksum_drift_is_rejected(self):
        self.write("0001_immutable.sql", "CREATE TABLE sample (id INTEGER);")
        apply_migrations(self.db, self.path)
        self.write("0001_immutable.sql", "CREATE TABLE sample (id INTEGER, name TEXT);")
        with self.assertRaisesRegex(MigrationError, "checksum"):
            apply_migrations(self.db, self.path)

    def test_missing_applied_file_is_rejected(self):
        self.write("0001_recorded.sql", "CREATE TABLE sample (id INTEGER);")
        apply_migrations(self.db, self.path)
        (self.path / "0001_recorded.sql").unlink()
        with self.assertRaisesRegex(MigrationError, "missing"):
            apply_migrations(self.db, self.path)

    def test_invalid_filename_is_rejected(self):
        self.write("migration.sql", "SELECT 1;")
        with self.assertRaisesRegex(MigrationError, "filename"):
            apply_migrations(self.db, self.path)

    def test_transaction_control_is_rejected(self):
        self.write("0001_bad.sql", "BEGIN; CREATE TABLE sample (id INTEGER);")
        with self.assertRaisesRegex(MigrationError, "Transaction control"):
            apply_migrations(self.db, self.path)
        self.assertIsNone(self.db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sample'"
        ).fetchone())


if __name__ == "__main__":
    unittest.main()
