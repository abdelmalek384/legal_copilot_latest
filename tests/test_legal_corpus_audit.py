import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_legal_corpus", ROOT / "tools" / "audit_legal_corpus.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class CorpusAuditTests(unittest.TestCase):
    def test_strict_cli_fails_on_high_severity_issues_and_supports_special_paths(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "sample ?audit.db"
            db = sqlite3.connect(db_path)
            db.execute("CREATE TABLE chunks(id INTEGER PRIMARY KEY, ref TEXT, article TEXT, text TEXT, source TEXT, verified INT, in_force INT, case_id INT)")
            db.execute("INSERT INTO chunks(ref,article,text,source,verified,in_force,case_id) VALUES('law','1','text','',0,1,NULL)")
            db.commit()
            db.close()
            out_dir = Path(td) / "audit output"
            result = MODULE.main(["--db", str(db_path), "--out-dir", str(out_dir), "--strict"])
            self.assertEqual(result, 1)
            report = json.loads((out_dir / "legal_corpus_audit.json").read_text(encoding="utf-8"))
            self.assertTrue(report["read_only"])
            self.assertEqual(report["database_sha256"], MODULE.sha256_file(db_path))
            self.assertIn("sqlite_sidecars", report)
            db = sqlite3.connect(db_path)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0], 1)
            db.close()

    def test_missing_registry_is_reported_and_database_is_read_only(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "sample.db"
            db = sqlite3.connect(db_path)
            db.execute("CREATE TABLE chunks(id INTEGER PRIMARY KEY, ref TEXT, article TEXT, text TEXT, source TEXT, verified INT, in_force INT, case_id INT)")
            db.execute("INSERT INTO chunks(ref,article,text,source,verified,in_force,case_id) VALUES('law - article 1','1','text','',0,1,NULL)")
            db.commit()
            db.close()
            report = MODULE.audit(db_path)
            self.assertTrue(report["read_only"])
            codes = {issue["code"] for issue in report["issues"]}
            self.assertIn("registry_tables_missing", codes)
            self.assertIn("chunks_missing_source", codes)
            self.assertIn("chunks_marked_in_force_but_unverified", codes)
            db = sqlite3.connect(db_path)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0], 1)
            db.close()

    def test_full_registry_quality_counts_are_reported(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "sample.db"
            db = sqlite3.connect(db_path)
            db.executescript("""
            CREATE TABLE chunks(id INTEGER PRIMARY KEY, ref TEXT, article TEXT, text TEXT, source TEXT, verified INT, in_force INT, case_id INT, document_version_id INT);
            CREATE TABLE legal_sources(source_id TEXT PRIMARY KEY, collection_permission TEXT);
            CREATE TABLE legal_documents(document_id TEXT PRIMARY KEY);
            CREATE TABLE legal_document_versions(version_id INTEGER PRIMARY KEY, source_url TEXT, original_path TEXT, original_sha256 TEXT, publication_date TEXT, effective_date TEXT, repeal_date TEXT, legal_status TEXT, review_status TEXT, authenticity_verified INT, status_verified INT, amendment_history_verified INT);
            CREATE TABLE legal_version_relations(relation_id INTEGER PRIMARY KEY);
            CREATE TABLE legal_review_events(review_event_id INTEGER PRIMARY KEY);
            INSERT INTO chunks(ref,article,text,source,verified,in_force,case_id,document_version_id) VALUES('law','1','text','url',1,1,NULL,NULL);
            INSERT INTO legal_sources VALUES('S1','unknown');
            INSERT INTO legal_document_versions VALUES(1,'url',NULL,NULL,NULL,NULL,NULL,'unknown','pending_source_review',0,0,0);
            """)
            db.commit()
            db.close()
            report = MODULE.audit(db_path)
            self.assertEqual(report["counts"]["chunks"], 1)
            self.assertEqual(report["chunk_quality"]["unlinked_to_version"], 1)
            self.assertEqual(report["source_permissions"]["unknown"], 1)
            self.assertEqual(report["version_quality"]["missing_hash"], 1)

    def test_reuse_permission_source_urls_hashes_and_dates_are_audited(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "evidence.db"
            db = sqlite3.connect(db_path)
            db.executescript("""
            CREATE TABLE legal_sources(source_id TEXT PRIMARY KEY, collection_permission TEXT, commercial_reuse_permission TEXT, permission_evidence TEXT, terms_url TEXT, source_page TEXT, terms_checked_on TEXT);
            CREATE TABLE legal_documents(document_id TEXT PRIMARY KEY);
            CREATE TABLE legal_document_versions(version_id INTEGER PRIMARY KEY, source_url TEXT, original_path TEXT, original_sha256 TEXT, publication_date TEXT, effective_date TEXT, repeal_date TEXT, consolidated_as_of TEXT, legal_status TEXT, review_status TEXT, authenticity_verified INT, status_verified INT, amendment_history_verified INT);
            CREATE TABLE legal_version_relations(relation_id INTEGER PRIMARY KEY, from_version_id INT, to_version_id INT, relation_type TEXT);
            CREATE TABLE legal_review_events(review_event_id INTEGER PRIMARY KEY, version_id INT, review_type TEXT, outcome TEXT, evidence_url TEXT);
            INSERT INTO legal_sources VALUES('S1','allowed','unknown',NULL,'http://terms.example.com','http://source.example.com','2024-13-01');
            INSERT INTO legal_document_versions VALUES(1,'http://unsafe.example.com/law','missing.pdf','not-a-hash','2024-13-40','2025-01-01','2024-12-31',NULL,'unknown','pending_source_review',0,0,0);
            INSERT INTO legal_sources VALUES('S2','allowed','allowed',NULL,'https://terms.example.com','https://source.example.com','2024-01-01');
            INSERT INTO legal_sources VALUES('S3','allowed','unknown',NULL,NULL,NULL,NULL);
            INSERT INTO legal_sources VALUES('S4','allowed','unknown','reviewed terms evidence','https://terms.example.com','https://source.example.com','9999-12-31');
            """)
            digest = "a" * 64
            db.executemany(
                "INSERT INTO legal_document_versions VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                [
                    (2, "https://example.gov/future", "future.pdf", digest, "2000-01-01", "9999-01-01", None, None, "in_force", "verified", 1, 1, 1),
                    (3, "https://example.gov/repealed", "repealed.pdf", digest, "2000-01-01", "2000-01-01", "2001-01-01", None, "in_force", "verified", 1, 1, 1),
                    (4, "https://example.gov/no-repeal-date", "no-repeal.pdf", digest, "2000-01-01", "2000-01-01", None, None, "repealed", "verified", 1, 1, 1),
                ],
            )
            db.commit()
            db.close()
            report = MODULE.audit(db_path)
            codes = {issue["code"] for issue in report["issues"]}
            self.assertIn("source_commercial_reuse_permission_unknown", codes)
            self.assertIn("source_allowed_without_permission_evidence", codes)
            self.assertIn("source_commercial_reuse_allowed_without_evidence", codes)
            self.assertIn("source_terms_url_not_https", codes)
            self.assertIn("source_page_not_https", codes)
            self.assertIn("source_page_missing", codes)
            self.assertIn("source_permission_terms_check_date_invalid", codes)
            self.assertIn("source_permission_terms_check_date_in_future", codes)
            self.assertIn("versions_in_force_before_effective_date", codes)
            self.assertIn("versions_in_force_after_repeal_date", codes)
            self.assertIn("versions_repealed_without_repeal_date", codes)
            self.assertIn("source_permission_terms_check_date_missing", codes)
            self.assertIn("versions_malformed_sha256", codes)
            self.assertIn("versions_invalid_source_url", codes)
            self.assertIn("versions_malformed_dates", codes)
            self.assertIn("versions_repeal_before_effective_date", codes)
            self.assertIn("commercial_reuse_permissions", report)

    def test_amendment_history_flags_require_review_evidence_and_relations_are_audited(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "versions.db"
            db = sqlite3.connect(db_path)
            db.executescript("""
            CREATE TABLE chunks(id INTEGER PRIMARY KEY, ref TEXT, article TEXT, text TEXT, source TEXT, verified INT, in_force INT, case_id INT, document_version_id INT);
            CREATE TABLE legal_sources(source_id TEXT PRIMARY KEY, collection_permission TEXT);
            CREATE TABLE legal_documents(document_id TEXT PRIMARY KEY);
            CREATE TABLE legal_document_versions(
              version_id INTEGER PRIMARY KEY, source_url TEXT, original_path TEXT, original_sha256 TEXT,
              publication_date TEXT, effective_date TEXT, repeal_date TEXT, legal_status TEXT,
              review_status TEXT, authenticity_verified INT, status_verified INT, amendment_history_verified INT
            );
            CREATE TABLE legal_version_relations(
              relation_id INTEGER PRIMARY KEY, from_version_id INT, to_version_id INT, relation_type TEXT
            );
            CREATE TABLE legal_review_events(
              review_event_id INTEGER PRIMARY KEY, version_id INT, review_type TEXT, outcome TEXT, evidence_url TEXT
            );
            INSERT INTO legal_document_versions VALUES
              (1,'https://example.gov/a',NULL,NULL,'2020-01-01','2020-01-01',NULL,'in_force','verified',1,1,0),
              (2,'https://example.gov/b',NULL,NULL,'2021-01-01','2021-01-01',NULL,'in_force','verified',1,1,1);
            INSERT INTO legal_version_relations VALUES(1,1,2,'amends');
            INSERT INTO legal_document_versions VALUES
              (3,'https://example.gov/c',NULL,NULL,'2022-01-01','2022-01-01',NULL,'in_force','verified',1,1,1);
            INSERT INTO legal_review_events VALUES
              (1,2,'amendment_history','pass','not-a-url'),
              (2,3,'amendment_history','pass','https://example.gov/evidence/review.pdf');
            """)
            db.commit()
            db.close()
            report = MODULE.audit(db_path)
            codes = {issue["code"] for issue in report["issues"]}
            self.assertIn("versions_verified_in_force_without_amendment_history_review", codes)
            self.assertIn("versions_amendment_history_flag_without_evidence", codes)
            self.assertIn("relations_touching_unreviewed_amendment_history", codes)
            self.assertEqual(report["version_quality"]["amendment_history_flag_without_evidence"], 1)
            self.assertEqual(report["relation_quality"]["relations_touching_unreviewed_amendment_history"], 1)

if __name__ == "__main__":
    unittest.main()
