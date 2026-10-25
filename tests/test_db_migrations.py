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

    def test_startup_schema_no_longer_creates_indexes_inline(self):
        # Guard the incremental DDL cutover: indexes belong in immutable
        # migrations, while legacy table/FTS bootstrap remains for now.
        import ast

        app_path = Path(__file__).resolve().parents[1] / "app.py"
        tree = ast.parse(app_path.read_text(encoding="utf-8"))
        schema = next(
            ast.literal_eval(node.value)
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "SCHEMA"
                    for target in node.targets)
        )
        self.assertNotIn("CREATE INDEX", schema.upper())
        self.assertIn("CREATE TABLE IF NOT EXISTS", schema.upper())
        self.assertNotIn("CREATE VIRTUAL TABLE", schema.upper())

    def test_repository_migrations_create_startup_indexes(self):
        # Startup creates these prerequisite tables/columns before applying
        # repository migrations. This guards the migration-backed index set.
        self.db.executescript("""
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
        """)
        migrations = Path(__file__).resolve().parents[1] / "migrations"
        self.assertEqual(apply_migrations(self.db, migrations), [1, 2, 3, 4, 5, 6, 7, 8])
        indexes = {
            row[0] for row in self.db.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            )
        }
        self.assertTrue({
            "idx_tenant_quarantine_first_seen",
            "idx_cases_firm",
            "idx_members_user_case",
            "idx_deadlines_case_due",
            "idx_docs_case_added",
            "idx_chunks_document_id",
            "idx_doc_reviews_document",
            "idx_login_attempts_window",
            "idx_case_deletion_audit_firm_id",
            "idx_api_rate_limit_windows_start",
            "idx_legal_version_sha256",
            "idx_legal_versions_dates",
            "idx_legal_versions_review",
            "idx_legal_review_events_version",
            "idx_research_conversations_owner",
            "idx_research_messages_conversation",
        } <= indexes)
        relation_columns = {
            row["name"] for row in self.db.execute("PRAGMA table_info(legal_version_relations)")
        }
        self.assertTrue({
            "relation_id", "from_version_id", "to_version_id", "relation_type",
            "notes", "created_at",
        } <= relation_columns)
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO legal_version_relations(from_version_id,to_version_id,relation_type) VALUES(1,1,'amends')"
            )
        audit_columns = {
            row["name"] for row in self.db.execute("PRAGMA table_info(security_audit_events)")
        }
        self.assertEqual(
            audit_columns, {"id", "firm_id", "user_id", "event", "created_at"}
        )
        workspace_columns = {
            table: {row["name"] for row in self.db.execute(f"PRAGMA table_info({table})")}
            for table in ("auth_sessions", "notes", "fees", "tasks", "events", "sessions")
        }
        self.assertEqual(workspace_columns["auth_sessions"], {"token_hash", "user_id", "expires"})
        self.assertEqual(workspace_columns["notes"], {"id", "case_id", "created_by", "text", "created_at"})
        self.assertEqual(workspace_columns["fees"], {"id", "case_id", "title", "amount", "paid", "due", "note", "created_by"})
        self.assertEqual(workspace_columns["tasks"], {"id", "case_id", "title", "assignee", "due", "status", "created_by"})
        self.assertEqual(workspace_columns["events"], {"id", "case_id", "who", "at", "text"})
        self.assertEqual(workspace_columns["sessions"], {"id", "case_id", "date", "note", "done"})
        source_columns = {
            row["name"] for row in self.db.execute("PRAGMA table_info(legal_sources)")
        }
        self.assertEqual(source_columns, {
            "source_id", "authority", "source_page", "access_status",
            "collection_permission", "commercial_reuse_permission", "terms_url",
            "terms_checked_on", "permission_evidence", "created_at",
        })
        fts_sql = self.db.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='chunks_fts'"
        ).fetchone()[0]
        self.assertIn("USING fts5(norm)", fts_sql.lower())
        self.db.execute("INSERT INTO chunks_fts(norm) VALUES('migration search sentinel')")
        self.assertEqual(
            self.db.execute(
                "SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH 'sentinel'"
            ).fetchone()[0],
            1,
        )
        self.assertEqual(apply_migrations(self.db, migrations), [])


if __name__ == "__main__":
    unittest.main()
