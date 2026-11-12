"""Tests for additional literal legal-reference and event-mention candidates."""
import unittest

from tools.document_intelligence_extensions import extract_legal_reference_and_event_mentions


class DocumentIntelligenceExtensionTests(unittest.TestCase):
    def test_legal_references_and_event_mentions_keep_pdf_page_provenance(self):
        text = (
            "Introductory text.\n[[PDF_PAGE:7]]\n"
            "قانون رقم ١٢ لسنة ٢٠٠٣، المادة ١٠١. جلسة ١٥/٠٣/٢٠٢٥. "
            "The court issued a notice before the hearing."
        )
        result = extract_legal_reference_and_event_mentions(text)
        candidates = result["candidates"]
        legal = [item for item in candidates if item["kind"] == "legal_reference"]
        events = [item for item in candidates if item["kind"] == "event_mention"]
        self.assertGreaterEqual(len(legal), 2)
        self.assertTrue(events)
        self.assertTrue(all(item["page"] == 7 for item in candidates))
        self.assertTrue(all(item["review_status"] == "candidate_unverified" for item in candidates))
        self.assertTrue(any("المادة ١٠١" in item["value"] for item in legal))
        self.assertTrue(any("جلسة" in item["value"] for item in events))

    def test_only_literal_event_terms_are_returned(self):
        result = extract_legal_reference_and_event_mentions("The agreement contains ordinary terms.")
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["candidate_count"], 0)

    def test_input_type_and_analysis_budget_are_enforced(self):
        with self.assertRaises(TypeError):
            extract_legal_reference_and_event_mentions(None)
        with self.assertRaises(ValueError):
            extract_legal_reference_and_event_mentions("X" * 1_000_001)


if __name__ == "__main__":
    unittest.main()
