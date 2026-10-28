import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "candidates" / "labour_law_14_2025" / "provision_evidence_cards_coverage_gaps_1_39.json"

class TestLabourLawCoverageGapSupplement(unittest.TestCase):
    def test_gap_supplement_contains_all_15_expected_articles_and_stays_ineligible(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        articles = {int("".join(ch for ch in card["pinpoint"]["article"] if ch.isdigit())) for card in data["cards"]}
        self.assertEqual(len(data["cards"]), 15)
        self.assertEqual(articles, {1, 2, 3, 14, 15, 17, 18, 19, 20, 21, 24, 26, 35, 38, 39})
        self.assertFalse(data["instrument"]["search_eligible"])
        for card in data["cards"]:
            self.assertTrue(card["primary_evidence"])
            self.assertTrue(card["limitations"])
            self.assertTrue(card["not_usable_for"])

if __name__ == "__main__":
    unittest.main()
