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

def bind_profile(db, profile="legal_corpus"):
    db.execute("CREATE TABLE database_profile(singleton INTEGER PRIMARY KEY CHECK(singleton=1), profile TEXT NOT NULL, bound_at TEXT NOT NULL DEFAULT (datetime('now')))")
    db.execute("INSERT INTO database_profile(singleton,profile) VALUES(1,?)", (profile,))


class CorpusAuditTests(unittest.TestCase):
    def test_evidence_url_validator_rejects_malformed_https_urls(self):
        self.assertTrue(MODULE.valid_evidence_url("https://example.gov/evidence"))
        for value in (
            " https://example.gov/evidence",
            "https://example.gov/evidence ",
            "https://example.gov/path with spaces",
            "https://user:pass@example.gov/evidence",
            "https://@example.gov/evidence",
            "https://example.gov:not-a-port/evidence",
            "https://example.gov:99999/evidence",
            "https://example.gov:0/evidence",
            "https://example.gov:/evidence",
        ):
            with self.subTest(value=value):
                self.assertFalse(MODULE.valid_evidence_url(value), value)

    def test_optional_fts_index_audit_detects_corruption_without_repairing_source(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "corpus.sqlite3"
            db = sqlite3.connect(path)
            bind_profile(db)
            db.executescript("""
                CREATE TABLE chunks(
                    id INTEGER PRIMARY KEY, ref TEXT, article TEXT, text TEXT,
                    source TEXT, verified INTEGER, in_force INTEGER, norm TEXT
                );
                CREATE VIRTUAL TABLE chunks_fts USING fts5(norm, content='chunks', content_rowid='id');
                INSERT INTO chunks(id,ref,article,text,source,verified,in_force,norm)
                VALUES(1,'Law - Article 1','1','hello world','synthetic-source',1,1,'hello world');
                INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild');
                INSERT INTO chunks_fts(chunks_fts) VALUES('delete-all');
            """)
            db.commit()
            db.close()

            report = MODULE.audit(path, check_fts_index=True)
            codes = {issue["code"] for issue in report["issues"]}
            self.assertIn("fts_fts_internal_index_integrity_failed", codes)
            self.assertEqual(report["fts_index_audit"]["status"], "review_required")

            db = sqlite3.connect(path)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0], 1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM chunks_fts").fetchone()[0], 1)
            db.close()

    def test_strict_cli_fails_on_high_severity_issues_and_supports_special_paths(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "sample ?audit.db"
            db = sqlite3.connect(db_path)

            bind_profile(db)
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

    def test_audit_rejects_unbound_and_wrong_profile_databases(self):
        with tempfile.TemporaryDirectory() as td:
            unbound = Path(td) / "unbound.db"
            sqlite3.connect(unbound).close()
            with self.assertRaisesRegex(ValueError, "legal_corpus profile"):
                MODULE.audit(unbound)

            wrong = Path(td) / "wrong.db"
            db = sqlite3.connect(wrong)
            bind_profile(db, "firm")
            db.commit()
            db.close()
            with self.assertRaisesRegex(ValueError, "legal_corpus profile"):
                MODULE.audit(wrong)

    def test_missing_registry_is_reported_and_database_is_read_only(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "sample.db"
            db = sqlite3.connect(db_path)

            bind_profile(db)
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

    def test_current_corpus_schema_without_case_id_is_audited(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "profile-corpus.db"
            db = sqlite3.connect(path)
            bind_profile(db)
            db.executescript("""
                CREATE TABLE chunks(id INTEGER PRIMARY KEY, ref TEXT, article TEXT, page TEXT, text TEXT, norm TEXT, document_version_id INTEGER, in_force INTEGER, as_of TEXT, source TEXT, verified INTEGER);
                CREATE TABLE legal_sources(source_id TEXT PRIMARY KEY);
                CREATE TABLE legal_documents(document_id TEXT PRIMARY KEY);
                CREATE TABLE legal_document_versions(version_id INTEGER PRIMARY KEY);
                CREATE TABLE legal_version_relations(relation_id INTEGER PRIMARY KEY);
                CREATE TABLE legal_review_events(review_event_id INTEGER PRIMARY KEY);
                INSERT INTO chunks(ref,article,text,norm,document_version_id,source,verified,in_force)
                    VALUES('law','1','text','text',NULL,'https://example.gov/law',0,0);
            """)
            db.commit()
            db.close()

            report = MODULE.audit(path)
            self.assertEqual(report["report_type"], "legal_corpus_audit")
            self.assertEqual(report["chunk_quality"]["unlinked_to_version"], 1)
            self.assertEqual(report["chunk_quality"]["missing_source"], 0)
            self.assertEqual(report["sqlite_integrity_check"], ["ok"])
            self.assertEqual(report["foreign_key_violation_count"], 0)

    def test_audit_reports_foreign_key_violations_without_modifying_database(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "foreign-keys.db"
            db = sqlite3.connect(path)
            bind_profile(db)
            db.executescript("""
                CREATE TABLE parent(id INTEGER PRIMARY KEY);
                CREATE TABLE child(id INTEGER PRIMARY KEY, parent_id INTEGER REFERENCES parent(id));
                INSERT INTO child(id,parent_id) VALUES(1,999);
            """)
            db.commit()
            db.close()

            report = MODULE.audit(path)
            self.assertEqual(report["sqlite_integrity_check"], ["ok"])
            self.assertEqual(report["foreign_key_violation_count"], 1)
            self.assertIn(
                "sqlite_foreign_key_violations",
                {issue["code"] for issue in report["issues"]},
            )
            db = sqlite3.connect(path)
            self.assertEqual(db.execute("SELECT parent_id FROM child WHERE id=1").fetchone()[0], 999)
            db.close()

    def test_full_registry_quality_counts_are_reported(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "sample.db"
            db = sqlite3.connect(db_path)

            bind_profile(db)
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

            bind_profile(db)
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

    def test_verification_flags_require_matching_passing_review_events(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "verification-events.db"
            db = sqlite3.connect(db_path)

            bind_profile(db)
            db.executescript("""
            CREATE TABLE legal_document_versions(
              version_id INTEGER PRIMARY KEY, source_url TEXT, original_path TEXT, original_sha256 TEXT,
              publication_date TEXT, effective_date TEXT, repeal_date TEXT, legal_status TEXT,
              review_status TEXT, authenticity_verified INT, status_verified INT, amendment_history_verified INT
            );
            CREATE TABLE legal_review_events(
              review_event_id INTEGER PRIMARY KEY, version_id INT, reviewer TEXT, review_type TEXT,
              outcome TEXT, evidence_url TEXT, reviewed_at TEXT, notes TEXT
            );
            INSERT INTO legal_document_versions VALUES
              (1,'https://example.gov/a',NULL,NULL,'2020-01-01','2020-01-01',NULL,'in_force','verified',1,1,0),
              (2,'https://example.gov/b',NULL,NULL,'2021-01-01','2021-01-01',NULL,'in_force','verified',1,1,0);
            INSERT INTO legal_review_events VALUES
              (1,2,'Reviewer','source_authenticity','pass','https://example.gov/evidence/authenticity','2026-10-24T10:00:00Z','Reviewed'),
              (2,2,'Reviewer','legal_status','pass','https://example.gov/evidence/status','2026-10-24T10:00:00Z','Reviewed'),
              (3,2,'Counsel','lawyer_approval','pass','https://example.gov/evidence/lawyer-review','2026-10-24T10:00:00Z','[qualified_egyptian_counsel_attested:user_id=42] reviewed');
            """)
            db.commit()
            db.close()

            report = MODULE.audit(db_path)
            codes = {issue["code"] for issue in report["issues"]}
            self.assertIn("versions_authenticity_flag_without_evidence", codes)
            self.assertIn("versions_status_flag_without_evidence", codes)
            self.assertIn("versions_verified_status_without_lawyer_approval_event", codes)
            self.assertEqual(report["version_quality"]["authenticity_flag_without_evidence"], 1)
            self.assertEqual(report["version_quality"]["status_flag_without_evidence"], 1)
            self.assertEqual(report["version_quality"]["verified_status_without_lawyer_approval_event"], 1)

    def test_review_event_integrity_checks_dates_reviewers_evidence_and_version_links(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "review-event-integrity.db"
            db = sqlite3.connect(db_path)

            bind_profile(db)
            db.executescript("""
            CREATE TABLE legal_document_versions(version_id INTEGER PRIMARY KEY);
            CREATE TABLE legal_review_events(
              review_event_id INTEGER PRIMARY KEY, version_id INT, reviewer TEXT,
              review_type TEXT, outcome TEXT, evidence_url TEXT, reviewed_at TEXT
            );
            INSERT INTO legal_document_versions VALUES(1);
            INSERT INTO legal_review_events VALUES
              (1,1,'Reviewer','source_authenticity','pass','https://example.gov/evidence','2026-01-01T12:00:00Z'),
              (2,1,'   ','unknown','pass','http://unsafe.example/evidence','not-a-date'),
              (3,99,'Reviewer','legal_status','pass',NULL,'2999-01-01T00:00:00Z');
            """)
            db.commit()
            db.close()
            report = MODULE.audit(db_path)
            codes = {issue["code"] for issue in report["issues"]}
            self.assertIn("review_events_reviewer_missing", codes)
            self.assertIn("review_events_invalid_review_type", codes)
            self.assertIn("review_events_reviewed_at_invalid", codes)
            self.assertIn("review_events_reviewed_at_in_future", codes)
            self.assertIn("review_events_passing_event_without_valid_evidence", codes)
            self.assertIn("review_events_orphan_version", codes)
            self.assertEqual(report["review_event_quality"]["reviewer_missing"], 1)
            self.assertEqual(report["review_event_quality"]["orphan_version"], 1)

    def test_verification_flags_require_latest_review_event_not_historical_pass(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "latest-review.db"
            db = sqlite3.connect(path)
            bind_profile(db)
            db.executescript("""
                CREATE TABLE legal_document_versions(
                    version_id INTEGER PRIMARY KEY, source_url TEXT, original_path TEXT, original_sha256 TEXT,
                    publication_date TEXT, effective_date TEXT, repeal_date TEXT, legal_status TEXT,
                    review_status TEXT, authenticity_verified INT, status_verified INT, amendment_history_verified INT
                );
                CREATE TABLE legal_review_events(
                    review_event_id INTEGER PRIMARY KEY, version_id INT, reviewer TEXT, review_type TEXT,
                    outcome TEXT, evidence_url TEXT, reviewed_at TEXT, notes TEXT
                );
                INSERT INTO legal_document_versions VALUES
                    (1,'https://example.gov/law',NULL,NULL,'2020-01-01','2020-01-01',NULL,'in_force','verified',1,1,0);
                INSERT INTO legal_review_events VALUES
                    (1,1,'Counsel','source_authenticity','pass','https://example.gov/old-auth','2026-10-24T10:00:00Z','Reviewed'),
                    (2,1,'Reviewer','source_authenticity','fail','https://example.gov/new-auth','2026-10-25T10:00:00Z','Rejected'),
                    (3,1,'Counsel','legal_status','pass','https://example.gov/old-status','2026-10-24T10:00:00Z','Reviewed'),
                    (4,1,'Reviewer','legal_status','needs_correction','https://example.gov/new-status','2026-10-25T10:00:00Z','Needs correction'),
                    (5,1,'Counsel','lawyer_approval','pass','https://example.gov/old-lawyer','2026-10-24T10:00:00Z','[qualified_egyptian_counsel_attested:user_id=42] reviewed'),
                    (6,1,'Reviewer','lawyer_approval','fail','https://example.gov/new-lawyer','2026-10-25T10:00:00Z','Withdrawn');
            """)
            db.commit()
            db.close()

            report = MODULE.audit(path)
            quality = report["version_quality"]
            self.assertEqual(quality["authenticity_flag_without_evidence"], 1)
            self.assertEqual(quality["status_flag_without_evidence"], 1)
            self.assertEqual(quality["verified_status_without_lawyer_approval_event"], 1)

    def test_latest_attested_counsel_approval_satisfies_verified_flag(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "current-counsel-approval.db"
            db = sqlite3.connect(path)
            bind_profile(db)
            db.executescript("""
                CREATE TABLE legal_document_versions(
                    version_id INTEGER PRIMARY KEY, source_url TEXT, original_path TEXT, original_sha256 TEXT,
                    publication_date TEXT, effective_date TEXT, repeal_date TEXT, legal_status TEXT,
                    review_status TEXT, authenticity_verified INT, status_verified INT, amendment_history_verified INT
                );
                CREATE TABLE legal_review_events(
                    review_event_id INTEGER PRIMARY KEY, version_id INT, reviewer TEXT, review_type TEXT,
                    outcome TEXT, evidence_url TEXT, reviewed_at TEXT, notes TEXT
                );
                INSERT INTO legal_document_versions VALUES
                    (1,'https://example.gov/law',NULL,NULL,'2020-01-01','2020-01-01',NULL,'in_force','verified',0,0,0);
                INSERT INTO legal_review_events VALUES
                    (1,1,'Counsel','lawyer_approval','pass','https://example.gov/review',
                     '2026-10-25T10:00:00Z','[qualified_egyptian_counsel_attested:user_id=42] approved');
            """)
            db.commit()
            db.close()

            report = MODULE.audit(path)
            self.assertEqual(
                report["version_quality"]["verified_status_without_lawyer_approval_event"],
                0,
            )

    def test_audit_flags_passing_lawyer_approval_without_counsel_attestation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "counsel-audit.db"
            db = sqlite3.connect(path)
            bind_profile(db)
            db.executescript("""
                CREATE TABLE legal_document_versions(version_id INTEGER PRIMARY KEY);
                CREATE TABLE legal_review_events(
                    review_event_id INTEGER PRIMARY KEY, version_id INTEGER, reviewer TEXT,
                    review_type TEXT, outcome TEXT, evidence_url TEXT, reviewed_at TEXT, notes TEXT
                );
                INSERT INTO legal_document_versions VALUES(1);
                INSERT INTO legal_review_events VALUES
                    (1,1,'Reviewer','lawyer_approval','pass','https://example.gov/review',
                     '2026-10-24T12:00:00Z','Ordinary platform reviewer');
            """)
            db.commit()
            db.close()
            report = MODULE.audit(path)
            self.assertEqual(
                report["review_event_quality"]["lawyer_approval_without_counsel_attestation"], 1
            )
            self.assertIn(
                "review_events_lawyer_approval_without_counsel_attestation",
                {issue["code"] for issue in report["issues"]},
            )

    def test_chunk_flags_must_match_linked_legal_version(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "chunk-version-consistency.db"
            db = sqlite3.connect(db_path)

            bind_profile(db)
            db.executescript("""
            CREATE TABLE chunks(
              id INTEGER PRIMARY KEY, ref TEXT, article TEXT, text TEXT, source TEXT,
              verified INT, in_force INT, case_id INT, document_version_id INT
            );
            CREATE TABLE legal_document_versions(
              version_id INTEGER PRIMARY KEY, review_status TEXT, authenticity_verified INT,
              status_verified INT, legal_status TEXT, effective_date TEXT, repeal_date TEXT
            );
            INSERT INTO legal_document_versions VALUES
              (1,'pending_source_review',0,0,'unknown','2020-01-01',NULL),
              (2,'verified',1,1,'in_force','9999-01-01',NULL);
            INSERT INTO chunks VALUES
              (1,'law','1','text','https://example.gov/law',1,1,NULL,1),
              (2,'law','2','text','https://example.gov/law',0,1,NULL,2),
              (3,'law','3','text','https://example.gov/law',1,0,NULL,999);
            """)
            db.commit()
            db.close()
            report = MODULE.audit(db_path)
            codes = {issue["code"] for issue in report["issues"]}
            self.assertIn("chunks_verified_without_verified_version", codes)
            self.assertIn("chunks_in_force_conflicting_with_version", codes)
            self.assertEqual(report["chunk_version_consistency"]["verified_chunks_without_verified_version"], 2)
            self.assertEqual(report["chunk_version_consistency"]["in_force_chunks_conflicting_with_version"], 2)

    def test_amendment_history_flags_require_review_evidence_and_relations_are_audited(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "versions.db"
            db = sqlite3.connect(db_path)

            bind_profile(db)
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
              review_event_id INTEGER PRIMARY KEY, version_id INT, reviewer TEXT, review_type TEXT,
              outcome TEXT, evidence_url TEXT, reviewed_at TEXT, notes TEXT
            );
            INSERT INTO legal_document_versions VALUES
              (1,'https://example.gov/a',NULL,NULL,'2020-01-01','2020-01-01',NULL,'in_force','verified',1,1,0),
              (2,'https://example.gov/b',NULL,NULL,'2021-01-01','2021-01-01',NULL,'in_force','verified',1,1,1);
            INSERT INTO legal_version_relations VALUES(1,1,2,'amends');
            INSERT INTO legal_document_versions VALUES
              (3,'https://example.gov/c',NULL,NULL,'2022-01-01','2022-01-01',NULL,'in_force','verified',1,1,1);
            INSERT INTO legal_review_events VALUES
              (1,2,'Reviewer','amendment_history','pass','not-a-url','2026-10-24T10:00:00Z','Reviewed'),
              (2,3,'Reviewer','amendment_history','pass','https://example.gov/evidence/review.pdf','2026-10-24T10:00:00Z','Reviewed');
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

    def test_markdown_renders_new_review_and_chunk_version_metrics(self):
        report = {
            "generated_at": "2026-10-27T00:00:00Z",
            "database_sha256": "a" * 64,
            "counts": {},
            "review_event_quality": {"reviewer_missing": 0, "orphan_version": 2},
            "chunk_version_consistency": {
                "verified_chunks_without_verified_version": 0,
                "in_force_chunks_conflicting_with_version": 3,
            },
            "issues": [],
        }
        markdown = MODULE.render_markdown(report)
        self.assertIn("## Review Event Quality", markdown)
        self.assertIn("reviewer missing", markdown)
        self.assertIn("orphan version", markdown)
        self.assertIn("## Chunk Version Consistency", markdown)
        self.assertIn("in force chunks conflicting with version", markdown)

if __name__ == "__main__":
    unittest.main()
