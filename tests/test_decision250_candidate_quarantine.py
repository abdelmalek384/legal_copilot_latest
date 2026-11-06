import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "candidates" / "labour_law_14_2025" / "decision_250_2026_source_candidate.json"


class Decision250CandidateQuarantineTests(unittest.TestCase):
    def test_official_catalogue_and_secondary_commencement_are_not_conflated(self):
        data = json.loads(RECORD.read_text(encoding="utf-8"))
        instrument = data["instrument"]
        self.assertEqual(instrument["gazette"]["publication_date"], "2026-10-12")
        self.assertTrue(instrument["gazette"]["official_catalogue_url"].startswith("https://dspace.id.com.eg/"))
        self.assertFalse(instrument["gazette"]["original_pdf_obtained"])
        self.assertIsNone(instrument["gazette"]["original_pdf_sha256"])
        self.assertEqual(instrument["candidate_commencement"]["date"], "2026-10-13")
        self.assertEqual(instrument["candidate_commencement"]["status"], "candidate_secondary_inference")
        self.assertFalse(instrument["candidate_commencement"]["verified"])
        self.assertFalse(data["effective_date_verified"])
        self.assertFalse(data["search_eligible"])
        self.assertFalse(data["import_eligible"])
        self.assertEqual(data["source_permission"], "unknown")
        self.assertEqual(data["commercial_reuse_permission"], "unknown")
        self.assertEqual(data["egyptian_lawyer_review"], "pending")


if __name__ == "__main__":
    unittest.main()
