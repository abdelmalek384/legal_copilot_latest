"""Regression contracts for bounded document-review history retrieval."""
import pathlib
import sqlite3
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP_SOURCE = (ROOT / "app.py").read_text(encoding="utf-8")


class DocumentReviewHistoryQueryTests(unittest.TestCase):
    def test_chunk_endpoint_fetches_only_latest_review_per_chunk(self):
        start = APP_SOURCE.index("def list_document_chunks(")
        end = APP_SOURCE.index("@app.post(\"/cases/{cid}/docs/{document_id}/chunks/{chunk_id}/review\")", start)
        endpoint = APP_SOURCE[start:end]
        self.assertIn("MAX(id) AS latest_id", endpoint)
        self.assertIn("GROUP BY chunk_id", endpoint)
        self.assertIn("latest.latest_id=r.id", endpoint)
        self.assertIn("WHERE document_id=? AND case_id=? AND firm_id=?", endpoint)
        self.assertIn("latest = {int(review[\"chunk_id\"]): dict(review) for review in review_rows}", endpoint)
        self.assertNotIn("for review in review_rows:", endpoint)

    def test_latest_review_query_returns_one_row_per_chunk(self):
        db = sqlite3.connect(":memory:")
        db.row_factory = sqlite3.Row
        db.execute(
            "CREATE TABLE document_extraction_reviews (id INTEGER PRIMARY KEY, document_id INTEGER, "
            "case_id INTEGER, firm_id INTEGER, chunk_id INTEGER, outcome TEXT, reviewer_user_id INTEGER, "
            "original_text TEXT, reviewed_text TEXT, page_reference TEXT, note TEXT, created_at TEXT)"
        )
        db.executemany(
            "INSERT INTO document_extraction_reviews "
            "(id,document_id,case_id,firm_id,chunk_id,outcome,created_at) VALUES(?,?,?,?,?,?,?)",
            [
                (1, 10, 5, 2, 100, "accepted", "2026-01-01"),
                (2, 10, 5, 2, 100, "corrected", "2026-01-02"),
                (3, 10, 5, 2, 101, "needs_recheck", "2026-01-03"),
                (4, 11, 5, 2, 100, "accepted", "2026-01-04"),
                (5, 10, 5, 3, 100, "accepted", "2026-01-05"),
            ],
        )
        query = (
            "SELECT r.chunk_id,r.outcome,r.reviewer_user_id,r.original_text,r.reviewed_text,"
            "r.page_reference,r.note,r.created_at "
            "FROM document_extraction_reviews r "
            "JOIN (SELECT chunk_id,MAX(id) AS latest_id FROM document_extraction_reviews "
            "WHERE document_id=? AND case_id=? AND firm_id=? GROUP BY chunk_id) latest "
            "ON latest.latest_id=r.id "
            "WHERE r.document_id=? AND r.case_id=? AND r.firm_id=? ORDER BY r.id DESC"
        )
        rows = db.execute(query, (10, 5, 2, 10, 5, 2)).fetchall()
        self.assertEqual([(row["chunk_id"], row["outcome"]) for row in rows],
                         [(101, "needs_recheck"), (100, "corrected")])
        db.close()


if __name__ == "__main__":
    unittest.main()
