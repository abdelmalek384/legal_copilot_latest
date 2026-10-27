import datetime as dt
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import production_release_gate as gate


class ProductionReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.clean_env = {"COPILOT_ENV": "production"}
        self.legal_report = {
            "ready_count": 1,
            "blocked_count": 0,
            "candidates": [{"ready": True, "blockers": []}],
        }

    def _approved_questions(self):
        today = dt.date.today().isoformat()
        areas = [
            "rent_and_tenancy", "personal_status", "civil_procedure", "civil_law",
            "criminal_procedure", "commercial_law", "tax_law", "social_insurance",
            "real_estate", "data_protection",
        ]
        return [
            {
                "id": f"Q-{i:03d}",
                "practice_area": areas[i % len(areas)],
                "review_status": "lawyer_approved",
                "reviewer_name": "Qualified Egyptian counsel",
                "reviewer_role": "qualified_egyptian_counsel",
                "review_evidence_url": "https://example.gov/review-record",
                "review_date": today,
                "answerable": True,
                "expected_answer": "Reviewed expected answer.",
                "expected_sources": ["SRC-1"],
                "expected_pin_cites": [{"source_id": "SRC-1", "pin_cite": "Article 1"}],
            }
            for i in range(gate.MIN_APPROVED_QUESTIONS)
        ]

    def test_unreviewed_default_draft_benchmark_blocks_release(self):
        with patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])), \
             patch.object(gate, "build_legal_report", return_value=self.legal_report):
            report = gate.evaluate_release(
                env=self.clean_env,
                candidate_paths=[Path("candidate.json")],
                benchmark_path=gate.DEFAULT_BENCHMARK,
            )
        self.assertFalse(report["ready"])
        self.assertEqual(report["benchmark"]["question_count"], 94)
        self.assertEqual(report["benchmark"]["unreviewed_count"], 94)
        codes = {blocker["code"] for blocker in report["blockers"]}
        self.assertIn("unreviewed_questions_present", codes)
        self.assertIn("benchmark_below_minimum", codes)

    def test_missing_candidates_blocks_release_even_with_other_gates_mocked_clean(self):
        with patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])):
            report = gate.evaluate_release(
                env=self.clean_env, candidate_paths=[], benchmark_path=gate.DEFAULT_BENCHMARK
            )
        self.assertFalse(report["ready"])
        self.assertIn("no_candidates", {blocker["code"] for blocker in report["blockers"]})

    def test_all_gates_must_pass_for_release_ready(self):
        questions = self._approved_questions()
        with patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])), \
             patch.object(gate, "build_legal_report", return_value=self.legal_report), \
             patch.object(gate, "read_jsonl", return_value=questions):
            report = gate.evaluate_release(
                env=self.clean_env,
                candidate_paths=[Path("candidate.json")],
                benchmark_path=Path("approved-benchmark.jsonl"),
            )
        self.assertTrue(report["ready"], report["blockers"])
        self.assertEqual(report["benchmark"]["approved_count"], gate.MIN_APPROVED_QUESTIONS)
        self.assertEqual(report["benchmark"]["practice_area_count"], gate.MIN_PRACTICE_AREAS)

    def test_invalid_lawyer_approved_question_blocks_release(self):
        questions = self._approved_questions()
        questions[0]["review_date"] = "2999-01-01"
        with patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])), \
             patch.object(gate, "build_legal_report", return_value=self.legal_report), \
             patch.object(gate, "read_jsonl", return_value=questions):
            report = gate.evaluate_release(
                env=self.clean_env,
                candidate_paths=[Path("candidate.json")],
                benchmark_path=Path("approved-benchmark.jsonl"),
            )
        self.assertFalse(report["ready"])
        self.assertEqual(report["benchmark"]["invalid_approved_count"], 1)
        self.assertIn("approved_questions_invalid", {blocker["code"] for blocker in report["blockers"]})

    def test_environment_warnings_are_release_blockers(self):
        with patch.object(gate, "inspect_environment", return_value=([], ["warning"], ["error"])), \
             patch.object(gate, "build_legal_report", return_value=self.legal_report), \
             patch.object(gate, "read_jsonl", return_value=self._approved_questions()):
            report = gate.evaluate_release(
                env=self.clean_env,
                candidate_paths=[Path("candidate.json")],
                benchmark_path=Path("approved-benchmark.jsonl"),
            )
        self.assertFalse(report["ready"])
        self.assertIn("environment_errors", {blocker["code"] for blocker in report["blockers"]})
        self.assertIn("environment_warnings", {blocker["code"] for blocker in report["blockers"]})


if __name__ == "__main__":
    unittest.main()
