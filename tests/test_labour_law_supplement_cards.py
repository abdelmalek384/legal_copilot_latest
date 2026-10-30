import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "candidates" / "labour_law_14_2025"


class LabourLawSupplementCardTests(unittest.TestCase):
    def load_batch(self, filename, expected_count):
        payload = json.loads((DATA / filename).read_text(encoding="utf-8"))
        self.assertEqual(payload["cards_count"], expected_count)
        self.assertEqual(len(payload["cards"]), expected_count)
        self.assertFalse(payload["search_eligible"])
        ids = [card["card_id"] for card in payload["cards"]]
        self.assertEqual(len(ids), len(set(ids)))
        for card in payload["cards"]:
            self.assertTrue(card["question"])
            self.assertTrue(card["provisional_answer_ar"])
            self.assertTrue(card["pinpoint"]["article"])
            self.assertTrue(card["primary_evidence"])
            for source in card["primary_evidence"]:
                self.assertTrue(source.get("supports"))
                self.assertTrue(source.get("retrieved_or_checked_on"))
                self.assertTrue(source["url"].startswith("https://"))
            self.assertTrue(card["limitations"])
            self.assertFalse(card["search_eligible"])
        return payload

    def test_articles_256_to_274_supplement(self):
        payload = self.load_batch("provision_evidence_cards_256_274.json", 19)
        articles = {int(card["pinpoint"]["article"].replace("المادة ", "")) for card in payload["cards"]}
        self.assertEqual(articles, set(range(256, 275)))
        for card in payload["cards"]:
            article = int(card["pinpoint"]["article"].replace("المادة ", ""))
            if 258 <= article <= 265 or 270 <= article <= 274:
                self.assertEqual(card["review_state"], "provisional_secondary_crosscheck")

    def test_articles_275_to_298_supplement(self):
        payload = self.load_batch("provision_evidence_cards_275_298.json", 24)
        articles = {int(card["pinpoint"]["article"].replace("المادة ", "")) for card in payload["cards"]}
        self.assertEqual(articles, set(range(275, 299)))
        for card in payload["cards"]:
            article = int(card["pinpoint"]["article"].replace("المادة ", ""))
            if 281 <= article <= 295:
                self.assertEqual(card["review_state"], "provisional_secondary_crosscheck")


    def test_promulgation_articles_2_to_11_supplement(self):
        payload = json.loads((DATA / "provision_evidence_cards_promulgation_2_11.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["cards_count"], 10)
        self.assertEqual(len(payload["cards"]), 10)
        self.assertFalse(payload["search_eligible"])
        articles = {int(card["pinpoint"]["article"].replace("المادة ", "")) for card in payload["cards"]}
        self.assertEqual(articles, set(range(2, 12)))
        for card in payload["cards"]:
            self.assertFalse(card["search_eligible"])
            self.assertIsNone(card["pinpoint"]["official_gazette_printed_page"])
            self.assertIn("not_verified", card["pinpoint"]["pinpoint_status"])
            self.assertTrue(card["limitations"])

    def test_all_supplement_cards_are_explicitly_non_authoritative(self):
        for filename, count in (
            ("provision_evidence_cards_256_274.json", 19),
            ("provision_evidence_cards_275_298.json", 24),
        ):
            payload = self.load_batch(filename, count)
            for card in payload["cards"]:
                self.assertIn("not_usable_for", card)
                self.assertIn("manual verification", card["usable_for"])


if __name__ == "__main__":
    unittest.main()
