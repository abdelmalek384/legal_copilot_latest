import datetime as dt
import json
import tempfile
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

    def _reviewer_registry(self):
        return {"reviewers": [{
            "reviewer_id": "reviewer-test",
            "display_name": "Qualified Egyptian counsel",
            "status": "approved",
            "qualification_basis": "Synthetic fixture: counsel qualification checked",
            "evidence_reference": "private-test-reference",
            "verified_by": "test-operator",
            "verified_on": dt.date.today().isoformat(),
        }]}

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
                "as_of_date": today,
                "review_status": "lawyer_approved",
                "reviewer_id": "reviewer-test",
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

    def _candidate_file(self, root, name="candidate.json", source_id="SRC-1",
                         anchors=None, effective_date="2020-01-01", repeal_date=None,
                         legal_status="in_force"):
        path = root / name
        path.write_text(json.dumps({
            "document": {"source_id": source_id},
            "version": {
                "effective_date": effective_date,
                "repeal_date": repeal_date,
                "legal_status": legal_status,
                "article_identifiers": anchors if anchors is not None else ["Article 1"],
            },
        }), encoding="utf-8")
        return path

    def _ready_report(self, candidate_path):
        return self._ready_report_many([candidate_path])

    def _ready_report_many(self, candidate_paths):
        return {
            "ready_count": len(candidate_paths),
            "blocked_count": 0,
            "candidates": [{
                "ready": True,
                "blockers": [],
                "candidate_file": str(path),
            } for path in candidate_paths],
        }

    def test_unreviewed_default_draft_benchmark_blocks_release(self):
        with patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])), \
             patch.object(gate, "build_legal_report", return_value=self.legal_report):
            report = gate.evaluate_release(
                env=self.clean_env,
                candidate_paths=[Path("candidate.json")],
                benchmark_path=gate.DEFAULT_BENCHMARK, reviewer_registry=self._reviewer_registry(),
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
        with tempfile.TemporaryDirectory() as td:
            candidate = self._candidate_file(Path(td))
            with patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])), \
                 patch.object(gate, "build_legal_report", return_value=self._ready_report(candidate)), \
                 patch.object(gate, "read_jsonl", return_value=questions):
                report = gate.evaluate_release(
                    env=self.clean_env,
                    candidate_paths=[candidate],
                    benchmark_path=Path("approved-benchmark.jsonl"), reviewer_registry=self._reviewer_registry(),
                )
        self.assertTrue(report["ready"], report["blockers"])
        self.assertEqual(report["benchmark"]["approved_count"], gate.MIN_APPROVED_QUESTIONS)
        self.assertEqual(report["benchmark"]["practice_area_count"], gate.MIN_PRACTICE_AREAS)
        self.assertEqual(report["benchmark"]["ready_source_count"], 1)

    def test_benchmark_sources_must_exist_in_ready_corpus(self):
        questions = self._approved_questions()
        questions[0]["expected_sources"] = ["SRC-OTHER"]
        questions[0]["expected_pin_cites"] = [{"source_id": "SRC-OTHER", "pin_cite": "Article 1"}]
        with tempfile.TemporaryDirectory() as td:
            candidate = self._candidate_file(Path(td))
            with patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])), \
                 patch.object(gate, "build_legal_report", return_value=self._ready_report(candidate)), \
                 patch.object(gate, "read_jsonl", return_value=questions):
                report = gate.evaluate_release(
                    env=self.clean_env, candidate_paths=[candidate], benchmark_path=Path("approved-benchmark.jsonl"), reviewer_registry=self._reviewer_registry()
                )
        self.assertFalse(report["ready"])
        self.assertIn("benchmark_sources_not_in_ready_corpus", {b["code"] for b in report["blockers"]})

    def test_benchmark_pin_cites_must_match_ready_corpus_anchors(self):
        questions = self._approved_questions()
        questions[0]["expected_pin_cites"] = [{"source_id": "SRC-1", "pin_cite": "Article 99"}]
        with tempfile.TemporaryDirectory() as td:
            candidate = self._candidate_file(Path(td))
            with patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])), \
                 patch.object(gate, "build_legal_report", return_value=self._ready_report(candidate)), \
                 patch.object(gate, "read_jsonl", return_value=questions):
                report = gate.evaluate_release(
                    env=self.clean_env, candidate_paths=[candidate], benchmark_path=Path("approved-benchmark.jsonl"), reviewer_registry=self._reviewer_registry()
                )
        self.assertFalse(report["ready"])
        self.assertIn("benchmark_pin_cites_not_in_ready_corpus", {b["code"] for b in report["blockers"]})

    def test_historical_status_without_repeal_date_is_excluded_even_if_report_says_ready(self):
        questions = self._approved_questions()
        with tempfile.TemporaryDirectory() as td:
            candidate = self._candidate_file(Path(td), legal_status="historical")
            with (
                patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])),
                patch.object(gate, "build_legal_report", return_value=self._ready_report(candidate)),
                patch.object(gate, "read_jsonl", return_value=questions),
            ):
                report = gate.evaluate_release(
                    env=self.clean_env, candidate_paths=[candidate], benchmark_path=Path("approved-benchmark.jsonl"), reviewer_registry=self._reviewer_registry()
                )
        self.assertFalse(report["ready"])
        self.assertEqual(report["benchmark"]["ready_source_count"], 0)
        self.assertIn("benchmark_sources_not_in_ready_corpus", {b["code"] for b in report["blockers"]})

    def test_benchmark_source_version_must_be_active_on_question_date(self):
        questions = self._approved_questions()
        with tempfile.TemporaryDirectory() as td:
            candidate = self._candidate_file(Path(td), repeal_date="2026-01-01")
            with patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])), \
                 patch.object(gate, "build_legal_report", return_value=self._ready_report(candidate)), \
                 patch.object(gate, "read_jsonl", return_value=questions):
                report = gate.evaluate_release(
                    env=self.clean_env, candidate_paths=[candidate], benchmark_path=Path("approved-benchmark.jsonl"), reviewer_registry=self._reviewer_registry()
                )
        self.assertFalse(report["ready"])
        self.assertIn("benchmark_sources_not_in_ready_corpus", {b["code"] for b in report["blockers"]})

    def test_overlapping_active_versions_block_benchmark_release(self):
        questions = self._approved_questions()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = self._candidate_file(root, "first.json", anchors=["Article 1"])
            second = self._candidate_file(root, "second.json", anchors=["Article 2"])
            with patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])), \
                 patch.object(gate, "build_legal_report", return_value=self._ready_report_many([first, second])), \
                 patch.object(gate, "read_jsonl", return_value=questions):
                report = gate.evaluate_release(
                    env=self.clean_env, candidate_paths=[first, second], benchmark_path=Path("approved-benchmark.jsonl"), reviewer_registry=self._reviewer_registry()
                )
        self.assertFalse(report["ready"])
        self.assertIn("benchmark_sources_not_in_ready_corpus", {b["code"] for b in report["blockers"]})
        self.assertGreater(report["benchmark"]["unlinked_expected_source_count"], 0)

    def test_invalid_lawyer_approved_question_blocks_release(self):
        questions = self._approved_questions()
        questions[0]["review_date"] = "2999-01-01"
        with tempfile.TemporaryDirectory() as td:
            candidate = self._candidate_file(Path(td))
            with patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])), \
                 patch.object(gate, "build_legal_report", return_value=self._ready_report(candidate)), \
                 patch.object(gate, "read_jsonl", return_value=questions):
                report = gate.evaluate_release(
                    env=self.clean_env, candidate_paths=[candidate], benchmark_path=Path("approved-benchmark.jsonl"), reviewer_registry=self._reviewer_registry()
                )
        self.assertFalse(report["ready"])
        self.assertEqual(report["benchmark"]["invalid_approved_count"], 1)
        self.assertIn("approved_questions_invalid", {blocker["code"] for blocker in report["blockers"]})

    def test_environment_warnings_are_release_blockers(self):
        questions = self._approved_questions()
        with tempfile.TemporaryDirectory() as td:
            candidate = self._candidate_file(Path(td))
            with patch.object(gate, "inspect_environment", return_value=([], ["warning"], ["error"])), \
                 patch.object(gate, "build_legal_report", return_value=self._ready_report(candidate)), \
                 patch.object(gate, "read_jsonl", return_value=questions):
                report = gate.evaluate_release(
                    env=self.clean_env, candidate_paths=[candidate], benchmark_path=Path("approved-benchmark.jsonl"), reviewer_registry=self._reviewer_registry()
                )
        self.assertFalse(report["ready"])
        self.assertIn("environment_errors", {blocker["code"] for blocker in report["blockers"]})
        self.assertIn("environment_warnings", {blocker["code"] for blocker in report["blockers"]})


if __name__ == "__main__":
    unittest.main()
