"""Tests for conservative Legal Research document-intelligence helpers."""
import unittest

from tools.document_intelligence import (
    classify_document, compare_extracted_text, extract_review_candidates,
    normalized_text_digest, sha256_bytes,
)


class DocumentIntelligenceTests(unittest.TestCase):
    def test_classification_is_transparent_and_never_auto_approved(self):
        result = classify_document("judgment.pdf", "حكم المحكمة في الدعوى")
        self.assertEqual(result["category"], "court_judgment")
        self.assertEqual(result["confidence"], "medium")
        self.assertTrue(result["requires_review"])
        self.assertIn("حكم", result["matched_terms"])

    def test_unknown_document_remains_unclassified(self):
        result = classify_document("scan.pdf", "نص غير واضح")
        self.assertEqual(result["category"], "unclassified")
        self.assertEqual(result["confidence"], "low")
        self.assertTrue(result["requires_review"])

    def test_extracts_literal_candidates_with_pdf_page_provenance(self):
        text = ("[[PDF_PAGE:3]]\nدعوى رقم ١٢٣/٢٠٢٥ بتاريخ ١٥/٠٣/٢٠٢٥. "
                "المدعي: أحمد محمد. والمبلغ ٥٠٠٠ جنيه.")
        result = extract_review_candidates(text)
        by_kind = {}
        for item in result["candidates"]:
            by_kind.setdefault(item["kind"], []).append(item)
            self.assertEqual(item["page"], 3)
            self.assertEqual(item["review_status"], "candidate_unverified")
            self.assertTrue(item["excerpt"])
        self.assertIn("case_reference", by_kind)
        self.assertIn("date", by_kind)
        self.assertIn("amount", by_kind)
        self.assertIn("party_label", by_kind)

    def test_docx_style_text_has_no_invented_page_number(self):
        result = extract_review_candidates("عقد بتاريخ 2025-04-03")
        self.assertTrue(result["candidates"])
        self.assertTrue(all(item["page"] is None for item in result["candidates"]))

    def test_text_size_is_bounded(self):
        with self.assertRaises(ValueError):
            extract_review_candidates("x" * 1_000_001)

    def test_exact_bytes_and_normalized_text_have_separate_hash_helpers(self):
        self.assertNotEqual(sha256_bytes(b"a\nb"), sha256_bytes(b"a b"))
        self.assertEqual(normalized_text_digest("a\nb"), normalized_text_digest("a  b"))

    def test_comparison_reports_literal_changes_for_review(self):
        changes = compare_extracted_text("قيمة العقد ١٠٠٠ جنيه", "قيمة العقد ٢٠٠٠ جنيه")
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["change_type"], "replace")
        self.assertIn("١٠٠٠", changes[0]["before"])
        self.assertIn("٢٠٠٠", changes[0]["after"])
        self.assertEqual(changes[0]["review_status"], "requires_lawyer_review")

    def test_comparison_rejects_invalid_context(self):
        with self.assertRaises(ValueError):
            compare_extracted_text("a", "b", context_chars=-1)

    def test_comparison_has_a_separate_cpu_bound(self):
        with self.assertRaises(ValueError):
            compare_extracted_text("a" * 100_001, "b")


if __name__ == "__main__":
    unittest.main()
