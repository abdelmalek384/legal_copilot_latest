import json
import tempfile
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.evaluate_legal_answers import EvaluationError, evaluate, main


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
    def test_cli_release_gate_passes_when_thresholds_are_met(self):
        with tempfile.TemporaryDirectory() as td:
            questions = Path(td) / "questions.jsonl"
            results = Path(td) / "results.jsonl"
            report_path = Path(td) / "report.json"
            questions.write_text(json.dumps(approved(), ensure_ascii=False) + "\n", encoding="utf-8")
            results.write_text(json.dumps(result(), ensure_ascii=False) + "\n", encoding="utf-8")
            code = main([
                "--questions", str(questions), "--results", str(results), "--out", str(report_path),
                "--min-questions", "1", "--min-practice-areas", "1", "--min-questions-per-practice-area", "1",
                "--min-source-precision", "1", "--min-pin-cite-precision", "1",
                "--min-abstention-accuracy", "1", "--max-invalid-citation-question-rate", "0",
            ])
            self.assertEqual(code, 0)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertTrue(report["release_gate"]["enabled"])
            self.assertTrue(report["release_gate"]["passed"])

    def test_cli_release_gate_fails_and_preserves_report_on_precision_failure(self):
        with tempfile.TemporaryDirectory() as td:
            questions = Path(td) / "questions.jsonl"
            results = Path(td) / "results.jsonl"
            report_path = Path(td) / "report.json"
            questions.write_text(json.dumps(approved(), ensure_ascii=False) + "\n", encoding="utf-8")
            r = result(sources=["LAW-10", "EXTRA"],
                       pins=[{"source_id": "LAW-10", "pin_cite": "المادة 12"},
                             {"source_id": "EXTRA", "pin_cite": "المادة 99"}])
            results.write_text(json.dumps(r, ensure_ascii=False) + "\n", encoding="utf-8")
            code = main([
                "--questions", str(questions), "--results", str(results), "--out", str(report_path),
                "--min-questions", "1", "--min-practice-areas", "1", "--min-questions-per-practice-area", "1",
                "--min-source-precision", "1",
            ])
            self.assertEqual(code, 1)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertFalse(report["release_gate"]["passed"])
            source_check = next(check for check in report["release_gate"]["checks"] if check["metric"] == "source_precision")
            self.assertEqual(source_check["actual"], 0.5)

    def test_quality_thresholds_require_explicit_minimum_sample_size(self):
        with tempfile.TemporaryDirectory() as td:
            questions = Path(td) / "questions.jsonl"
            results = Path(td) / "results.jsonl"
            questions.write_text(json.dumps(approved(), ensure_ascii=False) + "\n", encoding="utf-8")
            results.write_text(json.dumps(result(), ensure_ascii=False) + "\n", encoding="utf-8")
            with self.assertRaises(SystemExit) as raised:
                main(["--questions", str(questions), "--results", str(results), "--min-source-precision", "1"])
            self.assertEqual(raised.exception.code, 2)

    def test_quality_thresholds_require_explicit_practice_area_coverage(self):
        with tempfile.TemporaryDirectory() as td:
            questions = Path(td) / "questions.jsonl"
            results = Path(td) / "results.jsonl"
            questions.write_text(json.dumps(approved(), ensure_ascii=False) + "\\n", encoding="utf-8")
            results.write_text(json.dumps(result(), ensure_ascii=False) + "\\n", encoding="utf-8")
            with self.assertRaises(SystemExit) as raised:
                main(["--questions", str(questions), "--results", str(results),
                      "--min-questions", "1", "--min-source-precision", "1"])
            self.assertEqual(raised.exception.code, 2)

    def test_practice_area_gate_rejects_skewed_or_narrow_benchmark(self):
        with tempfile.TemporaryDirectory() as td:
            questions = Path(td) / "questions.jsonl"
            results = Path(td) / "results.jsonl"
            report_path = Path(td) / "report.json"
            q1 = approved("Q1")
            q2 = dict(approved("Q2"))
            q2["practice_area"] = "civil_law"
            questions.write_text("".join(json.dumps(q, ensure_ascii=False) + "\\n" for q in (q1, q2)), encoding="utf-8")
            results.write_text("".join(json.dumps(result(q["id"]), ensure_ascii=False) + "\\n" for q in (q1, q2)), encoding="utf-8")
            code = main(["--questions", str(questions), "--results", str(results), "--out", str(report_path),
                         "--min-questions", "2", "--min-practice-areas", "2",
                         "--min-questions-per-practice-area", "1"])
            self.assertEqual(code, 1)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            area_check = next(check for check in report["release_gate"]["checks"] if check["metric"] == "practice_area_count")
            self.assertEqual(area_check["actual"], 1)
            self.assertFalse(area_check["passed"])

    def test_minimum_sample_size_gate_fails_when_too_few_questions_are_scored(self):
        with tempfile.TemporaryDirectory() as td:
            questions = Path(td) / "questions.jsonl"
            results = Path(td) / "results.jsonl"
            report_path = Path(td) / "report.json"
            questions.write_text(json.dumps(approved(), ensure_ascii=False) + "\n", encoding="utf-8")
            results.write_text(json.dumps(result(), ensure_ascii=False) + "\n", encoding="utf-8")
            code = main(["--questions", str(questions), "--results", str(results), "--out", str(report_path),
                         "--min-questions", "2"])
            self.assertEqual(code, 1)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            sample_check = next(check for check in report["release_gate"]["checks"] if check["metric"] == "questions_scored")
            self.assertEqual(sample_check["actual"], 1)
            self.assertFalse(sample_check["passed"])

    def test_invalid_practice_area_is_rejected_instead_of_crashing_summary(self):
        for value in ("", "   ", None, [], {}):
            with self.subTest(value=value):
                q = dict(approved())
                q["practice_area"] = value
                with self.assertRaisesRegex(EvaluationError, "practice_area"):
                    evaluate([q], [result()])

    def test_scores_citation_recall_and_abstention_without_claiming_semantic_accuracy(self):
        report = evaluate([approved()], [result()])
        self.assertEqual(report["overall"]["source_recall"], 1.0)
        self.assertEqual(report["overall"]["pin_cite_recall"], 1.0)
        self.assertEqual(report["overall"]["abstention_accuracy"], 1.0)
        self.assertFalse(report["semantic_legal_correctness_scored"])
        self.assertEqual(report["unreviewed_questions_excluded"], 0)

    def test_precision_penalizes_unexpected_sources_and_pin_citations(self):
        pins = [
            {"source_id": "LAW-10", "pin_cite": "المادة 12"},
            {"source_id": "LAW-EXTRA", "pin_cite": "المادة 99"},
        ]
        report = evaluate([approved()], [result(sources=["LAW-10", "LAW-EXTRA"], pins=pins)])
        row = report["results"][0]
        self.assertEqual(row["source_precision"], 0.5)
        self.assertEqual(row["pin_cite_precision"], 0.5)
        self.assertEqual(row["unexpected_source_count"], 1)
        self.assertEqual(row["unexpected_pin_cite_count"], 1)
        self.assertEqual(report["overall"]["source_precision"], 0.5)
        self.assertEqual(report["overall"]["pin_cite_precision"], 0.5)

    def test_unanswerable_citation_rate_exposes_citations_on_abstention_cases(self):
        q = approved("Q-ABSTAIN", answerable=False)
        r = result("Q-ABSTAIN", abstained=True, sources=["UNEXPECTED-LAW"],
                   pins=[{"source_id": "UNEXPECTED-LAW", "pin_cite": "المادة 1"}])
        report = evaluate([q], [r])
        self.assertEqual(report["overall"]["unanswerable_citation_rate"], 1.0)
        self.assertEqual(report["overall"]["unanswerable_abstention_recall"], 1.0)
        self.assertEqual(report["results"][0]["unexpected_source_count"], 1)

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

    def test_future_lawyer_review_date_is_rejected(self):
        q = dict(approved())
        q["review_date"] = "9999-12-31"
        with self.assertRaisesRegex(EvaluationError, "cannot be in the future"):
            evaluate([q], [result()])

    def test_invalid_citation_indexes_are_reported_and_validated(self):
        r = result()
        r["invalid_citation_indices"] = [0, 7]
        report = evaluate([approved()], [r])
        self.assertEqual(report["results"][0]["invalid_citation_index_count"], 2)
        self.assertEqual(report["overall"]["invalid_citation_index_count"], 2)
        self.assertEqual(report["overall"]["questions_with_invalid_citation_indices"], 1)
        self.assertEqual(report["overall"]["invalid_citation_question_rate"], 1.0)
        for value in ([-1], [True], ["2"], [2, 2], "2"):
            with self.subTest(value=value):
                malformed = result()
                malformed["invalid_citation_indices"] = value
                with self.assertRaisesRegex(EvaluationError, "invalid_citation_indices"):
                    evaluate([approved()], [malformed])

    def test_expected_pin_citation_must_reference_expected_source(self):
        q = dict(approved())
        q["expected_sources"] = ["LAW-10"]
        q["expected_pin_cites"] = [{"source_id": "LAW-OTHER", "pin_cite": "المادة 1"}]
        with self.assertRaisesRegex(EvaluationError, "absent from expected_sources"):
            evaluate([q], [result()])

    def test_result_pin_citation_must_reference_cited_source(self):
        r = result(sources=["LAW-10"], pins=[{"source_id": "LAW-OTHER", "pin_cite": "المادة 1"}])
        with self.assertRaisesRegex(EvaluationError, "absent from cited_sources"):
            evaluate([approved()], [r])

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
