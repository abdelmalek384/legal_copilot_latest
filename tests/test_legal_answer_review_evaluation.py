import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.evaluate_legal_answer_reviews import DIMENSIONS, main, summarize_reviews, validate_review, validate_reviewer_registry


def review(**overrides):
    scores = {dimension: 2 for dimension in DIMENSIONS}
    rationales = {dimension: "Checked against the reviewed source passage." for dimension in DIMENSIONS}
    record = {
        "review_schema_version": 2,
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
    def test_cli_summary_records_hashes_of_exact_input_bytes_without_paths(self):
        with tempfile.TemporaryDirectory() as td:
            reviews_path = Path(td) / "reviews.jsonl"
            registry_path = Path(td) / "reviewers.json"
            reviews_path.write_text(json.dumps(review(), ensure_ascii=False) + "\n", encoding="utf-8")
            registry_path.write_text(json.dumps(reviewer_registry(), ensure_ascii=False), encoding="utf-8")

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main([str(reviews_path), "--reviewer-registry", str(registry_path)])

            self.assertEqual(code, 0)
            report = json.loads(output.getvalue())
            provenance = report["provenance"]
            self.assertRegex(provenance["generated_at_utc"], r"^\d{4}-\d{2}-\d{2}T.*Z$")
            self.assertEqual(provenance["inputs"]["reviews"]["sha256"], hashlib.sha256(reviews_path.read_bytes()).hexdigest())
            self.assertEqual(provenance["inputs"]["reviewer_registry"]["sha256"], hashlib.sha256(registry_path.read_bytes()).hexdigest())
            self.assertEqual(provenance["inputs"]["reviews"]["size_bytes"], reviews_path.stat().st_size)
            self.assertNotIn(td, output.getvalue())

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
        record = review(critical_defect=True, critical_defect_categories=["incorrect_article_or_page_pin"], critical_defect_description="Invented article citation.")
        self.assertTrue(any("requires disposition=unsafe" in e for e in validate_review(record)))
        record["disposition"] = "unsafe"
        self.assertEqual(validate_review(record), [])
        result = summarize_reviews([record], reviewer_registry())
        self.assertEqual(result["critical_defect_count"], 1)
        self.assertEqual(result["disposition_counts"]["unsafe"], 1)
        self.assertEqual(result["critical_defect_category_counts"]["incorrect_article_or_page_pin"], 1)
        self.assertEqual(result["critical_defects"][0]["categories"], ["incorrect_article_or_page_pin"])


    def test_critical_defect_requires_a_documented_human_category(self):
        missing = review(
            disposition="unsafe",
            critical_defect=True,
            critical_defect_description="The cited sentence reverses a prohibition.",
        )
        self.assertTrue(any("review_schema_version=2 critical defects require at least one critical_defect_category" in error
                            for error in validate_review(missing)))

        categorized = dict(missing, critical_defect_categories=["contradicted_source_or_polarity"])
        self.assertEqual(validate_review(categorized), [])

    def test_defect_categories_reject_unknown_duplicate_and_noncritical_labels(self):
        base = review()
        for categories in (["made_up_category"], ["unsupported_legal_claim", "unsupported_legal_claim"], ["unsupported_legal_claim", 7]):
            with self.subTest(categories=categories):
                errors = validate_review(dict(base, critical_defect_categories=categories))
                self.assertTrue(any("unique documented category values" in error for error in errors))
        errors = validate_review(dict(base, critical_defect_categories=["missing_material_issue"]))
        self.assertTrue(any("only valid when critical_defect=true" in error for error in errors))

    def test_multiple_human_defect_categories_are_counted_without_inference(self):
        first = review(
            disposition="unsafe", critical_defect=True,
            critical_defect_categories=["unsupported_legal_claim", "wrong_legal_actor_or_role"],
            critical_defect_description="Synthetic reviewed defect fixture.",
        )
        second = review(
            assessment_id="ASSESS-002", reviewer_id="reviewer-b", reviewer_name="Reviewer B",
            disposition="unsafe", critical_defect=True,
            critical_defect_categories=["unsupported_legal_claim"],
            critical_defect_description="Second synthetic reviewed defect fixture.",
        )
        report = summarize_reviews([first, second], reviewer_registry())
        self.assertEqual(report["critical_defect_count"], 2)
        self.assertEqual(report["critical_defect_category_counts"]["unsupported_legal_claim"], 2)
        self.assertEqual(report["critical_defect_category_counts"]["wrong_legal_actor_or_role"], 1)
        self.assertEqual(report["critical_defect_category_counts"]["overbroad_conditional_scope"], 0)


    def test_same_case_repeat_is_not_misreported_as_cross_case_recurrence(self):
        first = review(
            disposition="unsafe", critical_defect=True,
            critical_defect_categories=["unsupported_legal_claim"],
            critical_defect_description="Synthetic first assessment.",
        )
        second = review(
            assessment_id="ASSESS-002", reviewer_id="reviewer-b", reviewer_name="Reviewer B",
            disposition="unsafe", critical_defect=True,
            critical_defect_categories=["unsupported_legal_claim"],
            critical_defect_description="Synthetic independent assessment of same case.",
        )
        report = summarize_reviews([first, second], reviewer_registry())
        item = report["critical_defect_category_analysis"][0]
        self.assertEqual(item["category"], "unsupported_legal_claim")
        self.assertEqual(item["assessment_count"], 2)
        self.assertEqual(item["distinct_case_count"], 1)
        self.assertEqual(item["distinct_reviewer_count"], 2)
        self.assertEqual(item["repeat_assessments_within_same_case"], 1)
        self.assertFalse(item["recurs_across_multiple_cases"])
        self.assertTrue(item["reported_by_multiple_reviewers"])
        self.assertEqual(report["recurring_critical_defect_categories"], [])

    def test_defect_recurrence_requires_distinct_cases_not_just_more_reviews(self):
        first = review(
            disposition="unsafe", critical_defect=True,
            critical_defect_categories=["incorrect_article_or_page_pin"],
            critical_defect_description="Synthetic defect in case one.",
        )
        second = review(
            assessment_id="ASSESS-002", case_id="CASE-002", reviewer_id="reviewer-b",
            reviewer_name="Reviewer B", disposition="unsafe", critical_defect=True,
            critical_defect_categories=["incorrect_article_or_page_pin"],
            critical_defect_description="Synthetic defect in case two.",
        )
        third = review(
            assessment_id="ASSESS-003", case_id="CASE-002", reviewer_id="reviewer-a",
            reviewer_name="Qualified Reviewer A", disposition="unsafe", critical_defect=True,
            critical_defect_categories=["incorrect_article_or_page_pin"],
            critical_defect_description="Second synthetic assessment in case two.",
        )
        report = summarize_reviews([first, second, third], reviewer_registry())
        item = next(x for x in report["critical_defect_category_analysis"]
                    if x["category"] == "incorrect_article_or_page_pin")
        self.assertEqual(item["assessment_count"], 3)
        self.assertEqual(item["distinct_case_count"], 2)
        self.assertEqual(item["distinct_reviewer_count"], 2)
        self.assertEqual(item["repeat_assessments_within_same_case"], 1)
        self.assertTrue(item["recurs_across_multiple_cases"])
        self.assertTrue(item["reported_by_multiple_reviewers"])
        self.assertEqual(report["recurring_critical_defect_categories"], ["incorrect_article_or_page_pin"])

    def test_legacy_uncategorized_defects_do_not_get_invented_recurrence_categories(self):
        legacy = review(
            review_schema_version=1, disposition="unsafe", critical_defect=True,
            critical_defect_description="Legacy defect without a taxonomy label.",
        )
        report = summarize_reviews([legacy], reviewer_registry())
        self.assertEqual(report["critical_defect_category_analysis"], [])
        self.assertEqual(report["recurring_critical_defect_categories"], [])

    def test_legacy_v1_unsafe_reviews_remain_readable_and_are_counted_as_uncategorized(self):
        legacy = review(
            disposition="unsafe",
            critical_defect=True,
            critical_defect_description="Legacy record predating the defect taxonomy.",
        )
        legacy["review_schema_version"] = 1
        report = summarize_reviews([legacy], reviewer_registry())
        self.assertEqual(report["valid_assessments"], 1)
        self.assertEqual(report["critical_defect_count"], 1)
        self.assertEqual(report["critical_defect_category_counts"]["uncategorized_legacy_v1"], 1)
        self.assertEqual(report["critical_defect_category_counts"]["unsupported_legal_claim"], 0)

    def test_unknown_review_schema_version_is_rejected(self):
        errors = validate_review(review(review_schema_version=3))
        self.assertTrue(any("review_schema_version must be 1 (legacy) or 2" in error for error in errors))

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
