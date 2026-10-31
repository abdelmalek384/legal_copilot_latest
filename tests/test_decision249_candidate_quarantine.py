import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "candidates" / "labour_law_14_2025"


class Decision249CandidateQuarantineTests(unittest.TestCase):
    def test_article_table_map_retains_secondary_only_provenance(self):
        path = DATA / "decision_249_secondary_article_table_map_2026-10-30.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(record["source"]["class"], "secondary_scan_image_reproduction")
        self.assertEqual(record["source"]["gazette_issue"], "225 تابع (أ)")
        self.assertEqual(record["source"]["gazette_publication_date"], "2026-10-12")
        self.assertEqual(record["source"]["printed_page_range"], "19-44")
        self.assertFalse(record["source"]["original_gazette_pdf_obtained"])
        self.assertIsNone(record["source"]["official_pdf_sha256"])
        self.assertEqual(record["source"]["visual_reviewed_on"], "2026-10-31")
        self.assertEqual(
            [item["printed_page"] for item in record["source"]["visual_reviewed_images"]],
            [19, 33, 43, 44],
        )
        kinds = {}
        for item in record["records"]:
            kinds[item["record_type"]] = kinds.get(item["record_type"], 0) + 1
            self.assertEqual(item["source_class"], "secondary_scan_image_reproduction")
            self.assertEqual(item["official_gazette_match"], "not_performed")
            self.assertIsNone(item["official_pdf_sha256"])
            self.assertFalse(item["retrieval_eligible"])
            self.assertEqual(item["status"], "candidate_only_pending_official_match")
        self.assertEqual(kinds, {"article": 22, "table": 3, "appendix": 1})
        self.assertEqual(record["effective_date_candidate"], "2026-10-13")
        self.assertEqual(record["effective_date_candidate_status"], "secondary_scan_inference_not_verified")
        self.assertIs(record["effective_date_verified"], False)
        self.assertIn(
            32,
            [item["printed_page"] for item in record["source"]["visual_reviewed_images"]],
        )

    def test_table3_candidate_is_not_a_compliance_rule(self):
        path = DATA / "decision_249_table3_continuous_monitoring_candidate_2026-10-29.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(record["printed_page"], 44)
        self.assertEqual(record["source_quality"], "secondary_hosted_reproduction_of_gazette_page_image")
        self.assertFalse(record["official_pdf_downloaded_and_hashed"])
        self.assertEqual(record["official_file_comparison"], "pending")
        self.assertEqual(record["counsel_review"], "not_reviewed")
        self.assertFalse(record["authoritative_retrieval_eligible"])
        self.assertEqual(len(record["rows"]), 12)
        self.assertTrue(all(row["status"] == "scan_transcription_pending_official_match" for row in record["rows"]))


if __name__ == "__main__":
    unittest.main()
