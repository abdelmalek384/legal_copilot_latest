import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.evaluate_legal_answers import EvaluationError, evaluate


def approved(qid="Q1", answerable=True):
    return {
        "id": qid,
        "practice_area": "civil_law",
        "question_ar": "سؤال قانوني",
        "expected_answer": "إجابة راجعها محامٍ.",
        "expected_sources": ["LAW-10"] if answerable else [],
        "expected_pin_cites": [{"source_id": "LAW-10", "pin_cite": "المادة 12"}] if answerable else [],
        "answerable": answerable,
        "must_abstain_if_unverified": not answerable,
        "review_status": "lawyer_approved",
        "reviewer_name": "Egyptian counsel",
        "review_date": "2026-10-26",
    }


def result(qid="Q1", abstained=False, sources=None, pins=None):
    return {
        "id": qid,
        "answer": "model output",
        "abstained": abstained,
        "cited_sources": ["LAW-10"] if sources is None and not abstained else (sources or []),
        "cited_pin_cites": ([{"source_id": "LAW-10", "pin_cite": "المادة 12"}]
                            if pins is None and not abstained else (pins or [])),
    }


class LegalAnswerEvaluationTests(unittest.TestCase):
    def test_scores_citation_recall_and_abstention_without_claiming_semantic_accuracy(self):
        report = evaluate([approved()], [result()])
        self.assertEqual(report["overall"]["source_recall"], 1.0)
        self.assertEqual(report["overall"]["pin_cite_recall"], 1.0)
        self.assertEqual(report["overall"]["abstention_accuracy"], 1.0)
        self.assertFalse(report["semantic_legal_correctness_scored"])
        self.assertEqual(report["unreviewed_questions_excluded"], 0)

    def test_unreviewed_drafts_are_excluded_and_never_scored(self):
        draft = dict(approved("DRAFT"))
        draft["review_status"] = "needs_lawyer_review"
        report = evaluate([approved(), draft], [result(), result("DRAFT")])
        self.assertEqual(report["questions_scored"], 1)
        self.assertEqual(report["excluded_question_ids"], ["DRAFT"])

    def test_refuses_to_score_when_every_question_is_unreviewed(self):
        draft = dict(approved())
        draft["review_status"] = "needs_lawyer_review"
        with self.assertRaisesRegex(EvaluationError, "no questions"):
            evaluate([draft], [result()])

    def test_refuses_approved_question_without_reviewer_or_pin_cites(self):
        q = dict(approved())
        q["reviewer_name"] = ""
        with self.assertRaisesRegex(EvaluationError, "reviewer_name"):
            evaluate([q], [result()])
        q = dict(approved())
        q["expected_pin_cites"] = []
        with self.assertRaisesRegex(EvaluationError, "expected pin citation"):
            evaluate([q], [result()])

    def test_review_date_requires_exact_iso_calendar_date(self):
        for value in ("20261026", "2026-1-2", "2026-W44-1", "2026-02-30"):
            with self.subTest(value=value):
                q = dict(approved())
                q["review_date"] = value
                with self.assertRaisesRegex(EvaluationError, "review_date"):
                    evaluate([q], [result()])

    def test_missing_results_and_unknown_results_are_errors(self):
        with self.assertRaisesRegex(EvaluationError, "missing results"):
            evaluate([approved()], [])
        with self.assertRaisesRegex(EvaluationError, "unknown question ids"):
            evaluate([approved()], [result(), result("NOT-IN-BENCHMARK")])

    def test_unanswerable_case_rewards_abstention(self):
        q = approved("Q-ABSTAIN", answerable=False)
        report = evaluate([q], [result("Q-ABSTAIN", abstained=True)])
        self.assertEqual(report["overall"]["unanswerable_abstention_recall"], 1.0)
        self.assertEqual(report["overall"]["abstention_accuracy"], 1.0)

    def test_rejects_duplicate_ids_and_malformed_result_citations(self):
        with self.assertRaisesRegex(EvaluationError, "duplicate question id"):
            evaluate([approved(), approved()], [result()])
        bad = result()
        bad["cited_pin_cites"] = [{"source_id": "LAW-10"}]
        with self.assertRaisesRegex(EvaluationError, "needs source_id and pin_cite"):
            evaluate([approved()], [bad])


if __name__ == "__main__":
    unittest.main()
