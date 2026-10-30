"""Structural regression checks for Decision 250/2026 Table 24 candidates.

These checks prove only inventory consistency, never legal accuracy or provenance.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_DIR = ROOT / "data" / "candidates" / "labour_law_14_2025"


class Decision250Table24InventoryTests(unittest.TestCase):
    def test_technical_index_has_one_table_24_and_no_table_25(self):
        index = json.loads(
            (CANDIDATE_DIR / "decision_250_technical_table_index_2026-10-29.json").read_text(encoding="utf-8")
        )
        table_numbers = [int(item["table"]) for item in index["tables"]]
        self.assertEqual(len(table_numbers), 24)
        self.assertEqual(table_numbers.count(24), 1)
        self.assertNotIn(25, table_numbers)
        table24 = next(item for item in index["tables"] if int(item["table"]) == 24)
        self.assertEqual(table24["printed_pages"], "249-360")
        self.assertIn("primary_match_pending", table24["status"])
        self.assertFalse(index["official_pdf_bytes_downloaded_and_hashed"])
        self.assertFalse(index["authoritative_retrieval_eligible"])

    def test_secondary_candidate_inventory_is_contiguous_and_quarantined(self):
        batches = sorted(CANDIDATE_DIR.glob("decision_250_table24_candidate_batch*_2026-*.json"))
        self.assertEqual(len(batches), 38)
        row_numbers = []
        for path in batches:
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["table"], "24")
            self.assertEqual(payload["source"]["class"], "secondary_transcription")
            self.assertEqual(payload["source"]["official_gazette_match"], "not_performed")
            self.assertIsNone(payload["source"]["official_pdf_sha256"])
            self.assertEqual(payload["status"], "candidate_only_not_for_authoritative_retrieval")
            row_numbers.extend(int(row["row"]) for row in payload["rows"])
        self.assertEqual(len(row_numbers), 781)
        self.assertEqual(sorted(row_numbers), list(range(1, 782)))
        self.assertEqual(len(set(row_numbers)), 781)


if __name__ == "__main__":
    unittest.main()
