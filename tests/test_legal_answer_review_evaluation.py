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
from tools.assemble_legal_answer_evaluation import AssemblyError, assemble, main as assemble_main


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



def machine_evaluation(results=None):
    return {
        "schema_version": 2,
        "results": results if results is not None else [
            {"id": "Q-001", "answer_id": "ans-001", "source_precision": 1.0,
             "pin_cite_precision": 0.5, "abstention_accuracy": 1.0},
        ],
    }


def linked_assessment(assessment_id, answer_id, reviewer_id, disposition="pass_for_this_case",
                      case_id="CASE-001", critical=False, categories=None, score=2):
    return {
        "assessment_id": assessment_id,
        "case_id": case_id,
        "answer_id": answer_id,
        "reviewer_id": reviewer_id,
        "disposition": disposition,
        "scores": {dimension: score for dimension in DIMENSIONS},
        "critical_defect": critical,
        "critical_defect_categories": categories or [],
    }


def human_evaluation(assessments):
    return {
        "schema_version": 2,
        "valid_assessments": len(assessments),
        "answer_assessments": assessments,
    }


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


    def test_review_report_exports_minimal_answer_assessment_linkage(self):
        record = review(answer_id="ans_synthetic_opaque_id")
        report = summarize_reviews([record], reviewer_registry())
        self.assertEqual(report["schema_version"], 2)
        self.assertEqual(len(report["answer_assessments"]), 1)
        assessment = report["answer_assessments"][0]
        self.assertEqual(assessment["answer_id"], "ans_synthetic_opaque_id")
        self.assertEqual(assessment["assessment_id"], record["assessment_id"])
        self.assertEqual(assessment["reviewer_id"], record["reviewer_id"])
        self.assertEqual(assessment["disposition"], record["disposition"])
        self.assertEqual(assessment["scores"], record["scores"])
        self.assertNotIn("reviewer_name", assessment)
        self.assertNotIn("rationales", assessment)
        self.assertNotIn("critical_defect_description", assessment)

    def test_invalid_reviews_are_not_exported_in_answer_assessment_linkage(self):
        good = review(answer_id="ans-good")
        bad = review(assessment_id="ASSESS-BAD", answer_id="ans-bad")
        bad["reviewer_id"] = "unregistered-reviewer"
        report = summarize_reviews([good, bad], reviewer_registry())
        self.assertEqual(report["valid_assessments"], 1)
        self.assertEqual(report["invalid_assessments_excluded"], 1)
        self.assertEqual([item["answer_id"] for item in report["answer_assessments"]], ["ans-good"])


    def test_assembler_links_machine_and_human_reviews_by_exact_answer_id(self):
        machine = machine_evaluation([
            {"id": "Q-001", "answer_id": "ans-001", "source_precision": 1.0},
            {"id": "Q-002", "answer_id": None, "source_precision": 0.5},
        ])
        human = human_evaluation([
            linked_assessment("A-001", "ans-001", "reviewer-a"),
            linked_assessment(
                "A-002", "ans-001", "reviewer-b", disposition="unsafe",
                critical=True, categories=["contradicted_source_or_polarity"], score=1,
            ),
            linked_assessment("A-003", "ans-orphan", "reviewer-a"),
            linked_assessment("A-004", None, "reviewer-b"),
        ])
        report = assemble(machine, human)
        self.assertEqual(report["counts"]["linked_answers"], 1)
        self.assertEqual(report["counts"]["machine_results_without_answer_id"], 1)
        self.assertEqual(report["counts"]["human_assessments_without_answer_id"], 1)
        self.assertEqual(report["counts"]["unmatched_human_answer_ids"], 1)
        self.assertEqual(report["counts"]["answers_requiring_adjudication"], 1)
        self.assertEqual(report["counts"]["answers_with_critical_defects"], 1)
        self.assertEqual(report["answer_id_linkage_coverage"], 1.0)
        linked = report["results"][0]
        self.assertEqual(linked["human_review_status"], "linked")
        self.assertFalse(linked["human_review"]["disposition_agreement"])
        self.assertTrue(linked["human_review"]["insufficient_evidence_conflict"] is False)
        self.assertEqual(
            linked["human_review"]["critical_defect_category_counts"],
            {"contradicted_source_or_polarity": 1},
        )
        self.assertTrue(linked["human_review"]["requires_follow_up"])
        self.assertEqual(report["results"][1]["human_review_status"], "missing_answer_id")

    def test_assembler_separates_insufficient_evidence_conflicts(self):
        human = human_evaluation([
            linked_assessment("A-001", "ans-001", "reviewer-a"),
            linked_assessment(
                "A-002", "ans-001", "reviewer-b",
                disposition="not_scored_insufficient_evidence",
            ),
        ])
        report = assemble(machine_evaluation(), human)
        review = report["results"][0]["human_review"]
        self.assertTrue(review["insufficient_evidence_conflict"])
        self.assertTrue(review["requires_adjudication"])

    def test_assembler_does_not_join_answer_id_reused_across_cases(self):
        human = human_evaluation([
            linked_assessment("A-001", "ans-001", "reviewer-a", case_id="CASE-001"),
            linked_assessment("A-002", "ans-001", "reviewer-b", case_id="CASE-002"),
        ])
        report = assemble(machine_evaluation(), human)
        self.assertEqual(report["counts"]["linked_answers"], 0)
        self.assertEqual(report["counts"]["ambiguous_cross_case_answer_ids"], 1)
        self.assertEqual(report["results"][0]["human_review_status"], "ambiguous_cross_case_answer_id")
        self.assertIsNone(report["results"][0]["human_review"].get("dispositions"))

    def test_assembler_rejects_unsupported_schemas_duplicate_ids_and_duplicate_reviewers(self):
        with self.assertRaisesRegex(AssemblyError, "machine report must use schema_version=2"):
            assemble({"schema_version": 1, "results": []}, human_evaluation([]))
        with self.assertRaisesRegex(AssemblyError, "human review report must use schema_version=2"):
            assemble(machine_evaluation(), {"schema_version": 1, "answer_assessments": [], "valid_assessments": 0})
        duplicate_machine = machine_evaluation([
            {"id": "Q-001", "answer_id": "ans-dup"},
            {"id": "Q-002", "answer_id": "ans-dup"},
        ])
        with self.assertRaisesRegex(AssemblyError, "duplicate machine answer_id"):
            assemble(duplicate_machine, human_evaluation([]))
        duplicate_reviewer = human_evaluation([
            linked_assessment("A-001", "ans-001", "reviewer-a"),
            linked_assessment("A-002", "ans-001", "reviewer-a"),
        ])
        with self.assertRaisesRegex(AssemblyError, "duplicate reviewer assessment"):
            assemble(machine_evaluation(), duplicate_reviewer)

    def test_assembler_rejects_mismatched_human_assessment_count_and_empty_answer_id(self):
        bad_count = {"schema_version": 2, "valid_assessments": 2, "answer_assessments": []}
        with self.assertRaisesRegex(AssemblyError, "valid_assessments does not match"):
            assemble(machine_evaluation(), bad_count)
        bad_id = human_evaluation([linked_assessment("A-001", "   ", "reviewer-a")])
        with self.assertRaisesRegex(AssemblyError, "answer_id must be non-empty"):
            assemble(machine_evaluation(), bad_id)

    def test_assembler_cli_records_input_hashes_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as td:
            machine_path = Path(td) / "machine.json"
            human_path = Path(td) / "human.json"
            output_path = Path(td) / "combined.json"
            machine_bytes = json.dumps(machine_evaluation(), ensure_ascii=False).encode("utf-8")
            human_bytes = json.dumps(
                human_evaluation([linked_assessment("A-001", "ans-001", "reviewer-a")]),
                ensure_ascii=False,
            ).encode("utf-8")
            machine_path.write_bytes(machine_bytes)
            human_path.write_bytes(human_bytes)
            args = [
                "--machine-report", str(machine_path),
                "--human-review-report", str(human_path),
                "--out", str(output_path),
            ]
            self.assertEqual(assemble_main(args), 0)
            rendered = output_path.read_text(encoding="utf-8")
            report = json.loads(rendered)
            self.assertEqual(
                report["provenance"]["inputs"]["machine_report"]["sha256"],
                hashlib.sha256(machine_bytes).hexdigest(),
            )
            self.assertEqual(
                report["provenance"]["inputs"]["human_review_report"]["sha256"],
                hashlib.sha256(human_bytes).hexdigest(),
            )
            self.assertNotIn(td, rendered)
            self.assertEqual(assemble_main(args), 2)
            self.assertEqual(output_path.read_text(encoding="utf-8"), rendered)

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
