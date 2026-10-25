"""Tests for profile-aware migration boundaries."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from db_migrations import MigrationError
from schema_profiles import DatabaseProfileError, apply_profile_migrations


class DatabaseProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for profile in ("control_plane", "firm", "legal_corpus"):
            (self.root / profile).mkdir()
        self.db = sqlite3.connect(":memory:")

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def test_applies_only_selected_profile_migrations(self):
        (self.root / "firm" / "0001_firm_marker.sql").write_text(
            "CREATE TABLE firm_only (id INTEGER PRIMARY KEY);", encoding="utf-8"
        )
        (self.root / "legal_corpus" / "0001_corpus_marker.sql").write_text(
            "CREATE TABLE corpus_only (id INTEGER PRIMARY KEY);", encoding="utf-8"
        )
        self.assertEqual(apply_profile_migrations(self.db, "firm", self.root), [1])
        tables = {row[0] for row in self.db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        self.assertIn("firm_only", tables)
        self.assertNotIn("corpus_only", tables)

    def test_profile_binding_is_idempotent(self):
        self.assertEqual(apply_profile_migrations(self.db, "firm", self.root), [])
        self.assertEqual(apply_profile_migrations(self.db, "firm", self.root), [])
        self.assertEqual(
            self.db.execute("SELECT profile FROM database_profile WHERE singleton=1").fetchone()[0],
            "firm",
        )

    def test_rejects_reusing_database_for_another_profile(self):
        apply_profile_migrations(self.db, "firm", self.root)
        with self.assertRaisesRegex(DatabaseProfileError, "bound to profile"):
            apply_profile_migrations(self.db, "legal_corpus", self.root)

    def test_profile_binding_cannot_be_updated_or_deleted(self):
        apply_profile_migrations(self.db, "firm", self.root)
        with self.assertRaisesRegex(sqlite3.IntegrityError, "profile binding is immutable"):
            self.db.execute("UPDATE database_profile SET profile='legal_corpus' WHERE singleton=1")
        with self.assertRaisesRegex(sqlite3.IntegrityError, "profile binding is immutable"):
            self.db.execute("DELETE FROM database_profile WHERE singleton=1")
        self.assertEqual(
            self.db.execute("SELECT profile FROM database_profile WHERE singleton=1").fetchone()[0],
            "firm",
        )

    def test_rejects_unknown_or_path_like_profile(self):
        for profile in ("tenant-7", "../firm", "", None, 7):
            with self.subTest(profile=profile), self.assertRaises(DatabaseProfileError):
                apply_profile_migrations(self.db, profile, self.root)

    def test_missing_profile_migration_directory_fails(self):
        (self.root / "legal_corpus").rmdir()
        with self.assertRaisesRegex(MigrationError, "does not exist"):
            apply_profile_migrations(self.db, "legal_corpus", self.root)

    def test_failed_migration_rolls_back_migration_but_keeps_profile_binding(self):
        (self.root / "firm" / "0001_broken.sql").write_text(
            "CREATE TABLE partial (id INTEGER); INSERT INTO missing_table VALUES (1);",
            encoding="utf-8",
        )
        with self.assertRaises(sqlite3.OperationalError):
            apply_profile_migrations(self.db, "firm", self.root)
        self.assertIsNotNone(self.db.execute(
            "SELECT profile FROM database_profile WHERE singleton=1"
        ).fetchone())
        self.assertIsNone(self.db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='partial'"
        ).fetchone())
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
