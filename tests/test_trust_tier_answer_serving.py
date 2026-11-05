"""Exercise the answer-serving trust tier with fictional source evidence."""

import unittest
from pathlib import Path
from unittest.mock import patch

import app


ROOT = Path(__file__).resolve().parents[1]


def source_matched_hit():
    return {
        "id": 1,
        "cos": 1.0,
        "score": 1,
        "ref": "FICTIONAL-LAW-001 Article 7",
        "article": "7",
        "page": "2",
        "text": "The fictional procedure uses one review period.",
        "verified": False,
        "in_force": True,
        "applies_as_of": True,
        "case_id": None,
        "source_status": "source_matched_unreviewed",
        "source_id": "FICTIONAL-LAW-001",
        "source_match_evidence": {
            "validator_passed": True,
            "original_capture_sha256": "a" * 64,
            "independent_copy_sha256": "b" * 64,
            "independent_copy_source_id": "FICTIONAL-COPY-001",
            "publication_date": "2025-05-03",
            "effective_date": "2025-09-01",
            "reuse_rights_evidence": "Fictional test permission only.",
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
        "provenance": {},
    }


class TrustTierAnswerServingTests(unittest.TestCase):
    def test_source_matched_answer_is_served_with_tier_and_visible_banner(self):
        hit = source_matched_hit()
        with patch.object(app, "search", return_value=[hit]), patch.object(
            app, "LLM", return_value="The fictional procedure uses one review period [1]."
        ) as model:
            result = app.ask(
                None,
                "What review period applies?",
                scope="verified_corpus",
                source_matched_policy_approved=True,
                source_matched_feature_enabled=True,
            )

        self.assertEqual(result["answer"], "The fictional procedure uses one review period [1].")
        self.assertEqual(result["trust_tier"], "source_matched")
        self.assertEqual(result["sources"][0]["trust_tier"], "source_matched")
        self.assertNotEqual(result["trust_tier"], "verified")
        model.assert_called_once()

        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        self.assertIn("m.trust_tier||(m.result&&m.result.trust_tier)", html)
        self.assertIn("if(s.trust_tier)src.append(trustTierBadge(s.trust_tier))", html)
        self.assertIn("Source-matched — not lawyer-reviewed", html)
        self.assertIn("مطابق للمصدر — غير مُراجع قانونياً", html)

    def test_unreviewed_source_is_not_used_to_generate_or_serve_an_answer(self):
        hit = source_matched_hit()
        hit["source_status"] = "pending_source_review"
        hit.pop("source_match_evidence")
        with patch.object(app, "search", return_value=[hit]), patch.object(
            app, "LLM"
        ) as model:
            result = app.ask(
                None,
                "What review period applies?",
                scope="verified_corpus",
                source_matched_policy_approved=True,
                source_matched_feature_enabled=True,
            )

        self.assertIsNone(result["answer"])
        self.assertTrue(result["abstained"])
        model.assert_not_called()


if __name__ == "__main__":
    unittest.main()
