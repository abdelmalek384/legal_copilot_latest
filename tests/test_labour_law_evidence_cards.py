import importlib.util
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
        self.assertGreaterEqual(len(self.data["cards"]), 21)
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
                    self.assertTrue("not been downloaded" in gazette["full_text_status"] or "not been obtained" in gazette["full_text_status"])
                    self.assertIn("not verified", item["status"])
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
        self.assertIn("EG-LABOUR-DECISION-49-2026", actual)
        self.assertIn("EG-LABOUR-DECISION-294-2025", actual)
        for card in self.data["cards"]:
            self.assertIn(card["card_id"], actual)

    def test_working_time_and_annual_leave_cards_have_pinpoints_and_fail_closed(self):
        cards = {card["card_id"]: card for card in self.data["cards"]}
        expected = {
            "EG-LABOUR-14-2025-ART-117-DAILY-WEEKLY-HOURS": ("المادة 117", 52),
            "EG-LABOUR-14-2025-ART-118-BREAKS": ("المادة 118", 52),
            "EG-LABOUR-14-2025-ART-119-WORKDAY-SPAN": ("المادة 119", 52),
            "EG-LABOUR-14-2025-ART-120-WEEKLY-REST": ("المادة 120", 52),
            "EG-LABOUR-14-2025-ART-124-ANNUAL-LEAVE-ENTITLEMENT": ("المادة 124", 54),
            "EG-LABOUR-14-2025-ART-125-ANNUAL-LEAVE-SCHEDULING": ("المادة 125", 55),
        }
        for card_id, (article, printed_page) in expected.items():
            with self.subTest(card_id=card_id):
                card = cards[card_id]
                self.assertEqual(card["pinpoint"]["article"], article)
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], printed_page)
                self.assertTrue(any("alamiria.com" in item["url"] for item in card["primary_evidence"]))
                self.assertTrue(any("portal.eta.gov.eg" in item["url"] for item in card["primary_evidence"]))
                self.assertTrue(card["cross_checks"])
                self.assertEqual(card["review_state"], "provisional_primary_text_extract_reviewed")
                self.assertIn("لا توجد مراجعة محامٍ مصر", " ".join(card["limitations"]))
                self.assertTrue(card["not_usable_for"])
        self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_casual_and_holiday_leave_cards_have_pinpoints_and_fail_closed(self):
        cards = {card["card_id"]: card for card in self.data["cards"]}
        expected = {
            "EG-LABOUR-14-2025-ART-128-CASUAL-AND-CHILDBIRTH-LEAVE": ("المادة 128", 56),
            "EG-LABOUR-14-2025-ART-129-PUBLIC-HOLIDAY-WORK-COMPENSATION": ("المادة 129", 56),
        }
        for card_id, (article, printed_page) in expected.items():
            with self.subTest(card_id=card_id):
                card = cards[card_id]
                self.assertEqual(card["pinpoint"]["article"], article)
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], printed_page)
                self.assertTrue(any("alamiria.com" in item["url"] for item in card["primary_evidence"]))
                self.assertTrue(any("portal.eta.gov.eg" in item["url"] for item in card["primary_evidence"]))
                self.assertTrue(card["cross_checks"])
                self.assertEqual(card["review_state"], "provisional_primary_text_extract_reviewed")
                self.assertIn("لا توجد مراجعة محامٍ", " ".join(card["limitations"]))
                self.assertTrue(card["not_usable_for"])
        self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_sickness_and_infectious_contact_leave_cards_fail_closed(self):
        cards = {card["card_id"]: card for card in self.data["cards"]}
        expected = {
            "EG-LABOUR-14-2025-ART-131-SICK-LEAVE-AND-WAGE-COMPENSATION": ("المادة 131", 57),
            "EG-LABOUR-14-2025-ART-132-INFECTIOUS-DISEASE-CONTACT-LEAVE": ("المادة 132", 57),
        }
        for card_id, (article, printed_page) in expected.items():
            with self.subTest(card_id=card_id):
                card = cards[card_id]
                self.assertEqual(card["pinpoint"]["article"], article)
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], printed_page)
                self.assertTrue(any("alamiria.com" in item["url"] for item in card["primary_evidence"]))
                self.assertTrue(any("portal.eta.gov.eg" in item["url"] for item in card["primary_evidence"]))
                self.assertTrue(card["cross_checks"])
                self.assertEqual(card["review_state"], "provisional_primary_text_extract_reviewed")
                self.assertIn("لا توجد مراجعة محامٍ", " ".join(card["limitations"]))
                self.assertTrue(card["not_usable_for"])
        self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_working_time_and_leave_pinpoints_match_visual_gazette_page_map(self):
        expected_pages = {
            117: 52, 118: 52, 119: 52, 120: 52,
            121: 53, 122: 53, 123: 54, 124: 54,
            125: 55, 126: 55, 127: 55,
            128: 56, 129: 56, 130: 56,
            131: 57, 132: 57,
        }
        for card in self.data["cards"]:
            article_text = card.get("pinpoint", {}).get("article", "")
            article_numbers = [int(n) for n in __import__("re").findall(r"\d+", article_text)]
            relevant = [n for n in article_numbers if n in expected_pages]
            if not relevant:
                continue
            article = relevant[0]
            with self.subTest(card_id=card["card_id"]):
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], expected_pages[article])
                self.assertEqual(card["pinpoint"]["pdf_page_index_zero_based"], expected_pages[article] - 2)
                pdf_evidence = [
                    item for item in card["primary_evidence"]
                    if "portal.eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf" in item["url"]
                ]
                self.assertTrue(pdf_evidence)
                self.assertIn("visually checked", pdf_evidence[0]["supports"])
        self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_worker_duties_and_medical_fitness_cards_have_official_page_evidence(self):
        expected = {
            "EG-LABOUR-14-2025-ART-133-MEDICAL-UNFITNESS-DETERMINATION": ("المادة 133", 57),
            "EG-LABOUR-14-2025-ART-134-WORKER-DUTIES": ("المادة 134", 57),
            "EG-LABOUR-14-2025-ART-135-MEDICAL-TESTING-AND-HEALTH": ("المادة 135", 58),
            "EG-LABOUR-14-2025-ART-136-WORKER-CONFLICTS-AND-UNDUE-BENEFITS": ("المادة 136", 59),
        }
        cards = {card["card_id"]: card for card in self.data["cards"]}
        for card_id, (article, printed_page) in expected.items():
            with self.subTest(card_id=card_id):
                card = cards[card_id]
                self.assertEqual(card["pinpoint"]["article"], article)
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], printed_page)
                self.assertTrue(any("alamiria.com" in item["url"] for item in card["primary_evidence"]))
                gazette = [
                    item for item in card["primary_evidence"]
                    if "portal.eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf" in item["url"]
                ]
                self.assertTrue(gazette)
                self.assertIn("روجعت بصرياً", gazette[0]["supports"])
                self.assertTrue(card["cross_checks"])
                self.assertTrue(card["limitations"])
                self.assertTrue(card["not_usable_for"])
        self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_exam_leave_cards_have_pinpoints_and_fail_closed(self):
        cards = {card["card_id"]: card for card in self.data["cards"]}
        expected = {
            "EG-LABOUR-14-2025-ART-121-OVERTIME-EXCEPTION": ("المادة 121", 53),
            "EG-LABOUR-14-2025-ART-122-WORK-SCHEDULE-DISPLAY": ("المادة 122", 53),
            "EG-LABOUR-14-2025-ART-123-WORK-HOUR-EXEMPTIONS": ("المادة 123", 53),
            "EG-LABOUR-14-2025-ART-126-EXAM-LEAVE": ("المادة 126", 55),
            "EG-LABOUR-14-2025-ART-127-WORK-DURING-LEAVE": ("المادة 127", 55),
        }
        for card_id, (article, printed_page) in expected.items():
            with self.subTest(card_id=card_id):
                card = cards[card_id]
                self.assertEqual(card["pinpoint"]["article"], article)
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], printed_page)
                self.assertTrue(any("alamiria.com" in item["url"] for item in card["primary_evidence"]))
                self.assertTrue(any("portal.eta.gov.eg" in item["url"] for item in card["primary_evidence"]))
                self.assertEqual(card["review_state"], "provisional_primary_text_extract_reviewed")
                self.assertIn("لا توجد مراجعة محامٍ مسجلة", " ".join(card["limitations"]))
                self.assertTrue(card["not_usable_for"])
        self.assertFalse(self.data["instrument"]["search_eligible"])


if __name__ == "__main__":
    unittest.main()
