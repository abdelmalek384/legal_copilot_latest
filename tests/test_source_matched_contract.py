"""Contract tests for the proposed source-matched answer tier.

The fixture is fictional. The production feature remains disabled unless the
separate policy and deployment gates are explicitly enabled.
"""
import unittest
from pathlib import Path

from tools.answer_trust_tier import classify_answer_trust_tier


ROOT = Path(__file__).resolve().parents[1]


def fictional_source():
    return {
        "source_id": "FICTIONAL-LAW-001",
        "source_status": "source_matched_unreviewed",
        "source_match_evidence": {
            "validator_passed": True,
            "original_capture_sha256": "a" * 64,
            "independent_copy_sha256": "b" * 64,
            "independent_copy_source_id": "FICTIONAL-INDEPENDENT-COPY-001",
            "publication_date": "2025-05-03",
            "effective_date": "2025-09-01",
            "reuse_rights_evidence": "Fictional fixture permission evidence only.",
            "reuse_rights_evidence_url": "https://example.test/fictional-rights",
            "approved_uses": [
                "collection", "storage", "text_extraction", "indexing",
                "commercial_product_use", "excerpt_display",
            ],
            "article_inventory_complete": True,
            "differences_resolved_against_primary": True,
            "publication_and_effective_dates_verified": True,
            "reuse_rights_allowed": True,
        },
    }


class SourceMatchedContractTests(unittest.TestCase):
    def test_classifier_tier_has_non_verified_ui_label_contract(self):
        source = fictional_source()
        classification = classify_answer_trust_tier(
            [source],
            claims_supported=True,
            citations_complete=True,
            contradictory_sources=False,
            source_matched_policy_approved=True,
            source_matched_feature_enabled=True,
        )

        # Illustrative response shape only; app.ask() does not currently emit this field.
        answer = {
            "content": "Fictional answer supported by the fictional passage.",
            "trust_tier": classification["trust_tier"],
            "sources": [{
                "source_id": source["source_id"],
                "trust_tier": classification["trust_tier"],
            }],
        }
        self.assertEqual(answer["trust_tier"], "source_matched")
        self.assertEqual(answer["sources"][0]["trust_tier"], "source_matched")
        self.assertNotEqual(answer["trust_tier"], "verified")
        self.assertEqual(classification["reason_codes"], ["not_lawyer_reviewed"])
        self.assertEqual(source["source_status"], "source_matched_unreviewed")

        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        self.assertIn("m.trust_tier||(m.result&&m.result.trust_tier)", html)
        self.assertIn("if(s.trust_tier)src.append(trustTierBadge(s.trust_tier))", html)
        self.assertIn("Source-matched — not lawyer-reviewed", html)
        self.assertIn("مطابق للمصدر — غير مُراجع قانونياً", html)

    def test_missing_policy_or_feature_gate_keeps_candidate_unreviewed(self):
        source = fictional_source()
        result = classify_answer_trust_tier(
            [source],
            claims_supported=True,
            citations_complete=True,
            contradictory_sources=False,
            source_matched_policy_approved=True,
            source_matched_feature_enabled=False,
        )
        self.assertEqual(result["trust_tier"], "unreviewed")
        self.assertIn("source_matched_feature_disabled", result["reason_codes"])


if __name__ == "__main__":
    unittest.main()
