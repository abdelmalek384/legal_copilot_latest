"""Tests for the read-only tenant ownership preflight."""
import sqlite3
import unittest

from scripts.tenant_ownership_preflight import audit


class TenantOwnershipPreflightTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE firms(id INTEGER PRIMARY KEY, name TEXT);
            CREATE TABLE users(id INTEGER PRIMARY KEY, firm_id INTEGER);
            CREATE TABLE cases(id INTEGER PRIMARY KEY, firm_id INTEGER);
            CREATE TABLE members(case_id INTEGER, user_id INTEGER);
            CREATE TABLE docs(id INTEGER PRIMARY KEY, case_id INTEGER, firm_id INTEGER);
            CREATE TABLE chunks(id INTEGER PRIMARY KEY, case_id INTEGER, document_id INTEGER);
            CREATE TABLE research_conversations(id INTEGER PRIMARY KEY, user_id INTEGER, firm_id INTEGER);
            CREATE TABLE case_deletion_audit(id INTEGER PRIMARY KEY, firm_id INTEGER);
            INSERT INTO firms VALUES (1,'Firm One'),(2,'Firm Two');
            INSERT INTO users VALUES (1,1),(2,2),(3,NULL);
            INSERT INTO cases VALUES (10,1),(20,2),(30,NULL);
            INSERT INTO members VALUES (10,1),(10,2),(999,1);
            INSERT INTO docs VALUES (100,10,1),(200,20,1),(300,999,2),(400,10,NULL);
            INSERT INTO chunks VALUES (1000,10,100),(2000,20,100),(3000,999,999),(4000,NULL,NULL);
            INSERT INTO research_conversations VALUES (1,2,1);
            INSERT INTO case_deletion_audit VALUES (1,NULL);
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
        self.assertEqual(codes["docs_missing_firm"], 1)
        self.assertEqual(codes["chunks_document_case_mismatch"], 1)
        self.assertEqual(codes["chunks_unclassified_shared"], 1)
        self.assertEqual(codes["research_owner_firm_mismatch"], 1)
        self.assertEqual(report["status"], "review_required")

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
