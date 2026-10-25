import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("legal_source_review_queue",ROOT/"tools"/"legal_source_review_queue.py")
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

def make_db(path):
    db=sqlite3.connect(path)
    db.executescript("""
    CREATE TABLE legal_sources(source_id TEXT PRIMARY KEY,authority TEXT,source_page TEXT,collection_permission TEXT,commercial_reuse_permission TEXT,terms_url TEXT,permission_evidence TEXT);
    CREATE TABLE legal_documents(document_id TEXT PRIMARY KEY,source_id TEXT,official_title TEXT,document_type TEXT);
    CREATE TABLE legal_document_versions(version_id INTEGER PRIMARY KEY,document_id TEXT,version_label TEXT,source_url TEXT,original_sha256 TEXT,publication_date TEXT,effective_date TEXT,repeal_date TEXT,legal_status TEXT,review_status TEXT,authenticity_verified INTEGER,status_verified INTEGER,amendment_history_verified INTEGER,permission_evidence TEXT);
    CREATE TABLE legal_review_events(review_event_id INTEGER PRIMARY KEY,version_id INTEGER,review_type TEXT,outcome TEXT,evidence_url TEXT,reviewer TEXT,reviewed_at TEXT);
    INSERT INTO legal_sources VALUES('SRC-1','Test authority','https://example.gov','unknown','unknown',NULL,NULL);
    INSERT INTO legal_documents VALUES('DOC-1','SRC-1','Test law','law');
    INSERT INTO legal_document_versions VALUES(1,'DOC-1','initial','https://example.gov/law.pdf',NULL,NULL,NULL,NULL,'unknown','pending_source_review',0,0,0,NULL);
    """)
    db.commit()
    db.close()

class LegalSourceReviewQueueTests(unittest.TestCase):
    def test_queue_flags_missing_provenance_and_permission_without_mutating_db(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"legal.db"
            make_db(path)
            report=MODULE.review_queue(path)
            self.assertTrue(report["read_only"])
            self.assertEqual(report["summary"]["versions_in_queue"],1)
            self.assertEqual(report["summary"]["sources_with_permission_follow_up"],1)
            reasons=report["records"][0]["review_reasons"]
            self.assertIn("original_content_hash_missing",reasons)
            self.assertIn("review_evidence_missing:lawyer_approval",reasons)
            self.assertIn("source_collection_permission_not_confirmed",reasons)
            db=sqlite3.connect(path)
            self.assertEqual(db.execute("SELECT review_status FROM legal_document_versions").fetchone()[0],"pending_source_review")
            self.assertEqual(db.execute("SELECT COUNT(*) FROM legal_review_events").fetchone()[0],0)
            db.close()

    def test_commercial_reuse_restrictions_are_never_treated_as_approved(self):
        cases = (
            ("prohibited", "source_commercial_reuse_permission_not_allowed"),
            ("not_allowed_without_explicit_exception_or_license", "source_commercial_reuse_permission_not_allowed"),
            ("allowed_limited", "source_commercial_reuse_permission_scope_limited"),
            ("unknown", "commercial_reuse_permission_unknown"),
        )
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"legal.db"
            make_db(path)
            for permission, expected_reason in cases:
                db = sqlite3.connect(path)
                db.execute("UPDATE legal_sources SET commercial_reuse_permission=?", (permission,))
                db.commit()
                db.close()
                report = MODULE.review_queue(path)
                self.assertIn(expected_reason, report["source_permissions"][0]["review_reasons"], permission)
                self.assertIn(expected_reason, report["records"][0]["review_reasons"], permission)

    def test_orphaned_versions_are_included_in_review_queue(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"legal.db"
            make_db(path)
            db = sqlite3.connect(path)
            db.execute(
                "INSERT INTO legal_document_versions VALUES(2,'DOC-MISSING','orphaned','https://example.gov/orphan.pdf',NULL,NULL,NULL,NULL,'unknown','pending_source_review',0,0,0,NULL)"
            )
            db.execute(
                "INSERT INTO legal_documents VALUES('DOC-NO-SOURCE','SRC-MISSING','Missing source law','law')"
            )
            db.execute(
                "INSERT INTO legal_document_versions VALUES(3,'DOC-NO-SOURCE','initial','https://example.gov/no-source.pdf',NULL,NULL,NULL,NULL,'unknown','pending_source_review',0,0,0,NULL)"
            )
            db.commit()
            db.close()

            report = MODULE.review_queue(path)
            by_id = {record["version_id"]: record for record in report["records"]}
            self.assertIn(2, by_id)
            self.assertIn("document_missing_from_registry", by_id[2]["review_reasons"])
            self.assertIn(3, by_id)
            self.assertIn("source_missing_from_registry", by_id[3]["review_reasons"])
            self.assertEqual(report["summary"]["versions_scanned"], 3)

    def test_missing_registry_tables_report_schema_issue(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"empty.db"
            sqlite3.connect(path).close()
            report=MODULE.review_queue(path)
            self.assertEqual(report["issues"][0]["code"],"review_schema_tables_missing")
            self.assertEqual(report["records"],[])

if __name__=="__main__":
    unittest.main()
