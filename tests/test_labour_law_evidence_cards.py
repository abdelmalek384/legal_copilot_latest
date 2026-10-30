import importlib.util
from urllib.parse import urlsplit
import json
import unittest
from pathlib import Path

def _has_https_host(url, expected_host):
    try:
        parsed = urlsplit(url)
    except ValueError:
        return False
    hostname = (parsed.hostname or "").lower()
    expected_host = expected_host.lower()
    return (
        parsed.scheme == "https"
        and not parsed.username
        and not parsed.password
        and (hostname == expected_host or hostname.endswith("." + expected_host))
    )


ROOT = Path(__file__).resolve().parents[1]
CARDS_PATH = ROOT / "data" / "candidates" / "labour_law_14_2025" / "provision_evidence_cards.json"


class LabourLawEvidenceCardsTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(CARDS_PATH.read_text(encoding="utf-8"))

    def test_cards_have_primary_pinpoints_and_secondary_cross_checks(self):
        self.assertEqual(self.data["instrument"]["document_id"], "EG-LABOUR-LAW-14-2025")
        self.assertEqual(len(self.data["cards"]), 127)
        ids = set()
        for card in self.data["cards"]:
            with self.subTest(card=card.get("card_id")):
                self.assertTrue(card["card_id"])
                self.assertNotIn(card["card_id"], ids)
                ids.add(card["card_id"])
                self.assertTrue(card["provisional_answer_ar"].strip())
                self.assertTrue(card["pinpoint"]["article"])
                printed_page = card["pinpoint"].get("official_gazette_printed_page")
                if printed_page is None:
                    self.assertEqual(card["pinpoint"]["pinpoint_status"], "article_verified_in_public_transcription_page_not_verified")
                else:
                    self.assertGreaterEqual(printed_page, 1)
                self.assertTrue(any(_has_https_host(s["url"], "alamiria.com") for s in card["primary_evidence"]))
                self.assertTrue(any(_has_https_host(s["url"], "portal.eta.gov.eg") for s in card["primary_evidence"]))
                self.assertTrue(card["cross_checks"])
                self.assertTrue(card["limitations"])
                self.assertIn(card["review_state"], {"provisional_primary_text_extract_reviewed", "provisional_text_extract_crosschecked", "provisional_secondary_crosscheck"})

    def test_evidence_cards_fail_closed_and_are_not_authoritative_corpus(self):
        instrument = self.data["instrument"]
        self.assertFalse(instrument["authenticity_verified"])
        self.assertFalse(instrument["currentness_verified"])
        self.assertFalse(instrument["amendment_history_verified"])
        self.assertEqual(instrument["egyptian_lawyer_review"], "pending")
        self.assertEqual(instrument["collection_permission"], "unknown")
        self.assertEqual(instrument["commercial_reuse_permission"], "unknown")
        self.assertFalse(instrument["search_eligible"])
        self.assertTrue(all(card.get("search_eligible") is False for card in self.data["cards"]))
        self.assertGreaterEqual(len(self.data["activation_gates"]), 5)
        for card in self.data["cards"]:
            self.assertIn("not_usable_for", card)
            self.assertIn("usable_for", card)

    def test_secondary_crosschecked_cards_remain_explicitly_non_authoritative(self):
        cards = [card for card in self.data["cards"] if card["review_state"] == "provisional_secondary_crosscheck"]
        self.assertEqual(len(cards), 53)
        for card in cards:
            with self.subTest(card_id=card["card_id"]):
                self.assertFalse(card["search_eligible"])
                if card["pinpoint"].get("official_gazette_printed_page") is None:
                    self.assertEqual(card["pinpoint"]["pinpoint_status"], "article_verified_in_public_transcription_page_not_verified")
                else:
                    self.assertEqual(card["pinpoint"]["pinpoint_status"], "inferred_not_visually_verified")
                self.assertTrue(card["limitations"])
                self.assertIn("مراجعة محامٍ مصري", " ".join(card["limitations"]))
                self.assertTrue(card["not_usable_for"])

    def test_text_extract_crosschecked_coverage_cards_keep_inferred_pages(self):
        cards = [card for card in self.data["cards"] if card["review_state"] == "provisional_text_extract_crosschecked"]
        self.assertEqual(len(cards), 15)
        for card in cards:
            with self.subTest(card_id=card["card_id"]):
                self.assertFalse(card["search_eligible"])
                self.assertEqual(card["pinpoint"]["pinpoint_status"], "inferred_not_visually_verified")
                self.assertGreaterEqual(card["pinpoint"]["official_gazette_printed_page"], 1)
                self.assertIn("رقم الصفحة مستنتج", " ".join(card["limitations"]))
                self.assertIn("لا توجد مراجعة محامٍ", " ".join(card["limitations"]))
                self.assertTrue(card["not_usable_for"])

    def test_cards_do_not_embed_copied_statutory_text(self):
        # The card field is a concise paraphrase, not a full statutory transcription.
        for card in self.data["cards"]:
            self.assertLess(len(card["provisional_answer_ar"]), 700)
            self.assertNotIn("النص الكامل للقانون:", card["provisional_answer_ar"])


    def test_related_implementing_instruments_remain_discovery_only(self):
        inventory = json.loads(
            (ROOT / "docs" / "phase_2_document_inventory.json").read_text(encoding="utf-8")
        )
        documents = {item["document_id"]: item for item in inventory["documents"]}
        linked = []
        for card in self.data["cards"]:
            linked.extend(card.get("related_instruments_to_review", []))
        self.assertTrue(linked)
        for item in linked:
            with self.subTest(document_id=item["document_id"]):
                self.assertIn(item["document_id"], documents)
                self.assertEqual(documents[item["document_id"]]["review_status"], "discovery_only")
                self.assertEqual(documents[item["document_id"]]["legal_status"], "unknown")
                self.assertTrue("not verified" in item["status"] or "unverified" in item["status"])
                if item["document_id"] in {"EG-LABOUR-DECISION-49-2026", "EG-LABOUR-DECISION-294-2025"}:
                    gazette = item["official_gazette_metadata"]
                    self.assertIn("dspace.id.com.eg", gazette["source_url"])
                    if item["document_id"] == "EG-LABOUR-DECISION-49-2026":
                        self.assertIn("no original file has been downloaded", gazette["full_text_status"])
                    else:
                        self.assertIn("has not been obtained", gazette["full_text_status"])
                    self.assertTrue("not verified" in item["status"] or "unverified" in item["status"])
                    if item["document_id"] == "EG-LABOUR-DECISION-49-2026":
                        self.assertEqual(gazette["publication_date"], "2026-03-18")
                        self.assertIn("64", gazette["gazette_publication"])
                    else:
                        self.assertEqual(gazette["publication_date"], "2025-12-25")
                        self.assertIn("291", gazette["gazette_publication"])


    def test_markdown_review_report_matches_machine_readable_cards(self):
        script_path = ROOT / "tools" / "report_labour_law_evidence_cards.py"
        spec = importlib.util.spec_from_file_location("report_labour_law_evidence_cards", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        report_path = ROOT / "data" / "candidates" / "labour_law_14_2025" / "provision_evidence_cards_review.md"
        expected = module.render_report(self.data)
        actual = report_path.read_text(encoding="utf-8")
        self.assertEqual(actual, expected)
        self.assertIn("Not authoritative legal advice", actual)
        self.assertIn("Authoritative search eligibility: `false`", actual)
        self.assertIn("printed Gazette page not established (PDF page index not established)", actual)
        self.assertIn("EG-LABOUR-DECISION-49-2026", actual)
        self.assertIn("EG-LABOUR-DECISION-294-2025", actual)
        for card in self.data["cards"]:
            self.assertIn(card["card_id"], actual)

if __name__ == "__main__":
    unittest.main()
