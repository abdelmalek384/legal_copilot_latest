import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.evaluate_arabic_ocr import evaluate_records, normalize_arabic, score_page


class ArabicOcrEvaluationTests(unittest.TestCase):
    def test_normalization_handles_arabic_variants_without_dropping_punctuation(self):
        self.assertEqual(normalize_arabic("إِنَّـهُ ١٢، ى"), "انه 12، ي")

    def test_identical_text_after_normalization_has_zero_error(self):
        result = score_page({
            "document_id": "synthetic-1",
            "page": 1,
            "reference_text": "المادة ١٢: الأجر.",
            "ocr_text": "المادة 12: الاجر.",
        })
        self.assertEqual(result["cer"], 0)
        self.assertEqual(result["wer"], 0)

    def test_aggregate_is_micro_averaged_by_reference_length(self):
        result = evaluate_records([
            {"document_id": "a", "page": 1, "reference_text": "abc", "ocr_text": "abc"},
            {"document_id": "b", "page": 1, "reference_text": "abcd", "ocr_text": "abxd"},
        ])
        self.assertEqual(result["page_count"], 2)
        self.assertEqual(result["aggregate"]["character_errors"], 1)
        self.assertAlmostEqual(result["aggregate"]["cer"], 1 / 7)

    def test_missing_fields_and_empty_reference_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "missing required field"):
            score_page({"document_id": "x", "page": 1, "ocr_text": "text"})
        with self.assertRaisesRegex(ValueError, "reference_text must not be empty"):
            score_page({"document_id": "x", "page": 1, "reference_text": "  ", "ocr_text": "text"})

    def test_empty_dataset_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "no page records"):
            evaluate_records([])


if __name__ == "__main__":
    unittest.main()
