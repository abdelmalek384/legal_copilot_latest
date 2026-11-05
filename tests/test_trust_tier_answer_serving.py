"""Exercise the answer-serving trust tier through real fictional retrieval."""

import os
import unittest
from pathlib import Path
from unittest.mock import patch

import app
from test_synthetic_retrieval import SyntheticCorpus


ROOT = Path(__file__).resolve().parents[1]


SOURCE_MATCH_EVIDENCE = {
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
}


class TrustTierAnswerServingTests(unittest.TestCase):
    def setUp(self):
        self.fixture = SyntheticCorpus()
        self.fixture.add_passage(
            "FICTIONAL-LAW-001",
            "The fictional procedure uses one review period.",
            article="7",
        )
        self.patches = [
            patch.dict(os.environ, {"LEGAL_QUALIFIED_EGYPTIAN_COUNSEL_USER_IDS": "42"}),
            patch.object(app, "corpus_conn", return_value=self.fixture.db),
            patch.object(
                app,
                "citation_provenance",
                return_value={
                    "status": "registry_linked",
                    "source_id": "FICTIONAL-LAW-001",
                    "version_id": 1,
                    "legal_status": "in_force",
                    "source_match_evidence": SOURCE_MATCH_EVIDENCE,
                },
            ),
            patch.object(app, "citation_text", return_value="Synthetic test citation"),
        ]
        for patcher in self.patches:
            patcher.start()

    def tearDown(self):
        for patcher in reversed(self.patches):
            patcher.stop()
        self.fixture.db.close()

    def test_source_matched_answer_is_served_with_tier_and_visible_banner(self):
        with patch.object(app, "source_status", return_value="source_matched_unreviewed"), patch.object(
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
        with patch.object(app, "source_status", return_value="pending_source_review"), patch.object(
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
