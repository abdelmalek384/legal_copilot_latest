import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.run_legal_eval import RunnerError, read_questions, result_from_response


class LegalEvalRunnerTests(unittest.TestCase):
    def test_maps_only_cited_stable_source_ids_and_exact_pin_cites(self):
        q = {"id": "Q1", "question_ar": "سؤال", "as_of_date": "2026-10-26"}
        response = {
            "found": True,
            "answer": "قاعدة قانونية [1]. وشرح آخر [1] ومصدر ثان [2].",
            "abstained": False,
            "scope": "verified_corpus",
            "sources": [
                {"source_id": "EG-LAW-10", "article": "12", "citation": "القانون 10 المادة 12", "source_status": "verified"},
                {"source_id": None, "article": "4", "citation": "Legacy source", "source_status": "outdated_or_under_review"},
            ],
        }
        row = result_from_response(q, response)
        self.assertEqual(row["cited_sources"], ["EG-LAW-10"])
        self.assertEqual(row["cited_pin_cites"], [{"source_id": "EG-LAW-10", "pin_cite": "المادة 12"}])
        self.assertFalse(row["abstained"])
        self.assertEqual(row["invalid_citation_indices"], [])

    def test_records_invalid_citation_indices_without_inventing_sources(self):
        q = {"id": "Q2", "question_ar": "سؤال"}
        response = {"found": True, "answer": "قاعدة [3].", "sources": [{"ref": "legacy"}]}
        row = result_from_response(q, response)
        self.assertEqual(row["invalid_citation_indices"], [3])
        self.assertEqual(row["cited_sources"], [])
        self.assertTrue(row["abstained"] is False)

    def test_no_answer_is_an_abstention(self):
        row = result_from_response({"id": "Q3", "question_ar": "سؤال"}, {"found": False, "answer": None})
        self.assertTrue(row["abstained"])

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
