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
        self.assertIn(4, applied)
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


if __name__ == "__main__":
    unittest.main()
