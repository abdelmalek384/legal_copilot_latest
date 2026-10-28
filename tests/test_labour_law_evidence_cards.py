import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS_PATH = ROOT / "data" / "candidates" / "labour_law_14_2025" / "provision_evidence_cards.json"


class LabourLawEvidenceCardsTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(CARDS_PATH.read_text(encoding="utf-8"))

    def test_cards_have_primary_pinpoints_and_secondary_cross_checks(self):
        self.assertEqual(self.data["instrument"]["document_id"], "EG-LABOUR-LAW-14-2025")
        self.assertGreaterEqual(len(self.data["cards"]), 9)
        ids = set()
        for card in self.data["cards"]:
            with self.subTest(card=card.get("card_id")):
                self.assertTrue(card["card_id"])
                self.assertNotIn(card["card_id"], ids)
                ids.add(card["card_id"])
                self.assertTrue(card["provisional_answer_ar"].strip())
                self.assertTrue(card["pinpoint"]["article"])
                self.assertGreaterEqual(card["pinpoint"]["official_gazette_printed_page"], 1)
                self.assertTrue(any("alamiria.com" in s["url"] for s in card["primary_evidence"]))
                self.assertTrue(any("portal.eta.gov.eg" in s["url"] for s in card["primary_evidence"]))
                self.assertTrue(card["cross_checks"])
                self.assertTrue(card["limitations"])
                self.assertEqual(card["review_state"], "provisional_primary_text_extract_reviewed")

    def test_evidence_cards_fail_closed_and_are_not_authoritative_corpus(self):
        instrument = self.data["instrument"]
        self.assertFalse(instrument["authenticity_verified"])
        self.assertFalse(instrument["currentness_verified"])
        self.assertFalse(instrument["amendment_history_verified"])
        self.assertEqual(instrument["egyptian_lawyer_review"], "pending")
        self.assertEqual(instrument["collection_permission"], "unknown")
        self.assertEqual(instrument["commercial_reuse_permission"], "unknown")
        self.assertFalse(instrument["search_eligible"])
        self.assertGreaterEqual(len(self.data["activation_gates"]), 5)
        for card in self.data["cards"]:
            self.assertIn("not_usable_for", card)
            self.assertIn("usable_for", card)

    def test_cards_do_not_embed_copied_statutory_text(self):
        # The card field is a concise paraphrase, not a full statutory transcription.
        for card in self.data["cards"]:
            self.assertLess(len(card["provisional_answer_ar"]), 700)
            self.assertNotIn("النص الكامل", card["provisional_answer_ar"])


if __name__ == "__main__":
    unittest.main()
