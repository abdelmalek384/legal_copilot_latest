import importlib
import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class LabourLawCandidateRegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["COPILOT_DB"] = str(Path(self.tmp.name) / "candidate.db")
        import app
        self.app = importlib.reload(app)
        from tools.register_labour_law_candidate import register, DEFAULT_RECORD
        self.register = register
        self.record = json.loads(DEFAULT_RECORD.read_text(encoding="utf-8"))
        self.db = self.app.conn()

    def tearDown(self):
        self.db.close()
        self.app._t.c = None
        self.app._schema_ready = False
        os.environ.pop("COPILOT_DB", None)
        self.tmp.cleanup()

    def test_registers_pending_metadata_without_chunks(self):
        result = self.register(self.db, self.record)
        self.assertEqual(result["version_state"]["legal_status"], "under_review")
        self.assertEqual(result["version_state"]["review_status"], "pending_source_review")
        self.assertEqual(result["version_state"]["authenticity_verified"], 0)
        self.assertEqual(result["version_state"]["status_verified"], 0)
        self.assertEqual(result["version_state"]["amendment_history_verified"], 0)
        self.assertEqual(result["linked_chunk_count"], 0)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0], 0)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM legal_review_events").fetchone()[0], 6)

    def test_registration_is_idempotent_and_preserves_review_decisions(self):
        first = self.register(self.db, self.record)
        self.register(self.db, self.record)
        self.db.execute(
            "UPDATE legal_document_versions SET review_status='pending_lawyer_review' WHERE version_id=?",
            (first["version_id"],),
        )
        self.db.commit()
        self.register(self.db, self.record)
        row = self.db.execute(
            "SELECT review_status FROM legal_document_versions WHERE version_id=?",
            (first["version_id"],),
        ).fetchone()
        self.assertEqual(row[0], "pending_lawyer_review")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM legal_document_versions").fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
