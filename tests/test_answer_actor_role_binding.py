"""Conservative tests for cited legal actor/role substitution."""
import unittest
from unittest.mock import patch
import app


class CitedActorRoleBindingTests(unittest.TestCase):
    def test_opposite_actor_with_same_legal_action_is_rejected_for_each_role_pair(self):
        for source_actor, answer_actor in app._LEGAL_ACTOR_ROLE_PAIRS:
            with self.subTest(source_actor=source_actor, answer_actor=answer_actor):
                source = {"text": f"يجوز لـ{source_actor} طلب التعويض عن الضرر."}
                answer = f"يجوز لـ{answer_actor} طلب التعويض عن الضرر [1]."
                self.assertTrue(app._answer_has_cited_actor_role_mismatch(answer, [source]))

    def test_husband_phrase_does_not_match_inside_wife_phrase(self):
        hits = [{"text": "يجوز للزوجة طلب فسخ عقد الزواج والتعويض عن الضرر."}]
        self.assertTrue(app._answer_has_cited_actor_role_mismatch(
            "يجوز للزوج طلب فسخ عقد الزواج والتعويض عن الضرر [1].", hits
        ))
    def test_same_actor_and_same_action_pass(self):
        hits = [{"text": "يجوز لصاحب العمل إنهاء العقد في الحالة المحددة."}]
        self.assertFalse(app._answer_has_cited_actor_role_mismatch(
            "يجوز لصاحب العمل إنهاء العقد في الحالة المحددة [1].", hits
        ))

    def test_source_that_discusses_both_roles_is_ambiguous_and_passes(self):
        hits = [{"text": "يجوز لصاحب العمل إنهاء العقد، ويجوز للعامل طلب التعويض."}]
        self.assertFalse(app._answer_has_cited_actor_role_mismatch(
            "يجوز للعامل إنهاء العقد [1].", hits
        ))

    def test_opposite_role_without_shared_action_does_not_trigger(self):
        hits = [{"text": "يجوز لصاحب العمل إنهاء العقد."}]
        self.assertFalse(app._answer_has_cited_actor_role_mismatch(
            "يجوز للعامل طلب إجازة سنوية [1].", hits
        ))

    def test_uncited_or_code_only_role_swap_is_ignored_by_this_guard(self):
        hits = [{"text": "يجوز لصاحب العمل إنهاء العقد."}]
        self.assertFalse(app._answer_has_cited_actor_role_mismatch(
            "```text\nيجوز للعامل إنهاء العقد [1].\n```", hits
        ))

    def test_invalid_citation_index_fails_closed(self):
        hits = [{"text": "يجوز لصاحب العمل إنهاء العقد."}]
        self.assertTrue(app._answer_has_cited_actor_role_mismatch(
            "يجوز للعامل إنهاء العقد [2].", hits
        ))

    def test_ask_abstains_when_answer_assigns_employer_action_to_worker(self):
        hit = {
            "cos": 1.0, "score": 1, "ref": "SYNTHETIC-ACTOR",
            "text": "يجوز لصاحب العمل إنهاء العقد في الحالة المحددة.",
            "verified": True, "in_force": True, "applies_as_of": True,
            "case_id": None, "source_status": app.STATUS_VERIFIED, "provenance": {},
        }
        with patch.object(app, "search", return_value=[hit]), patch.object(
            app, "LLM", return_value="يجوز للعامل إنهاء العقد في الحالة المحددة [1]."
        ):
            result = app.ask(None, "من يجوز له إنهاء العقد؟", scope="verified_corpus")
        self.assertIsNone(result["answer"])
        self.assertTrue(result["abstained"])
        self.assertIn("طرف قانوني مختلف", result["message"])


if __name__ == "__main__":
    unittest.main()