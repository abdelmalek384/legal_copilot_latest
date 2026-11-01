import sys
import io
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from unittest.mock import patch
from tools.run_legal_eval import MAX_API_RESPONSE_BYTES, RunnerError, _request_json, read_questions, result_from_response, validate_base_url
from tools.evaluate_retrieval_quality import score_evaluation


class LegalEvalRunnerTests(unittest.TestCase):
    def test_maps_only_cited_stable_source_ids_and_exact_pin_cites(self):
        q = {"id": "Q1", "question_ar": "سؤال", "as_of_date": "2026-10-26"}
        response = {
            "found": True,
            "answer": "قاعدة قانونية [1]. وشرح آخر [1] ومصدر ثان [2].",
            "abstained": False,
            "scope": "verified_corpus",
            "sources": [
                {"source_id": "EG-LAW-10", "article": "12", "citation": "القانون 10 المادة 12", "source_status": "verified_operative_text"},
                {"source_id": None, "article": "4", "citation": "Legacy source", "source_status": "outdated_or_under_review"},
            ],
        }
        row = result_from_response(q, response)
        self.assertEqual(row["cited_sources"], ["EG-LAW-10"])
        self.assertEqual(row["cited_pin_cites"], [{"source_id": "EG-LAW-10", "pin_cite": "المادة 12"}])
        self.assertEqual(row["question_id"], "Q1")
        self.assertEqual(row["retrieved_source_ids"], ["EG-LAW-10"])
        self.assertEqual(row["citations"], [{"source_id": "EG-LAW-10", "pin_cite": "المادة 12"}])
        self.assertFalse(row["used_unverified_source"])
        self.assertEqual(row["citation_marker_count"], 2)
        self.assertFalse(row["abstained"])
        self.assertEqual(row["invalid_citation_indices"], [2])

    def test_runner_row_can_be_scored_without_manual_schema_conversion(self):
        question = {
            "id": "Q-SCORABLE",
            "question_ar": "سؤال اختباري",
            "practice_area": "civil_law",
            "review_status": "lawyer_reviewed",
            "reviewer_name": "Reviewer A",
            "review_date": "2026-10-24",
            "expected_source_ids": ["EG-LAW-10"],
            "expected_pin_cites": [{"source_id": "EG-LAW-10", "pin_cite": "المادة 12"}],
            "answerable": True,
            "must_abstain_if_unverified": True,
        }
        row = result_from_response(
            question,
            {
                "found": True,
                "answer": "القاعدة القانونية [1].",
                "abstained": False,
                "scope": "verified_corpus",
                "sources": [{
                    "source_id": "EG-LAW-10",
                    "article": "12",
                    "source_status": "verified_operative_text",
                }],
            },
        )

        report = score_evaluation([question], [row])

        self.assertEqual(report["reviewed_cases_scored"], 1)
        self.assertEqual(report["citation_precision"], 1.0)
        self.assertEqual(report["citation_coverage"], 1.0)
        self.assertEqual(report["expected_pin_cite_recall"], 1.0)

    def test_records_invalid_citation_indices_without_inventing_sources(self):
        q = {"id": "Q2", "question_ar": "سؤال"}
        response = {"found": True, "answer": "قاعدة [3].", "sources": [{"ref": "legacy"}]}
        row = result_from_response(q, response)
        self.assertEqual(row["invalid_citation_indices"], [3])
        self.assertEqual(row["retrieved_source_ids"], [])
        self.assertEqual(row["citations"], [])
        self.assertEqual(row["cited_sources"], [])
        self.assertTrue(row["abstained"] is False)

    def test_missing_source_id_for_visible_citation_is_reported_invalid(self):
        q = {"id": "Q-MISSING-ID", "question_ar": "سؤال"}
        response = {"answer": "قاعدة [1].", "sources": [{"article": "12"}]}
        row = result_from_response(q, response)
        self.assertEqual(row["invalid_citation_indices"], [1])
        self.assertEqual(row["citations"], [])
        self.assertEqual(row["retrieved_source_ids"], [])
        self.assertFalse(row["used_unverified_source"])

    def test_cited_unverified_source_is_marked_for_evaluation(self):
        q = {"id": "Q-UNVERIFIED", "question_ar": "سؤال"}
        response = {
            "answer": "قاعدة [1].",
            "sources": [{"source_id": "LAW-UNVERIFIED", "source_status": "outdated_or_under_review"}],
        }
        row = result_from_response(q, response)
        self.assertEqual(row["retrieved_source_ids"], ["LAW-UNVERIFIED"])
        self.assertEqual(row["citations"], [{"source_id": "LAW-UNVERIFIED"}])
        self.assertTrue(row["used_unverified_source"])

    def test_missing_source_status_is_treated_as_unverified(self):
        row = result_from_response(
            {"id": "Q-STATUS-MISSING", "question_ar": "سؤال"},
            {"answer": "قاعدة [1].", "sources": [{"source_id": "LAW-1"}]},
        )
        self.assertEqual(row["retrieved_source_ids"], ["LAW-1"])
        self.assertEqual(row["citations"], [{"source_id": "LAW-1"}])
        self.assertTrue(row["used_unverified_source"])

    def test_citations_inside_fenced_inline_code_and_html_comments_are_ignored(self):
        response = {
            "answer": "No visible citation.\n\n\x60\x60\x60text\n[2]\n\x60\x60\x60\nInline \x60[3]\x60 <!-- [4] -->",
            "sources": [
                {"source_id": "LAW-1"},
                {"source_id": "LAW-2"},
                {"source_id": "LAW-3"},
                {"source_id": "LAW-4"},
            ],
        }
        row = result_from_response({"id": "Q-CODE", "question_ar": "سؤال"}, response)
        self.assertEqual(row["cited_sources"], [])
        self.assertEqual(row["invalid_citation_indices"], [])

    def test_visible_prose_citations_count_but_unclosed_fence_does_not(self):
        response = {
            "answer": "Claim supported [1].\n~~~text\n[2]\n~~~\n\x60[3]\x60 <!-- [4] -->\n\x60\x60\x60python\n[5]",
            "sources": [
                {"source_id": "LAW-1"},
                {"source_id": "LAW-2"},
                {"source_id": "LAW-3"},
                {"source_id": "LAW-4"},
                {"source_id": "LAW-5"},
            ],
        }
        row = result_from_response({"id": "Q-VISIBLE", "question_ar": "سؤال"}, response)
        self.assertEqual(row["cited_sources"], ["LAW-1"])
        self.assertEqual(row["invalid_citation_indices"], [])

    def test_no_answer_is_an_abstention(self):
        row = result_from_response({"id": "Q3", "question_ar": "سؤال"}, {"found": False, "answer": None})
        self.assertTrue(row["abstained"])

    def test_remote_targets_require_explicit_opt_in_and_https(self):
        self.assertEqual(validate_base_url("http://127.0.0.1:8000"), "http://127.0.0.1:8000")
        self.assertEqual(validate_base_url("http://localhost:8000/path"), "http://localhost:8000/path")
        with self.assertRaisesRegex(RunnerError, "explicit --allow-remote"):
            validate_base_url("https://legal.example.com")
        with self.assertRaisesRegex(RunnerError, "HTTPS"):
            validate_base_url("http://legal.example.com", allow_remote=True)
        self.assertEqual(validate_base_url("https://legal.example.com", allow_remote=True), "https://legal.example.com")
        with self.assertRaisesRegex(RunnerError, "embedded credentials"):
            validate_base_url("https://user:secret@legal.example.com", allow_remote=True)
        with self.assertRaisesRegex(RunnerError, "query string"):
            validate_base_url("http://127.0.0.1:8000?token=secret")

    def test_base_url_rejects_empty_credentials_whitespace_and_malformed_ports(self):
        invalid_urls = (
            "https://@legal.example.com",
            " https://legal.example.com",
            "https://legal.example.com ",
            "https://legal.example.com/path with spaces",
            "https://legal.example.com:not-a-port",
            "https://legal.example.com:99999",
            "https://legal.example.com:0",
            "https://legal.example.com:",
            "https://[malformed",
        )
        for value in invalid_urls:
            with self.subTest(value=value), self.assertRaises(RunnerError):
                validate_base_url(value, allow_remote=True)

    def test_api_response_reader_is_bounded_and_closes_response(self):
        class FakeOpener:
            def __init__(self, response):
                self.response = response
            def open(self, request, timeout=0):
                return self.response

        valid = b'{"ok":true}'
        response = io.BytesIO(valid)
        with patch("tools.run_legal_eval.MAX_API_RESPONSE_BYTES", 64):
            self.assertEqual(_request_json(FakeOpener(response), "http://localhost/api", {}), {"ok": True})
        self.assertTrue(response.closed)

        exact = io.BytesIO(valid + b" " * (64 - len(valid)))
        with patch("tools.run_legal_eval.MAX_API_RESPONSE_BYTES", 64):
            self.assertEqual(_request_json(FakeOpener(exact), "http://localhost/api", {}), {"ok": True})
        self.assertTrue(exact.closed)

        oversized = io.BytesIO(b"x" * 65)
        with patch("tools.run_legal_eval.MAX_API_RESPONSE_BYTES", 64):
            with self.assertRaisesRegex(RunnerError, "16 MiB safety limit"):
                _request_json(FakeOpener(oversized), "http://localhost/api", {})
        self.assertTrue(oversized.closed)

    def test_question_loader_rejects_duplicate_ids_and_empty_sets(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "q.jsonl"
            p.write_text('{"id":"Q1","question_ar":"سؤال"}\n{"id":"Q1","question_ar":"سؤال آخر"}\n', encoding="utf-8")
            with self.assertRaisesRegex(RunnerError, "duplicate question id"):
                read_questions(p)
            p.write_text("\n", encoding="utf-8")
            with self.assertRaisesRegex(RunnerError, "no questions"):
                read_questions(p)


if __name__ == "__main__":
    unittest.main()
