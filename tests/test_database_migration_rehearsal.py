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
                CREATE TABLE tenant_ownership_quarantine(first_seen TEXT);
                CREATE TABLE cases(firm_id INTEGER);
                CREATE TABLE members(user_id INTEGER, case_id INTEGER);
                CREATE TABLE deadlines(case_id INTEGER, due TEXT, status TEXT);
                CREATE TABLE docs(case_id INTEGER, id INTEGER);
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
                INSERT INTO cases VALUES (1);
            """)
        self.migrations = Path(__file__).resolve().parents[1] / "migrations"

    def tearDown(self):
        self.temp.cleanup()

    def test_migrations_apply_to_copy_without_changing_source(self):
        report = rehearse(self.database, self.migrations)
        self.assertEqual(report["status"], "passed")
        self.assertFalse(report["source_modified"])
        self.assertEqual(report["migrations_applied"], [1, 2, 3, 4, 5, 6])
        self.assertEqual(report["source_quick_check"], ["ok"])
        self.assertEqual(report["staged_quick_check"], ["ok"])
        self.assertEqual(report["source_foreign_key_violations"], 0)
        self.assertEqual(report["staged_foreign_key_violations"], 0)
        with sqlite3.connect(self.database) as db:
            names = {row[0] for row in db.execute("SELECT name FROM sqlite_master")}
            self.assertNotIn("schema_migrations", names)
            self.assertNotIn("idx_cases_firm", names)
            self.assertNotIn("idx_login_attempts_window", names)
            self.assertTrue({
                "auth_sessions", "notes", "fees", "tasks", "events", "sessions"
            } <= names)
            self.assertEqual(db.execute("SELECT firm_id FROM cases").fetchone()[0], 1)

    def test_missing_source_fails_closed(self):
        with self.assertRaises(FileNotFoundError):
            rehearse(self.root / "missing.sqlite3", self.migrations)


if __name__ == "__main__":
    unittest.main()
