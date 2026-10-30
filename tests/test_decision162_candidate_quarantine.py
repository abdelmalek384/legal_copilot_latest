import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "data" / "candidates" / "labour_law_14_2025" / "decision_162_2026_candidate.json"


class Decision162CandidateQuarantineTests(unittest.TestCase):
    def test_candidate_is_not_promoted_to_authoritative_retrieval(self):
        record = json.loads(CANDIDATE.read_text(encoding="utf-8"))
        policy = record["policy"]
        instrument = record["instrument"]

        self.assertFalse(policy["search_eligible"])
        self.assertTrue(policy["do_not_assume_amendment"])
        self.assertTrue(policy["do_not_import_text_or_chunks"])
        self.assertFalse(instrument["formal_amendment_confirmed"])
        self.assertEqual(instrument["legal_review"], "pending")
        self.assertEqual(instrument["permission"], "unknown")

    def test_effective_date_remains_an_unverified_secondary_inference(self):
        instrument = json.loads(CANDIDATE.read_text(encoding="utf-8"))["instrument"]

        self.assertEqual(instrument["effective_date"], "2026-08-14")
        self.assertEqual(instrument["effective_date_status"], "candidate_secondary_inference")
        self.assertIs(instrument["effective_date_verified"], False)
        self.assertIn("secondary transcription only", instrument["effective_date_basis"])
        self.assertEqual(instrument["original_gazette_file_access"], "restricted_request_copy")
        self.assertIs(instrument["original_gazette_pdf_obtained"], False)
        self.assertIsNone(instrument["original_gazette_pdf_sha256"])


if __name__ == "__main__":
    unittest.main()
