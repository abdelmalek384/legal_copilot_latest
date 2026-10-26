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

    def test_multiple_statements_per_line_and_trigger_bodies(self):
        self.write(
            "0001_compact_schema.sql",
            "CREATE TABLE sample(id INTEGER PRIMARY KEY); "
            "CREATE TABLE audit(value INTEGER); "
            "CREATE TRIGGER sample_audit AFTER INSERT ON sample BEGIN "
            "INSERT INTO audit(value) VALUES(new.id); "
            "INSERT INTO audit(value) VALUES(new.id + 1); END;"
        )
        self.assertEqual(apply_migrations(self.db, self.path), [1])
        self.db.execute("INSERT INTO sample(id) VALUES(40)")
        self.assertEqual(
            [row[0] for row in self.db.execute("SELECT value FROM audit ORDER BY value")],
            [40, 41],
        )

    def test_concurrent_runners_do_not_apply_the_same_migration_twice(self):
        import threading

        database = self.path / "concurrent.sqlite3"
        self.write("0001_create_sample.sql", """
            CREATE TABLE sample(id INTEGER PRIMARY KEY, value TEXT);
            INSERT INTO sample(value) VALUES('once');
        """)
        barrier = threading.Barrier(2)
        failures = []
        failure_lock = threading.Lock()

        class BarrierConnection(sqlite3.Connection):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._initial_ledger_read = False

            def execute(self, sql, parameters=()):
                cursor = super().execute(sql, parameters)
                if (
                    sql.strip().startswith(
                        "SELECT version, name, checksum_sha256 FROM schema_migrations"
                    )
                    and not self._initial_ledger_read
                ):
                    self._initial_ledger_read = True
                    barrier.wait(timeout=10)
                return cursor

        def run_migrations():
            connection = sqlite3.connect(
                database, timeout=10, factory=BarrierConnection
            )
            try:
                apply_migrations(connection, self.path)
            except Exception as exc:
                with failure_lock:
                    failures.append(exc)
            finally:
                connection.close()

        threads = [threading.Thread(target=run_migrations) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=15)

        self.assertFalse(any(thread.is_alive() for thread in threads), "migration runner deadlocked")
        self.assertEqual(failures, [])
        with sqlite3.connect(database) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM sample").fetchone()[0], 1)
            self.assertEqual(
                db.execute("SELECT COUNT(*) FROM schema_migrations WHERE version=1").fetchone()[0],
                1,
            )

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

    def test_interrupted_migration_keeps_prior_version_and_can_retry(self):
        self.write(
            "0001_create_sample.sql",
            "CREATE TABLE sample(id INTEGER PRIMARY KEY, value TEXT); "
            "INSERT INTO sample(value) VALUES('preserved');",
        )
        self.write(
            "0002_add_status.sql",
            "ALTER TABLE sample ADD COLUMN status TEXT; "
            "INSERT INTO missing_table(value) VALUES('fail');",
        )

        with self.assertRaises(sqlite3.OperationalError):
            apply_migrations(self.db, self.path)

        # Each migration is its own transaction: version 1 remains committed,
        # while the failed version's DDL and ledger entry are rolled back.
        self.assertEqual(
            [row[0] for row in self.db.execute(
                "SELECT version FROM schema_migrations ORDER BY version"
            )],
            [1],
        )
        self.assertEqual(
            self.db.execute("SELECT value FROM sample").fetchone()[0], "preserved"
        )
        self.assertNotIn(
            "status",
            [row["name"] for row in self.db.execute("PRAGMA table_info(sample)")],
        )

        # A failed, unrecorded migration can be repaired before it is applied;
        # the already-applied migration remains immutable and is not rerun.
        self.write(
            "0002_add_status.sql",
            "ALTER TABLE sample ADD COLUMN status TEXT DEFAULT 'ready';",
        )
        self.assertEqual(apply_migrations(self.db, self.path), [2])
        self.assertEqual(
            tuple(self.db.execute("SELECT value,status FROM sample").fetchone()),
            ("preserved", "ready"),
        )
        self.assertEqual(
            [row[0] for row in self.db.execute(
                "SELECT version FROM schema_migrations ORDER BY version"
            )],
            [1, 2],
        )

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
    def test_symlinked_migration_file_is_rejected(self):
        target = self.path / "outside.sql"
        target.write_text("CREATE TABLE unexpected (id INTEGER);", encoding="utf-8")
        link = self.path / "0001_linked.sql"
        link.symlink_to(target)
        with self.assertRaisesRegex(MigrationError, "must not be a symlink"):
            apply_migrations(self.db, self.path)
        self.assertIsNone(self.db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='unexpected'"
        ).fetchone())

    def test_symlinked_migration_directory_is_rejected(self):
        actual = self.path / "actual"
        actual.mkdir()
        (actual / "0001_create_sample.sql").write_text(
            "CREATE TABLE sample (id INTEGER);", encoding="utf-8"
        )
        link = self.path / "linked"
        link.symlink_to(actual, target_is_directory=True)
        with self.assertRaisesRegex(MigrationError, "directory must not be a symlink"):
            apply_migrations(self.db, link)
        self.assertIsNone(self.db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sample'"
        ).fetchone())

    def test_transaction_control_is_rejected(self):
        self.write("0001_bad.sql", "BEGIN; CREATE TABLE sample (id INTEGER);")
        with self.assertRaisesRegex(MigrationError, "Transaction control"):
            apply_migrations(self.db, self.path)
        self.assertIsNone(self.db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sample'"
        ).fetchone())

    def test_startup_schema_no_longer_creates_indexes_inline(self):
        # Guard the incremental DDL cutover: indexes belong in immutable
        # migrations, while legacy table bootstrap remains for now.
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

    def test_conditional_column_migration_adds_missing_column(self):
        self.write("0001_create_sample.sql", "CREATE TABLE sample(id INTEGER PRIMARY KEY);")
        self.write("0002_optional_column.sql", """
            -- @add-column-if-missing sample value
            ALTER TABLE sample ADD COLUMN value TEXT DEFAULT '';
        """)
        self.assertEqual(apply_migrations(self.db, self.path), [1, 2])
        columns = {row["name"] for row in self.db.execute("PRAGMA table_info(sample)")}
        self.assertIn("value", columns)

    def test_conditional_column_migration_skips_existing_column(self):
        self.write("0001_create_sample.sql", "CREATE TABLE sample(id INTEGER PRIMARY KEY, value TEXT);")
        self.write("0002_optional_column.sql", """
            -- @add-column-if-missing sample value
            ALTER TABLE sample ADD COLUMN value TEXT DEFAULT '';
        """)
        self.assertEqual(apply_migrations(self.db, self.path), [1, 2])
        columns = [row["name"] for row in self.db.execute("PRAGMA table_info(sample)")]
        self.assertEqual(columns, ["id", "value"])

    def test_repository_migrations_create_startup_indexes(self):
        # Startup creates these prerequisite tables/columns before applying
        # repository migrations. This guards the migration-backed index set.
        self.db.executescript("""
            CREATE TABLE firms(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
            CREATE TABLE users(id INTEGER PRIMARY KEY, firm_id INTEGER);
            CREATE TABLE legal_documents(document_id TEXT PRIMARY KEY, official_title TEXT, document_type TEXT);
            CREATE TABLE tenant_ownership_quarantine(first_seen TEXT);
            CREATE TABLE cases(id INTEGER PRIMARY KEY, firm_id INTEGER);
            INSERT INTO cases(id,firm_id) VALUES (1,7);
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
        migrations = Path(__file__).resolve().parents[1] / "migrations"
        self.assertEqual(apply_migrations(self.db, migrations), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
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
        self.assertIn("using fts5(norm)", fts_sql.lower())
        self.db.execute("INSERT INTO chunks_fts(norm) VALUES('migration search sentinel')")
        self.assertEqual(
            self.db.execute(
                "SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH 'sentinel'"
            ).fetchone()[0],
            1,
        )
        self.assertEqual(self.db.execute("SELECT name FROM firms WHERE id=1").fetchone()[0], "Default Firm")
        self.assertEqual(self.db.execute("SELECT firm_id FROM docs WHERE id=10").fetchone()[0], 7)
        for table, expected in {
            "users": {"active"},
            "legal_documents": {"practice_area"},
            "chunks": {"verified", "document_version_id", "page"},
            "docs": {"firm_id", "uploader_user_id", "sha256", "content_type", "byte_size", "extraction_status", "ocr_used"},
            "document_extraction_reviews": {"page_reference"},
            "cases": {"case_number", "case_year", "court", "circuit", "opposing_party"},
        }.items():
            columns = {row["name"] for row in self.db.execute(f"PRAGMA table_info({table})")}
            self.assertTrue(expected <= columns, f"{table} missing columns: {expected - columns}")
        self.assertEqual(apply_migrations(self.db, migrations), [])


    def test_conditional_column_migration_matches_existing_column_case_insensitively(self):
        self.write("0001_create_sample.sql", "CREATE TABLE sample(id INTEGER PRIMARY KEY, Value TEXT);")
        self.write("0002_optional_column.sql", """
            -- @add-column-if-missing sample value
            ALTER TABLE sample ADD COLUMN value TEXT DEFAULT '';
        """)
        self.assertEqual(apply_migrations(self.db, self.path), [1, 2])
        columns = [row["name"] for row in self.db.execute("PRAGMA table_info(sample)")]
        self.assertEqual(columns, ["id", "Value"])

if __name__ == "__main__":
    unittest.main()
