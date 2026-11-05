"""Tests for the optional claim-support screen using fictional passages only."""
import json
import os
import unittest
from unittest import mock

import app
from app import norm, tokens, _mask_markdown_code
from tools.claim_support import _has_modal_mismatch, claim_support_enabled, has_unsupported_claims


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

    def test_raw_negated_obligation_cannot_be_rewritten_as_positive(self):
        cases = (
            ("The employer is not required to provide notice.", "The employer must provide notice."),
            ("The employer must not deduct wages.", "The employer must deduct wages."),
            ("لا يجب على صاحب العمل تقديم الإخطار.", "يجب على صاحب العمل تقديم الإخطار."),
            ("لا يلتزم صاحب العمل بتقديم الإخطار.", "يلتزم صاحب العمل بتقديم الإخطار."),
            ("The employer must provide notice.", "The employer is not required to provide notice."),
            ("يجب على صاحب العمل تقديم الإخطار.", "لا يجب على صاحب العمل تقديم الإخطار."),
        )
        for evidence, claim in cases:
            with self.subTest(evidence=evidence, claim=claim):
                self.assertTrue(has_unsupported_claims(
                    claim + " [1].", [{"text": evidence}],
                    tokens, norm, _mask_markdown_code
                ))

    def test_faithful_raw_negated_obligation_paraphrases_pass(self):
        cases = (
            ("The employer is not required to provide notice.", "The employer is not required to provide notice."),
            ("The employer must not deduct wages.", "The employer must not deduct wages."),
            ("لا يجب على صاحب العمل تقديم الإخطار.", "لا يجب على صاحب العمل تقديم الإخطار."),
            ("لا يلتزم صاحب العمل بتقديم الإخطار.", "لا يلتزم صاحب العمل بتقديم الإخطار."),
        )
        for evidence, claim in cases:
            with self.subTest(evidence=evidence):
                self.assertFalse(has_unsupported_claims(
                    claim + " [1].", [{"text": evidence}],
                    tokens, norm, _mask_markdown_code
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
        self.assertTrue(response["claim_support_blocked"])
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
        self.assertFalse(response["claim_support_blocked"])
        checker.assert_not_called()

    def test_feature_flag_is_off_by_default_and_requires_explicit_opt_in(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(claim_support_enabled())
        with mock.patch.dict(os.environ, {"LEGAL_CLAIM_SUPPORT_CHECK": "1"}):
            self.assertTrue(claim_support_enabled())



    def test_modal_strength_change_from_may_to_must_is_blocked(self):
        hits = [{"text": "The employee may request leave after six months."}]
        self.assertTrue(has_unsupported_claims(
            "The employee must request leave after six months [1].",
            hits, tokens, norm, _mask_markdown_code
        ))

    def test_modal_strength_change_from_must_to_may_is_blocked(self):
        hits = [{"text": "The employer must provide written notice."}]
        self.assertTrue(has_unsupported_claims(
            "The employer may provide written notice [1].",
            hits, tokens, norm, _mask_markdown_code
        ))

    def test_arabic_permission_to_obligation_change_is_blocked(self):
        hits = [{"text": "يجوز للعامل طلب الإجازة بعد ستة أشهر."}]
        self.assertTrue(has_unsupported_claims(
            "يجب على العامل طلب الإجازة بعد ستة أشهر [1].",
            hits, tokens, norm, _mask_markdown_code
        ))

    def test_arabic_prohibition_is_not_misread_as_permission(self):
        hits = [{"text": "لا يجوز لصاحب العمل خصم الأجر."}]
        self.assertFalse(has_unsupported_claims(
            "لا يجوز لصاحب العمل خصم الأجر [1].",
            hits, tokens, norm, _mask_markdown_code
        ))

    def test_english_prohibition_change_is_blocked(self):
        hits = [{"text": "The employer may not deduct wages."}]
        self.assertTrue(has_unsupported_claims(
            "The employer may deduct wages [1].",
            hits, tokens, norm, _mask_markdown_code
        ))

    def test_must_not_is_not_misclassified_as_a_positive_obligation(self):
        hits = [{"text": "The employer must provide written notice."}]
        self.assertTrue(has_unsupported_claims(
            "The employer must not provide written notice [1].",
            hits, tokens, norm, _mask_markdown_code
        ))

    def test_not_required_to_conflicts_with_required_to(self):
        hits = [{"text": "The employee is required to submit the request."}]
        self.assertTrue(has_unsupported_claims(
            "The employee is not required to submit the request [1].",
            hits, tokens, norm, _mask_markdown_code
        ))

    def test_not_permitted_to_conflicts_with_permitted_to(self):
        hits = [{"text": "The employee is permitted to request leave."}]
        self.assertTrue(has_unsupported_claims(
            "The employee is not permitted to request leave [1].",
            hits, tokens, norm, _mask_markdown_code
        ))

    def test_arabic_no_right_conflicts_with_positive_right(self):
        hits = [{"text": "يحق للعامل طلب الإجازة بعد ستة أشهر."}]
        self.assertTrue(has_unsupported_claims(
            "لا يحق للعامل طلب الإجازة بعد ستة أشهر [1].",
            hits, tokens, norm, _mask_markdown_code
        ))

    def test_arabic_no_obligation_conflicts_with_positive_obligation(self):
        hits = [{"text": "يلتزم صاحب العمل بتقديم إخطار مكتوب."}]
        self.assertTrue(has_unsupported_claims(
            "لا يلتزم صاحب العمل بتقديم إخطار مكتوب [1].",
            hits, tokens, norm, _mask_markdown_code
        ))

    def test_absence_of_obligation_is_not_confused_with_permission(self):
        self.assertFalse(_has_modal_mismatch(
            "The employee is not required to request leave.",
            "The employee may request leave.",
        ))
        self.assertFalse(_has_modal_mismatch(
            "لا يجب على العامل طلب الإجازة.",
            "يجوز للعامل طلب الإجازة.",
        ))

    def test_faithful_negative_modality_paraphrases_pass(self):
        english = [{"text": "The employer must not deduct wages."}]
        arabic = [{"text": "لا يحق لصاحب العمل خصم الأجر."}]
        self.assertFalse(has_unsupported_claims(
            "The employer must not deduct wages [1].",
            english, tokens, norm, _mask_markdown_code
        ))
        self.assertFalse(has_unsupported_claims(
            "لا يحق لصاحب العمل خصم الأجر [1].",
            arabic, tokens, norm, _mask_markdown_code
        ))

    def test_modality_comparison_does_not_mix_english_and_arabic(self):
        self.assertFalse(_has_modal_mismatch(
            "The employer must provide notice.",
            "يجب على صاحب العمل تقديم إخطار."
        ))
        self.assertFalse(_has_modal_mismatch(
            "The employee may request leave.",
            "يجوز للعامل طلب الإجازة."
        ))

    def test_faithful_permission_paraphrase_is_not_rejected(self):
        hits = [{"text": "The employee may request leave after six months."}]
        self.assertFalse(has_unsupported_claims(
            "The employee is permitted to request leave after six months [1].",
            hits, tokens, norm, _mask_markdown_code
        ))


    def test_fictional_60_sentence_claim_support_measurement(self):
        """Measure false passes/blocks on fictional claims with known labels."""
        groups = {
            "supported": (
                ("The filing period lasts five years [1].", "The fictional filing period is five years."),
                ("تبلغ مدة الإجراء الخيالي خمس سنوات [1].", "مدة الإجراء الخيالي خمس سنوات."),
                ("The request must be submitted within 30 days [1].", "The fictional request must be filed within 30 days."),
                ("يحق للعضو طلب تمديد واحد عقب ستة أشهر [1].", "يجوز للعضو طلب تمديد واحد بعد ستة أشهر."),
                ("The fee amounts to 10 units [1].", "The fictional fee is 10 units."),
                ("The applicant is permitted to request one extension [1].", "The applicant may request one extension."),
                ("The board always meets on the fifth day [1].", "The fictional board always meets on day 5."),
                ("Every registered member may use the fictional form [1].", "All registered members may use the fictional form."),
                ("The allowance goes up by 2 units [1].", "The fictional allowance increases by 2 units."),
                ("The form covers registered members [1].", "The fictional form includes registered members."),
                ("The notice is valid prior to day 10 [1].", "The fictional notice is valid before day 10."),
                ("لا يجوز للجهة رفض الطلب المستوفي للشروط [1].", "لا يجوز للجهة رفض الطلب المستوفي للشروط."),
            ),
            "unsupported_number": (
                ("The fictional limitation period is seven years [1].", "The fictional limitation period is five years."),
                ("The fictional filing window is 45 days [1].", "The fictional filing window is 30 days."),
                ("The fictional fee is 15 units [1].", "The fictional fee is 10 units."),
                ("The fictional rate is 15 percent [1].", "The fictional rate is 10 percent."),
                ("The fictional charge is EGP 1500 [1].", "The fictional charge is EGP 1000."),
                ("مدة الإجراء الخيالي 7 أيام [1].", "مدة الإجراء الخيالي 5 أيام."),
                ("مدة المراجعة الخيالية 6 أشهر [1].", "مدة المراجعة الخيالية 3 أشهر."),
                ("The fictional response window is 48 hours [1].", "The fictional response window is 24 hours."),
                ("The fictional review cycle is eight weeks [1].", "The fictional review cycle is four weeks."),
                ("The fictional permit lasts 18 months [1].", "The fictional permit lasts 12 months."),
                ("The fictional allowance is 25 units [1].", "The fictional allowance is 20 units."),
                ("The applicant may request two extensions [1].", "The applicant may request one extension."),
            ),
            "unsupported_qualitative": (
                ("The fictional permit is renewable forever for five years [1].", "The fictional permit is renewable for five years."),
                ("The board may always approve the request after review [1].", "The board may approve the request after review."),
                ("The fictional rule applies only to registered applicants before day 10 [1].", "The fictional rule applies to registered applicants before day 10."),
                ("All applicants may submit the fictional form before day 10 [1].", "Registered applicants may submit the fictional form before day 10."),
                ("The board never rejects a complete fictional request [1].", "The board may reject a complete fictional request."),
                ("The fictional permit is automatically renewed for five years [1].", "The fictional permit may be renewed for five years."),
                ("The fictional extension lasts five years after approval without limit [1].", "The fictional extension lasts five years after approval."),
                ("The fictional fee is always refundable on request [1].", "The fictional fee is refundable on request."),
                ("The fictional notice always takes effect on day 5 [1].", "The fictional notice may take effect on day 5."),
                ("The fictional board automatically approves each complete request [1].", "The fictional board approves complete requests."),
                ("يسري النموذج على كل الأعضاء المسجلين [1].", "يسري النموذج على الأعضاء المسجلين."),
                ("يجوز للمجلس دائما تمديد المدة بعد الإخطار [1].", "يجوز للمجلس تمديد المدة بعد الإخطار."),
            ),
            "reversed_meaning": (
                ("The fictional allowance decreases by 2 units [1].", "The fictional allowance increases by 2 units."),
                ("The fictional review happens after day 10 [1].", "The fictional review happens before day 10."),
                ("The fictional form excludes registered members [1].", "The fictional form includes registered members."),
                ("The fictional request is invalid [1].", "The fictional request is valid."),
                ("The fictional permit is non-renewable [1].", "The fictional permit is renewable."),
                ("The board rejects complete requests [1].", "The board accepts complete requests."),
                ("The fictional fee is not payable in advance [1].", "The fictional fee is payable in advance."),
                ("The minimum fictional period is 10 days [1].", "The maximum fictional period is 10 days."),
                ("تنقص القيمة الخيالية بمقدار وحدتين [1].", "تزيد القيمة الخيالية بمقدار وحدتين."),
                ("تتم المراجعة الخيالية بعد اليوم العاشر [1].", "تتم المراجعة الخيالية قبل اليوم العاشر."),
                ("يستثني النموذج الأعضاء المسجلين [1].", "يشمل النموذج الأعضاء المسجلين."),
                ("يرفض المجلس الطلب المستوفي [1].", "يقبل المجلس الطلب المستوفي."),
            ),
            "over_generalization": (
                ("Every applicant may request one extension after a valid notice [1].", "A registered applicant may request one extension after a valid notice."),
                ("The board always grants extensions when evidence is complete [1].", "The board may grant extensions when evidence is complete."),
                ("The fictional fee applies to all requests [1].", "The fictional fee applies to commercial requests."),
                ("Every member with any permit may use the fictional form [1].", "A member with an active permit may use the fictional form."),
                ("The rule applies to all requests [1].", "The rule applies to requests submitted online."),
                ("The board may extend the period in all cases [1].", "The board may extend the period in exceptional cases."),
                ("The fictional fee applies to every request [1].", "The fictional fee applies to commercial requests."),
                ("Any request may be reviewed by the board [1].", "A request filed before day 10 may be reviewed by the board."),
                ("يجوز لكل عضو طلب تمديد واحد بعد إخطار صحيح [1].", "يجوز للعضو المسجل طلب تمديد واحد بعد إخطار صحيح."),
                ("تطبق الرسوم على جميع الطلبات [1].", "تطبق الرسوم على الطلبات التجارية."),
                ("يجوز للمجلس تمديد المدة في كل الحالات [1].", "يجوز للمجلس تمديد المدة في حالات استثنائية."),
                ("يسري النموذج على كل الأعضاء [1].", "يسري النموذج على الأعضاء المسجلين."),
            ),
        }

        self.assertEqual(sum(len(items) for items in groups.values()), 60)
        false_passes = {}
        false_pass_examples = {}
        false_block_examples = []
        false_blocks = 0
        for category, examples in groups.items():
            blocked_count = 0
            for claim, evidence in examples:
                blocked = has_unsupported_claims(
                    claim, [{"text": evidence}], tokens, norm, _mask_markdown_code
                )
                if category == "supported":
                    false_blocks += int(blocked)
                    if blocked:
                        false_block_examples.append({"claim": claim, "evidence": evidence})
                else:
                    blocked_count += int(blocked)
                    if not blocked:
                        false_pass_examples.setdefault(category, []).append({"claim": claim, "evidence": evidence})
            if category != "supported":
                false_passes[category] = len(examples) - blocked_count

        false_pass_total = sum(false_passes.values())
        report = {
            "total": 60,
            "supported": {"n": 12, "false_blocks": false_blocks},
            "unsupported": {
                "n": 48, "false_passes": false_pass_total,
                "false_pass_rate": round(false_pass_total / 48, 4),
                "by_category": false_passes,
            },
            "false_block_rate": round(false_blocks / 12, 4),
            "false_block_examples": false_block_examples,
            "false_pass_examples": false_pass_examples,
        }
        print("FICTIONAL_CLAIM_SUPPORT_BENCHMARK=" + json.dumps(report, ensure_ascii=False, sort_keys=True))
        self.assertEqual(false_pass_total, 0, "unsupported fictional claim passed the support check")

if __name__ == "__main__":
    unittest.main()
