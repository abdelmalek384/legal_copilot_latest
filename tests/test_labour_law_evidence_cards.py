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

    def test_source_host_assertions_reject_lookalike_and_userinfo_urls(self):
        self.assertTrue(_has_https_host("https://www.alamiria.com/Sec/TashTxt?id=x", "alamiria.com"))
        self.assertFalse(_has_https_host("https://alamiria.com.attacker.test/path", "alamiria.com"))
        self.assertFalse(_has_https_host("https://attacker.test/?next=alamiria.com", "alamiria.com"))
        self.assertFalse(_has_https_host("https://alamiria.com@attacker.test/path", "alamiria.com"))
        self.assertFalse(_has_https_host("http://alamiria.com/path", "alamiria.com"))

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
                    full_text_status = gazette["full_text_status"].casefold()
                    self.assertIn("original file", full_text_status)
                    self.assertIn("not been downloaded", full_text_status)
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
                self.assertTrue(any(_has_https_host(item["url"], "alamiria.com") for item in card["primary_evidence"]))
                self.assertTrue(any(_has_https_host(item["url"], "portal.eta.gov.eg") for item in card["primary_evidence"]))
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
                self.assertTrue(any(_has_https_host(item["url"], "alamiria.com") for item in card["primary_evidence"]))
                self.assertTrue(any(_has_https_host(item["url"], "portal.eta.gov.eg") for item in card["primary_evidence"]))
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
                self.assertTrue(any(_has_https_host(item["url"], "alamiria.com") for item in card["primary_evidence"]))
                self.assertTrue(any(_has_https_host(item["url"], "portal.eta.gov.eg") for item in card["primary_evidence"]))
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
                    if _has_https_host(item["url"], "portal.eta.gov.eg") and urlsplit(item["url"]).path == "/sites/default/files/2026-03/law.no_.14.of_.2025.pdf"
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
                self.assertTrue(any(_has_https_host(item["url"], "alamiria.com") for item in card["primary_evidence"]))
                gazette = [
                    item for item in card["primary_evidence"]
                    if _has_https_host(item["url"], "portal.eta.gov.eg") and urlsplit(item["url"]).path == "/sites/default/files/2026-03/law.no_.14.of_.2025.pdf"
                ]
                self.assertTrue(gazette)
                self.assertIn("روجعت بصرياً", gazette[0]["supports"])
                self.assertTrue(card["cross_checks"])
                self.assertTrue(card["limitations"])
                self.assertTrue(card["not_usable_for"])
        self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_work_rules_and_disciplinary_procedure_cards_have_official_pinpoints(self):
        expected = {
            "EG-LABOUR-14-2025-ART-137-WORK-REGULATIONS-REQUIREMENTS": ("المادة 137", 60),
            "EG-LABOUR-14-2025-ART-138-DISCIPLINARY-SCOPE-AND-PROPORTIONALITY": ("المادة 138", 60),
            "EG-LABOUR-14-2025-ART-139-DISCIPLINARY-PENALTIES-LIST": ("المادة 139", 61),
            "EG-LABOUR-14-2025-ART-140-SINGLE-PENALTY-AND-DEDUCTION-LIMIT": ("المادة 140", 61),
            "EG-LABOUR-14-2025-ART-141-DISCIPLINARY-INVESTIGATION-TIME-LIMITS": ("المادة 141", 61),
        }
        cards = {card["card_id"]: card for card in self.data["cards"]}
        for card_id, (article, printed_page) in expected.items():
            with self.subTest(card_id=card_id):
                card = cards[card_id]
                self.assertEqual(card["pinpoint"]["article"], article)
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], printed_page)
                self.assertTrue(any(_has_https_host(item["url"], "alamiria.com") for item in card["primary_evidence"]))
                gazette = [
                    item for item in card["primary_evidence"]
                    if _has_https_host(item["url"], "portal.eta.gov.eg") and urlsplit(item["url"]).path == "/sites/default/files/2026-03/law.no_.14.of_.2025.pdf"
                ]
                self.assertTrue(gazette)
                self.assertIn("روجعت بصرياً", gazette[0]["supports"])
                self.assertTrue(card["cross_checks"])
                self.assertTrue(card["limitations"])
                self.assertTrue(card["not_usable_for"])
        self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_articles_142_to_148_have_official_page_evidence(self):
        expected = {
            142: 62, 143: 62, 144: 62, 145: 62,
            146: 63, 147: 63, 148: 63,
        }
        cards = {card["card_id"]: card for card in self.data["cards"]}
        for article, page in expected.items():
            matching = [card for card in cards.values() if card["pinpoint"]["article"] == f"المادة {article}"]
            with self.subTest(article=article):
                self.assertTrue(matching)
                card = matching[-1]
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], page)
                self.assertTrue(any(_has_https_host(item["url"], "alamiria.com") for item in card["primary_evidence"]))
                self.assertTrue(any(_has_https_host(item["url"], "portal.eta.gov.eg") for item in card["primary_evidence"]))
                self.assertTrue(card["limitations"])
        self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_individual_dispute_cards_have_official_pinpoints(self):
        expected = {149: 64, 150: 65}
        cards = {card["card_id"]: card for card in self.data["cards"]}
        for article, page in expected.items():
            matching = [card for card in cards.values() if card["pinpoint"]["article"] == f"المادة {article}"]
            with self.subTest(article=article):
                self.assertTrue(matching)
                card = matching[-1]
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], page)
                self.assertTrue(any(_has_https_host(item["url"], "alamiria.com") for item in card["primary_evidence"]))
                self.assertTrue(any(_has_https_host(item["url"], "portal.eta.gov.eg") for item in card["primary_evidence"]))
                self.assertTrue(card["limitations"])
        self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_worker_liability_and_termination_cards_have_official_pinpoints(self):
        expected = {151: 65, 152: 66, 153: 66, 154: 66, 155: 67, 156: 67, 157: 67, 158: 67}
        cards = {card["card_id"]: card for card in self.data["cards"]}
        for article, page in expected.items():
            matching = [card for card in cards.values() if card["pinpoint"]["article"] == f"المادة {article}"]
            with self.subTest(article=article):
                self.assertTrue(matching)
                card = matching[-1]
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], page)
                self.assertTrue(any(_has_https_host(item["url"], "alamiria.com") for item in card["primary_evidence"]))
                self.assertTrue(any(_has_https_host(item["url"], "portal.eta.gov.eg") for item in card["primary_evidence"]))
                self.assertTrue(card["limitations"])
        self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_notice_period_cards_have_official_pinpoints(self):
        expected = {159: 68, 160: 68, 161: 68, 162: 68, 163: 68, 164: 69}
        cards = {card["card_id"]: card for card in self.data["cards"]}
        for article, page in expected.items():
            matching = [card for card in cards.values() if card["pinpoint"]["article"] == f"المادة {article}"]
            with self.subTest(article=article):
                self.assertTrue(matching)
                card = matching[-1]
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], page)
                self.assertTrue(any(_has_https_host(item["url"], "alamiria.com") for item in card["primary_evidence"]))
                self.assertTrue(any(_has_https_host(item["url"], "portal.eta.gov.eg") for item in card["primary_evidence"]))
                self.assertTrue(card["limitations"])
        self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_exam_leave_cards_have_pinpoints_and_fail_closed(self):
        cards = {card["card_id"]: card for card in self.data["cards"]}
        expected = {
            "EG-LABOUR-14-2025-ART-121-OVERTIME-EXCEPTION": ("المادة 121", 53),
            "EG-LABOUR-14-2025-ART-122-WORK-SCHEDULE-DISPLAY": ("المادة 122", 53),
            "EG-LABOUR-14-2025-ART-123-WORK-HOUR-EXEMPTIONS": ("المادة 123", 54),
            "EG-LABOUR-14-2025-ART-126-EXAM-LEAVE": ("المادة 126", 55),
            "EG-LABOUR-14-2025-ART-127-WORK-DURING-LEAVE": ("المادة 127", 55),
        }
        for card_id, (article, printed_page) in expected.items():
            with self.subTest(card_id=card_id):
                card = cards[card_id]
                self.assertEqual(card["pinpoint"]["article"], article)
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], printed_page)
                self.assertTrue(any(_has_https_host(item["url"], "alamiria.com") for item in card["primary_evidence"]))
                self.assertTrue(any(_has_https_host(item["url"], "portal.eta.gov.eg") for item in card["primary_evidence"]))
                self.assertEqual(card["review_state"], "provisional_primary_text_extract_reviewed")
                self.assertIn("لا توجد مراجعة محامٍ مسجلة", " ".join(card["limitations"]))
                self.assertTrue(card["not_usable_for"])
        self.assertFalse(self.data["instrument"]["search_eligible"])


if __name__ == "__main__":
    unittest.main()

    def test_termination_and_end_of_service_cards_165_to_175_have_pinpoints(self):
        cards = {card["card_id"]: card for card in self.data["cards"]}
        expected = {
            "EG-LABOUR-14-2025-ART-165-UNLAWFUL-TERMINATION-COMPENSATION": ("المادة 165", 69, 67),
            "EG-LABOUR-14-2025-ART-166-ABSENCE-DEEMED-RESIGNATION": ("المادة 166", 70, 68),
            "EG-LABOUR-14-2025-ART-167-RESIGNATION-FORMALITY-ACCEPTANCE-WITHDRAWAL": ("المادة 167", 70, 68),
            "EG-LABOUR-14-2025-ART-168-WORKER-TERMINATION-EMPLOYER-BREACH-OR-ASSAULT": ("المادة 168", 70, 68),
            "EG-LABOUR-14-2025-ART-169-DEATH-EMPLOYEE-EMPLOYER-AND-FAMILY-PAYMENTS": ("المادة 169", 70, 68),
            "EG-LABOUR-14-2025-ART-170-TOTAL-PARTIAL-DISABILITY": ("المادة 170", 71, 69),
            "EG-LABOUR-14-2025-ART-171-RETIREMENT-AGE-AND-FIXED-TERM": ("المادة 171", 71, 69),
            "EG-LABOUR-14-2025-ART-172-POST-RETIREMENT-SERVICE-GRATUITY": ("المادة 172", 72, 70),
            "EG-LABOUR-14-2025-ART-173-TERMINATION-DURING-ILLNESS-LEAVE": ("المادة 173", 72, 70),
            "EG-LABOUR-14-2025-ART-174-FINAL-CRIMINAL-CONVICTION-TERMINATION": ("المادة 174", 72, 70),
            "EG-LABOUR-14-2025-ART-175-EMPLOYMENT-CERTIFICATE-AND-RETURN-OF-DOCUMENTS": ("المادة 175", 72, 70),
        }
        self.assertEqual(len(self.data["cards"]), 360)
        for card_id, (article, printed_page, pdf_index) in expected.items():
            with self.subTest(card_id=card_id):
                card = cards[card_id]
                self.assertEqual(card["pinpoint"]["article"], article)
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], printed_page)
                self.assertEqual(card["pinpoint"]["pdf_page_index_zero_based"], pdf_index)
                self.assertFalse(self.data["instrument"]["search_eligible"])
                self.assertTrue(card["limitations"])
                self.assertIn("portal.eta.gov.eg", " ".join(s["url"] for s in card["primary_evidence"]))

    def test_procedural_cards_176_to_187_have_pinpoints(self):
        cards = {card["card_id"]: card for card in self.data["cards"]}
        expected = {
            "EG-LABOUR-14-2025-ART-176-SPECIALIZED-LABOUR-COURTS": ("المادة 176", 73, 71),
            "EG-LABOUR-14-2025-ART-177-LABOUR-COURT-SUBJECT-MATTER-JURISDICTION": ("المادة 177", 73, 71),
            "EG-LABOUR-14-2025-ART-178-LABOUR-COURT-CHAMBER-COMPOSITION": ("المادة 178", 73, 71),
            "EG-LABOUR-14-2025-ART-179-URGENT-MATTERS-LABOUR-COURT-JUDGE": ("المادة 179", 73, 71),
            "EG-LABOUR-14-2025-ART-180-CHALLENGE-URGENT-ORDERS": ("المادة 180", 73, 71),
            "EG-LABOUR-14-2025-ART-181-LABOUR-COURT-CRIMINAL-JURISDICTION": ("المادة 181", 74, 72),
            "EG-LABOUR-14-2025-ART-182-CASSATION-LIMITS-LABOUR-CRIMINAL-CASES": ("المادة 182", 74, 72),
            "EG-LABOUR-14-2025-ART-183-LABOUR-JUDGMENT-ENFORCEMENT-DISPUTES": ("المادة 183", 74, 72),
            "EG-LABOUR-14-2025-ART-184-LABOUR-COURT-REGISTRY-ENFORCEMENT-OFFICE": ("المادة 184", 74, 72),
            "EG-LABOUR-14-2025-ART-185-LABOUR-COURT-LEGAL-AID-OFFICE": ("المادة 185", 74, 72),
            "EG-LABOUR-14-2025-ART-186-COURT-OF-CASSATION-LABOUR-CHAMBERS": ("المادة 186", 75, 73),
            "EG-LABOUR-14-2025-ART-187-LABOUR-JUDGMENT-APPEAL-PROCEDURE": ("المادة 187", 75, 73),
        }
        self.assertEqual(len(self.data["cards"]), 360)
        for card_id, (article, printed_page, pdf_index) in expected.items():
            with self.subTest(card_id=card_id):
                card = cards[card_id]
                self.assertEqual(card["pinpoint"]["article"], article)
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], printed_page)
                self.assertEqual(card["pinpoint"]["pdf_page_index_zero_based"], pdf_index)
                self.assertTrue(card["limitations"])
                self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_decree_162_2026_primary_text_access_and_secondary_crosscheck_are_explicit(self):
        inventory = json.loads(
            (ROOT / "docs" / "phase_2_document_inventory.json").read_text(encoding="utf-8")
        )
        record = next(
            item for item in inventory["documents"]
            if item["document_id"] == "EG-LABOUR-WORK-REGULATION-RULES-2026"
        )
        self.assertEqual(record["instrument_number"], 162)
        self.assertEqual(record["instrument_year"], 2026)
        self.assertEqual(record["review_status"], "discovery_only")
        self.assertEqual(record["legal_status"], "unknown")
        self.assertEqual(record["collection_permission"], "unknown")
        self.assertIn("primary_text_restricted", record["source_status"])
        self.assertTrue(any("dspace.id.com.eg/items/" in item["url"] for item in record["source_urls"]))
        self.assertTrue(any("ahmedazimelgamel.blogspot.com/2026/08/162-2026.html" in item["url"] for item in record["source_urls"]))
        self.assertIn("no copy was requested", record["notes"])

    def test_collective_labour_relations_cards_188_to_200_have_pinpoints(self):
        cards = {card["card_id"]: card for card in self.data["cards"]}
        expected = {
            "EG-LABOUR-14-2025-ART-188-SUPREME-SOCIAL-CONSULTATION-COUNCIL": ("المادة 188", 76, 74),
            "EG-LABOUR-14-2025-ART-189-SOCIAL-CONSULTATION-COUNCIL-COMPETENCIES": ("المادة 189", 76, 74),
            "EG-LABOUR-14-2025-ART-190-SOCIAL-COUNCIL-COMPOSITION": ("المادة 190", 76, 74),
            "EG-LABOUR-14-2025-ART-191-SOCIAL-COUNCIL-TERM": ("المادة 191", 76, 74),
            "EG-LABOUR-14-2025-ART-192-SOCIAL-COUNCIL-BRANCHES-COMMITTEES": ("المادة 192", 76, 74),
            "EG-LABOUR-14-2025-ART-193-SOCIAL-COUNCIL-FUNDING-AND-AUDIT": ("المادة 193", 76, 74),
            "EG-LABOUR-14-2025-ART-194-COLLECTIVE-BARGAINING-PURPOSES": ("المادة 194", 77, 75),
            "EG-LABOUR-14-2025-ART-195-COLLECTIVE-BARGAINING-LEVELS": ("المادة 195", 77, 75),
            "EG-LABOUR-14-2025-ART-196-COLLECTIVE-DISPUTE-MANDATORY-NEGOTIATION": ("المادة 196", 77, 75),
            "EG-LABOUR-14-2025-ART-197-COLLECTIVE-AGREEMENT-FROM-NEGOTIATION": ("المادة 197", 77, 75),
            "EG-LABOUR-14-2025-ART-198-NO-UNILATERAL-ACTIONS-DURING-NEGOTIATION": ("المادة 198", 77, 75),
            "EG-LABOUR-14-2025-ART-199-COLLECTIVE-AGREEMENT-DURATION": ("المادة 199", 78, 76),
            "EG-LABOUR-14-2025-ART-200-COLLECTIVE-AGREEMENT-CONFLICT-AND-BETTER-BENEFIT": ("المادة 200", 78, 76),
        }
        self.assertEqual(len(self.data["cards"]), 360)
        for card_id, (article, printed_page, pdf_index) in expected.items():
            with self.subTest(card_id=card_id):
                card = cards[card_id]
                self.assertEqual(card["pinpoint"]["article"], article)
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], printed_page)
                self.assertEqual(card["pinpoint"]["pdf_page_index_zero_based"], pdf_index)
                self.assertTrue(card["limitations"])
                self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_collective_agreement_cards_201_to_214_have_pinpoints(self):
        cards = {card["card_id"]: card for card in self.data["cards"]}
        expected = {
            "EG-LABOUR-14-2025-ART-201-COLLECTIVE-AGREEMENT-ARABIC-LANGUAGE": ("المادة 201", 78, 76),
            "EG-LABOUR-14-2025-ART-202-COLLECTIVE-AGREEMENT-RENEWAL-TIMELINE": ("المادة 202", 78, 76),
            "EG-LABOUR-14-2025-ART-203-COLLECTIVE-AGREEMENT-FILING-AND-OBJECTION": ("المادة 203", 78, 76),
            "EG-LABOUR-14-2025-ART-204-COLLECTIVE-AGREEMENT-REGISTRATION-COURT-CHALLENGE": ("المادة 204", 78, 76),
            "EG-LABOUR-14-2025-ART-205-COLLECTIVE-AGREEMENT-WORKPLACE-DISPLAY": ("المادة 205", 78, 76),
            "EG-LABOUR-14-2025-ART-206-COLLECTIVE-AGREEMENT-JOINING-AFTER-REGISTRATION": ("المادة 206", 79, 77),
            "EG-LABOUR-14-2025-ART-207-COLLECTIVE-AGREEMENT-REGISTER-UPDATES": ("المادة 207", 79, 77),
            "EG-LABOUR-14-2025-ART-208-COLLECTIVE-AGREEMENT-GOOD-FAITH-IMPLEMENTATION": ("المادة 208", 79, 77),
            "EG-LABOUR-14-2025-ART-209-COLLECTIVE-AGREEMENT-UNFORESEEN-HARDSHIP": ("المادة 209", 79, 77),
            "EG-LABOUR-14-2025-ART-210-COLLECTIVE-AGREEMENT-ENFORCEMENT-AND-COMPENSATION": ("المادة 210", 79, 77),
            "EG-LABOUR-14-2025-ART-211-COLLECTIVE-AGREEMENT-UNION-REPRESENTATIVE-ACTIONS": ("المادة 211", 79, 77),
            "EG-LABOUR-14-2025-ART-212-COLLECTIVE-AGREEMENT-DISPUTE-PROCEDURES": ("المادة 212", 79, 77),
            "EG-LABOUR-14-2025-ART-213-COLLECTIVE-LABOUR-DISPUTE-SCOPE": ("المادة 213", 80, 78),
            "EG-LABOUR-14-2025-ART-214-COLLECTIVE-DISPUTE-CONCILIATION-THRESHOLD": ("المادة 214", 80, 78),
        }
        self.assertEqual(len(self.data["cards"]), 360)
        for card_id, (article, printed_page, pdf_index) in expected.items():
            with self.subTest(card_id=card_id):
                card = cards[card_id]
                self.assertEqual(card["pinpoint"]["article"], article)
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], printed_page)
                self.assertEqual(card["pinpoint"]["pdf_page_index_zero_based"], pdf_index)
                self.assertTrue(card["limitations"])
                self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_collective_dispute_resolution_cards_215_to_230_have_pinpoints(self):
        cards = {card["card_id"]: card for card in self.data["cards"]}
        expected = {
            "EG-LABOUR-14-2025-ART-215-COLLECTIVE-DISPUTE-CONCILIATION-HEARING": ("المادة 215", 80, 78),
            "EG-LABOUR-14-2025-ART-216-COLLECTIVE-DISPUTE-CONCILIATION-SETTLEMENT": ("المادة 216", 80, 78),
            "EG-LABOUR-14-2025-ART-217-COLLECTIVE-DISPUTE-REFERRAL-TO-MEDIATION-ARBITRATION": ("المادة 217", 80, 78),
            "EG-LABOUR-14-2025-ART-218-LABOUR-MEDIATION-ARBITRATION-CENTRE": ("المادة 218", 81, 79),
            "EG-LABOUR-14-2025-ART-219-LABOUR-MEDIATOR-AND-ARBITRATOR-LISTS": ("المادة 219", 81, 79),
            "EG-LABOUR-14-2025-ART-220-JUDICIAL-MEMBERS-MEDIATION-ARBITRATION": ("المادة 220", 81, 79),
            "EG-LABOUR-14-2025-ART-221-LABOUR-MEDIATOR-ELIGIBILITY": ("المادة 221", 81, 79),
            "EG-LABOUR-14-2025-ART-222-LABOUR-MEDIATOR-SELECTION-DEADLINE": ("المادة 222", 81, 79),
            "EG-LABOUR-14-2025-ART-223-LABOUR-MEDIATOR-TASK-AND-DURATION": ("المادة 223", 82, 80),
            "EG-LABOUR-14-2025-ART-224-LABOUR-MEDIATOR-REPLACEMENT": ("المادة 224", 82, 80),
            "EG-LABOUR-14-2025-ART-225-LABOUR-MEDIATION-RECOMMENDATIONS-AND-REPORT": ("المادة 225", 82, 80),
            "EG-LABOUR-14-2025-ART-226-LABOUR-ARBITRATOR-ELIGIBILITY": ("المادة 226", 82, 80),
            "EG-LABOUR-14-2025-ART-227-LABOUR-ARBITRATION-TRIBUNAL-COMPOSITION": ("المادة 227", 82, 80),
            "EG-LABOUR-14-2025-ART-228-LABOUR-ARBITRATION-SUBMISSION": ("المادة 228", 82, 80),
            "EG-LABOUR-14-2025-ART-229-LABOUR-ARBITRAL-AWARD-RULES-AND-DEADLINE": ("المادة 229", 83, 81),
            "EG-LABOUR-14-2025-ART-230-LABOUR-ARBITRAL-AWARD-REVIEW": ("المادة 230", 83, 81),
        }
        self.assertEqual(len(self.data["cards"]), 360)
        for card_id, (article, printed_page, pdf_index) in expected.items():
            with self.subTest(card_id=card_id):
                card = cards[card_id]
                self.assertEqual(card["pinpoint"]["article"], article)
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], printed_page)
                self.assertEqual(card["pinpoint"]["pdf_page_index_zero_based"], pdf_index)
                self.assertTrue(card["limitations"])
                self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_strike_and_economic_closure_cards_231_to_241_have_pinpoints(self):
        cards = {card["card_id"]: card for card in self.data["cards"]}
        expected = {
            "EG-LABOUR-14-2025-ART-231-WORKERS-STRIKE-PREREQUISITES": ("المادة 231", 83, 81),
            "EG-LABOUR-14-2025-ART-232-STRIKE-ADVANCE-NOTICE": ("المادة 232", 83, 81),
            "EG-LABOUR-14-2025-ART-233-STRIKE-DURING-COLLECTIVE-AGREEMENT": ("المادة 233", 83, 81),
            "EG-LABOUR-14-2025-ART-234-STRIKE-ESSENTIAL-SERVICES-AND-EXCEPTIONAL-CIRCUMSTANCES": ("المادة 234", 83, 81),
            "EG-LABOUR-14-2025-ART-235-STRIKE-EFFECT-ON-EMPLOYMENT-OBLIGATIONS": ("المادة 235", 83, 81),
            "EG-LABOUR-14-2025-ART-236-EMPLOYER-ECONOMIC-CLOSURE-OR-DOWNSIZING": ("المادة 236", 83, 81),
            "EG-LABOUR-14-2025-ART-237-ECONOMIC-CLOSURE-COMMITTEE-APPLICATION": ("المادة 237", 84, 82),
            "EG-LABOUR-14-2025-ART-238-ECONOMIC-CLOSURE-NOTICE-AND-IMPLEMENTATION": ("المادة 238", 84, 82),
            "EG-LABOUR-14-2025-ART-239-ECONOMIC-DOWNSIZING-SELECTION-CRITERIA": ("المادة 239", 84, 82),
            "EG-LABOUR-14-2025-ART-240-ECONOMIC-CLOSURE-DURING-COLLECTIVE-DISPUTE-OR-STRIKE": ("المادة 240", 84, 82),
            "EG-LABOUR-14-2025-ART-241-TEMPORARY-ECONOMIC-CHANGES-IN-EMPLOYMENT-TERMS": ("المادة 241", 84, 82),
        }
        self.assertEqual(len(self.data["cards"]), 360)
        for card_id, (article, printed_page, pdf_index) in expected.items():
            with self.subTest(card_id=card_id):
                card = cards[card_id]
                self.assertEqual(card["pinpoint"]["article"], article)
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], printed_page)
                self.assertEqual(card["pinpoint"]["pdf_page_index_zero_based"], pdf_index)
                self.assertTrue(card["limitations"])
                self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_occupational_safety_cards_242_to_255_have_pinpoints(self):
        cards = {card["card_id"]: card for card in self.data["cards"]}
        expected = {
            "EG-LABOUR-14-2025-ART-242-OCCUPATIONAL-SAFETY-CHAPTER-SCOPE": ("المادة 242", 85, 83),
            "EG-LABOUR-14-2025-ART-243-OCCUPATIONAL-SAFETY-ESTABLISHMENT-DEFINITION": ("المادة 243", 85, 83),
            "EG-LABOUR-14-2025-ART-244-OCCUPATIONAL-SAFETY-APPLICATION-SCOPE": ("المادة 244", 85, 83),
            "EG-LABOUR-14-2025-ART-245-OCCUPATIONAL-COMPLIANCE-OFFICES": ("المادة 245", 85, 83),
            "EG-LABOUR-14-2025-ART-246-OCCUPATIONAL-PHYSICAL-HAZARDS": ("المادة 246", 85, 83),
            "EG-LABOUR-14-2025-ART-247-OCCUPATIONAL-ENGINEERING-HAZARDS": ("المادة 247", 85, 83),
            "EG-LABOUR-14-2025-ART-248-OCCUPATIONAL-BIOLOGICAL-HAZARDS": ("المادة 248", 86, 84),
            "EG-LABOUR-14-2025-ART-249-OCCUPATIONAL-CHEMICAL-HAZARDS": ("المادة 249", 86, 84),
            "EG-LABOUR-14-2025-ART-250-OCCUPATIONAL-INDIRECT-HAZARDS": ("المادة 250", 86, 84),
            "EG-LABOUR-14-2025-ART-251-OCCUPATIONAL-FIRE-PREVENTION": ("المادة 251", 86, 84),
            "EG-LABOUR-14-2025-ART-252-OCCUPATIONAL-CONFINED-SPACE-SAFETY": ("المادة 252", 86, 84),
            "EG-LABOUR-14-2025-ART-253-OCCUPATIONAL-EMERGENCY-PLANS-AND-WORKER-WITHDRAWAL": ("المادة 253", 86, 84),
            "EG-LABOUR-14-2025-ART-254-WORKPLACE-HARASSMENT-BULLYING-VIOLENCE-PREVENTION": ("المادة 254", 87, 85),
            "EG-LABOUR-14-2025-ART-255-OCCUPATIONAL-SAFETY-TECHNICAL-STANDARDS": ("المادة 255", 87, 85),
        }
        self.assertEqual(len(self.data["cards"]), 360)
        for card_id, (article, printed_page, pdf_index) in expected.items():
            with self.subTest(card_id=card_id):
                card = cards[card_id]
                self.assertEqual(card["pinpoint"]["article"], article)
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], printed_page)
                self.assertEqual(card["pinpoint"]["pdf_page_index_zero_based"], pdf_index)
                self.assertTrue(card["limitations"])
                self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_occupational_safety_inspection_and_welfare_cards_256_to_274_have_pinpoints(self):
        cards = {card["card_id"]: card for card in self.data["cards"]}
        expected = {
            "EG-LABOUR-14-2025-ART-256-OCCUPATIONAL-SAFETY-INSPECTION-UNIT": ("المادة 256", 87, 85),
            "EG-LABOUR-14-2025-ART-257-OCCUPATIONAL-SAFETY-INSPECTOR-POWERS": ("المادة 257", 88, 86),
            "EG-LABOUR-14-2025-ART-258-OCCUPATIONAL-SAFETY-INSPECTOR-ACCESS": ("المادة 258", 88, 86),
            "EG-LABOUR-14-2025-ART-259-OCCUPATIONAL-SAFETY-INTERNAL-UNITS-COMMITTEES": ("المادة 259", 88, 86),
            "EG-LABOUR-14-2025-ART-260-OCCUPATIONAL-ACCIDENT-REPORTING-DEADLINES": ("المادة 260", 88, 86),
            "EG-LABOUR-14-2025-ART-261-OCCUPATIONAL-SAFETY-TRAINING-LICENSING": ("المادة 261", 88, 86),
            "EG-LABOUR-14-2025-ART-262-OCCUPATIONAL-SAFETY-CONSULTANT-LICENSE": ("المادة 262", 88, 86),
            "EG-LABOUR-14-2025-ART-263-NATIONAL-OCCUPATIONAL-SAFETY-CENTRE": ("المادة 263", 89, 87),
            "EG-LABOUR-14-2025-ART-264-SUPREME-OCCUPATIONAL-SAFETY-COUNCIL": ("المادة 264", 89, 87),
            "EG-LABOUR-14-2025-ART-265-GOVERNORATE-OCCUPATIONAL-SAFETY-COMMITTEES": ("المادة 265", 89, 87),
            "EG-LABOUR-14-2025-ART-266-PRE-EMPLOYMENT-MEDICAL-AND-CAPABILITY-EXAMS": ("المادة 266", 90, 88),
            "EG-LABOUR-14-2025-ART-267-EMPLOYER-TRAINING-AND-PPE-NO-CHARGE": ("المادة 267", 90, 88),
            "EG-LABOUR-14-2025-ART-268-WORKER-USE-AND-CARE-OF-PPE": ("المادة 268", 90, 88),
            "EG-LABOUR-14-2025-ART-269-WORKPLACE-DAILY-SAFETY-INSPECTIONS-AND-MEDICAL-CHECKS": ("المادة 269", 90, 88),
            "EG-LABOUR-14-2025-ART-270-WORKPLACE-FIRST-AID-AND-NURSING": ("المادة 270", 90, 88),
            "EG-LABOUR-14-2025-ART-271-REMOTE-WORKSITE-TRANSPORT-FOOD-HOUSING": ("المادة 271", 91, 89),
            "EG-LABOUR-14-2025-ART-272-SOCIAL-CULTURAL-SERVICES-50-WORKERS": ("المادة 272", 91, 89),
            "EG-LABOUR-14-2025-ART-273-SOCIAL-HEALTH-CULTURAL-SERVICES-FUND": ("المادة 273", 91, 89),
            "EG-LABOUR-14-2025-ART-274-SOCIAL-SERVICES-FUND-BENEFITS": ("المادة 274", 91, 89),
        }
        self.assertEqual(len(self.data["cards"]), 360)
        for card_id, (article, printed_page, pdf_index) in expected.items():
            with self.subTest(card_id=card_id):
                card = cards[card_id]
                self.assertEqual(card["pinpoint"]["article"], article)
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], printed_page)
                self.assertEqual(card["pinpoint"]["pdf_page_index_zero_based"], pdf_index)
                self.assertTrue(card["limitations"])
                self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_labour_inspection_and_penalty_cards_275_to_298_have_pinpoints(self):
        cards = {card["card_id"]: card for card in self.data["cards"]}
        expected = {
            "EG-LABOUR-14-2025-ART-275-LABOUR-INSPECTOR-JUDICIAL-POLICE-STATUS": ("المادة 275", 105, 103),
            "EG-LABOUR-14-2025-ART-276-LABOUR-INSPECTOR-ENTRY-AND-RECORDS": ("المادة 276", 106, 104),
            "EG-LABOUR-14-2025-ART-277-EMPLOYER-DUTY-TO-COOPERATE-WITH-INSPECTORS": ("المادة 277", 106, 104),
            "EG-LABOUR-14-2025-ART-278-EMPLOYER-ATTENDANCE-REQUESTS": ("المادة 278", 106, 104),
            "EG-LABOUR-14-2025-ART-279-PUBLIC-AUTHORITY-ASSISTANCE-TO-INSPECTORS": ("المادة 279", 106, 104),
            "EG-LABOUR-14-2025-ART-280-LABOUR-OFFENCES-PENALTY-INTRODUCTION": ("المادة 280", 106, 104),
            "EG-LABOUR-14-2025-ART-281-LABOUR-PENALTY-ARTICLES-4-5": ("المادة 281", 107, 105),
            "EG-LABOUR-14-2025-ART-282-LABOUR-PENALTY-ARTICLES-82-273-21": ("المادة 282", 107, 105),
            "EG-LABOUR-14-2025-ART-283-LABOUR-PENALTY-ARTICLES-37-48-153-137": ("المادة 283", 107, 105),
            "EG-LABOUR-14-2025-ART-284-LABOUR-PENALTY-ARTICLE-26": ("المادة 284", 107, 105),
            "EG-LABOUR-14-2025-ART-285-LABOUR-PENALTY-ARTICLE-23": ("المادة 285", 107, 105),
            "EG-LABOUR-14-2025-ART-286-LABOUR-PENALTY-ARTICLES-7-24-25-36-46-51-52-68": ("المادة 286", 108, 106),
            "EG-LABOUR-14-2025-ART-287-LABOUR-PENALTY-ARTICLES-45-104-108": ("المادة 287", 108, 106),
            "EG-LABOUR-14-2025-ART-288-LABOUR-PENALTY-MULTIPLE-WORKER-RIGHTS-ARTICLES": ("المادة 288", 108, 106),
            "EG-LABOUR-14-2025-ART-289-LABOUR-PENALTY-ARTICLES-62-66": ("المادة 289", 109, 107),
            "EG-LABOUR-14-2025-ART-290-LABOUR-PENALTY-ARTICLES-33-37-35-205": ("المادة 290", 109, 107),
            "EG-LABOUR-14-2025-ART-291-LABOUR-PENALTY-UNLICENSED-RECRUITMENT-AND-UNLAWFUL-CHARGES": ("المادة 291", 109, 107),
            "EG-LABOUR-14-2025-ART-292-LABOUR-PENALTY-ARTICLE-42": ("المادة 292", 110, 108),
            "EG-LABOUR-14-2025-ART-293-LABOUR-PENALTY-ARTICLES-70-74": ("المادة 293", 110, 108),
            "EG-LABOUR-14-2025-ART-294-LABOUR-PENALTY-DISCIPLINE-AND-RELATED-ARTICLES": ("المادة 294", 110, 108),
            "EG-LABOUR-14-2025-ART-295-LABOUR-PENALTY-ECONOMIC-CLOSURE-ARTICLES": ("المادة 295", 110, 108),
            "EG-LABOUR-14-2025-ART-296-LABOUR-PENALTY-OCCUPATIONAL-SAFETY-ARTICLES": ("المادة 296", 111, 109),
            "EG-LABOUR-14-2025-ART-297-LABOUR-PENALTY-INSPECTION-OBSTRUCTION": ("المادة 297", 111, 109),
            "EG-LABOUR-14-2025-ART-298-LABOUR-CORPORATE-MANAGER-AND-ENTITY-LIABILITY": ("المادة 298", 111, 109),
        }
        self.assertEqual(len(self.data["cards"]), 360)
        for card_id, (article, printed_page, pdf_index) in expected.items():
            with self.subTest(card_id=card_id):
                card = cards[card_id]
                self.assertEqual(card["pinpoint"]["article"], article)
                self.assertEqual(card["pinpoint"]["official_gazette_printed_page"], printed_page)
                self.assertEqual(card["pinpoint"]["pdf_page_index_zero_based"], pdf_index)
                self.assertTrue(card["limitations"])
                self.assertFalse(self.data["instrument"]["search_eligible"])

    def test_articles_275_to_298_use_visually_verified_official_pdf_pages(self):
        cards = self.data["cards"]
        checked = 0
        source_url = "https://portal.eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf"
        for card in cards:
            article_text = card["pinpoint"]["article"]
            try:
                article = int(article_text.split()[-1])
            except (TypeError, ValueError):
                continue
            if not 275 <= article <= 298:
                continue
            if article == 275:
                printed_page, pdf_index = 105, 103
            elif article <= 280:
                printed_page, pdf_index = 106, 104
            elif article <= 285:
                printed_page, pdf_index = 107, 105
            elif article <= 288:
                printed_page, pdf_index = 108, 106
            elif article <= 291:
                printed_page, pdf_index = 109, 107
            elif article <= 295:
                printed_page, pdf_index = 110, 108
            else:
                printed_page, pdf_index = 111, 109
            with self.subTest(card_id=card["card_id"]):
                pinpoint = card["pinpoint"]
                self.assertEqual(pinpoint["official_gazette_printed_page"], printed_page)
                self.assertEqual(pinpoint["pdf_page_index_zero_based"], pdf_index)
                self.assertEqual(pinpoint["pinpoint_status"], "visually_verified_on_official_eta_pdf")
                visual = pinpoint["visual_verification"]
                self.assertEqual(visual["checked_on"], "2026-10-31")
                self.assertEqual(visual["printed_page"], printed_page)
                self.assertEqual(visual["pdf_page_index_zero_based"], pdf_index)
                self.assertEqual(visual["source_url"], source_url)
            checked += 1
        self.assertEqual(checked, 46)
        self.assertFalse(self.data["instrument"]["search_eligible"])
