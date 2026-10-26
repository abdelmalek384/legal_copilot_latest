"""Tests for the read-only legacy chunk evidence manifest."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.legacy_chunk_evidence_manifest import build_manifest


class LegacyChunkEvidenceManifestTests(unittest.TestCase):
    def test_classifies_provenance_without_exposing_text_or_mutating_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            database = Path(tmp) / "legacy.sqlite3"
            with sqlite3.connect(database) as db:
                db.executescript("""
                    CREATE TABLE cases(id INTEGER PRIMARY KEY, firm_id INTEGER);
                    INSERT INTO cases(id,firm_id) VALUES (10,1),(11,2);
                    CREATE TABLE docs(
                        id INTEGER PRIMARY KEY, case_id INTEGER, firm_id INTEGER,
                        uploader_user_id INTEGER, sha256 TEXT
                    );
                    INSERT INTO docs(id,case_id,firm_id,sha256) VALUES
                        (100,10,1,'doc-hash');
                    CREATE TABLE legal_document_versions(
                        version_id INTEGER PRIMARY KEY, document_id TEXT,
                        original_sha256 TEXT, legal_status TEXT, review_status TEXT
                    );
                    INSERT INTO legal_document_versions(version_id,document_id,legal_status,review_status)
                        VALUES (50,'LAW-1','in_force','verified');
                    CREATE TABLE chunks(
                        id INTEGER PRIMARY KEY, case_id INTEGER, document_id INTEGER,
                        document_version_id INTEGER, source TEXT, ref TEXT, article TEXT,
                        page TEXT, text TEXT, norm TEXT, verified INTEGER, in_force INTEGER, as_of TEXT
                    );
                    INSERT INTO chunks(id,case_id,document_id,document_version_id,source,ref,text,norm)
                        VALUES
                        (1,10,100,NULL,'upload','case 10','MATTER-SECRET-TEXT','matter-secret-text'),
                        (2,NULL,100,NULL,'upload','missing case','PRIVATE-ORPHAN-TEXT','private-orphan-text'),
                        (3,NULL,NULL,50,'law-registry','LAW-1','LEGAL-CORPUS-CANDIDATE','legal-corpus-candidate'),
                        (4,NULL,NULL,NULL,'unknown','unknown source','UNCLASSIFIED-SECRET','unclassified-secret'),
                        (5,11,100,NULL,'upload','cross firm','MISMATCH-SECRET','mismatch-secret'),
                        (6,NULL,999,NULL,'upload','dangling doc','DANGLING-SECRET','dangling-secret');
                """)

            with sqlite3.connect(database) as db:
                db.row_factory = sqlite3.Row
                db.execute("PRAGMA query_only=ON")
                report = build_manifest(db)

            self.assertFalse(report["source_modified"])
            self.assertFalse(report["ownership_assigned"])
            self.assertEqual(report["summary"]["chunks_seen"], 6)
            by_id = {record["chunk_id"]: record for record in report["records"]}
            self.assertEqual(by_id[1]["classification"], "matter_linked")
            self.assertEqual(by_id[2]["classification"], "chunk_missing_case_but_document_has_case")
            self.assertEqual(by_id[3]["classification"], "legal_version_linked_candidate_not_auto_shared")
            self.assertEqual(by_id[4]["classification"], "unclassified_no_case_or_document_link")
            self.assertEqual(by_id[5]["classification"], "document_case_mismatch")
            self.assertEqual(by_id[6]["classification"], "document_reference_unresolved")
            self.assertRegex(by_id[4]["text_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(by_id[4]["text_byte_length"], len("UNCLASSIFIED-SECRET".encode()))
            rendered = str(report)
            for secret in (
                "MATTER-SECRET-TEXT", "PRIVATE-ORPHAN-TEXT", "LEGAL-CORPUS-CANDIDATE",
                "UNCLASSIFIED-SECRET", "MISMATCH-SECRET", "DANGLING-SECRET",
            ):
                self.assertNotIn(secret, rendered)
            with sqlite3.connect(database) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0], 6)
                self.assertIsNone(db.execute(
                    "SELECT name FROM sqlite_master WHERE name='schema_migrations'"
                ).fetchone())

    def test_missing_chunks_table_requires_review(self):
        with sqlite3.connect(":memory:") as db:
            db.row_factory = sqlite3.Row
            report = build_manifest(db)
        self.assertEqual(report["status"], "review_required")
        self.assertEqual(report["schema_issue"], "chunks table is missing")
        self.assertFalse(report["source_modified"])


if __name__ == "__main__":
    unittest.main()
