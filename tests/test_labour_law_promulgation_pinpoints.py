import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "candidates" / "labour_law_14_2025" / "provision_evidence_cards_promulgation_2_11.json"


class LabourLawPromulgationPinpointTests(unittest.TestCase):
    def test_articles_2_to_11_have_visually_checked_official_pdf_page_pins(self):
        data = json.loads(RECORD.read_text(encoding="utf-8"))
        self.assertEqual(data["cards_count"], 10)
        self.assertFalse(data["search_eligible"])
        self.assertIsNone(data["source_pdf_sha256"])
        expected = {
            2: (2, 0),
            3: (3, 1),
            4: (3, 1),
            5: (3, 1),
            6: (3, 1),
            7: (4, 2),
            8: (4, 2),
            9: (4, 2),
            10: (5, 3),
            11: (5, 3),
        }
        self.assertEqual(len(data["cards"]), 10)
        for card in data["cards"]:
            article = int("".join(ch for ch in card["pinpoint"]["article"] if ch.isdigit()))
            printed_page, pdf_index = expected[article]
            pin = card["pinpoint"]
            self.assertEqual(pin["official_gazette_printed_page"], printed_page)
            self.assertEqual(pin["pdf_page_index_zero_based"], pdf_index)
            self.assertEqual(
                pin["pinpoint_status"],
                "visually_verified_against_government_hosted_official_gazette_pdf_not_hashed",
            )
            self.assertEqual(pin["visual_checked_on"], "2026-10-31")
            source = next(
                s for s in card["primary_evidence"]
                if s["source_id"] == "EG-ETA-GAZETTE-2025-18-LABOUR-PDF"
            )
            self.assertIn("not obtained", source["supports"])
            self.assertEqual(source["retrieved_or_checked_on"], "2026-10-31")
            self.assertFalse(card["search_eligible"])
        article6 = next(c for c in data["cards"] if c["pinpoint"]["article"] == "المادة 6")
        self.assertEqual(article6["pinpoint"]["continuation_printed_pages"], [4])


if __name__ == "__main__":
    unittest.main()
