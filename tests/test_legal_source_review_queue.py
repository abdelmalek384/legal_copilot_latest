import importlib.util
import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("legal_source_review_queue",ROOT/"tools"/"legal_source_review_queue.py")
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

def make_db(path):
    db=sqlite3.connect(path)
    db.executescript("""
    CREATE TABLE database_profile(singleton INTEGER PRIMARY KEY CHECK(singleton=1), profile TEXT NOT NULL, bound_at TEXT NOT NULL DEFAULT (datetime('now')));
    INSERT INTO database_profile(singleton,profile) VALUES(1,'legal_corpus');
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

    def test_passing_lawyer_approval_requires_counsel_attestation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "legal.db"
            make_db(path)
            db = sqlite3.connect(path)
            db.execute("ALTER TABLE legal_review_events ADD COLUMN notes TEXT")
            db.execute(
                "INSERT INTO legal_review_events(version_id,review_type,outcome,evidence_url,reviewer,reviewed_at,notes) "
                "VALUES(1,'lawyer_approval','pass','https://example.gov/review','Reviewer','2026-10-24T12:00:00Z','Ordinary reviewer')"
            )
            db.commit()
            db.close()
            report = MODULE.review_queue(path)
            reasons = report["records"][0]["review_reasons"]
            self.assertIn("lawyer_approval_counsel_attestation_missing", reasons)
            db = sqlite3.connect(path)
            db.execute(
                "UPDATE legal_review_events SET notes=? WHERE review_type='lawyer_approval'",
                ("[qualified_egyptian_counsel_attested:user_id=42] reviewed",),
            )
            db.commit()
            db.close()
            report = MODULE.review_queue(path)
            self.assertNotIn(
                "lawyer_approval_counsel_attestation_missing",
                report["records"][0]["review_reasons"],
            )

    def test_newer_failed_lawyer_review_supersedes_older_counsel_approval(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "legal.db"
            make_db(path)
            db = sqlite3.connect(path)
            db.execute("ALTER TABLE legal_review_events ADD COLUMN notes TEXT")
            db.execute(
                "INSERT INTO legal_review_events(version_id,review_type,outcome,evidence_url,reviewer,reviewed_at,notes) "
                "VALUES(1,'lawyer_approval','pass','https://example.gov/old','Counsel','2026-10-24T12:00:00Z',"
                "'[qualified_egyptian_counsel_attested:user_id=42] approved')"
            )
            db.execute(
                "INSERT INTO legal_review_events(version_id,review_type,outcome,evidence_url,reviewer,reviewed_at,notes) "
                "VALUES(1,'lawyer_approval','fail','https://example.gov/new','Reviewer','2026-10-25T12:00:00Z','Approval withdrawn')"
            )
            db.commit()
            db.close()

            report = MODULE.review_queue(path)
            reasons = report["records"][0]["review_reasons"]
            self.assertIn("review_evidence_missing:lawyer_approval", reasons)
            self.assertNotIn("lawyer_approval_counsel_attestation_missing", reasons)

    def test_newer_unattested_pass_supersedes_older_counsel_approval(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "legal.db"
            make_db(path)
            db = sqlite3.connect(path)
            db.execute("ALTER TABLE legal_review_events ADD COLUMN notes TEXT")
            db.execute(
                "INSERT INTO legal_review_events(version_id,review_type,outcome,evidence_url,reviewer,reviewed_at,notes) "
                "VALUES(1,'lawyer_approval','pass','https://example.gov/old','Counsel','2026-10-24T12:00:00Z',"
                "'[qualified_egyptian_counsel_attested:user_id=42] approved')"
            )
            db.execute(
                "INSERT INTO legal_review_events(version_id,review_type,outcome,evidence_url,reviewer,reviewed_at,notes) "
                "VALUES(1,'lawyer_approval','pass','https://example.gov/new','Reviewer','2026-10-25T12:00:00Z','Ordinary reviewer')"
            )
            db.commit()
            db.close()

            report = MODULE.review_queue(path)
            reasons = report["records"][0]["review_reasons"]
            self.assertIn("lawyer_approval_counsel_attestation_missing", reasons)

    def test_latest_attested_counsel_pass_remains_eligible(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "legal.db"
            make_db(path)
            db = sqlite3.connect(path)
            db.execute("ALTER TABLE legal_review_events ADD COLUMN notes TEXT")
            db.execute(
                "INSERT INTO legal_review_events(version_id,review_type,outcome,evidence_url,reviewer,reviewed_at,notes) "
                "VALUES(1,'lawyer_approval','pass','https://example.gov/old','Reviewer','2026-10-24T12:00:00Z','Old approval')"
            )
            db.execute(
                "INSERT INTO legal_review_events(version_id,review_type,outcome,evidence_url,reviewer,reviewed_at,notes) "
                "VALUES(1,'lawyer_approval','pass','https://example.gov/new','Counsel','2026-10-25T12:00:00Z',"
                "'[qualified_egyptian_counsel_attested:user_id=42] approved')"
            )
            db.commit()
            db.close()

            report = MODULE.review_queue(path)
            reasons = report["records"][0]["review_reasons"]
            self.assertNotIn("review_evidence_missing:lawyer_approval", reasons)
            self.assertNotIn("lawyer_approval_counsel_attestation_missing", reasons)

    def test_latest_pass_requires_reviewer_and_notes_like_runtime_gate(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "legal.db"
            make_db(path)
            db = sqlite3.connect(path)
            db.execute("ALTER TABLE legal_review_events ADD COLUMN notes TEXT")
            db.execute(
                "INSERT INTO legal_review_events(version_id,review_type,outcome,evidence_url,reviewer,reviewed_at,notes) "
                "VALUES(1,'source_authenticity','pass','https://example.gov/review','',"
                "'2026-10-25T12:00:00Z','')"
            )
            db.commit()
            db.close()

            report = MODULE.review_queue(path)
            self.assertIn(
                "review_evidence_missing:source_authenticity",
                report["records"][0]["review_reasons"],
            )

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

    def test_review_events_require_valid_https_evidence_urls(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"legal.db"
            make_db(path)
            db = sqlite3.connect(path)
            db.execute("ALTER TABLE legal_review_events ADD COLUMN notes TEXT")
            review_types = (
                "source_authenticity", "extraction_quality", "legal_status",
                "amendment_history", "licensing", "lawyer_approval",
            )
            for index, review_type in enumerate(review_types, start=1):
                url = "not-a-url" if review_type == "source_authenticity" else f"https://example.gov/evidence/{index}"
                notes = "review recorded"
                if review_type == "lawyer_approval":
                    notes = "[qualified_egyptian_counsel_attested:user_id=42] review recorded"
                db.execute(
                    "INSERT INTO legal_review_events(version_id,review_type,outcome,evidence_url,reviewer,reviewed_at,notes) "
                    "VALUES(?,?,?,?,?,?,?)",
                    (1, review_type, "pass", url, "Reviewer", "2026-10-25T10:00:00Z", notes),
                )
            db.commit()
            db.close()

            report = MODULE.review_queue(path)
            reasons = report["records"][0]["review_reasons"]
            self.assertIn("review_evidence_missing:source_authenticity", reasons)
            self.assertNotIn("review_evidence_missing:legal_status", reasons)

    def test_evidence_url_validator_rejects_credentials_and_non_https(self):
        for value in (
            "http://example.gov/evidence",
            "https://user:secret@example.gov/evidence",
            "https://@example.gov/evidence",
            " https://example.gov/evidence",
            "https://example.gov/path with spaces",
            "https://example.gov:not-a-port/evidence",
            "https://example.gov:99999/evidence",
            "https://example.gov:0/evidence",
            "https://example.gov:/evidence",
            "",
            None,
            "not a url",
        ):
            with self.subTest(value=value):
                self.assertFalse(MODULE.valid_evidence_url(value))
        self.assertTrue(MODULE.valid_evidence_url("https://example.gov/evidence"))

    def test_rejects_unbound_or_wrong_profile_database(self):
        with tempfile.TemporaryDirectory() as td:
            wrong=Path(td)/"wrong.db"
            make_db(wrong)
            db=sqlite3.connect(wrong)
            db.execute("UPDATE database_profile SET profile='firm' WHERE singleton=1")
            db.commit()
            db.close()
            with self.assertRaisesRegex(ValueError,"legal_corpus profile"):
                MODULE.review_queue(wrong)

            unbound=Path(td)/"unbound.db"
            make_db(unbound)
            db=sqlite3.connect(unbound)
            db.execute("DROP TABLE database_profile")
            db.commit()
            db.close()
            with self.assertRaisesRegex(ValueError,"legal_corpus profile"):
                MODULE.review_queue(unbound)

    def test_future_dated_latest_review_event_is_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "legal.db"
            make_db(path)
            db = sqlite3.connect(path)
            db.execute("ALTER TABLE legal_review_events ADD COLUMN notes TEXT")
            review_types = (
                "source_authenticity", "extraction_quality", "legal_status",
                "amendment_history", "licensing", "lawyer_approval",
            )
            for index, review_type in enumerate(review_types, start=1):
                notes = "review recorded"
                if review_type == "lawyer_approval":
                    notes = "[qualified_egyptian_counsel_attested:user_id=42] review recorded"
                reviewed_at = (
                    "2099-01-01T00:00:00Z"
                    if review_type == "source_authenticity"
                    else "2026-10-25T10:00:00Z"
                )
                db.execute(
                    "INSERT INTO legal_review_events(version_id,review_type,outcome,evidence_url,reviewer,reviewed_at,notes) "
                    "VALUES(?,?,?,?,?,?,?)",
                    (1, review_type, "pass", f"https://example.gov/evidence/{index}",
                     "Reviewer", reviewed_at, notes),
                )
            db.commit()
            db.close()

            report = MODULE.review_queue(path)
            reasons = report["records"][0]["review_reasons"]
            self.assertIn("review_event_history_invalid_or_future", reasons)

    def test_cli_refuses_implicit_and_compatibility_database_paths(self):
        with patch.dict(os.environ, {}, clear=True), patch(
            "sys.argv", ["legal_source_review_queue.py"]
        ):
            with self.assertRaises(SystemExit) as missing:
                MODULE.main()
            self.assertEqual(missing.exception.code, 2)
        with patch.dict(os.environ, {"COPILOT_DB": "/tmp/compat.sqlite3"}, clear=True), patch(
            "sys.argv", ["legal_source_review_queue.py", "--db", "/tmp/corpus.sqlite3"]
        ):
            with self.assertRaises(SystemExit) as legacy:
                MODULE.main()
            self.assertEqual(legacy.exception.code, 2)

    def test_missing_registry_tables_report_schema_issue(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"empty.db"
            sqlite3.connect(path).close()
            report=MODULE.review_queue(path)
            self.assertEqual(report["issues"][0]["code"],"review_schema_tables_missing")
            self.assertEqual(report["records"],[])

if __name__=="__main__":
    unittest.main()
