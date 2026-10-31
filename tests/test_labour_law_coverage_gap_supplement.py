import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "candidates" / "labour_law_14_2025" / "provision_evidence_cards_coverage_gaps_1_39.json"
MAIN = ROOT / "data" / "candidates" / "labour_law_14_2025" / "provision_evidence_cards.json"


def _article_number(value):
    digits = "".join(ch for ch in value if ch.isdigit())
    if digits:
        return int(digits)
    # Promulgation Article 1 is conventionally written as "المادة الأولى".
    if value.strip() == "المادة الأولى":
        return 1
    raise AssertionError(f"Unrecognized article pinpoint: {value!r}")

class TestLabourLawCoverageGapSupplement(unittest.TestCase):
    def test_gap_supplement_contains_all_15_expected_articles_and_stays_ineligible(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        articles = {_article_number(card["pinpoint"]["article"]) for card in data["cards"]}
        self.assertEqual(len(data["cards"]), 15)
        self.assertEqual(articles, {1, 2, 3, 14, 15, 17, 18, 19, 20, 21, 24, 26, 35, 38, 39})
        self.assertFalse(data["instrument"]["search_eligible"])
        for card in data["cards"]:
            self.assertTrue(card["primary_evidence"])
            self.assertTrue(card["limitations"])
            self.assertTrue(card["not_usable_for"])

    def test_combined_main_and_supplement_cover_all_298_law_articles(self):
        main = json.loads(MAIN.read_text(encoding="utf-8"))
        supplement = json.loads(DATA.read_text(encoding="utf-8"))
        all_cards = main["cards"] + supplement["cards"]
        articles = {int("".join(ch for ch in card["pinpoint"]["article"] if ch.isdigit())) for card in all_cards}
        self.assertEqual(len(main["cards"]), 294)
        self.assertEqual(len(supplement["cards"]), 15)
        self.assertEqual(articles, set(range(1, 299)))
        self.assertFalse(main["instrument"]["search_eligible"])
        self.assertFalse(supplement["instrument"]["search_eligible"])

if __name__ == "__main__":
    unittest.main()
