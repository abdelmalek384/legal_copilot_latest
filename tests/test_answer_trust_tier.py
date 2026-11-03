import unittest

from tools.answer_trust_tier import (
    TIER_SOURCE_MATCHED,
    TIER_UNREVIEWED,
    TIER_VERIFIED,
    classify_answer_trust_tier,
)


class AnswerTrustTierTests(unittest.TestCase):
    def classify(self, sources, **kwargs):
        defaults = {"claims_supported": True, "citations_complete": True}
        defaults.update(kwargs)
        return classify_answer_trust_tier(sources, **defaults)

    def test_verified_requires_backend_verified_status_and_supported_claims(self):
        result = self.classify([{"source_id": "LAW-1", "source_status": "verified_operative_text"}])
        self.assertEqual(result["trust_tier"], TIER_VERIFIED)
        self.assertEqual(result["reason_codes"], [])

    def test_citation_presence_alone_does_not_verify_an_answer(self):
        result = self.classify(
            [{"source_id": "LAW-1", "source_status": "outdated_or_under_review", "citation": "Article 1"}],
            claims_supported=False,
        )
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)
        self.assertIn("claims_not_verified_supported", result["reason_codes"])

    def test_missing_sources_fail_closed(self):
        self.assertEqual(self.classify([])["trust_tier"], TIER_UNREVIEWED)
        self.assertEqual(self.classify(None)["trust_tier"], TIER_UNREVIEWED)

    def test_mixed_verified_and_unreviewed_sources_never_upgrade(self):
        result = self.classify([
            {"source_id": "LAW-1", "source_status": "verified_operative_text"},
            {"source_id": "LAW-2", "source_status": "secondary_copy"},
        ])
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)
        self.assertIn("mixed_source_statuses", result["reason_codes"])

    def test_conflicting_sources_force_unreviewed(self):
        result = self.classify(
            [{"source_id": "LAW-1", "source_status": "verified_operative_text"}],
            contradictory_sources=True,
        )
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)
        self.assertIn("contradictory_sources_unresolved", result["reason_codes"])

    def test_missing_citations_force_unreviewed(self):
        result = self.classify(
            [{"source_id": "LAW-1", "source_status": "verified_operative_text"}],
            citations_complete=False,
        )
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)

    def test_source_matched_tier_is_disabled_without_both_gates(self):
        source = source_matched_source()
        result = self.classify([source])
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)
        self.assertIn("source_matched_policy_not_approved", result["reason_codes"])

        result = self.classify([source], source_matched_policy_approved=True)
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)
        self.assertIn("source_matched_feature_disabled", result["reason_codes"])

    def test_source_matched_requires_complete_independent_evidence(self):
        result = self.classify(
            [source_matched_source()],
            source_matched_policy_approved=True,
            source_matched_feature_enabled=True,
        )
        self.assertEqual(result["trust_tier"], TIER_SOURCE_MATCHED)
        self.assertIn("not_lawyer_reviewed", result["reason_codes"])

    def test_missing_independent_source_provenance_blocks_source_matched_tier(self):
        source = source_matched_source()
        source["source_match_evidence"]["independent_copy_source_id"] = source["source_id"]
        result = self.classify([source], source_matched_policy_approved=True, source_matched_feature_enabled=True)
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)

    def test_missing_reuse_rights_evidence_url_blocks_source_matched_tier(self):
        source = source_matched_source()
        source["source_match_evidence"]["reuse_rights_evidence_url"] = "http://example.gov/terms"
        result = self.classify([source], source_matched_policy_approved=True, source_matched_feature_enabled=True)
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)

    def test_missing_reuse_rights_blocks_source_matched_tier(self):
        source = source_matched_source()
        source["source_match_evidence"]["reuse_rights_allowed"] = False
        result = self.classify(
            [source],
            source_matched_policy_approved=True,
            source_matched_feature_enabled=True,
        )
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)

    def test_source_matched_is_never_promoted_to_verified(self):
        result = self.classify(
            [source_matched_source()],
            source_matched_policy_approved=True,
            source_matched_feature_enabled=True,
        )
        self.assertNotEqual(result["trust_tier"], TIER_VERIFIED)

    def test_duplicate_source_identifiers_fail_closed(self):
        source = {"source_id": "LAW-1", "source_status": "verified_operative_text"}
        result = self.classify([source, dict(source)])
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)
        self.assertIn("duplicate_source_id", result["reason_codes"])

    def test_missing_source_identifier_fails_closed(self):
        result = self.classify([{"source_status": "verified_operative_text"}])
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)


def source_matched_source():
    return {
        "source_id": "LAW-CANDIDATE-1",
        "source_status": "source_matched_unreviewed",
        "source_match_evidence": {
            "validator_passed": True,
            "original_capture_sha256": "a" * 64,
            "independent_copy_sha256": "b" * 64,
            "independent_copy_source_id": "INDEPENDENT-SOURCE-2",
            "publication_date": "2025-05-03",
            "effective_date": "2025-09-01",
            "reuse_rights_evidence_url": "https://example.gov/terms/reuse",
            "article_inventory_complete": True,
            "differences_resolved_against_primary": True,
            "publication_and_effective_dates_verified": True,
            "reuse_rights_allowed": True,
        },
    }


if __name__ == "__main__":
    unittest.main()
