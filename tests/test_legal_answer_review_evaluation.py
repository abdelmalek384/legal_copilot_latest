import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.evaluate_legal_answer_reviews import DIMENSIONS, summarize_reviews, validate_review, validate_reviewer_registry


def review(**overrides):
    scores = {dimension: 2 for dimension in DIMENSIONS}
    rationales = {dimension: "Checked against the reviewed source passage." for dimension in DIMENSIONS}
    record = {
        "assessment_id": "ASSESS-001",
        "case_id": "CASE-001",
        "practice_area": "labour_law",
        "reviewer_id": "reviewer-a",
        "reviewer_name": "Qualified Reviewer A",
        "review_date": "2026-10-25",
        "disposition": "pass_for_this_case",
        "scores": scores,
        "rationales": rationales,
        "critical_defect": False,
    }
    record.update(overrides)
    return record


def reviewer_registry():
    return {"reviewers": [
        {
            "reviewer_id": "reviewer-a",
            "display_name": "Qualified Reviewer A",
            "status": "approved",
            "professional_role": "egyptian_lawyer",
            "jurisdiction": "Egypt",
            "practice_areas": ["labour_law", "civil_law"],
            "qualification_basis": "Synthetic test fixture: Egyptian-law qualification reviewed",
            "evidence_reference": "private-test-reference-A",
            "verified_by": "test-operator",
            "verified_on": "2026-10-25",
        },
        {
            "reviewer_id": "reviewer-b",
            "display_name": "Reviewer B",
            "status": "approved",
            "professional_role": "egyptian_lawyer",
            "jurisdiction": "Egypt",
            "practice_areas": ["labour_law", "civil_law"],
            "qualification_basis": "Synthetic test fixture: Egyptian-law qualification reviewed",
            "evidence_reference": "private-test-reference-B",
            "verified_by": "test-operator",
            "verified_on": "2026-10-25",
        },
    ]}


class LegalAnswerReviewEvaluationTests(unittest.TestCase):
    def test_cli_refuses_to_overwrite_existing_review_summary(self):
        with tempfile.TemporaryDirectory() as td:
            reviews_path = Path(td) / "reviews.jsonl"
            registry_path = Path(td) / "reviewers.json"
            output_path = Path(td) / "summary.json"
            reviews_path.write_text(json.dumps(review(), ensure_ascii=False) + "\n", encoding="utf-8")
            registry_path.write_text(json.dumps(reviewer_registry(), ensure_ascii=False), encoding="utf-8")
            original = "previous human-review summary\n"
            output_path.write_text(original, encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "evaluate_legal_answer_reviews.py"),
                    str(reviews_path),
                    "--reviewer-registry",
                    str(registry_path),
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertIn("evaluation refused: output already exists", completed.stderr)
            self.assertEqual(output_path.read_text(encoding="utf-8"), original)

    def test_unregistered_or_pending_reviewer_is_excluded(self):
        unregistered = review(reviewer_id="reviewer-unknown")
        pending_registry = reviewer_registry()
        pending_registry["reviewers"][0]["status"] = "pending"
        result = summarize_reviews([unregistered], pending_registry)
        self.assertEqual(result["valid_assessments"], 0)
        self.assertEqual(result["invalid_assessments_excluded"], 1)
        self.assertIn("approved reviewer registry", " ".join(result["invalid_records"][0]["errors"]))

    def test_reviewer_must_be_approved_for_assessment_practice_area(self):
        result = summarize_reviews([review(practice_area="criminal_law")], reviewer_registry())
        self.assertEqual(result["valid_assessments"], 0)
        self.assertIn("not approved for this practice_area", " ".join(result["invalid_records"][0]["errors"]))

    def test_reviewer_name_must_match_approved_registry(self):
        result = summarize_reviews([review(reviewer_name="Someone Else")], reviewer_registry())
        self.assertEqual(result["valid_assessments"], 0)
        self.assertIn("does not match", " ".join(result["invalid_records"][0]["errors"]))

    def test_duplicate_registry_ids_are_excluded(self):
        registry = reviewer_registry()
        registry["reviewers"].append(dict(registry["reviewers"][0]))
        approved, errors = validate_reviewer_registry(registry)
        self.assertNotIn("reviewer-a", approved)
        self.assertTrue(any("duplicate reviewer_id" in " ".join(item["errors"]) for item in errors))

    def test_registry_rejects_future_verification_date(self):
        registry = reviewer_registry()
        registry["reviewers"][0]["verified_on"] = "9999-12-31"
        approved, errors = validate_reviewer_registry(registry)
        self.assertNotIn("reviewer-a", approved)
        self.assertTrue(any("not in the future" in " ".join(item["errors"]) for item in errors))

    def test_valid_pass_is_summarized(self):
        result = summarize_reviews([review()], reviewer_registry())
        self.assertEqual(result["valid_assessments"], 1)
        self.assertEqual(result["disposition_counts"]["pass_for_this_case"], 1)
        self.assertEqual(result["dimension_summary"]["legal_correctness"]["mean_score_0_to_2"], 2.0)
        self.assertEqual(result["critical_defect_count"], 0)

    def test_insufficient_evidence_is_not_counted_as_a_pass_or_score(self):
        record = review(disposition="not_scored_insufficient_evidence")
        result = summarize_reviews([record], reviewer_registry())
        self.assertEqual(result["disposition_counts"]["pass_for_this_case"], 0)
        self.assertEqual(result["disposition_counts"]["not_scored_insufficient_evidence"], 1)
        self.assertEqual(result["dimension_summary"]["legal_correctness"]["scored_assessments"], 0)
        self.assertIsNone(result["dimension_summary"]["legal_correctness"]["mean_score_0_to_2"])

    def test_critical_defect_requires_unsafe_disposition_and_description(self):
        record = review(critical_defect=True, critical_defect_description="Invented article citation.")
        self.assertTrue(any("requires disposition=unsafe" in e for e in validate_review(record)))
        record["disposition"] = "unsafe"
        self.assertEqual(validate_review(record), [])
        result = summarize_reviews([record], reviewer_registry())
        self.assertEqual(result["critical_defect_count"], 1)
        self.assertEqual(result["disposition_counts"]["unsafe"], 1)

    def test_missing_rationale_invalidates_record(self):
        rationales = dict(review()["rationales"])
        rationales["temporal_correctness"] = " "
        result = summarize_reviews([review(rationales=rationales)], reviewer_registry())
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

    def test_duplicate_assessment_ids_are_excluded(self):
        first = review()
        second = review(case_id="CASE-002", reviewer_id="reviewer-b", reviewer_name="Reviewer B")
        result = summarize_reviews([first, second], reviewer_registry())
        self.assertEqual(result["valid_assessments"], 1)
        self.assertEqual(result["invalid_assessments_excluded"], 1)
        self.assertIn("duplicate assessment_id", " ".join(result["invalid_records"][0]["errors"]))

    def test_multiple_reviewers_can_review_same_case(self):
        first = review()
        second = review(assessment_id="ASSESS-002", reviewer_id="reviewer-b", reviewer_name="Reviewer B")
        result = summarize_reviews([first, second], reviewer_registry())
        self.assertEqual(result["valid_assessments"], 2)

    def test_malformed_disposition_does_not_crash(self):
        for value in ([], {}, 7, None):
            with self.subTest(disposition=value):
                errors = validate_review(review(disposition=value))
                self.assertTrue(any("disposition must be one" in error for error in errors))

    def test_review_date_must_be_a_real_iso_calendar_date(self):
        for value in ("2026-02-30", "26-10-25", "20261025", "not-a-date"):
            with self.subTest(review_date=value):
                errors = validate_review(review(review_date=value))
                self.assertTrue(any("review_date must be a real calendar date" in error for error in errors))
        self.assertEqual(validate_review(review(review_date="2026-10-25")), [])

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
