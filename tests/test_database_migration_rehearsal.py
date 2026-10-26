"""Tests for disposable-copy migration rehearsal."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.rehearse_database_migrations import rehearse


class DatabaseMigrationRehearsalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.database = self.root / "source.sqlite3"
        with sqlite3.connect(self.database) as db:
            db.executescript("""
                CREATE TABLE firms(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
                CREATE TABLE users(id INTEGER PRIMARY KEY, firm_id INTEGER);
                CREATE TABLE legal_documents(document_id TEXT PRIMARY KEY, official_title TEXT, document_type TEXT);
                CREATE TABLE tenant_ownership_quarantine(first_seen TEXT);
                CREATE TABLE cases(id INTEGER PRIMARY KEY, firm_id INTEGER);
                INSERT INTO cases(id,firm_id) VALUES (1,1);
                CREATE TABLE members(user_id INTEGER, case_id INTEGER);
                CREATE TABLE deadlines(case_id INTEGER, due TEXT, status TEXT);
                CREATE TABLE docs(case_id INTEGER, id INTEGER);
                INSERT INTO docs(case_id,id) VALUES (1,10);
                CREATE TABLE chunks(document_id INTEGER);
                CREATE TABLE document_extraction_reviews(
                    firm_id INTEGER, document_id INTEGER, id INTEGER
                );
                CREATE TABLE login_attempts(window_start INTEGER, locked_until INTEGER);
                CREATE TABLE case_deletion_audit(firm_id INTEGER, id INTEGER);
                CREATE TABLE api_rate_limit_windows(window_start INTEGER);
                CREATE TABLE legal_document_versions(
                    version_id INTEGER PRIMARY KEY, original_sha256 TEXT,
                    effective_date TEXT, repeal_date TEXT, legal_status TEXT,
                    review_status TEXT, status_verified INTEGER
                );
                CREATE TABLE legal_review_events(version_id INTEGER, reviewed_at TEXT);
                CREATE TABLE research_conversations(firm_id INTEGER, user_id INTEGER, updated_at TEXT);
                CREATE TABLE research_messages(conversation_id INTEGER, id INTEGER);
            """)
        self.migrations = Path(__file__).resolve().parents[1] / "migrations"

    def tearDown(self):
        self.temp.cleanup()

    def test_migrations_apply_to_copy_without_changing_source(self):
        report = rehearse(self.database, self.migrations)
        self.assertEqual(report["status"], "passed")
        self.assertFalse(report["source_modified"])
        self.assertEqual(report["migrations_applied"], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(report["source_quick_check"], ["ok"])
        self.assertEqual(report["staged_quick_check"], ["ok"])
        self.assertEqual(report["source_foreign_key_violations"], 0)
        self.assertEqual(report["staged_foreign_key_violations"], 0)
        self.assertEqual(report["row_count_decreases"], [])
        self.assertEqual(report["source_table_row_counts"]["cases"], 1)
        self.assertEqual(report["staged_table_row_counts"]["cases"], 1)
        with sqlite3.connect(self.database) as db:
            names = {row[0] for row in db.execute("SELECT name FROM sqlite_master")}
            self.assertNotIn("schema_migrations", names)
            self.assertNotIn("idx_cases_firm", names)
            self.assertNotIn("idx_login_attempts_window", names)
            self.assertTrue({
                "auth_sessions", "notes", "fees", "tasks", "events", "sessions", "chunks_fts"
            }.isdisjoint(names))
            self.assertEqual(db.execute("SELECT firm_id FROM cases").fetchone()[0], 1)
            self.assertIsNone(db.execute("SELECT id FROM firms WHERE id=1").fetchone())
            self.assertNotIn("firm_id", {row[1] for row in db.execute("PRAGMA table_info(docs)")})
            self.assertNotIn("practice_area", {row[1] for row in db.execute("PRAGMA table_info(legal_documents)")})

    def test_row_count_decrease_requires_review(self):
        migration_dir = self.root / "destructive_migrations"
        migration_dir.mkdir()
        (migration_dir / "0001_delete_cases.sql").write_text(
            "DELETE FROM cases;", encoding="utf-8"
        )
        report = rehearse(self.database, migration_dir)
        self.assertEqual(report["status"], "review_required")
        self.assertEqual(report["row_count_decreases"], [{
            "table": "cases", "source_rows": 1, "staged_rows": 0,
        }])
        self.assertFalse(report["source_modified"])
        with sqlite3.connect(self.database) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM cases").fetchone()[0], 1)


    def test_failed_migration_only_changes_disposable_copy(self):
        migration_dir = self.root / "failing_migrations"
        migration_dir.mkdir()
        (migration_dir / "0001_partial.sql").write_text(
            "CREATE TABLE should_rollback(id INTEGER); INSERT INTO missing_table VALUES (1);",
            encoding="utf-8",
        )

        with self.assertRaises(sqlite3.OperationalError):
            rehearse(self.database, migration_dir)

        # A failed DDL/data migration must not leak the migration ledger or
        # partially-created schema back into the source database.
        with sqlite3.connect(self.database) as db:
            names = {
                row[0] for row in db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            self.assertNotIn("schema_migrations", names)
            self.assertNotIn("should_rollback", names)
            self.assertEqual(db.execute("SELECT firm_id FROM cases WHERE id=1").fetchone()[0], 1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM docs").fetchone()[0], 1)

    def test_missing_source_fails_closed(self):
        with self.assertRaises(FileNotFoundError):
            rehearse(self.root / "missing.sqlite3", self.migrations)


if __name__ == "__main__":
    unittest.main()
