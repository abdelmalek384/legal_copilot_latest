import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.research_inspector import (
    STATUS_METADATA_ONLY, STATUS_REVIEW, STATUS_USER_SUPPLIED, STATUS_VERIFIED,
    citation_text, research_memo, source_status,
)


def valid_source():
    return {
        "text": "Exact quoted passage.",
        "article": "12",
        "requested_as_of": "2026-10-24",
        "scope": "verified_corpus",
        "provenance": {
            "status": "registry_linked",
            "official_title": "Test instrument",
            "document_type": "law",
            "law_number": "10",
            "law_year": 2020,
            "version_label": "consolidated-2025",
            "source_url": "https://example.gov/law",
            "review_status": "verified",
            "legal_status": "in_force",
            "authenticity_verified": True,
            "status_verified": True,
            "amendment_history_verified": True,
            "collection_permission": "allowed",
            "commercial_reuse_permission": "allowed",
            "source_permission_evidence": "license ref",
            "permission_evidence": "version permission ref",
            "effective_date": "2020-01-01",
            "repeal_date": None,
        },
    }


class ResearchInspectorTests(unittest.TestCase):
    def test_only_all_explicit_gates_yield_verified_operative_status(self):
        source = valid_source()
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_VERIFIED)
        for key, value in (
            ("status_verified", False),
            ("authenticity_verified", False),
            ("amendment_history_verified", False),
            ("commercial_reuse_permission", "unknown"),
            ("source_permission_evidence", ""),
            ("permission_evidence", ""),
            ("review_status", "pending_lawyer_review"),
            ("legal_status", "under_review"),
        ):
            candidate = valid_source()
            candidate["provenance"][key] = value
            self.assertEqual(source_status(candidate, "2026-10-24"), STATUS_REVIEW, key)

    def test_future_or_repealed_version_is_not_labelled_current(self):
        source = valid_source()
        source["provenance"]["effective_date"] = "2027-01-01"
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)
        source = valid_source()
        source["provenance"]["repeal_date"] = "2026-10-01"
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_REVIEW)

    def test_metadata_only_and_firm_document_statuses_are_separate(self):
        self.assertEqual(source_status({"text": "", "provenance": {}}, "2026-10-24"), STATUS_METADATA_ONLY)
        source = valid_source()
        source["scope"] = "firm_documents"
        self.assertEqual(source_status(source, "2026-10-24"), STATUS_USER_SUPPLIED)

    def test_citation_uses_only_recorded_pin_cite_and_metadata(self):
        citation = citation_text(valid_source(), "2026-10-24")
        self.assertIn("Test instrument", citation)
        self.assertIn("No. 10/2020", citation)
        self.assertIn("Article 12", citation)
        self.assertIn("as of 2026-10-24", citation)
        self.assertIn("https://example.gov/law", citation)
        self.assertNotIn("page", citation.lower())

    def test_memo_preserves_exact_passage_and_no_source_caveat(self):
        source = valid_source()
        memo = research_memo("What is the rule?", {"answer": "Answer [1]", "sources": [source], "requested_as_of": "2026-10-24", "scope": "verified_corpus"})
        self.assertIn("Exact passage (verbatim):\nExact quoted passage.", memo)
        self.assertIn("As of: 2026-10-24", memo)
        empty = research_memo("Question", {"answer": None, "sources": [], "requested_as_of": "2026-10-24"})
        self.assertIn("No relevant verified passage was found", empty)
        self.assertIn("not evidence that no applicable law exists", empty)


if __name__ == "__main__":
    unittest.main()
