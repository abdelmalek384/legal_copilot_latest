import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.evaluate_retrieval_quality import DEFAULT_QUESTIONS, _load_jsonl, _write_report, main, score_evaluation as _score_evaluation, validate_reviewed_question
from tools.answer_trust_tier import (
    TIER_SOURCE_MATCHED, TIER_UNREVIEWED, TIER_VERIFIED, classify_answer_trust_tier,
)


def reviewed_question(**overrides):
    question = {
        "id": "Q-TEST-001",
        "practice_area": "civil_law",
        "question_ar": "سؤال اختباري لا يمثل استشارة قانونية",
        "review_status": "lawyer_reviewed",
        "reviewer_id": "reviewer-a",
        "reviewer_name": "Reviewer A",
        "reviewer_role": "qualified_egyptian_counsel",
        "review_evidence_url": "https://example.gov/review-record",
        "review_date": "2026-10-24",
        "expected_source_ids": ["LAW-A", "LAW-B"],
        "expected_pin_cites": [
            {"source_id": "LAW-A", "pin_cite": "Article 12"},
        ],
        "answerable": True,
        "must_abstain_if_unverified": True,
    }
    question.update(overrides)
    return question


def reviewer_registry():
    return {"reviewers": [{
        "reviewer_id": "reviewer-a",
        "display_name": "Reviewer A",
        "status": "approved",
        "professional_role": "qualified_egyptian_counsel",
        "jurisdiction": "Egypt",
        "practice_areas": ["civil_law"],
        "qualification_basis": "Synthetic test fixture only",
        "evidence_reference": "private-test-reference",
        "verified_by": "test-operator",
        "verified_on": "2026-10-24",
    }]}


def score_evaluation(questions, runs, k_values=(1, 3, 5)):
    return _score_evaluation(questions, runs, k_values, reviewer_registry=reviewer_registry())


def run_main(args, registry=None):
    with tempfile.TemporaryDirectory() as td:
        registry_path = Path(td) / "reviewers.json"
        registry_path.write_text(json.dumps(registry or reviewer_registry()), encoding="utf-8")
        return main([*args, "--reviewer-registry", str(registry_path)])


class RetrievalEvaluationTests(unittest.TestCase):
    def test_report_writer_creates_new_file_and_never_overwrites_existing_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            report = Path(td) / "evaluation-report.json"
            _write_report(report, "first report\n")
            self.assertEqual(report.read_text(encoding="utf-8"), "first report\n")
            with self.assertRaises(FileExistsError):
                _write_report(report, "replacement report\n")
            self.assertEqual(report.read_text(encoding="utf-8"), "first report\n")

    def test_unreviewed_seed_questions_are_excluded_not_scored(self):
        seeds = _load_jsonl(DEFAULT_QUESTIONS)
        result = score_evaluation(seeds, [])
        self.assertEqual(result["reviewed_cases_scored"], 0)
        self.assertEqual(len(result["excluded_cases"]), len(seeds))
        self.assertIsNone(result["metrics"]["recall_at_5"])
        self.assertIsNone(result["citation_precision"])
        self.assertTrue(all("not marked" in " ".join(x["reasons"]) for x in result["excluded_cases"]))

    def test_egyptian_colloquial_seed_questions_remain_excluded_until_lawyer_review(self):
        seeds = _load_jsonl(DEFAULT_QUESTIONS)
        dialect = [item for item in seeds if item.get("id", "").startswith("Q-EG-DIALECT-")]
        self.assertEqual(len(dialect), 10)
        self.assertTrue(all(item["review_status"] == "needs_lawyer_review" for item in dialect))
        self.assertTrue(all(item["expected_sources"] == [] for item in dialect))
        result = score_evaluation(dialect, [])
        self.assertEqual(result["reviewed_cases_scored"], 0)
        self.assertEqual(len(result["excluded_cases"]), 10)

    def test_all_unreviewed_multi_area_questions_require_abstention_without_verified_sources(self):
        path = ROOT / "tests" / "legal_eval" / "multi_area_questions.draft.jsonl"
        questions = _load_jsonl(path)
        self.assertEqual(len(questions), 94)
        self.assertTrue(all(q["review_status"] == "needs_lawyer_review" for q in questions))
        self.assertTrue(all(q["must_abstain_if_unverified"] is True for q in questions))
        out_of_scope = [q for q in questions if q.get("question_type") == "يجب الامتناع/خارج النطاق"]
        self.assertEqual(len(out_of_scope), 7)
        self.assertTrue(all(q["answerable"] is None and q["expected_sources"] == [] for q in questions))

    def test_all_unreviewed_legal_question_sets_default_to_abstention(self):
        paths = (
            ROOT / "tests" / "legal_eval" / "practice_questions.seed.jsonl",
            ROOT / "tests" / "legal_eval" / "multi_area_questions.draft.jsonl",
            ROOT / "tests" / "legal_eval" / "labour_law_questions.draft.jsonl",
            ROOT / "tests" / "legal_eval" / "labour_law_14_2025_provisional_review_questions.draft.jsonl",
        )
        total = 0
        for path in paths:
            questions = _load_jsonl(path)
            unreviewed = [q for q in questions if q.get("review_status") == "needs_lawyer_review"]
            total += len(unreviewed)
            with self.subTest(path=path.name):
                self.assertTrue(all(q.get("must_abstain_if_unverified") is True for q in unreviewed))
        self.assertEqual(total, 251)

    def test_seed_schema_expected_sources_alias_is_supported_after_review(self):
        question = reviewed_question()
        question["expected_sources"] = question.pop("expected_source_ids")
        run = {
            "question_id": question["id"],
            "retrieved_source_ids": ["LAW-A", "LAW-B"],
            "citations": [{"source_id": "LAW-A", "pin_cite": "Article 12"}],
            "abstained": False,
            "used_unverified_source": False,
        }
        result = score_evaluation([question], [run])
        self.assertEqual(result["reviewed_cases_scored"], 1)
        self.assertEqual(result["metrics"]["recall_at_5"], 1.0)

    def test_duplicate_or_whitespace_padded_expected_source_ids_are_excluded(self):
        cases = (
            (["LAW-A", "LAW-A"], "duplicates"),
            ([" LAW-A", "LAW-B"], "surrounding whitespace"),
        )
        for expected_ids, reason in cases:
            with self.subTest(expected_ids=expected_ids):
                result = score_evaluation(
                    [reviewed_question(expected_source_ids=expected_ids)], []
                )
                self.assertEqual(result["reviewed_cases_scored"], 0)
                self.assertIn(reason, " ".join(result["excluded_cases"][0]["reasons"]))

    def test_duplicate_or_whitespace_padded_ranked_source_ids_are_invalid_runs(self):
        cases = (
            (["LAW-A", "LAW-A"], "duplicate source IDs"),
            (["LAW-A", " LAW-B"], "surrounding whitespace"),
        )
        for ranked_ids, reason in cases:
            with self.subTest(ranked_ids=ranked_ids):
                run = {
                    "question_id": "Q-TEST-001",
                    "retrieved_source_ids": ranked_ids,
                    "citations": [],
                    "abstained": False,
                    "used_unverified_source": False,
                }
                result = score_evaluation([reviewed_question()], [run])
                self.assertEqual(result["reviewed_cases_scored"], 0)
                self.assertIn(reason, " ".join(result["invalid_run_records"][0]["reasons"]))

    def test_reviewed_pin_cites_must_be_unique_trimmed_and_reference_expected_sources(self):
        cases = (
            ([{"source_id": "LAW-X", "pin_cite": "Article 12"}], "absent from expected_source_ids"),
            ([{"source_id": "LAW-A", "pin_cite": "Article 12"},
              {"source_id": "LAW-A", "pin_cite": "Article 12"}], "duplicate source/pin-cite"),
            ([{"source_id": " LAW-A", "pin_cite": "Article 12"}], "surrounding whitespace"),
            ([{"source_id": "LAW-A", "pin_cite": " Article 12 "}], "surrounding whitespace"),
        )
        for pin_cites, reason in cases:
            with self.subTest(pin_cites=pin_cites):
                result = score_evaluation(
                    [reviewed_question(expected_pin_cites=pin_cites)], []
                )
                self.assertEqual(result["reviewed_cases_scored"], 0)
                self.assertIn(reason, " ".join(result["excluded_cases"][0]["reasons"]))

    def test_run_citation_and_source_summary_ids_reject_surrounding_whitespace(self):
        base = {
            "question_id": "Q-TEST-001",
            "retrieved_source_ids": ["LAW-A", "LAW-B"],
            "citations": [{"source_id": "LAW-A", "pin_cite": "Article 12"}],
            "source_summary": [
                {"source_id": "LAW-A", "source_status": "verified_operative_text"},
                {"source_id": "LAW-B", "source_status": "verified_operative_text"},
            ],
            "abstained": False,
            "used_unverified_source": False,
        }
        cases = (
            ({"citations": [{"source_id": " LAW-A", "pin_cite": "Article 12"}]}, "citations[0].source_id"),
            ({"citations": [{"source_id": "LAW-A", "pin_cite": " Article 12"}]}, "citations[0].pin_cite"),
            ({"source_summary": [
                {"source_id": " LAW-A", "source_status": "verified_operative_text"},
                {"source_id": "LAW-B", "source_status": "verified_operative_text"},
            ]}, "source_summary[0].source_id"),
        )
        for overrides, reason in cases:
            with self.subTest(overrides=overrides):
                run = dict(base, **overrides)
                result = score_evaluation([reviewed_question()], [run])
                self.assertEqual(result["reviewed_cases_scored"], 0)
                self.assertIn(reason, " ".join(result["invalid_run_records"][0]["reasons"]))

    def test_duplicate_retrieval_cutoffs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "k_values must not contain duplicates"):
            _score_evaluation(
                [reviewed_question()], [], k_values=(1, 3, 3),
                reviewer_registry=reviewer_registry(),
            )

    def test_conflicting_expected_source_aliases_are_excluded(self):
        question = reviewed_question(expected_sources=["LAW-X"])
        result = score_evaluation([question], [])
        self.assertEqual(result["reviewed_cases_scored"], 0)
        self.assertIn("conflict", " ".join(result["excluded_cases"][0]["reasons"]))

    def test_recall_mrr_citation_and_pin_cite_metrics(self):
        question = reviewed_question()
        run = {
            "question_id": "Q-TEST-001",
            "retrieved_source_ids": ["IRRELEVANT", "LAW-A", "LAW-B"],
            "citations": [
                {"source_id": "LAW-A", "pin_cite": "Article 12"},
                {"source_id": "LAW-X", "pin_cite": "Article 99"},
            ],
            "source_summary": [
                {"source_id": "IRRELEVANT", "source_status": "verified_operative_text"},
                {"source_id": "LAW-A", "source_status": "verified_operative_text"},
                {"source_id": "LAW-B", "source_status": "verified_operative_text"},
                {"source_id": "LAW-X", "source_status": "verified_operative_text"},
            ],
            "abstained": False,
            "used_unverified_source": False,
        }
        result = score_evaluation([question], [run], k_values=(1, 3, 5))
        self.assertEqual(result["reviewed_cases_scored"], 1)
        self.assertEqual(result["metrics"]["recall_at_1"], 0.0)
        self.assertEqual(result["metrics"]["recall_at_3"], 1.0)
        self.assertEqual(result["metrics"]["mrr_at_3"], 0.5)
        self.assertEqual(result["citation_precision"], 0.5)
        self.assertEqual(result["pin_cite_accuracy"], 0.5)
        self.assertEqual(result["citation_coverage"], 1.0)
        self.assertEqual(result["expected_pin_cite_recall"], 1.0)
        self.assertEqual(result["unsafe_unverified_source_uses"], 0)

    def test_invalid_citation_indices_reduce_precision(self):
        question = reviewed_question()
        run = {
            "question_id": question["id"],
            "retrieved_source_ids": ["LAW-A", "LAW-B"],
            "citations": [{"source_id": "LAW-A", "pin_cite": "Article 12"}],
            "invalid_citation_indices": [9],
            "abstained": False,
            "used_unverified_source": False,
        }

        result = score_evaluation([question], [run])

        self.assertEqual(result["citation_precision"], 0.5)
        self.assertEqual(result["citation_count"], 2)
        self.assertEqual(result["source_citation_count"], 1)
        self.assertEqual(result["invalid_citation_index_count"], 1)
        self.assertEqual(
            result["invalid_citation_index_records"],
            [{"question_id": question["id"], "indices": [9]}],
        )

    def test_invalid_citation_index_schema_is_rejected(self):
        question = reviewed_question()
        run = {
            "question_id": question["id"],
            "retrieved_source_ids": ["LAW-A"],
            "citations": [{"source_id": "LAW-A"}],
            "invalid_citation_indices": [1, True],
            "abstained": False,
            "used_unverified_source": False,
        }
        result = score_evaluation([question], [run])
        self.assertEqual(result["reviewed_cases_scored"], 0)
        self.assertIn("invalid_citation_indices", " ".join(result["invalid_run_records"][0]["reasons"]))

    def test_citations_to_sources_not_retrieved_do_not_count_as_supported(self):
        question = reviewed_question()
        run = {
            "question_id": question["id"],
            "retrieved_source_ids": ["LAW-B"],
            "citations": [{"source_id": "LAW-A", "pin_cite": "Article 12"}],
            "abstained": False,
            "used_unverified_source": False,
        }

        result = score_evaluation([question], [run])

        self.assertEqual(result["citation_precision"], 0.0)
        self.assertEqual(result["citation_coverage"], 0.0)
        self.assertEqual(result["pin_cite_accuracy"], 0.0)
        self.assertEqual(result["expected_pin_cite_recall"], 0.0)
        self.assertEqual(result["citations_outside_retrieval_count"], 1)
        self.assertEqual(
            result["citations_outside_retrieval"],
            [{"question_id": question["id"], "source_id": "LAW-A", "pin_cite": "Article 12"}],
        )

    def test_source_summary_must_cover_every_ranked_candidate_when_supplied(self):
        question = reviewed_question()
        run = {
            "question_id": question["id"],
            "retrieved_source_ids": ["LAW-A", "LAW-B"],
            "citations": [],
            "source_summary": [{"source_id": "LAW-A", "source_status": "verified_operative_text"}],
            "abstained": False,
            "used_unverified_source": False,
        }
        result = score_evaluation([question], [run])
        self.assertEqual(result["reviewed_cases_scored"], 0)
        self.assertIn("missing retrieved source IDs", " ".join(result["invalid_run_records"][0]["reasons"]))

    def test_duplicate_source_summary_ids_are_rejected_even_when_status_matches(self):
        question = reviewed_question()
        run = {
            "question_id": question["id"],
            "retrieved_source_ids": ["LAW-A"],
            "citations": [],
            "source_summary": [
                {"source_id": "LAW-A", "source_status": "verified_operative_text"},
                {"source_id": "LAW-A", "source_status": "verified_operative_text"},
            ],
            "abstained": False,
            "used_unverified_source": False,
        }
        result = score_evaluation([question], [run])
        self.assertEqual(result["reviewed_cases_scored"], 0)
        self.assertIn("duplicate source IDs", " ".join(result["invalid_run_records"][0]["reasons"]))

    def test_source_summary_cannot_contradict_unverified_source_flag(self):
        question = reviewed_question()
        run = {
            "question_id": question["id"],
            "retrieved_source_ids": ["LAW-A"],
            "citations": [{"source_id": "LAW-A"}],
            "source_summary": [{"source_id": "LAW-A", "source_status": "outdated_or_under_review"}],
            "abstained": False,
            "used_unverified_source": False,
        }
        result = score_evaluation([question], [run])
        self.assertEqual(result["reviewed_cases_scored"], 0)
        self.assertIn("not verified", " ".join(result["invalid_run_records"][0]["reasons"]))

    def test_cited_source_without_status_evidence_fails_closed(self):
        question = reviewed_question()
        run = {
            "question_id": question["id"],
            "retrieved_source_ids": ["LAW-A"],
            "citations": [{"source_id": "LAW-A"}],
            "abstained": False,
            "used_unverified_source": False,
        }
        result = score_evaluation([question], [run])
        self.assertEqual(result["source_status_evidence_missing_count"], 1)
        self.assertEqual(result["unsafe_unverified_source_uses"], 1)

    def test_retrieval_labels_require_approved_registry_identity_and_scope(self):
        cases = (
            ({"reviewer_id": "not-registered"}, "approved reviewer registry"),
            ({"reviewer_name": "Unmatched name"}, "display_name"),
            ({"practice_area": "criminal_law"}, "not approved for this practice_area"),
            ({"reviewer_role": "administrator"}, "registry role"),
            ({"review_evidence_url": "http://example.gov/review"}, "HTTPS"),
            ({"review_evidence_url": "https://user:pass@example.gov/review"}, "HTTPS"),
            ({"review_evidence_url": "https://example.gov/review?token=secret"}, "HTTPS"),
            ({"review_evidence_url": "https://example.gov/review#private"}, "HTTPS"),
            ({"review_evidence_url": "https://example.gov:/review"}, "HTTPS"),
            ({"review_evidence_url": "https://example.gov/review\x00"}, "HTTPS"),
            ({"review_evidence_url": "https://example.gov/review\x7f"}, "HTTPS"),
            ({"review_date": "2999-01-01"}, "real YYYY-MM-DD"),
        )
        for overrides, expected_error in cases:
            with self.subTest(overrides=overrides):
                question = reviewed_question(**overrides)
                result = score_evaluation([question], [])
                self.assertEqual(result["reviewed_cases_scored"], 0)
                self.assertIn(expected_error, " ".join(result["excluded_cases"][0]["reasons"]))

    def test_retrieval_evaluator_rejects_malformed_reviewer_registry(self):
        question = reviewed_question()
        bad_registry = {"reviewers": [{
            "reviewer_id": "reviewer-a",
            "display_name": "Reviewer A",
            "status": "approved",
            "professional_role": "administrator",
            "jurisdiction": "Egypt",
            "practice_areas": ["civil_law"],
            "qualification_basis": "test",
            "evidence_reference": "test",
            "verified_by": "test",
            "verified_on": "2026-10-24",
        }]}
        with self.assertRaisesRegex(ValueError, "reviewer registry is invalid"):
            _score_evaluation([question], [], reviewer_registry=bad_registry)

    def test_unanswerable_case_requires_abstention(self):
        question = reviewed_question(
            id="Q-TEST-002",
            expected_source_ids=["LAW-A"],
            expected_pin_cites=[],
            answerable=False,
        )
        compliant = {
            "question_id": "Q-TEST-002",
            "retrieved_source_ids": [],
            "citations": [],
            "abstained": True,
            "used_unverified_source": False,
        }
        result = score_evaluation([question], [compliant])
        self.assertEqual(result["abstention_compliance"], 1.0)
        unsafe = dict(compliant, abstained=False, used_unverified_source=True)
        result = score_evaluation([question], [unsafe])
        self.assertEqual(result["abstention_compliance"], 0.0)
        self.assertEqual(result["unsafe_unverified_source_uses"], 1)

    def test_invalid_reviewed_labels_are_excluded(self):
        question = reviewed_question(expected_source_ids=[], reviewer_name=None)
        result = score_evaluation([question], [{"question_id": question["id"]}])
        self.assertEqual(result["reviewed_cases_scored"], 0)
        reasons = " ".join(result["excluded_cases"][0]["reasons"])
        self.assertIn("expected_source_ids", reasons)
        self.assertIn("reviewer_name", reasons)

    def test_duplicate_run_records_are_reported(self):
        question = reviewed_question()
        run = {
            "question_id": question["id"], "retrieved_source_ids": [], "citations": [],
            "abstained": False, "used_unverified_source": False,
        }
        result = score_evaluation([question], [run, run])
        self.assertEqual(result["duplicate_run_question_ids"], [question["id"]])

    def test_malformed_question_shapes_and_dates_are_excluded_without_crashing(self):
        question = reviewed_question(review_date="2026-02-30")
        result = score_evaluation([None, ["not", "an", "object"], question], [])
        self.assertEqual(result["reviewed_cases_scored"], 0)
        self.assertEqual(len(result["invalid_question_records"]), 3)
        reasons = " ".join(result["excluded_cases"][0]["reasons"])
        self.assertIn("real YYYY-MM-DD", reasons)
        self.assertIsNone(result["metrics"]["recall_at_5"])

    def test_malformed_run_shapes_and_citations_are_reported_and_excluded(self):
        question = reviewed_question()
        malformed = {
            "question_id": question["id"],
            "retrieved_source_ids": "LAW-A",
            "citations": [None],
            "abstained": "false",
            "used_unverified_source": False,
        }
        result = score_evaluation([question], [None, malformed])
        self.assertEqual(result["reviewed_cases_scored"], 0)
        self.assertEqual(len(result["invalid_run_records"]), 2)
        self.assertIn("run record is malformed", result["excluded_cases"][0]["reasons"][0])

    def test_duplicate_run_records_are_excluded_not_arbitrarily_scored(self):
        question = reviewed_question()
        run = {
            "question_id": question["id"], "retrieved_source_ids": ["LAW-A"], "citations": [],
            "abstained": False, "used_unverified_source": False,
        }
        result = score_evaluation([question], [run, run])
        self.assertEqual(result["reviewed_cases_scored"], 0)
        self.assertEqual(result["duplicate_run_question_ids"], [question["id"]])
        self.assertIn("duplicate run records", result["excluded_cases"][0]["reasons"][0])

    def test_duplicate_question_ids_are_excluded(self):
        question = reviewed_question()
        run = {
            "question_id": question["id"], "retrieved_source_ids": ["LAW-A"], "citations": [],
            "abstained": False, "used_unverified_source": False,
        }
        result = score_evaluation([question, dict(question)], [run])
        self.assertEqual(result["reviewed_cases_scored"], 0)
        self.assertEqual(result["duplicate_question_ids"], [question["id"]])
        self.assertIn("duplicate question ID", result["excluded_cases"][0]["reasons"][0])

    def test_invalid_pin_cite_labels_are_excluded(self):
        question = reviewed_question(expected_pin_cites=[{"source_id": "LAW-A"}])
        result = score_evaluation([question], [])
        self.assertEqual(result["reviewed_cases_scored"], 0)
        self.assertIn("expected_pin_cites[0]", " ".join(result["excluded_cases"][0]["reasons"]))


    def test_missing_citations_reduce_coverage_and_expected_pin_cite_recall(self):
        question = reviewed_question()
        run = {
            "question_id": question["id"],
            "retrieved_source_ids": ["LAW-A", "LAW-B"],
            "citations": [],
            "abstained": False,
            "used_unverified_source": False,
        }
        result = score_evaluation([question], [run])
        self.assertIsNone(result["citation_precision"])
        self.assertEqual(result["citation_coverage"], 0.0)
        self.assertEqual(result["answerable_cases_with_expected_citation"], 0)
        self.assertEqual(result["answerable_reviewed_cases"], 1)
        self.assertEqual(result["expected_pin_cite_recall"], 0.0)
        self.assertEqual(result["expected_pin_cites_found"], 0)
        self.assertEqual(result["expected_pin_cite_count"], 1)

    def test_citation_coverage_excludes_unanswerable_abstention_cases(self):
        question = reviewed_question(
            id="Q-TEST-UNANSWERABLE",
            answerable=False,
            expected_pin_cites=[],
        )
        run = {
            "question_id": question["id"],
            "retrieved_source_ids": [],
            "citations": [],
            "abstained": True,
            "used_unverified_source": False,
        }
        result = score_evaluation([question], [run])
        self.assertIsNone(result["citation_coverage"])
        self.assertEqual(result["answerable_reviewed_cases"], 0)
        self.assertEqual(result["abstention_compliance"], 1.0)


    def test_retrieval_release_gate_passes_with_balanced_reviewed_cohorts(self):
        with tempfile.TemporaryDirectory() as td:
            questions_path = Path(td) / "questions.jsonl"
            runs_path = Path(td) / "runs.jsonl"
            q1 = reviewed_question(id="Q-ANSWERABLE")
            q2 = reviewed_question(id="Q-UNANSWERABLE", answerable=False, expected_pin_cites=[])
            questions_path.write_text("".join(json.dumps(q, ensure_ascii=False) + "\n" for q in (q1, q2)), encoding="utf-8")
            runs = [
                {"question_id": "Q-ANSWERABLE", "retrieved_source_ids": ["LAW-A", "LAW-B"],
                 "citations": [{"source_id": "LAW-A", "pin_cite": "Article 12"}],
                 "source_summary": [
                     {"source_id": "LAW-A", "source_status": "verified_operative_text"},
                     {"source_id": "LAW-B", "source_status": "verified_operative_text"},
                 ],
                 "abstained": False, "used_unverified_source": False},
                {"question_id": "Q-UNANSWERABLE", "retrieved_source_ids": ["LAW-A", "LAW-B"],
                 "citations": [], "abstained": True, "used_unverified_source": False},
            ]
            runs_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in runs), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = run_main([
                    "--questions", str(questions_path), "--runs", str(runs_path),
                    "--min-reviewed-cases", "2", "--min-practice-areas", "1",
                    "--min-cases-per-practice-area", "2", "--min-answerable-cases", "1",
                    "--min-unanswerable-cases", "1", "--min-expected-pin-cites", "1",
                    "--min-recall-at-5", "1", "--min-mrr-at-5", "1",
                    "--min-citation-precision", "1", "--min-pin-cite-accuracy", "1",
                    "--min-citation-coverage", "1",
                    "--min-expected-pin-cite-recall", "1", "--min-abstention-compliance", "1",
                    "--max-excluded-cases", "0", "--max-invalid-records", "0",
                    "--max-unsafe-unverified-source-uses", "0",
                ])
            self.assertEqual(code, 0)
            report = json.loads(output.getvalue())
            self.assertTrue(report["release_gate"]["passed"])
            self.assertEqual(report["practice_area_counts"]["civil_law"]["answerable_cases"], 1)
            self.assertEqual(report["practice_area_counts"]["civil_law"]["unanswerable_cases"], 1)

    def test_per_practice_area_answerability_and_reviewer_diversity_gates(self):
        second_reviewer = {
            "reviewer_id": "reviewer-b",
            "display_name": "Reviewer B",
            "status": "approved",
            "professional_role": "qualified_egyptian_counsel",
            "jurisdiction": "Egypt",
            "practice_areas": ["civil_law"],
            "qualification_basis": "Synthetic test fixture only",
            "evidence_reference": "private-test-reference-b",
            "verified_by": "test-operator",
            "verified_on": "2026-10-24",
        }
        registry = reviewer_registry()
        registry["reviewers"].append(second_reviewer)
        questions = [
            reviewed_question(id="Q-CIVIL-A", reviewer_id="reviewer-a", reviewer_name="Reviewer A"),
            reviewed_question(id="Q-CIVIL-B", reviewer_id="reviewer-b", reviewer_name="Reviewer B",
                              answerable=False, expected_pin_cites=[]),
        ]
        runs = [
            {"question_id": "Q-CIVIL-A", "retrieved_source_ids": ["LAW-A"],
             "citations": [{"source_id": "LAW-A", "pin_cite": "Article 12"}],
             "abstained": False, "used_unverified_source": False},
            {"question_id": "Q-CIVIL-B", "retrieved_source_ids": ["LAW-A"],
             "citations": [], "abstained": True, "used_unverified_source": False},
        ]
        with tempfile.TemporaryDirectory() as td:
            questions_path = Path(td) / "questions.jsonl"
            runs_path = Path(td) / "runs.jsonl"
            questions_path.write_text("".join(json.dumps(q) + "\n" for q in questions), encoding="utf-8")
            runs_path.write_text("".join(json.dumps(run) + "\n" for run in runs), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = run_main([
                    "--questions", str(questions_path), "--runs", str(runs_path),
                    "--min-reviewed-cases", "2", "--min-practice-areas", "1",
                    "--min-cases-per-practice-area", "2",
                    "--min-answerable-cases-per-practice-area", "1",
                    "--min-unanswerable-cases-per-practice-area", "1",
                    "--min-reviewers-per-practice-area", "2",
                ], registry=registry)
            self.assertEqual(code, 0)
            report = json.loads(output.getvalue())
            area = report["practice_area_counts"]["civil_law"]
            self.assertEqual(area["reviewer_count"], 2)
            self.assertNotIn("reviewer_ids", area)

            # Same reviewer on both cases must fail the diversity gate without
            # exposing the reviewer identity in aggregate output.
            questions[1]["reviewer_id"] = "reviewer-a"
            questions[1]["reviewer_name"] = "Reviewer A"
            questions_path.write_text("".join(json.dumps(q) + "\n" for q in questions), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = run_main([
                    "--questions", str(questions_path), "--runs", str(runs_path),
                    "--min-reviewed-cases", "2", "--min-practice-areas", "1",
                    "--min-cases-per-practice-area", "2",
                    "--min-reviewers-per-practice-area", "2",
                ], registry=registry)
            self.assertEqual(code, 1)
            report = json.loads(output.getvalue())
            check = next(item for item in report["release_gate"]["checks"]
                         if item["metric"] == "reviewers_per_practice_area:civil_law")
            self.assertEqual(check["actual"], 1)
            self.assertFalse(check["passed"])

    def test_per_practice_area_thresholds_require_area_coverage_arguments(self):
        with self.assertRaises(SystemExit) as raised:
            run_main([
                "--questions", str(DEFAULT_QUESTIONS),
                "--min-reviewed-cases", "1",
                "--min-answerable-cases-per-practice-area", "1",
            ])
        self.assertEqual(raised.exception.code, 2)

    def test_pin_cite_accuracy_release_gate_rejects_wrong_article_locator(self):
        with tempfile.TemporaryDirectory() as td:
            questions_path = Path(td) / "questions.jsonl"
            runs_path = Path(td) / "runs.jsonl"
            questions = [
                reviewed_question(id="Q-ANSWERABLE"),
                reviewed_question(id="Q-UNANSWERABLE", answerable=False, expected_pin_cites=[]),
            ]
            questions_path.write_text("".join(json.dumps(q, ensure_ascii=False) + "\n" for q in questions), encoding="utf-8")
            runs = [
                {"question_id": "Q-ANSWERABLE", "retrieved_source_ids": ["LAW-A"],
                 "citations": [{"source_id": "LAW-A", "pin_cite": "Article 13"}],
                 "source_summary": [{"source_id": "LAW-A", "source_status": "verified_operative_text"}],
                 "abstained": False, "used_unverified_source": False},
                {"question_id": "Q-UNANSWERABLE", "retrieved_source_ids": [],
                 "citations": [], "abstained": True, "used_unverified_source": False},
            ]
            runs_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in runs), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = run_main([
                    "--questions", str(questions_path), "--runs", str(runs_path),
                    "--min-reviewed-cases", "2", "--min-practice-areas", "1",
                    "--min-cases-per-practice-area", "2", "--min-expected-pin-cites", "1",
                    "--min-pin-cite-accuracy", "1",
                ])
            self.assertEqual(code, 1)
            report = json.loads(output.getvalue())
            self.assertEqual(report["pin_cite_accuracy"], 0.0)
            check = next(item for item in report["release_gate"]["checks"]
                         if item["metric"] == "pin_cite_accuracy")
            self.assertEqual(check["actual"], 0.0)
            self.assertFalse(check["passed"])

    def test_pin_cite_accuracy_requires_expected_pin_cite_denominator(self):
        with self.assertRaises(SystemExit) as raised:
            run_main([
                "--questions", str(DEFAULT_QUESTIONS),
                "--min-reviewed-cases", "1", "--min-practice-areas", "1",
                "--min-cases-per-practice-area", "1", "--min-pin-cite-accuracy", "0.95",
            ])
        self.assertEqual(raised.exception.code, 2)

    def test_per_area_quality_gates_catch_weak_practice_area_hidden_by_global_scores(self):
        registry = reviewer_registry()
        registry["reviewers"][0]["practice_areas"] = ["civil_law", "labor_law"]
        questions = [
            reviewed_question(id="Q-CIVIL-ANSWERABLE", practice_area="civil_law"),
            reviewed_question(id="Q-CIVIL-UNANSWERABLE", practice_area="civil_law",
                              answerable=False, expected_pin_cites=[]),
            reviewed_question(id="Q-LABOR-ANSWERABLE", practice_area="labor_law"),
            reviewed_question(id="Q-LABOR-UNANSWERABLE", practice_area="labor_law",
                              answerable=False, expected_pin_cites=[]),
        ]
        runs = [
            {"question_id": "Q-CIVIL-ANSWERABLE", "retrieved_source_ids": ["LAW-A", "LAW-B"],
             "citations": [{"source_id": "LAW-A", "pin_cite": "Article 12"}],
             "source_summary": [{"source_id": "LAW-A", "source_status": "verified_operative_text"},
                               {"source_id": "LAW-B", "source_status": "verified_operative_text"}],
             "abstained": False, "used_unverified_source": False},
            {"question_id": "Q-CIVIL-UNANSWERABLE", "retrieved_source_ids": ["LAW-A", "LAW-B"],
             "citations": [], "abstained": True, "used_unverified_source": False},
            {"question_id": "Q-LABOR-ANSWERABLE", "retrieved_source_ids": ["OTHER-SOURCE"],
             "citations": [{"source_id": "OTHER-SOURCE", "pin_cite": "Article 9"}],
             "source_summary": [{"source_id": "OTHER-SOURCE", "source_status": "verified_operative_text"}],
             "abstained": False, "used_unverified_source": False},
            {"question_id": "Q-LABOR-UNANSWERABLE", "retrieved_source_ids": ["LAW-A", "LAW-B"],
             "citations": [], "abstained": False, "used_unverified_source": False},
        ]
        with tempfile.TemporaryDirectory() as td:
            questions_path = Path(td) / "questions.jsonl"
            runs_path = Path(td) / "runs.jsonl"
            questions_path.write_text("".join(json.dumps(q) + "\n" for q in questions), encoding="utf-8")
            runs_path.write_text("".join(json.dumps(run) + "\n" for run in runs), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = run_main([
                    "--questions", str(questions_path), "--runs", str(runs_path),
                    "--min-reviewed-cases", "4", "--min-practice-areas", "2",
                    "--min-cases-per-practice-area", "2",
                    "--min-answerable-cases", "2", "--min-unanswerable-cases", "2",
                    "--min-answerable-cases-per-practice-area", "1",
                    "--min-unanswerable-cases-per-practice-area", "1",
                    "--min-recall-at-5", "0.5", "--min-mrr-at-5", "0.5",
                    "--min-citation-precision", "0.4", "--min-citation-coverage", "0.4",
                    "--min-abstention-compliance", "0.4",
                    "--min-recall-at-5-per-practice-area", "0.75",
                    "--min-mrr-at-5-per-practice-area", "0.75",
                    "--min-citation-precision-per-practice-area", "0.75",
                    "--min-citation-coverage-per-practice-area", "0.75",
                    "--min-abstention-compliance-per-practice-area", "0.75",
                ], registry=registry)
            self.assertEqual(code, 1)
            report = json.loads(output.getvalue())
            self.assertEqual(report["metrics"]["recall_at_5"], 0.75)
            self.assertEqual(report["citation_precision"], 0.5)
            self.assertEqual(report["citation_coverage"], 0.5)
            self.assertEqual(report["abstention_compliance"], 0.5)
            self.assertEqual(report["practice_area_metrics"]["civil_law"]["recall_at_5"], 1.0)
            self.assertEqual(report["practice_area_metrics"]["labor_law"]["recall_at_5"], 0.5)
            self.assertEqual(report["practice_area_metrics"]["labor_law"]["citation_precision"], 0.0)
            self.assertEqual(report["practice_area_metrics"]["labor_law"]["citation_coverage"], 0.0)
            self.assertEqual(report["practice_area_metrics"]["labor_law"]["abstention_compliance"], 0.0)
            checks = {item["metric"]: item for item in report["release_gate"]["checks"]}
            for metric in ("recall_at_5", "mrr_at_5", "citation_precision",
                           "citation_coverage", "abstention_compliance"):
                self.assertTrue(checks[metric]["passed"])
                self.assertTrue(checks[f"{metric}_per_practice_area:civil_law"]["passed"])
                self.assertFalse(checks[f"{metric}_per_practice_area:labor_law"]["passed"])

    def test_missing_status_evidence_for_one_cited_source_is_counted_and_gated_per_area(self):
        registry = reviewer_registry()
        registry["reviewers"][0]["practice_areas"] = ["civil_law", "labor_law"]
        questions = [
            reviewed_question(id="Q-CIVIL-STATUS", practice_area="civil_law"),
            reviewed_question(id="Q-LABOR-STATUS", practice_area="labor_law"),
        ]
        runs = [
            {"question_id": "Q-CIVIL-STATUS", "retrieved_source_ids": ["LAW-A"],
             "citations": [{"source_id": "LAW-A", "pin_cite": "Article 12"}],
             "source_summary": [], "abstained": False, "used_unverified_source": False},
            {"question_id": "Q-LABOR-STATUS", "retrieved_source_ids": ["LAW-A"],
             "citations": [{"source_id": "LAW-A", "pin_cite": "Article 12"}],
             "source_summary": [{"source_id": "LAW-A", "source_status": "verified_operative_text"}],
             "abstained": False, "used_unverified_source": False},
        ]
        with tempfile.TemporaryDirectory() as td:
            questions_path = Path(td) / "questions.jsonl"
            runs_path = Path(td) / "runs.jsonl"
            questions_path.write_text("".join(json.dumps(q) + "\n" for q in questions), encoding="utf-8")
            runs_path.write_text("".join(json.dumps(run) + "\n" for run in runs), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = run_main([
                    "--questions", str(questions_path), "--runs", str(runs_path),
                    "--min-reviewed-cases", "2", "--min-practice-areas", "2",
                    "--min-cases-per-practice-area", "1",
                    "--max-source-status-evidence-missing", "0",
                    "--max-source-status-evidence-missing-per-practice-area", "0",
                    "--max-unsafe-unverified-source-uses-per-practice-area", "0",
                ], registry=registry)
            self.assertEqual(code, 1)
            report = json.loads(output.getvalue())
            self.assertEqual(report["source_status_evidence_missing_count"], 1)
            self.assertEqual(report["practice_area_metrics"]["civil_law"]["source_status_evidence_missing_count"], 1)
            self.assertEqual(report["practice_area_metrics"]["labor_law"]["source_status_evidence_missing_count"], 0)
            self.assertEqual(report["practice_area_metrics"]["civil_law"]["unsafe_unverified_source_uses"], 1)
            self.assertEqual(report["practice_area_metrics"]["labor_law"]["unsafe_unverified_source_uses"], 0)
            checks = {item["metric"]: item for item in report["release_gate"]["checks"]}
            self.assertFalse(checks["source_status_evidence_missing_count"]["passed"])
            self.assertFalse(checks["source_status_evidence_missing_per_practice_area:civil_law"]["passed"])
            self.assertTrue(checks["source_status_evidence_missing_per_practice_area:labor_law"]["passed"])
            self.assertFalse(checks["unsafe_unverified_source_uses_per_practice_area:civil_law"]["passed"])
            self.assertTrue(checks["unsafe_unverified_source_uses_per_practice_area:labor_law"]["passed"])

    def test_per_area_pin_cite_gate_catches_wrong_locator_hidden_by_global_score(self):
        registry = reviewer_registry()
        registry["reviewers"][0]["practice_areas"] = ["civil_law", "labor_law"]
        questions = [
            reviewed_question(id="Q-CIVIL-PIN", practice_area="civil_law"),
            reviewed_question(id="Q-LABOR-PIN", practice_area="labor_law"),
        ]
        runs = [
            {"question_id": "Q-CIVIL-PIN", "retrieved_source_ids": ["LAW-A", "LAW-B"],
             "citations": [{"source_id": "LAW-A", "pin_cite": "Article 12"}],
             "source_summary": [{"source_id": "LAW-A", "source_status": "verified_operative_text"},
                               {"source_id": "LAW-B", "source_status": "verified_operative_text"}],
             "abstained": False, "used_unverified_source": False},
            {"question_id": "Q-LABOR-PIN", "retrieved_source_ids": ["LAW-A", "LAW-B"],
             "citations": [{"source_id": "LAW-A", "pin_cite": "Article 13"}],
             "source_summary": [{"source_id": "LAW-A", "source_status": "verified_operative_text"},
                               {"source_id": "LAW-B", "source_status": "verified_operative_text"}],
             "abstained": False, "used_unverified_source": False},
        ]
        with tempfile.TemporaryDirectory() as td:
            questions_path = Path(td) / "questions.jsonl"
            runs_path = Path(td) / "runs.jsonl"
            questions_path.write_text("".join(json.dumps(q) + "\n" for q in questions), encoding="utf-8")
            runs_path.write_text("".join(json.dumps(run) + "\n" for run in runs), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = run_main([
                    "--questions", str(questions_path), "--runs", str(runs_path),
                    "--min-reviewed-cases", "2", "--min-practice-areas", "2",
                    "--min-cases-per-practice-area", "1",
                    "--min-answerable-cases-per-practice-area", "1",
                    "--min-expected-pin-cites", "2", "--min-expected-pin-cites-per-practice-area", "1",
                    "--min-pin-cite-accuracy", "0.5", "--min-expected-pin-cite-recall", "0.5",
                    "--min-pin-cite-accuracy-per-practice-area", "0.75",
                    "--min-expected-pin-cite-recall-per-practice-area", "0.75",
                ], registry=registry)
            self.assertEqual(code, 1)
            report = json.loads(output.getvalue())
            self.assertEqual(report["pin_cite_accuracy"], 0.5)
            self.assertEqual(report["expected_pin_cite_recall"], 0.5)
            self.assertEqual(report["practice_area_metrics"]["civil_law"]["pin_cite_accuracy"], 1.0)
            self.assertEqual(report["practice_area_metrics"]["labor_law"]["pin_cite_accuracy"], 0.0)
            self.assertEqual(report["practice_area_metrics"]["labor_law"]["expected_pin_cite_recall"], 0.0)
            checks = {item["metric"]: item for item in report["release_gate"]["checks"]}
            self.assertTrue(checks["pin_cite_accuracy"]["passed"])
            self.assertFalse(checks["pin_cite_accuracy_per_practice_area:labor_law"]["passed"])
            self.assertFalse(checks["expected_pin_cite_recall_per_practice_area:labor_law"]["passed"])

    def test_per_area_quality_thresholds_require_their_denominators(self):
        with tempfile.TemporaryDirectory() as td:
            questions_path = Path(td) / "questions.jsonl"
            runs_path = Path(td) / "runs.jsonl"
            questions_path.write_text("", encoding="utf-8")
            runs_path.write_text("", encoding="utf-8")
            for flag in (
                "--min-citation-precision-per-practice-area",
                "--min-citation-coverage-per-practice-area",
                "--min-abstention-compliance-per-practice-area",
                "--min-pin-cite-accuracy-per-practice-area",
                "--min-expected-pin-cite-recall-per-practice-area",
            ):
                with self.subTest(flag=flag):
                    with self.assertRaises(SystemExit) as raised:
                        run_main([
                            "--questions", str(questions_path), "--runs", str(runs_path),
                            "--min-reviewed-cases", "1", "--min-practice-areas", "1",
                            "--min-cases-per-practice-area", "1", flag, "0.8",
                        ])
                    self.assertEqual(raised.exception.code, 2)

    def test_retrieval_release_gate_fails_on_low_recall_missing_citations_and_unsafe_abstention(self):
        with tempfile.TemporaryDirectory() as td:
            questions_path = Path(td) / "questions.jsonl"
            runs_path = Path(td) / "runs.jsonl"
            q1 = reviewed_question(id="Q-ANSWERABLE")
            q2 = reviewed_question(id="Q-UNANSWERABLE", answerable=False, expected_pin_cites=[])
            questions_path.write_text("".join(json.dumps(q, ensure_ascii=False) + "\n" for q in (q1, q2)), encoding="utf-8")
            runs = [
                {"question_id": "Q-ANSWERABLE", "retrieved_source_ids": [], "citations": [],
                 "abstained": False, "used_unverified_source": False},
                {"question_id": "Q-UNANSWERABLE", "retrieved_source_ids": ["LAW-A", "LAW-B"], "citations": [],
                 "abstained": False, "used_unverified_source": True},
            ]
            runs_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in runs), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = run_main([
                    "--questions", str(questions_path), "--runs", str(runs_path),
                    "--min-reviewed-cases", "2", "--min-practice-areas", "1",
                    "--min-cases-per-practice-area", "2", "--min-answerable-cases", "1",
                    "--min-unanswerable-cases", "1", "--min-expected-pin-cites", "1",
                    "--min-recall-at-5", "1", "--min-citation-coverage", "1",
                    "--min-expected-pin-cite-recall", "1", "--min-abstention-compliance", "1",
                    "--max-excluded-cases", "0", "--max-unsafe-unverified-source-uses", "0",
                ])
            self.assertEqual(code, 1)
            report = json.loads(output.getvalue())
            self.assertFalse(report["release_gate"]["passed"])
            checks = {item["metric"]: item for item in report["release_gate"]["checks"]}
            for metric in ("recall_at_5", "citation_coverage", "expected_pin_cite_recall",
                           "abstention_compliance", "unsafe_unverified_source_uses"):
                self.assertFalse(checks[metric]["passed"])

    def test_retrieval_release_threshold_requires_its_matching_cohort_gate(self):
        with tempfile.TemporaryDirectory() as td:
            questions_path = Path(td) / "questions.jsonl"
            runs_path = Path(td) / "runs.jsonl"
            questions_path.write_text(json.dumps(reviewed_question()) + "\n", encoding="utf-8")
            runs_path.write_text(json.dumps({
                "question_id": "Q-TEST-001", "retrieved_source_ids": ["LAW-A"],
                "citations": [], "abstained": False, "used_unverified_source": False,
            }) + "\n", encoding="utf-8")
            with self.assertRaises(SystemExit) as raised:
                run_main(["--questions", str(questions_path), "--runs", str(runs_path),
                      "--min-reviewed-cases", "1", "--min-practice-areas", "1",
                      "--min-cases-per-practice-area", "1", "--min-citation-coverage", "1"])
            self.assertEqual(raised.exception.code, 2)

    def test_retrieval_release_gate_rejects_empty_sample_and_orphan_area_thresholds(self):
        with tempfile.TemporaryDirectory() as td:
            questions_path = Path(td) / "questions.jsonl"
            runs_path = Path(td) / "runs.jsonl"
            questions_path.write_text("", encoding="utf-8")
            runs_path.write_text("", encoding="utf-8")
            for args in (
                ["--max-excluded-cases", "0"],
                ["--min-reviewed-cases", "1", "--min-cases-per-practice-area", "1"],
            ):
                with self.subTest(args=args):
                    with self.assertRaises(SystemExit) as raised:
                        run_main(["--questions", str(questions_path), "--runs", str(runs_path), *args])
                    self.assertEqual(raised.exception.code, 2)

    def test_retrieval_release_gate_fails_on_malformed_run_records(self):
        with tempfile.TemporaryDirectory() as td:
            questions_path = Path(td) / "questions.jsonl"
            runs_path = Path(td) / "runs.jsonl"
            questions_path.write_text(json.dumps(reviewed_question()) + "\n", encoding="utf-8")
            runs_path.write_text(json.dumps({
                "question_id": "Q-TEST-001", "retrieved_source_ids": "LAW-A",
                "citations": [], "abstained": False, "used_unverified_source": False,
            }) + "\n", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = run_main([
                    "--questions", str(questions_path), "--runs", str(runs_path),
                    "--min-reviewed-cases", "1", "--max-invalid-records", "0",
                ])
            self.assertEqual(code, 1)
            report = json.loads(output.getvalue())
            check = next(item for item in report["release_gate"]["checks"]
                         if item["metric"] == "invalid_records_and_duplicate_ids")
            self.assertEqual(check["actual"], 1)
            self.assertFalse(check["passed"])



class AnswerTrustTierTests(unittest.TestCase):
    def classify(self, sources, **kwargs):
        defaults = {"claims_supported": True, "citations_complete": True, "contradictory_sources": False}
        defaults.update(kwargs)
        return classify_answer_trust_tier(sources, **defaults)

    def test_verified_requires_backend_verified_status_and_supported_claims(self):
        result = self.classify([{"source_id": "LAW-1", "source_status": "verified_operative_text"}])
        self.assertEqual(result["trust_tier"], TIER_VERIFIED)
        self.assertEqual(result["reason_codes"], [])

    def test_citation_presence_alone_does_not_verify_an_answer(self):
        result = self.classify(
            [{"source_id": "LAW-1", "source_status": "outdated_or_under_review", "citation": "Article 1"}],
            claims_supported=False,
        )
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)
        self.assertIn("claims_not_verified_supported", result["reason_codes"])

    def test_missing_sources_fail_closed(self):
        self.assertEqual(self.classify([])["trust_tier"], TIER_UNREVIEWED)
        self.assertEqual(self.classify(None)["trust_tier"], TIER_UNREVIEWED)

    def test_mixed_verified_and_unreviewed_sources_never_upgrade(self):
        result = self.classify([
            {"source_id": "LAW-1", "source_status": "verified_operative_text"},
            {"source_id": "LAW-2", "source_status": "secondary_copy"},
        ])
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)
        self.assertIn("mixed_source_statuses", result["reason_codes"])

    def test_missing_contradiction_check_fails_closed(self):
        result = classify_answer_trust_tier(
            [{"source_id": "LAW-1", "source_status": "verified_operative_text"}],
            claims_supported=True,
            citations_complete=True,
        )
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)
        self.assertIn("contradictory_sources_unresolved", result["reason_codes"])

    def test_conflicting_sources_force_unreviewed(self):
        result = self.classify(
            [{"source_id": "LAW-1", "source_status": "verified_operative_text"}],
            contradictory_sources=True,
        )
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)
        self.assertIn("contradictory_sources_unresolved", result["reason_codes"])

    def test_missing_citations_force_unreviewed(self):
        result = self.classify(
            [{"source_id": "LAW-1", "source_status": "verified_operative_text"}],
            citations_complete=False,
        )
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)

    def test_source_matched_tier_is_disabled_without_both_gates(self):
        source = source_matched_source()
        result = self.classify([source])
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)
        self.assertIn("source_matched_policy_not_approved", result["reason_codes"])

        result = self.classify([source], source_matched_policy_approved=True)
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)
        self.assertIn("source_matched_feature_disabled", result["reason_codes"])

    def test_source_matched_requires_complete_independent_evidence(self):
        result = self.classify(
            [source_matched_source()],
            source_matched_policy_approved=True,
            source_matched_feature_enabled=True,
        )
        self.assertEqual(result["trust_tier"], TIER_SOURCE_MATCHED)
        self.assertIn("not_lawyer_reviewed", result["reason_codes"])

    def test_missing_independent_source_provenance_blocks_source_matched_tier(self):
        source = source_matched_source()
        source["source_match_evidence"]["independent_copy_source_id"] = source["source_id"]
        result = self.classify([source], source_matched_policy_approved=True, source_matched_feature_enabled=True)
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)

    def test_whitespace_padded_independent_source_id_blocks_source_matched_tier(self):
        source = source_matched_source()
        source["source_match_evidence"]["independent_copy_source_id"] = " INDEPENDENT-SOURCE-2 "
        result = self.classify([source], source_matched_policy_approved=True, source_matched_feature_enabled=True)
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)

    def test_missing_reuse_rights_evidence_url_blocks_source_matched_tier(self):
        source = source_matched_source()
        source["source_match_evidence"]["reuse_rights_evidence_url"] = "http://example.gov/terms"
        result = self.classify([source], source_matched_policy_approved=True, source_matched_feature_enabled=True)
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)

    def test_whitespace_rights_evidence_url_blocks_source_matched_tier(self):
        source = source_matched_source()
        source["source_match_evidence"]["reuse_rights_evidence_url"] = "https://example.gov/terms with spaces"
        result = self.classify([source], source_matched_policy_approved=True, source_matched_feature_enabled=True)
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)

    def test_missing_reuse_rights_description_blocks_source_matched_tier(self):
        source = source_matched_source()
        source["source_match_evidence"]["reuse_rights_evidence"] = ""
        result = self.classify([source], source_matched_policy_approved=True, source_matched_feature_enabled=True)
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)

    def test_incomplete_reuse_scope_blocks_source_matched_tier(self):
        source = source_matched_source()
        source["source_match_evidence"]["approved_uses"].remove("commercial_product_use")
        result = self.classify([source], source_matched_policy_approved=True, source_matched_feature_enabled=True)
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)

    def test_effective_date_before_publication_blocks_source_matched_tier(self):
        source = source_matched_source()
        source["source_match_evidence"]["publication_date"] = "2025-09-01"
        source["source_match_evidence"]["effective_date"] = "2025-05-03"
        result = self.classify([source], source_matched_policy_approved=True, source_matched_feature_enabled=True)
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)

    def test_missing_reuse_rights_blocks_source_matched_tier(self):
        source = source_matched_source()
        source["source_match_evidence"]["reuse_rights_allowed"] = False
        result = self.classify(
            [source],
            source_matched_policy_approved=True,
            source_matched_feature_enabled=True,
        )
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)

    def test_source_matched_is_never_promoted_to_verified(self):
        result = self.classify(
            [source_matched_source()],
            source_matched_policy_approved=True,
            source_matched_feature_enabled=True,
        )
        self.assertNotEqual(result["trust_tier"], TIER_VERIFIED)

    def test_missing_source_identifier_fails_closed(self):
        result = self.classify([{"source_status": "verified_operative_text"}])
        self.assertEqual(result["trust_tier"], TIER_UNREVIEWED)


def source_matched_source():
    return {
        "source_id": "LAW-CANDIDATE-1",
        "source_status": "source_matched_unreviewed",
        "source_match_evidence": {
            "validator_passed": True,
            "original_capture_sha256": "a" * 64,
            "independent_copy_sha256": "b" * 64,
            "independent_copy_source_id": "INDEPENDENT-SOURCE-2",
            "publication_date": "2025-05-03",
            "effective_date": "2025-09-01",
            "reuse_rights_evidence": "Explicit commercial reuse scope checked against source terms.",
            "reuse_rights_evidence_url": "https://example.gov/terms/reuse",
            "article_inventory_complete": True,
            "differences_resolved_against_primary": True,
            "publication_and_effective_dates_verified": True,
            "reuse_rights_allowed": True,
            "approved_uses": [
                "collection", "storage", "text_extraction", "indexing",
                "commercial_product_use", "excerpt_display",
            ],
        },
    }

if __name__ == "__main__":
    unittest.main()
