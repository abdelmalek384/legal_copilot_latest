import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.evaluate_retrieval_quality import DEFAULT_QUESTIONS, _load_jsonl, _write_report, score_evaluation as _score_evaluation, validate_reviewed_question


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
    return _score_evaluation(questions, runs, k_values, reviewer_registry())


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
                {"source_id": "LAW-A", "source_status": "verified_operative_text"},
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
            ({"review_evidence_url": "https://example.gov/review\\x00"}, "HTTPS"),
            ({"review_evidence_url": "https://example.gov/review\\x7f"}, "HTTPS"),
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
        from tools.evaluate_retrieval_quality import score_evaluation as raw_score_evaluation
        with self.assertRaisesRegex(ValueError, "reviewer registry is invalid"):
            raw_score_evaluation([question], [], reviewer_registry=bad_registry)

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


if __name__ == "__main__":
    unittest.main()
