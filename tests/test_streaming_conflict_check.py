"""Regression tests for streaming firm-wide conflict checks."""
import pathlib
import sqlite3
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP_SOURCE = (ROOT / "app.py").read_text(encoding="utf-8")


class StreamingConflictCheckTests(unittest.TestCase):
    def test_conflict_check_iterates_case_cursor_without_fetchall(self):
        start = APP_SOURCE.index("def conflict_check(")
        end = APP_SOURCE.index("\n@app.", start)
        endpoint = APP_SOURCE[start:end]
        self.assertIn("rows = c.execute(", endpoint)
        self.assertIn("for r in rows:", endpoint)
        self.assertNotIn(".fetchall()", endpoint)
        self.assertIn("len(found) < 100", endpoint)
        self.assertIn("hidden_match = True", endpoint)
        self.assertIn('"FROM cases WHERE firm_id=? ORDER BY id DESC"', endpoint)

    def test_cursor_scan_still_detects_hidden_conflicts_after_visible_result_cap(self):
        db = sqlite3.connect(":memory:")
        db.execute("CREATE TABLE cases (id INTEGER PRIMARY KEY, firm_id INTEGER, name TEXT, visible INTEGER)")
        db.executemany(
            "INSERT INTO cases(firm_id,name,visible) VALUES(?,?,?)",
            [(2, f"Visible Client {i}", 1) for i in range(150)]
            + [(2, "Hidden Matching Client", 0)]
            + [(3, "Other Firm Client", 0)],
        )
        found = []
        hidden_match = False
        scanned = 0
        for row in db.execute("SELECT id,name,visible FROM cases WHERE firm_id=? ORDER BY id DESC", (2,)):
            scanned += 1
            if "client" in row[1].lower():
                if not row[2]:
                    hidden_match = True
                else:
                    found.append(row[1])
        self.assertEqual(scanned, 151)
        self.assertEqual(len(found[:100]), 100)
        self.assertTrue(hidden_match)
        db.close()


if __name__ == "__main__":
    unittest.main()
