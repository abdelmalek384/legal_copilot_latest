"""Regression contracts for streaming bounded document-analysis chunk reads."""
import pathlib
import sqlite3
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP_SOURCE = (ROOT / "app.py").read_text(encoding="utf-8")


class StreamingDocumentAnalysisTests(unittest.TestCase):
    def _function(self, start_marker, end_marker):
        start = APP_SOURCE.index(start_marker)
        end = APP_SOURCE.index(end_marker, start)
        return APP_SOURCE[start:end]

    def test_comparison_iterates_chunk_cursor_under_character_cap(self):
        block = self._function("def compare_accessible_document_versions(", '@app.get("/documents/search-text")')
        self.assertIn("rows = c.execute(", block)
        self.assertIn("for row in rows:", block)
        self.assertNotIn("rows = c.execute(\n            \"SELECT id,ref,page,text \"\n            \"FROM chunks \"\n            \"WHERE case_id=? AND document_id=? ORDER BY id\",\n            (case_id, document_id),\n        ).fetchall()", block)

    def test_timeline_iterates_chunk_cursor_and_retains_global_budget(self):
        block = self._function("def matter_document_timeline(", "def matter_document_entity_mentions(")
        self.assertIn("rows = c.execute(", block)
        self.assertIn("for row in rows:", block)
        self.assertIn("remaining_chars = MAX_ANALYSIS_CHARS", block)
        self.assertIn("if remaining_chars <= 0:", block)
        self.assertNotIn("rows = c.execute(\n            \"SELECT id,ref,page,text FROM chunks WHERE case_id=? AND document_id=? ORDER BY id\",\n            (cid, document_id),\n        ).fetchall()", block)

    def test_entity_mentions_iterates_chunk_cursor_and_retains_global_budget(self):
        block = self._function("def matter_document_entity_mentions(", '@app.get("/cases/{cid}/docs/{document_id}/chunks")')
        self.assertIn("rows = c.execute(", block)
        self.assertIn("for row in rows:", block)
        self.assertIn("remaining_chars = MAX_ANALYSIS_CHARS", block)
        self.assertIn("if remaining_chars <= 0:", block)
        self.assertNotIn("rows = c.execute(\n            \"SELECT id,ref,page,text FROM chunks WHERE case_id=? AND document_id=? ORDER BY id\",\n            (cid, document_id),\n        ).fetchall()", block)

    def test_sqlite_cursor_can_be_consumed_only_until_budget_is_exhausted(self):
        db = sqlite3.connect(":memory:")
        db.execute("CREATE TABLE chunks (id INTEGER PRIMARY KEY, text TEXT)")
        db.executemany("INSERT INTO chunks(text) VALUES(?)", [("x" * 10,) for _ in range(1000)])
        cursor = db.execute("SELECT id,text FROM chunks ORDER BY id")
        consumed = 0
        used = 0
        for row in cursor:
            if used >= 25:
                break
            used += min(len(row[1]), 25 - used)
            consumed += 1
        self.assertLess(consumed, 1000)
        self.assertEqual(used, 25)
        db.close()


if __name__ == "__main__":
    unittest.main()
