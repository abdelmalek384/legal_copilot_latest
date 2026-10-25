"""Tests for the read-only tenant ownership preflight."""
import contextlib
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.tenant_ownership_preflight import audit, main


class TenantOwnershipPreflightTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE firms(id INTEGER PRIMARY KEY, name TEXT);
            CREATE TABLE users(id INTEGER PRIMARY KEY, firm_id INTEGER);
            CREATE TABLE cases(id INTEGER PRIMARY KEY, firm_id INTEGER);
            CREATE TABLE notes(id INTEGER PRIMARY KEY, case_id INTEGER, text TEXT);
            CREATE TABLE deadlines(id INTEGER PRIMARY KEY, case_id INTEGER, title TEXT);
            INSERT INTO notes VALUES (1,999,'orphan note');
            INSERT INTO notes VALUES (2,10,'valid note');
            INSERT INTO notes VALUES (3,NULL,'unlinked note');
            CREATE TABLE members(case_id INTEGER, user_id INTEGER);
            CREATE TABLE docs(id INTEGER PRIMARY KEY, case_id INTEGER, firm_id INTEGER, uploader_user_id INTEGER);
            CREATE TABLE chunks(id INTEGER PRIMARY KEY, case_id INTEGER, document_id INTEGER);
            CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, case_id INTEGER, assignee INTEGER, created_by INTEGER, status TEXT);
            INSERT INTO tasks VALUES (1,10,2,1,'open'),(2,999,1,1,'open'),(3,10,999,1,'open'),(4,10,NULL,999,'open'),(5,10,NULL,2,'open');
            CREATE TABLE research_conversations(id INTEGER PRIMARY KEY, user_id INTEGER, firm_id INTEGER);
            CREATE TABLE case_deletion_audit(id INTEGER PRIMARY KEY, firm_id INTEGER, actor_user_id INTEGER);
            CREATE TABLE document_extraction_reviews(id INTEGER PRIMARY KEY, document_id INTEGER, case_id INTEGER, firm_id INTEGER, chunk_id INTEGER, reviewer_user_id INTEGER);
            INSERT INTO firms VALUES (1,'Firm One'),(2,'Firm Two');
            INSERT INTO users VALUES (1,1),(2,2),(3,NULL);
            INSERT INTO cases VALUES (10,1),(20,2),(30,NULL);
            INSERT INTO members VALUES (10,1),(10,2),(999,1);
            INSERT INTO docs VALUES (100,10,1,1),(200,20,1,2),(300,999,2,2),(400,10,NULL,1),(500,NULL,1,2),(600,10,1,999);
            INSERT INTO chunks VALUES (1000,10,100),(2000,20,100),(3000,999,999),(4000,NULL,NULL);
            INSERT INTO research_conversations VALUES (1,2,1),(2,999,1),(3,NULL,99),(4,NULL,NULL);
            CREATE TABLE research_messages(id INTEGER PRIMARY KEY, conversation_id INTEGER);
            INSERT INTO research_messages VALUES (1,1),(2,999),(3,NULL);
            INSERT INTO case_deletion_audit VALUES (1,NULL,1);
            INSERT INTO document_extraction_reviews VALUES (1,100,10,1,1000,2),(2,999,10,1,9999,1),(3,100,10,2,1000,2),(4,100,999,1,1000,1);
        """)

    def tearDown(self):
        self.db.close()

    def test_detects_ownership_anomalies_and_mixed_chunks(self):
        report = audit(self.db)
        codes = {finding["code"]: finding["count"] for finding in report["findings"]}
        self.assertEqual(report["mode"], "read_only")
        self.assertEqual(codes["users_missing_firm"], 1)
        self.assertEqual(codes["cases_missing_firm"], 1)
        self.assertEqual(codes["cross_firm_membership"], 1)
        self.assertEqual(codes["orphan_membership_case"], 1)
        self.assertEqual(codes["docs_case_firm_mismatch"], 1)
        self.assertEqual(codes["docs_case_unlinked"], 1)
        self.assertEqual(codes["docs_missing_firm"], 1)
        self.assertEqual(codes["chunks_document_case_mismatch"], 1)
        self.assertEqual(codes["chunks_unclassified_shared"], 1)
        self.assertEqual(codes["research_owner_firm_mismatch"], 1)
        self.assertEqual(codes["research_owner_missing_user"], 1)
        self.assertEqual(codes["research_owner_unassigned"], 2)
        self.assertEqual(codes["research_missing_firm"], 1)
        self.assertEqual(codes["research_unknown_firm"], 1)
        self.assertEqual(codes["research_message_conversation_missing"], 1)
        self.assertEqual(codes["research_message_conversation_unassigned"], 1)
        self.assertEqual(codes["orphan_notes_case"], 1)
        self.assertEqual(codes["task_assignee_missing_user"], 1)
        self.assertEqual(codes["task_assignee_firm_mismatch"], 1)
        self.assertEqual(codes["task_creator_missing_user"], 1)
        self.assertEqual(codes["task_creator_firm_mismatch"], 1)
        self.assertEqual(codes["unlinked_notes_case"], 1)
        self.assertEqual(codes["docs_uploader_missing_user"], 1)
        self.assertEqual(codes["docs_uploader_firm_mismatch"], 2)
        self.assertEqual(codes["document_review_document_missing"], 1)
        self.assertEqual(codes["document_review_case_missing"], 1)
        self.assertEqual(codes["document_review_document_firm_mismatch"], 1)
        self.assertEqual(codes["document_review_case_firm_mismatch"], 1)
        self.assertEqual(codes["document_review_reviewer_firm_mismatch"], 1)
        self.assertEqual(codes["document_review_chunk_missing"], 1)
        self.assertEqual(codes["document_review_chunk_scope_mismatch"], 1)
        self.assertEqual(codes["deletion_audit_actor_firm_mismatch"], 1)
        self.assertEqual(codes.get("deletion_audit_actor_missing", 0), 0)
        self.assertEqual(report["status"], "review_required")

    def test_empty_database_is_not_reported_as_clean(self):
        db = sqlite3.connect(":memory:")
        try:
            report = audit(db)
            self.assertEqual(report["status"], "review_required")
            codes = {finding["code"] for finding in report["findings"]}
            self.assertIn("core_schema_table_missing", codes)
            self.assertEqual(report["finding_count"], 3)
        finally:
            db.close()

    def test_missing_firm_column_is_reported_as_incomplete_schema(self):
        db = sqlite3.connect(":memory:")
        try:
            db.executescript("""
                CREATE TABLE firms(id INTEGER PRIMARY KEY);
                CREATE TABLE users(id INTEGER PRIMARY KEY);
                CREATE TABLE cases(id INTEGER PRIMARY KEY, firm_id INTEGER);
            """)
            report = audit(db)
            self.assertEqual(report["status"], "review_required")
            self.assertIn(
                "core_schema_columns_missing",
                {finding["code"] for finding in report["findings"]},
            )
        finally:
            db.close()

    def test_cli_refuses_symlinked_database_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "actual.db"
            with sqlite3.connect(target) as db:
                db.executescript("CREATE TABLE firms(id INTEGER PRIMARY KEY); CREATE TABLE users(id INTEGER PRIMARY KEY, firm_id INTEGER); CREATE TABLE cases(id INTEGER PRIMARY KEY, firm_id INTEGER);")
            link = root / "linked.db"
            try:
                link.symlink_to(target)
            except (NotImplementedError, OSError) as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = main([str(link)])
            self.assertEqual(result, 2)
            self.assertIn("database path must not be a symlink", stderr.getvalue())

    def test_clean_minimal_database_has_no_findings(self):
        db = sqlite3.connect(":memory:")
        try:
            db.executescript("""
                CREATE TABLE firms(id INTEGER PRIMARY KEY);
                CREATE TABLE users(id INTEGER PRIMARY KEY, firm_id INTEGER);
                CREATE TABLE cases(id INTEGER PRIMARY KEY, firm_id INTEGER);
                INSERT INTO firms VALUES (1);
                INSERT INTO users VALUES (1,1);
                INSERT INTO cases VALUES (1,1);
            """)
            report = audit(db)
            self.assertEqual(report["finding_count"], 0)
            self.assertEqual(report["status"], "no_detected_anomalies")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
