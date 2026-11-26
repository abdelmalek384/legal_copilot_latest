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
        self.assertIn(6, applied)
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

    def test_bad_source_identifier_syntax_fails_closed_before_database_access(self):
        class Connection:
            calls = 0
            def execute(self, sql, params):
                self.calls += 1
                raise AssertionError("database must not be queried for malformed identifiers")
        for source_id in (" leading", "trailing ", "contains space", "slash/name", "semi;colon", "x" * 129, "قانون"):
            db = Connection()
            with self.subTest(source_id=source_id):
                self.assertIsNone(load_source_match_evidence(db, 1, source_id))
                self.assertEqual(db.calls, 0)
        db = Connection()
        self.assertIsNone(load_source_match_evidence(db, 1, "EG-LAW.14_2025-A"))
        self.assertEqual(db.calls, 1)

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
               "original_capture_sha256":"a"*64,"independent_copy_source_id":"independent","independent_copy_sha256":"b"*64,"evidence_revision":1,"publication_date":"2020-01-01",
               "effective_date":"2020-01-02","evidence_id":1,"validator_passed":1,
               "article_inventory_complete":1,"differences_resolved_against_primary":1,
               "publication_and_effective_dates_verified":1,"reuse_rights_allowed":1}
        columns=list(rec)
        class Connection:
            def execute(self, sql, params):
                if "legal_source_match_evidence_uses" in sql:
                    return Cursor(["approved_use"], rows=[(None,)])
                return Cursor(columns, tuple(rec[k] for k in columns))
        self.assertIsNone(load_source_match_evidence(Connection(), 1, "src"))


    def test_adapter_rejects_malformed_hashes_dates_and_independent_source_identity(self):
        base = {
            "registry_source_id": "src", "registry_publication_date": "2020-01-01",
            "registry_effective_date": "2020-01-02", "registry_original_sha256": "a" * 64,
            "original_capture_sha256": "a" * 64, "independent_copy_source_id": "independent",
            "independent_copy_sha256": "b" * 64, "publication_date": "2020-01-01",
            "effective_date": "2020-01-02", "evidence_id": 7, "evidence_revision": 1,
            "reuse_rights_allowed": 1, "validator_passed": 1, "article_inventory_complete": 1,
            "differences_resolved_against_primary": 1, "publication_and_effective_dates_verified": 1,
        }
        class Cursor:
            def __init__(self, description, row=None, rows=None):
                self.description = [(name,) for name in description]
                self.row, self.rows = row, rows or []
            def fetchone(self): return self.row
            def fetchall(self): return self.rows
        class Connection:
            def __init__(self, record): self.record = record
            def execute(self, sql, params):
                if "legal_source_match_evidence_uses" in sql:
                    return Cursor(["approved_use"], rows=[])
                return Cursor(list(self.record), tuple(self.record.values()))
        malformed = [
            ("original_capture_sha256", "not-a-hash"),
            ("independent_copy_sha256", "c" * 63),
            ("independent_copy_source_id", "src"),
            ("independent_copy_source_id", "bad source id"),
            ("publication_date", "2020-02-30"),
            ("effective_date", "2020-1-02"),
            ("evidence_revision", 0),
            ("evidence_revision", True),
        ]
        for field, value in malformed:
            record = dict(base)
            record[field] = value
            with self.subTest(field=field, value=value):
                self.assertIsNone(load_source_match_evidence(Connection(record), 1, "src"))

    def test_adapter_rejects_legacy_use_rows_without_affirmative_rights(self):
        # Simulate a pre-guard or manually altered database: the adapter must
        # fail closed even if an inconsistent approved-use row already exists.
        record = {
            "registry_source_id": "src",
            "registry_publication_date": "2020-01-01",
            "registry_effective_date": "2020-01-02",
            "registry_original_sha256": "a" * 64,
            "original_capture_sha256": "a" * 64,
            "publication_date": "2020-01-01",
            "effective_date": "2020-01-02",
            "evidence_id": 7,
            "validator_passed": 1,
            "independent_copy_source_id": "independent",
            "independent_copy_sha256": "b" * 64,
            "reuse_rights_evidence": "synthetic",
            "reuse_rights_evidence_url": "https://example.test/rights",
            "article_inventory_complete": 1,
            "differences_resolved_against_primary": 1,
            "publication_and_effective_dates_verified": 1,
            "reuse_rights_allowed": 0,
            "evidence_revision": 1,
            "recorded_at": "2026-11-25 00:00:00",
        }
        class Cursor:
            def __init__(self, description, row=None, rows=None):
                self.description = [(name,) for name in description]
                self.row, self.rows = row, rows or []
            def fetchone(self):
                return self.row
            def fetchall(self):
                return self.rows
        class Connection:
            def execute(self, sql, params):
                if "legal_source_match_evidence_uses" in sql:
                    return Cursor(["approved_use"], rows=[("collection",)])
                return Cursor(list(record), tuple(record.values()))
        self.assertIsNone(load_source_match_evidence(Connection(), 1, "src"))


    def test_adapter_rejects_unknown_or_duplicate_approved_uses(self):
        record = {
            "registry_source_id": "src", "registry_publication_date": "2020-01-01",
            "registry_effective_date": "2020-01-02", "registry_original_sha256": "a" * 64,
            "original_capture_sha256": "a" * 64, "publication_date": "2020-01-01",
            "effective_date": "2020-01-02", "evidence_id": 7, "evidence_revision": 1,
            "independent_copy_source_id": "independent", "independent_copy_sha256": "b" * 64,
            "reuse_rights_allowed": 1,
            "validator_passed": 1, "article_inventory_complete": 1,
            "differences_resolved_against_primary": 1,
            "publication_and_effective_dates_verified": 1,
        }
        class Cursor:
            def __init__(self, description, row=None, rows=None):
                self.description = [(name,) for name in description]
                self.row, self.rows = row, rows or []
            def fetchone(self): return self.row
            def fetchall(self): return self.rows
        class Connection:
            def __init__(self, uses): self.uses = uses
            def execute(self, sql, params):
                if "legal_source_match_evidence_uses" in sql:
                    return Cursor(["approved_use"], rows=[(value,) for value in self.uses])
                return Cursor(list(record), tuple(record.values()))
        for uses in (["collection", "unknown_use"], ["collection", "collection"]):
            with self.subTest(uses=uses):
                self.assertIsNone(load_source_match_evidence(Connection(uses), 1, "src"))


    def test_adapter_rejects_non_boolean_permission_and_validation_flags(self):
        base = {
            "registry_source_id": "src", "registry_publication_date": "2020-01-01",
            "registry_effective_date": "2020-01-02", "registry_original_sha256": "a" * 64,
            "original_capture_sha256": "a" * 64, "publication_date": "2020-01-01",
            "effective_date": "2020-01-02", "evidence_id": 7, "evidence_revision": 1,
            "independent_copy_source_id": "independent", "independent_copy_sha256": "b" * 64,
            "validator_passed": 1, "article_inventory_complete": 1,
            "differences_resolved_against_primary": 1,
            "publication_and_effective_dates_verified": 1, "reuse_rights_allowed": 1,
        }
        class Cursor:
            def __init__(self, description, row=None, rows=None):
                self.description = [(name,) for name in description]
                self.row, self.rows = row, rows or []
            def fetchone(self): return self.row
            def fetchall(self): return self.rows
        class Connection:
            def __init__(self, record): self.record = record
            def execute(self, sql, params):
                if "legal_source_match_evidence_uses" in sql:
                    return Cursor(["approved_use"], rows=[("collection",)])
                return Cursor(list(self.record), tuple(self.record.values()))
        for field in ("validator_passed", "article_inventory_complete",
                      "differences_resolved_against_primary",
                      "publication_and_effective_dates_verified", "reuse_rights_allowed"):
            for malformed in (2, -1, "1", None, True):
                record = dict(base)
                record[field] = malformed
                with self.subTest(field=field, malformed=malformed):
                    self.assertIsNone(load_source_match_evidence(Connection(record), 1, "src"))


    def test_store_is_append_only_and_adapter_reads_exact_version_evidence(self):
        db = sqlite3.connect(":memory:")
        apply_profile_migrations(
            db, "legal_corpus", Path(__file__).resolve().parents[1] / "migrations"
        )
        db.execute(
            "INSERT INTO legal_sources(source_id, authority, source_page) VALUES (?, ?, ?)",
            ("primary", "official", "https://example.test/primary"),
        )
        db.execute(
            "INSERT INTO legal_sources(source_id, authority, source_page) VALUES (?, ?, ?)",
            ("independent", "independent_copy", "https://example.test/independent"),
        )
        db.execute(
            "INSERT INTO legal_documents(document_id, source_id, official_title, document_type) "
            "VALUES (?, ?, ?, ?)",
            ("doc-1", "primary", "Fictional test instrument", "fictional_test"),
        )
        version_id = db.execute(
            "INSERT INTO legal_document_versions("
            "document_id, version_label, source_url, original_sha256, publication_date, effective_date"
            ") VALUES (?, ?, ?, ?, ?, ?)",
            ("doc-1", "test-v1", "https://example.test/text", "a" * 64,
             "2020-01-01", "2020-01-02"),
        ).lastrowid
        values = (
            version_id, "primary", 1, 0, "a" * 64, "independent", "b" * 64,
            "2020-01-01", "2020-01-02", "synthetic rights evidence",
            "https://example.test/rights", 1, 1, 1, 0, "synthetic-test",
        )
        insert = (
            "INSERT INTO legal_source_match_evidence("
            "version_id, source_id, evidence_revision, validator_passed, "
            "original_capture_sha256, independent_copy_source_id, independent_copy_sha256, "
            "publication_date, effective_date, reuse_rights_evidence, reuse_rights_evidence_url, "
            "article_inventory_complete, differences_resolved_against_primary, "
            "publication_and_effective_dates_verified, reuse_rights_allowed, recorded_by"
            ") VALUES (" + ",".join("?" for _ in values) + ")"
        )
        evidence_id = db.execute(insert, values).lastrowid
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO legal_source_match_evidence_uses(evidence_id, approved_use) VALUES (?, ?)",
                (evidence_id, "collection"),
            )

        packet = load_source_match_evidence(db, version_id, "primary")
        self.assertIsNotNone(packet)
        self.assertFalse(packet["validator_passed"])
        self.assertFalse(packet["reuse_rights_allowed"])
        self.assertEqual(packet["approved_uses"], [])

        # A later, explicitly permissive synthetic revision may carry scoped uses.
        permissive = list(values)
        permissive[2] = 2
        permissive[14] = 1
        permissive_id = db.execute(insert, tuple(permissive)).lastrowid
        db.execute(
            "INSERT INTO legal_source_match_evidence_uses(evidence_id, approved_use) VALUES (?, ?)",
            (permissive_id, "collection"),
        )
        packet = load_source_match_evidence(db, version_id, "primary")
        self.assertTrue(packet["reuse_rights_allowed"])
        self.assertEqual(packet["approved_uses"], ["collection"])

        with self.assertRaises(sqlite3.IntegrityError):
            db.execute(
                "UPDATE legal_source_match_evidence SET recorded_by='changed' WHERE evidence_id=?",
                (evidence_id,),
            )
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute(
                "DELETE FROM legal_source_match_evidence WHERE evidence_id=?",
                (evidence_id,),
            )
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute(
                "UPDATE legal_source_match_evidence_uses SET approved_use='storage' "
                "WHERE evidence_id=?",
                (evidence_id,),
            )
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute(
                "DELETE FROM legal_source_match_evidence_uses WHERE evidence_id=?",
                (evidence_id,),
            )

        mismatched = list(values)
        mismatched[1] = "independent"
        mismatched[2] = 2
        mismatched[5] = "primary"
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute(insert, tuple(mismatched))
        db.close()


if __name__ == "__main__":
    unittest.main()
