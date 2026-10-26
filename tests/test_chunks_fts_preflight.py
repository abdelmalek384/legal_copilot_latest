"""Tests for read-only chunks / FTS5 consistency auditing."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.chunks_fts_preflight import audit, audit_path


class ChunksFtsPreflightTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript("""
            CREATE TABLE chunks(id INTEGER PRIMARY KEY, text TEXT, norm TEXT);
            CREATE VIRTUAL TABLE chunks_fts USING fts5(norm);
        """)

    def tearDown(self):
        self.db.close()

    def test_clean_index_has_no_findings(self):
        self.db.execute("INSERT INTO chunks(id,text,norm) VALUES(1,'hello world','hello world')")
        self.db.execute("INSERT INTO chunks_fts(rowid,norm) VALUES(1,'hello world')")
        report = audit(self.db)
        self.assertEqual(report["status"], "no_detected_anomalies")
        self.assertEqual(report["chunks_row_count"], 1)
        self.assertEqual(report["fts_row_count"], 1)
        self.assertEqual(report["finding_count"], 0)

    def test_detects_missing_fts_rows(self):
        self.db.executemany(
            "INSERT INTO chunks(id,text,norm) VALUES(?,?,?)",
            [(1, "hello", "hello"), (2, "world", "world")],
        )
        self.db.execute("INSERT INTO chunks_fts(rowid,norm) VALUES(1,'hello')")
        report = audit(self.db)
        codes = {item["code"]: item["count"] for item in report["findings"]}
        self.assertEqual(report["status"], "review_required")
        self.assertEqual(codes["fts_rows_missing"], 1)

    def test_detects_content_mismatch_and_orphaned_fts_row(self):
        self.db.execute("INSERT INTO chunks(id,text,norm) VALUES(1,'hello world','hello world')")
        self.db.execute("INSERT INTO chunks_fts(rowid,norm) VALUES(1,'stale content')")
        self.db.execute("INSERT INTO chunks_fts(rowid,norm) VALUES(2,'orphan content')")
        report = audit(self.db)
        codes = {item["code"]: item["count"] for item in report["findings"]}
        self.assertEqual(codes["fts_content_mismatch"], 1)
        self.assertEqual(codes["fts_rows_orphaned"], 1)

    def test_healthy_external_content_index_uses_canonical_norm_not_legacy_tokenization(self):
        db = sqlite3.connect(":memory:")
        try:
            db.executescript("""
                CREATE TABLE chunks(id INTEGER PRIMARY KEY, text TEXT, norm TEXT);
                CREATE VIRTUAL TABLE chunks_fts USING fts5(norm, content='chunks', content_rowid='id');
                INSERT INTO chunks(id,text,norm) VALUES(1,'Arabic text source','canonical_norm');
                INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild');
            """)
            report = audit(db)
            codes = {item["code"] for item in report["findings"]}
            self.assertEqual(report["status"], "no_detected_anomalies")
            self.assertNotIn("fts_content_mismatch", codes)
            self.assertNotIn("fts_internal_index_integrity_failed", codes)
        finally:
            db.close()

    def test_detects_corrupt_external_content_fts_index_without_mutating_source(self):
        db = sqlite3.connect(":memory:")
        try:
            db.executescript("""
                CREATE TABLE chunks(id INTEGER PRIMARY KEY, text TEXT, norm TEXT);
                CREATE VIRTUAL TABLE chunks_fts USING fts5(norm, content='chunks', content_rowid='id');
                INSERT INTO chunks(id,text,norm) VALUES(1,'hello world','hello world');
                INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild');
                INSERT INTO chunks_fts(chunks_fts) VALUES('delete-all');
            """)
            before = db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
            report = audit(db)
            codes = {item["code"] for item in report["findings"]}
            self.assertIn("fts_internal_index_integrity_failed", codes)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0], before)
            # The source remains broken and untouched; the audit is diagnostic only.
            self.assertEqual(db.execute("SELECT COUNT(*) FROM chunks_fts").fetchone()[0], before)
        finally:
            db.close()

    def test_missing_fts_table_is_reported(self):
        db = sqlite3.connect(":memory:")
        try:
            db.execute("CREATE TABLE chunks(id INTEGER PRIMARY KEY, text TEXT)")
            report = audit(db)
            self.assertEqual(report["findings"][0]["code"], "fts_table_missing")
        finally:
            db.close()

    def test_path_audit_is_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.sqlite3"
            with sqlite3.connect(path) as db:
                db.executescript("""
                    CREATE TABLE chunks(id INTEGER PRIMARY KEY, text TEXT);
                    CREATE VIRTUAL TABLE chunks_fts USING fts5(norm);
                    INSERT INTO chunks(id,text) VALUES(1,'hello');
                    INSERT INTO chunks_fts(rowid,norm) VALUES(1,'hello');
                """)
            before = path.stat().st_size
            report = audit_path(path)
            self.assertEqual(report["status"], "no_detected_anomalies")
            self.assertEqual(path.stat().st_size, before)
            with sqlite3.connect(path) as db:
                names = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                self.assertNotIn("schema_migrations", names)


if __name__ == "__main__":
    unittest.main()
