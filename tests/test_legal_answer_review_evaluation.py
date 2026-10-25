import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.evaluate_legal_answer_reviews import DIMENSIONS, summarize_reviews, validate_review


def review(**overrides):
    scores = {dimension: 2 for dimension in DIMENSIONS}
    rationales = {dimension: "Checked against the reviewed source passage." for dimension in DIMENSIONS}
    record = {
        "case_id": "CASE-001",
        "practice_area": "labour_law",
        "reviewer_name": "Qualified Reviewer A",
        "review_date": "2026-10-25",
        "disposition": "pass_for_this_case",
        "scores": scores,
        "rationales": rationales,
        "critical_defect": False,
    }
    record.update(overrides)
    return record


class LegalAnswerReviewEvaluationTests(unittest.TestCase):
    def test_valid_pass_is_summarized(self):
        result = summarize_reviews([review()])
        self.assertEqual(result["valid_assessments"], 1)
        self.assertEqual(result["disposition_counts"]["pass_for_this_case"], 1)
        self.assertEqual(result["dimension_summary"]["legal_correctness"]["mean_score_0_to_2"], 2.0)
        self.assertEqual(result["critical_defect_count"], 0)

    def test_insufficient_evidence_is_not_counted_as_a_pass_or_score(self):
        record = review(disposition="not_scored_insufficient_evidence")
        result = summarize_reviews([record])
        self.assertEqual(result["disposition_counts"]["pass_for_this_case"], 0)
        self.assertEqual(result["disposition_counts"]["not_scored_insufficient_evidence"], 1)
        self.assertEqual(result["dimension_summary"]["legal_correctness"]["scored_assessments"], 0)
        self.assertIsNone(result["dimension_summary"]["legal_correctness"]["mean_score_0_to_2"])

    def test_critical_defect_requires_unsafe_disposition_and_description(self):
        record = review(critical_defect=True, critical_defect_description="Invented article citation.")
        self.assertTrue(any("requires disposition=unsafe" in e for e in validate_review(record)))
        record["disposition"] = "unsafe"
        self.assertEqual(validate_review(record), [])
        result = summarize_reviews([record])
        self.assertEqual(result["critical_defect_count"], 1)
        self.assertEqual(result["disposition_counts"]["unsafe"], 1)

    def test_missing_rationale_invalidates_record(self):
        rationales = dict(review()["rationales"])
        rationales["temporal_correctness"] = " "
        result = summarize_reviews([review(rationales=rationales)])
        self.assertEqual(result["valid_assessments"], 0)
        self.assertEqual(result["invalid_assessments_excluded"], 1)
        self.assertIn("temporal_correctness requires", " ".join(result["invalid_records"][0]["errors"]))

    def test_not_applicable_requires_explanation(self):
        scores = dict(review()["scores"])
        rationales = dict(review()["rationales"])
        scores["temporal_correctness"] = "not_applicable"
        rationales["temporal_correctness"] = "No explanation supplied."
        self.assertTrue(any("must explain why" in e for e in validate_review(review(scores=scores, rationales=rationales))))
        rationales["temporal_correctness"] = "Not applicable because the case has no date-dependent issue."
        self.assertEqual(validate_review(review(scores=scores, rationales=rationales)), [])

    def test_duplicate_case_ids_are_excluded(self):
        result = summarize_reviews([review(), review()])
        self.assertEqual(result["valid_assessments"], 1)
        self.assertEqual(result["invalid_assessments_excluded"], 1)
        self.assertIn("duplicate case_id", " ".join(result["invalid_records"][0]["errors"]))

    def test_unknown_dimensions_are_rejected(self):
        scores = dict(review()["scores"])
        scores["overall_vibe"] = 2
        self.assertTrue(any("unknown score dimensions" in e for e in validate_review(review(scores=scores))))

    def test_boolean_is_not_accepted_as_numeric_score(self):
        scores = dict(review()["scores"])
        scores["legal_correctness"] = True
        self.assertTrue(any("legal_correctness must be 0, 1, 2" in e for e in validate_review(review(scores=scores))))


if __name__ == "__main__":
    unittest.main()
