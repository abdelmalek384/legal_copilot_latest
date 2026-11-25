import sqlite3
import unittest
from pathlib import Path

from schema_profiles import apply_profile_migrations
from tools.source_match_evidence import load_source_match_evidence


class SourceMatchEvidenceAdapterTests(unittest.TestCase):
    def test_legal_corpus_migration_creates_append_only_evidence_store(self):
        db = sqlite3.connect(":memory:")
        db.execute("PRAGMA foreign_keys=ON")
        applied = apply_profile_migrations(
            db, "legal_corpus", Path(__file__).resolve().parents[1] / "migrations"
        )
        self.assertIn(5, applied)
        tables = {
            row[0] for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        triggers = {
            row[0] for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger'"
            )
        }
        self.assertIn("legal_source_match_evidence", tables)
        self.assertIn("legal_source_match_evidence_uses", tables)
        self.assertIn("legal_source_match_evidence_no_update", triggers)
        db.close()

    def test_bad_ids_fail_closed_before_database_access(self):
        self.assertIsNone(load_source_match_evidence(None, True, "source"))
        self.assertIsNone(load_source_match_evidence(None, 1, " source"))
        self.assertIsNone(load_source_match_evidence(None, 1, None))


    def test_adapter_rejects_registry_hash_mismatch_before_loading_uses(self):
        class Cursor:
            description = [(name,) for name in ("registry_source_id", "registry_publication_date", "registry_effective_date", "registry_original_sha256", "original_capture_sha256", "publication_date", "effective_date", "evidence_id")]
            def fetchone(self):
                return ("src", "2020-01-01", "2020-01-02", "b" * 64, "a" * 64, "2020-01-01", "2020-01-02", 1)
        class Connection:
            calls = 0
            def execute(self, sql, params):
                self.calls += 1
                return Cursor()
        db = Connection()
        self.assertIsNone(load_source_match_evidence(db, 1, "src"))
        self.assertEqual(db.calls, 1)

    def test_adapter_fails_closed_on_non_string_approved_use(self):
        class Cursor:
            def __init__(self, description, row=None, rows=None):
                self.description = [(x,) for x in description]
                self.row, self.rows = row, rows or []
            def fetchone(self): return self.row
            def fetchall(self): return self.rows
        rec = {"registry_source_id":"src","registry_publication_date":"2020-01-01",
               "registry_effective_date":"2020-01-02","registry_original_sha256":"a"*64,
               "original_capture_sha256":"a"*64,"publication_date":"2020-01-01",
               "effective_date":"2020-01-02","evidence_id":1}
        columns=list(rec)
        class Connection:
            def execute(self, sql, params):
                if "legal_source_match_evidence_uses" in sql:
                    return Cursor(["approved_use"], rows=[(None,)])
                return Cursor(columns, tuple(rec[k] for k in columns))
        self.assertIsNone(load_source_match_evidence(Connection(), 1, "src"))

if __name__ == "__main__":
    unittest.main()
