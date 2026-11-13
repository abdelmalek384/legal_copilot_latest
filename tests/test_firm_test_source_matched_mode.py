"""Response-path contract for the explicitly gated, non-production firm-test tier.

All source text and permission evidence are synthetic; search is stubbed to inject a candidate hit.
"""
import os
import unittest
from unittest.mock import patch

import app
from tools.answer_trust_tier import classify_answer_trust_tier, firm_test_source_matched_enabled


def synthetic_source_match_evidence():
    return {
        "validator_passed": True,
        "original_capture_sha256": "a" * 64,
        "independent_copy_sha256": "b" * 64,
        "independent_copy_source_id": "SYNTHETIC-INDEPENDENT-COPY",
        "publication_date": "2025-05-03",
        "effective_date": "2025-09-01",
        "reuse_rights_evidence": "Synthetic test-only permission evidence.",
        "reuse_rights_evidence_url": "https://example.test/fictional-rights",
        "approved_uses": [
            "collection", "storage", "text_extraction", "indexing",
            "commercial_product_use", "excerpt_display",
        ],
        "article_inventory_complete": True,
        "differences_resolved_against_primary": True,
        "publication_and_effective_dates_verified": True,
        "reuse_rights_allowed": True,
    }


def source_hit():
    return {
        "id": 1,
        "cos": 1.0,
        "score": 1.0,
        "ref": "SYNTHETIC-TEST-LAW-ARTICLE-1",
        "text": "The fictional employer must give written notice.",
        "verified": False,
        "in_force": False,
        "applies_as_of": False,
        "case_id": None,
        "source_id": "SYNTHETIC-SOURCE-1",
        "source_status": "source_matched_unreviewed",
        "source_match_evidence": synthetic_source_match_evidence(),
        "provenance": {
            "status": "registry_linked",
            "official_title": "Synthetic test-only instrument",
            "document_type": "legislation",
            "law_number": "999",
            "law_year": 2099,
            "source_url": "https://example.test/fictional-source",
        },
        "article": "1",
        "page": "1",
        "citation": "Synthetic test-only instrument, Article 1",
    }


class FirmTestSourceMatchedModeTests(unittest.TestCase):
    def _ask_with_environment(self, environment):
        hit = source_hit()
        with patch.dict(os.environ, environment, clear=True):
            with patch.object(app, "search", return_value=[hit]), patch.object(
                app, "LLM",
                return_value="The fictional employer must give written notice [1].",
            ):
                result = app.ask(
                    None, "What notice must the fictional employer give?",
                    firm_id=42, scope="firm_test_source_matched",
                )
        return result, hit

    def test_enabled_test_firm_gets_cited_source_matched_answer_never_verified(self):
        result, hit = self._ask_with_environment({
            "COPILOT_ENV": "test",
            "LEGAL_FIRM_TEST_SOURCE_MATCHED": "1",
            "LEGAL_FIRM_TEST_SOURCE_MATCHED_FIRM_ID": "42",
        })
        self.assertEqual(result["answer"], "The fictional employer must give written notice [1].")
        self.assertEqual(result["trust_tier"], "source_matched")
        self.assertEqual(result["sources"][0]["trust_tier"], "source_matched")
        self.assertEqual(result["trust_tier_label"], "source-matched, not lawyer-verified")
        self.assertFalse(hit["verified"])
        self.assertNotEqual(result["trust_tier"], "verified")
        self.assertNotEqual(result["sources"][0]["trust_tier"], "verified")

    def test_flag_off_returns_sources_only_and_unreviewed_label(self):
        result, hit = self._ask_with_environment({
            "COPILOT_ENV": "development",
            "LEGAL_FIRM_TEST_SOURCE_MATCHED_FIRM_ID": "42",
        })
        self.assertIsNone(result["answer"])
        self.assertTrue(result["abstained"])
        self.assertEqual(result["trust_tier"], "unreviewed")
        self.assertNotIn("trust_tier_label", result)
        self.assertEqual(result["sources"][0]["trust_tier"], "unreviewed")
        self.assertFalse(hit["verified"])

    def test_production_unconditionally_ignores_explicit_flag(self):
        result, hit = self._ask_with_environment({
            "COPILOT_ENV": "production",
            "LEGAL_FIRM_TEST_SOURCE_MATCHED": "1",
            "LEGAL_FIRM_TEST_SOURCE_MATCHED_FIRM_ID": "42",
        })
        self.assertIsNone(result["answer"])
        self.assertTrue(result["abstained"])
        self.assertEqual(result["trust_tier"], "unreviewed")
        self.assertFalse(hit["verified"])
        self.assertFalse(firm_test_source_matched_enabled(42, {
            "COPILOT_ENV": "production",
            "LEGAL_FIRM_TEST_SOURCE_MATCHED": "1",
            "LEGAL_FIRM_TEST_SOURCE_MATCHED_FIRM_ID": "42",
        }))

    def test_source_match_evidence_url_rejects_raw_backslash(self):
        evidence = synthetic_source_match_evidence()
        source = {
            "source_id": "SYNTHETIC-SOURCE-1",
            "source_status": "source_matched_unreviewed",
            "source_match_evidence": evidence,
        }
        def classify():
            return classify_answer_trust_tier(
                [source], claims_supported=True, citations_complete=True,
                contradictory_sources=False, source_matched_policy_approved=True,
                source_matched_feature_enabled=True,
            )
        self.assertEqual(classify()["trust_tier"], "source_matched")
        evidence["reuse_rights_evidence_url"] = "https://example.test\\\\rights"
        self.assertEqual(classify()["trust_tier"], "unreviewed")

    def test_gate_rejects_float_boolean_and_malformed_firm_ids(self):
        environment = {
            "COPILOT_ENV": "test",
            "LEGAL_FIRM_TEST_SOURCE_MATCHED": "1",
            "LEGAL_FIRM_TEST_SOURCE_MATCHED_FIRM_ID": "42",
        }
        self.assertFalse(firm_test_source_matched_enabled(42.5, environment))
        self.assertFalse(firm_test_source_matched_enabled(True, environment))
        self.assertFalse(firm_test_source_matched_enabled("42x", environment))

    def test_flag_is_scoped_to_exact_test_firm_id(self):
        self.assertTrue(firm_test_source_matched_enabled(42, {
            "COPILOT_ENV": "test",
            "LEGAL_FIRM_TEST_SOURCE_MATCHED": "1",
            "LEGAL_FIRM_TEST_SOURCE_MATCHED_FIRM_ID": "42",
        }))
        self.assertFalse(firm_test_source_matched_enabled(43, {
            "COPILOT_ENV": "test",
            "LEGAL_FIRM_TEST_SOURCE_MATCHED": "1",
            "LEGAL_FIRM_TEST_SOURCE_MATCHED_FIRM_ID": "42",
        }))


if __name__ == "__main__":
    unittest.main()
