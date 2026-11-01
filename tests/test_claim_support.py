"""Tests for the optional claim-support screen using fictional passages only."""
import os
import unittest
from unittest import mock

import app
from app import norm, tokens, _mask_markdown_code
from tools.claim_support import claim_support_enabled, has_unsupported_claims


class ClaimSupportTests(unittest.TestCase):
    def test_never_expires_is_blocked_against_a_five_year_limitation_source(self):
        hits = [{"text": "The limitation period is five years."}]
        self.assertTrue(has_unsupported_claims(
            "The claim never expires [1].", hits, tokens, norm, _mask_markdown_code
        ))

    def test_faithful_five_year_paraphrase_passes(self):
        hits = [{"text": "The limitation period is five years."}]
        self.assertFalse(has_unsupported_claims(
            "The limitation period lasts five years [1].",
            hits, tokens, norm, _mask_markdown_code
        ))

    def test_arabic_no_expiry_claim_is_blocked_by_finite_limitation_period(self):
        hits = [{"text": "مدة التقادم خمس سنوات."}]
        for claim in ("الحق لا يتقادم أبدا [1].", "الدعوى لا تسقط مطلقا [1]."):
            with self.subTest(claim=claim):
                self.assertTrue(has_unsupported_claims(
                    claim, hits, tokens, norm, _mask_markdown_code
                ))

    def test_faithful_arabic_limitation_paraphrase_passes(self):
        hits = [{"text": "مدة التقادم خمس سنوات."}]
        self.assertFalse(has_unsupported_claims(
            "التقادم مدته خمس سنوات [1].",
            hits, tokens, norm, _mask_markdown_code
        ))

    def test_invalid_citation_fails_closed(self):
        self.assertTrue(has_unsupported_claims(
            "The limitation period is five years [2].",
            [{"text": "The limitation period is five years."}],
            tokens, norm, _mask_markdown_code
        ))

    def test_enabled_claim_support_failure_returns_sources_only_from_ask(self):
        hit = {
            "ref": "Synthetic source [1]", "text": "Synthetic fictional passage.",
            "cos": 1.0, "score": 1, "verified": True,
            "source_status": app.STATUS_VERIFIED, "case_id": None,
            "in_force": True, "applies_as_of": True,
        }
        with (
            mock.patch.object(app, "search", return_value=[hit]),
            mock.patch.object(app, "LLM", return_value="Unsupported factual claim [1]."),
            mock.patch.object(app, "claim_support_enabled", return_value=True),
            mock.patch.object(app, "has_unsupported_claims", return_value=True) as checker,
            mock.patch.object(app, "_prompt_provenance", return_value={}),
            mock.patch.object(app, "_answer_has_unsupported_quantities", return_value=False),
            mock.patch.object(app, "_answer_has_uncited_claims", return_value=False),
            mock.patch.object(app, "_answer_has_unanchored_citations", return_value=False),
            mock.patch.object(app, "_answer_has_source_polarity_conflict", return_value=False),
            mock.patch.object(app, "_answer_has_mismatched_pincites", return_value=False),
            mock.patch.object(app, "_answer_has_cited_actor_role_mismatch", return_value=False),
            mock.patch.object(app, "_answer_has_unqualified_claim_against_conditional_source", return_value=False),
        ):
            response = app.ask(None, "سؤال اختباري", scope="verified_corpus")
        self.assertIsNone(response["answer"])
        self.assertTrue(response["abstained"])
        self.assertEqual(response["sources"], [hit])
        checker.assert_called_once()

    def test_claim_support_is_not_applied_by_ask_when_feature_flag_is_off(self):
        hit = {
            "ref": "Synthetic source [1]", "text": "Synthetic fictional passage.",
            "cos": 1.0, "score": 1, "verified": True,
            "source_status": app.STATUS_VERIFIED, "case_id": None,
            "in_force": True, "applies_as_of": True,
        }
        with (
            mock.patch.object(app, "search", return_value=[hit]),
            mock.patch.object(app, "LLM", return_value="Supported-looking claim [1]."),
            mock.patch.object(app, "claim_support_enabled", return_value=False),
            mock.patch.object(app, "has_unsupported_claims", return_value=True) as checker,
            mock.patch.object(app, "_prompt_provenance", return_value={}),
            mock.patch.object(app, "_answer_has_unsupported_quantities", return_value=False),
            mock.patch.object(app, "_answer_has_uncited_claims", return_value=False),
            mock.patch.object(app, "_answer_has_unanchored_citations", return_value=False),
            mock.patch.object(app, "_answer_has_source_polarity_conflict", return_value=False),
            mock.patch.object(app, "_answer_has_mismatched_pincites", return_value=False),
            mock.patch.object(app, "_answer_has_cited_actor_role_mismatch", return_value=False),
            mock.patch.object(app, "_answer_has_unqualified_claim_against_conditional_source", return_value=False),
        ):
            response = app.ask(None, "سؤال اختباري", scope="verified_corpus")
        self.assertEqual(response["answer"], "Supported-looking claim [1].")
        self.assertFalse(response["abstained"])
        checker.assert_not_called()

    def test_feature_flag_is_off_by_default_and_requires_explicit_opt_in(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(claim_support_enabled())
        with mock.patch.dict(os.environ, {"LEGAL_CLAIM_SUPPORT_CHECK": "1"}):
            self.assertTrue(claim_support_enabled())


if __name__ == "__main__":
    unittest.main()
