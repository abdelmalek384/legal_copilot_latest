import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.evaluate_ocr_quality import OCREvaluationError, edit_distance, evaluate, normalize_arabic


class OCRQualityEvaluationTests(unittest.TestCase):
    def test_exact_and_substitution_character_error_rates(self):
        report = evaluate([{
            "id": "P1", "document_id": "DOC1", "page": 1,
            "reference_text": "المادة ١٢ صحيحة",
            "ocr_text": "المادة ١٢ صحيحة",
        }])
        self.assertEqual(report["overall"]["raw_cer"]["error_rate"], 0.0)
        self.assertEqual(report["overall"]["raw_wer"]["error_rate"], 0.0)
        self.assertFalse(report["legal_correctness_scored"])
        self.assertEqual(report["by_document"]["DOC1"]["pages_scored"], 1)
        self.assertEqual(edit_distance("قانون", "قانو") , 1)

    def test_arabic_normalization_removes_diacritics_tatweel_and_digit_variants(self):
        self.assertEqual(normalize_arabic("أَحْكَامـ ١٢ى"), "احكام 12ي")
        report = evaluate([{
            "id": "P2", "reference_text": "أحكام ١٢", "ocr_text": "احكام 12",
        }])
        self.assertGreater(report["overall"]["raw_cer"]["error_rate"], 0)
        self.assertEqual(report["overall"]["normalized_cer"]["error_rate"], 0.0)

    def test_word_error_rate_and_document_grouping(self):
        report = evaluate([
            {"id": "A", "document_id": "DOC", "page": 1, "reference_text": "هذا نص قانوني", "ocr_text": "هذا نص"},
            {"id": "B", "document_id": "DOC", "page": 2, "reference_text": "نص آخر", "ocr_text": "نص آخر"},
        ])
        self.assertGreater(report["overall"]["raw_wer"]["error_rate"], 0)
        self.assertEqual(report["pages"][0]["raw_wer"]["edits"], 1)
        self.assertEqual(report["pages"][0]["raw_wer"]["reference_units"], 3)
        self.assertEqual(report["by_document"]["DOC"]["pages_scored"], 2)
        self.assertEqual(report["rows_scored"], 2)

    def test_critical_token_metrics_catch_missing_article_numbers_and_negation(self):
        report = evaluate([{
            "id": "CRITICAL-1",
            "document_id": "DOC-CRITICAL",
            "reference_text": "المادة ١٢ لا يجوز",
            "ocr_text": "المادة ١٢ يجوز",
            "critical_tokens": ["المادة ١٢", "لا يجوز"],
        }])
        page = report["pages"][0]
        self.assertEqual(page["critical_tokens_expected_count"], 2)
        self.assertEqual(page["critical_tokens_found_count"], 1)
        self.assertEqual(page["critical_token_recall"], 0.5)
        self.assertEqual(page["missing_critical_tokens"], ["لا يجوز"])
        self.assertEqual(report["overall"]["critical_token_recall"], 0.5)
        self.assertEqual(report["overall"]["pages_with_missing_critical_tokens"], 1)
        self.assertEqual(report["by_document"]["DOC-CRITICAL"]["critical_token_page_failure_rate"], 1.0)

    def test_critical_tokens_must_be_present_in_reference_and_well_formed(self):
        base = {"id": "CRITICAL-2", "reference_text": "المادة ١٢ لا يجوز", "ocr_text": "المادة ١٢ لا يجوز"}
        with self.assertRaisesRegex(OCREvaluationError, "must appear in reference_text"):
            evaluate([{**base, "critical_tokens": ["المادة ١٣"]}])
        for value in ("لا يجوز", [""], ["   "], [None], ["المادة ١٢", "المادة 12"]):
            with self.subTest(value=value):
                with self.assertRaisesRegex(OCREvaluationError, "critical_tokens"):
                    evaluate([{**base, "critical_tokens": value}])

    def test_rejects_duplicate_ids_bad_rows_and_excessive_edit_distance(self):
        row = {"id": "A", "reference_text": "a", "ocr_text": "b"}
        with self.assertRaisesRegex(OCREvaluationError, "duplicate id"):
            evaluate([row, row])
        with self.assertRaisesRegex(OCREvaluationError, "must be strings"):
            evaluate([{"id": "B", "reference_text": None, "ocr_text": ""}])
        with self.assertRaisesRegex(OCREvaluationError, "too large"):
            edit_distance("a" * 3000, "b" * 3000)


if __name__ == "__main__":
    unittest.main()
