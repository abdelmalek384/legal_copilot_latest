import json
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / "tests/legal_eval/labour_law_14_2025_provisional_review_questions.draft.jsonl"
PROVISIONS = ROOT / "data/candidates/labour_law_14_2025/provisional_provisions_seed.json"


class LabourLawProvisionalReviewQuestionTests(unittest.TestCase):
    def test_each_question_is_linked_to_a_provision_and_source(self):
        rows = [json.loads(line) for line in QUESTIONS.read_text(encoding="utf-8").splitlines() if line.strip()]
        provisions = json.loads(PROVISIONS.read_text(encoding="utf-8"))["provisions"]
        provision_ids = {item["provision_id"] for item in provisions}
        self.assertEqual(len(rows), 58)
        self.assertEqual(len({row["id"] for row in rows}), len(rows))
        for row in rows:
            self.assertTrue(row["question_ar"])
            self.assertTrue(row["provisional_answer_ar"])
            self.assertIn(row["provision_id"], provision_ids)
            self.assertEqual(row["source_document_id"], "EG-LABOUR-LAW-14-2025")
            self.assertTrue(row["expected_pin_cite"])
            self.assertTrue(row["supporting_source_urls"])
            provision = next(item for item in provisions if item["provision_id"] == row["provision_id"])
            pinpoint = provision["page_pinpoint"]
            if pinpoint.get("source_type") == "official_text_page":
                self.assertEqual(pinpoint["source_url"], "https://www.alamiria.com/Sec/TashTxt?id=vPdoWGGYwoE%3D")
                self.assertTrue(any(ref.get("url") == pinpoint["source_url"] and ref.get("retrieved_on") == "2026-10-28" for ref in provision["source_refs"]))
                self.assertEqual(row["source_page_ref"], "الهيئة العامة لشئون المطابع الأميرية، النص الرسمي الإلكتروني، مادة (" + pinpoint["pinpoint"].replace("مادة (", "").replace(")", "") + ")؛ لم تتم مراجعة صفحة ممسوحة من الجريدة الرسمية")
                self.assertFalse(row["targeted_pdf_text_reviewed"])
            else:
                if "printed_pages" in pinpoint:
                    page_text = "-".join(pinpoint["printed_pages"])
                    index_text = ", ".join(str(value) for value in pinpoint["pdf_page_indices_zero_based"])
                else:
                    page_text = pinpoint["printed_page"]
                    index_text = str(pinpoint["pdf_page_index_zero_based"])
                expected_page = "الجريدة الرسمية، العدد 18 (تابع)، ص. " + page_text + " (PDF page index " + index_text + ")"
                self.assertEqual(row["source_page_ref"], expected_page)
                self.assertTrue(row["targeted_pdf_text_reviewed"])
            self.assertFalse(row["original_pdf_downloaded"])
            for url in row["supporting_source_urls"]:
                parsed = urlparse(url)
                self.assertEqual(parsed.scheme, "https")
                self.assertTrue(parsed.netloc)

    def test_questions_cannot_be_used_as_lawyer_approved_truth_or_release_answers(self):
        rows = [json.loads(line) for line in QUESTIONS.read_text(encoding="utf-8").splitlines() if line.strip()]
        for row in rows:
            self.assertEqual(row["review_status"], "needs_lawyer_review")
            self.assertIsNone(row["reviewer_id"])
            self.assertIsNone(row["review_date"])
            self.assertFalse(row["source_text_page_reviewed"])
            self.assertFalse(row["amendment_history_verified"])
            self.assertFalse(row["answerable_for_release"])
            self.assertTrue(row["must_abstain_if_unverified"])
            self.assertFalse(row["release_eligible"])


if __name__ == "__main__":
    unittest.main()
