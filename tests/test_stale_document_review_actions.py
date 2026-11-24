"""Regression tests for compare-and-swap on every document review outcome."""
import pathlib
import sqlite3
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP_SOURCE = (ROOT / "app.py").read_text(encoding="utf-8")


class StaleDocumentReviewTests(unittest.TestCase):
    def test_non_correction_reviews_check_current_text_before_audit_insert(self):
        start = APP_SOURCE.index("def review_document_chunk(")
        end = APP_SOURCE.index("def rm_case(", start)
        endpoint = APP_SOURCE[start:end]
        non_correction = endpoint.index("    else:\n        # Every review outcome")
        insert = endpoint.index('INSERT INTO document_extraction_reviews', non_correction)
        guard = endpoint[non_correction:insert]
        self.assertIn("UPDATE chunks SET page=CASE WHEN ?<>'' THEN ? ELSE page END", guard)
        self.assertIn("AND text=?", guard)
        self.assertIn("if updated.rowcount != 1:", guard)
        self.assertIn("c.rollback()", guard)
        self.assertIn("raise HTTPException(409", guard)

    def test_non_correction_compare_and_swap_rejects_changed_source_text(self):
        db = sqlite3.connect(":memory:")
        db.execute("CREATE TABLE chunks (id INTEGER PRIMARY KEY, document_id INTEGER, case_id INTEGER, text TEXT, page TEXT)")
        db.execute("INSERT INTO chunks VALUES (7, 10, 5, 'newer text', '2')")
        cursor = db.execute(
            "UPDATE chunks SET page=CASE WHEN ?<>'' THEN ? ELSE page END "
            "WHERE id=? AND document_id=? AND case_id=? AND text=?",
            ("", "", 7, 10, 5, "older text"),
        )
        self.assertEqual(cursor.rowcount, 0)
        self.assertEqual(db.execute("SELECT text,page FROM chunks WHERE id=7").fetchone(), ("newer text", "2"))
        db.close()

    def test_non_correction_compare_and_swap_preserves_page_when_unspecified(self):
        db = sqlite3.connect(":memory:")
        db.execute("CREATE TABLE chunks (id INTEGER PRIMARY KEY, document_id INTEGER, case_id INTEGER, text TEXT, page TEXT)")
        db.execute("INSERT INTO chunks VALUES (7, 10, 5, 'current text', '2')")
        cursor = db.execute(
            "UPDATE chunks SET page=CASE WHEN ?<>'' THEN ? ELSE page END "
            "WHERE id=? AND document_id=? AND case_id=? AND text=?",
            ("", "", 7, 10, 5, "current text"),
        )
        self.assertEqual(cursor.rowcount, 1)
        self.assertEqual(db.execute("SELECT text,page FROM chunks WHERE id=7").fetchone(), ("current text", "2"))
        db.close()


if __name__ == "__main__":
    unittest.main()
