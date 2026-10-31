import datetime as dt
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import production_release_gate as gate
from tools.migrate_tenant_fleet import FleetMigrationError
from tools.database_release_acceptance import original_storage_config_fingerprint
from tools.validate_device_browser_acceptance import REQUIRED_RESULTS


class ProductionReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.clean_env = {
            "COPILOT_ENV": "production",
            "COPILOT_OBJECT_STORAGE_BACKEND": "s3",
            "COPILOT_S3_BUCKET": "acceptance-test-bucket",
            "COPILOT_S3_REGION": "us-east-1",
            "COPILOT_S3_KMS_KEY_ID": "test-kms-key",
            "COPILOT_S3_ENDPOINT_URL": "",
            "COPILOT_S3_RECOVERY_BUCKET": "acceptance-recovery-test-bucket",
            "COPILOT_S3_RECOVERY_REGION": "us-east-1",
            "COPILOT_S3_RECOVERY_KMS_KEY_ID": "test-recovery-kms-key",
            "COPILOT_S3_RECOVERY_ENDPOINT_URL": "",
        }
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
            "professional_role": "qualified_egyptian_counsel",
            "jurisdiction": "Egypt",
            "practice_areas": [
                "rent_and_tenancy", "personal_status", "civil_procedure", "civil_law",
                "criminal_procedure", "commercial_law", "tax_law", "social_insurance",
                "real_estate", "data_protection",
            ],
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

    def _database_acceptance_manifest(self):
        verified_at = dt.datetime.now(dt.timezone.utc).isoformat()
        return {
            "schema_version": 1,
            "gates": {
                "original_file_storage": {
                    "status": "passed", "evidence_ref": "synthetic-test-evidence",
                    "verified_at": verified_at, "verified_by": "test-operator",
                    "storage_config_sha256": original_storage_config_fingerprint(self.clean_env),
                },
                "backup_restore_rollback": {
                    "status": "passed", "evidence_ref": "synthetic-test-evidence",
                    "verified_at": verified_at, "verified_by": "test-operator",
                    "witnessed_by": "independent-test-witness",
                    "verified_scenarios": [
                        "staging_restore", "rollback", "staged_upload_recovery", "deletion_recovery",
                    ],
                },
                "retention_export_deletion_policy": {
                    "status": "passed", "evidence_ref": "synthetic-test-evidence",
                    "approved_at": verified_at, "approved_by": "test-policy-owner",
                },
                "production_identity_email": {
                    "status": "passed", "evidence_ref": "synthetic-test-evidence",
                    "verified_at": verified_at, "verified_by": "test-operator",
                },
                "privileged_recovery_bootstrap": {
                    "status": "passed", "evidence_ref": "synthetic-test-evidence",
                    "verified_at": verified_at, "verified_by": "test-operator",
                    "witnessed_by": "independent-test-witness",
                },
                "independent_security_review": {
                    "status": "passed", "evidence_ref": "synthetic-test-evidence",
                    "reviewed_at": verified_at, "reviewer": "independent-test-reviewer",
                    "unresolved_critical_high": 0,
                },
            },
        }

    def _device_acceptance_records(self, commit="a" * 40):
        records = []
        for device_class, locale, suffix in (
            ("desktop", "ar-EG", "130"),
            ("desktop", "en-US", "131"),
            ("phone", "ar-EG", "132"),
            ("phone", "en-US", "133"),
        ):
            records.append({
                "record_version": 1,
                "tested_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "application_commit": commit,
                "environment": "staging",
                "os_and_build": "Synthetic OS build",
                "device": f"Synthetic {device_class} {suffix}",
                "device_class": device_class,
                "browser_and_version": f"Chromium {suffix}",
                "locale": locale,
                "viewport": "1440x900" if device_class == "desktop" else "390x844",
                "network": "online and offline",
                "tester_role": "synthetic acceptance tester",
                "results": {key: "PASS" for key in REQUIRED_RESULTS},
                "defect_ids": [],
                "evidence_paths": [f"restricted-evidence/{device_class}-{locale}.json"],
                "notes": "Synthetic test fixture only; no manual tests were performed.",
            })
        return records

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

    def test_missing_device_acceptance_blocks_release(self):
        report = gate._evaluate_device_acceptance(None, "a" * 40)
        self.assertFalse(report["ready"])
        self.assertIn("not configured", report["error"])

    def test_device_acceptance_must_match_exact_release_commit(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "device-acceptance.json"
            path.write_text(json.dumps(self._device_acceptance_records("b" * 40)), encoding="utf-8")
            report = gate._evaluate_device_acceptance(path, "a" * 40)
        self.assertFalse(report["ready"])
        self.assertIn("does not match expected commit", report["error"])

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
            root = Path(td)
            candidate = self._candidate_file(root)
            acceptance_path = root / "database-acceptance.json"
            acceptance_path.write_text(
                json.dumps(self._database_acceptance_manifest()), encoding="utf-8"
            )
            device_acceptance_path = root / "device-acceptance.json"
            device_acceptance_path.write_text(
                json.dumps(self._device_acceptance_records()), encoding="utf-8"
            )
            release_env = {
                **self.clean_env,
                "COPILOT_DATABASE_ACCEPTANCE_FILE": str(acceptance_path),
                "COPILOT_DEVICE_ACCEPTANCE_FILE": str(device_acceptance_path),
                "COPILOT_RELEASE_COMMIT": "a" * 40,
            }
            with patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])), \
                 patch.object(gate, "build_legal_report", return_value=self._ready_report(candidate)), \
                 patch.object(gate, "read_jsonl", return_value=questions):
                report = gate.evaluate_release(
                    env=release_env,
                    candidate_paths=[candidate],
                    benchmark_path=Path("approved-benchmark.jsonl"),
                    reviewer_registry=self._reviewer_registry(),
                )
        self.assertTrue(report["ready"], report["blockers"])
        self.assertEqual(report["benchmark"]["approved_count"], gate.MIN_APPROVED_QUESTIONS)
        self.assertEqual(report["benchmark"]["practice_area_count"], gate.MIN_PRACTICE_AREAS)
        self.assertEqual(report["benchmark"]["ready_source_count"], 1)

    def test_changed_s3_bucket_invalidates_previously_accepted_storage_evidence(self):
        questions = self._approved_questions()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = self._candidate_file(root)
            acceptance_path = root / "database-acceptance.json"
            acceptance_path.write_text(
                json.dumps(self._database_acceptance_manifest()), encoding="utf-8"
            )
            changed_env = {
                **self.clean_env,
                "COPILOT_S3_BUCKET": "different-bucket",
                "COPILOT_DATABASE_ACCEPTANCE_FILE": str(acceptance_path),
            }
            with patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])), \
                 patch.object(gate, "build_legal_report", return_value=self._ready_report(candidate)), \
                 patch.object(gate, "read_jsonl", return_value=questions):
                report = gate.evaluate_release(
                    env=changed_env,
                    candidate_paths=[candidate],
                    benchmark_path=Path("approved-benchmark.jsonl"),
                    reviewer_registry=self._reviewer_registry(),
                )
        self.assertFalse(report["ready"])
        acceptance = report["database_operational_acceptance"]
        self.assertFalse(acceptance["ready"])
        self.assertIn(
            ("original_file_storage", "storage_configuration_mismatch"),
            {(item["gate"], item["code"]) for item in acceptance["blockers"]},
        )

    def test_release_report_cannot_overwrite_environment_configured_acceptance_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest_path = root / "database-acceptance.json"
            manifest_path.write_text("{}", encoding="utf-8")
            reviewer_path = root / "reviewers.json"
            reviewer_path.write_text(json.dumps(self._reviewer_registry()), encoding="utf-8")
            with patch.dict(os.environ, {"COPILOT_DATABASE_ACCEPTANCE_FILE": str(manifest_path)}), \
                 patch.object(gate, "evaluate_release", return_value={"ready": True}):
                result = gate.main([
                    "--reviewer-registry", str(reviewer_path),
                    "--out", str(manifest_path),
                ])
                self.assertEqual(result, 2)
                self.assertEqual(manifest_path.read_text(encoding="utf-8"), "{}")

    def test_release_report_cannot_overwrite_device_acceptance_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            evidence_path = root / "device-acceptance.json"
            evidence_records = self._device_acceptance_records()
            evidence_path.write_text(json.dumps(evidence_records), encoding="utf-8")
            reviewer_path = root / "reviewers.json"
            reviewer_path.write_text(json.dumps(self._reviewer_registry()), encoding="utf-8")
            with patch.dict(os.environ, {
                "COPILOT_DEVICE_ACCEPTANCE_FILE": str(evidence_path),
                "COPILOT_RELEASE_COMMIT": "a" * 40,
            }), patch.object(gate, "evaluate_release", return_value={"ready": True}):
                result = gate.main([
                    "--reviewer-registry", str(reviewer_path),
                    "--out", str(evidence_path),
                ])
                self.assertEqual(result, 2)
                self.assertEqual(
                    json.loads(evidence_path.read_text(encoding="utf-8")),
                    evidence_records,
                )

    def test_pending_tenant_schema_migrations_block_release(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = self._candidate_file(root)
            acceptance_path = root / "database-acceptance.json"
            acceptance_path.write_text(json.dumps(self._database_acceptance_manifest()), encoding="utf-8")
            release_env = {
                **self.clean_env,
                "COPILOT_DATABASE_ACCEPTANCE_FILE": str(acceptance_path),
                "COPILOT_CONTROL_DB": str(root / "control.sqlite3"),
                "COPILOT_TENANT_DB_ROOT": str(root / "tenants"),
            }
            with patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])), \
                 patch.object(gate, "build_tenant_migration_plan", return_value={
                     "schema": "tenant-fleet-migration-plan/v1",
                     "pending_database_count": 2,
                     "pending_migration_count": 3,
                     "skipped": [],
                     "targets": [],
                 }), \
                 patch.object(gate, "build_legal_report", return_value=self._ready_report(candidate)), \
                 patch.object(gate, "read_jsonl", return_value=self._approved_questions()):
                report = gate.evaluate_release(
                    env=release_env,
                    candidate_paths=[candidate],
                    benchmark_path=Path("approved-benchmark.jsonl"),
                    reviewer_registry=self._reviewer_registry(),
                )
        self.assertFalse(report["ready"])
        self.assertEqual(report["tenant_schema_migrations"]["pending_migration_count"], 3)
        self.assertIn(
            "tenant_schema_migrations_pending",
            {item["code"] for item in report["blockers"]},
        )

    def test_tenant_migration_preflight_error_blocks_release(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            candidate = self._candidate_file(root)
            acceptance_path = root / "database-acceptance.json"
            acceptance_path.write_text(json.dumps(self._database_acceptance_manifest()), encoding="utf-8")
            release_env = {
                **self.clean_env,
                "COPILOT_DATABASE_ACCEPTANCE_FILE": str(acceptance_path),
                "COPILOT_CONTROL_DB": str(root / "control.sqlite3"),
                "COPILOT_TENANT_DB_ROOT": str(root / "tenants"),
            }
            with patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])), \
                 patch.object(gate, "build_tenant_migration_plan", side_effect=FleetMigrationError("catalog unavailable")), \
                 patch.object(gate, "build_legal_report", return_value=self._ready_report(candidate)), \
                 patch.object(gate, "read_jsonl", return_value=self._approved_questions()):
                report = gate.evaluate_release(
                    env=release_env,
                    candidate_paths=[candidate],
                    benchmark_path=Path("approved-benchmark.jsonl"),
                    reviewer_registry=self._reviewer_registry(),
                )
        self.assertFalse(report["ready"])
        self.assertEqual(report["tenant_schema_migrations"]["error"], "catalog unavailable")
        self.assertIn(
            "tenant_schema_migration_preflight_failed",
            {item["code"] for item in report["blockers"]},
        )

    def test_missing_database_operational_acceptance_blocks_otherwise_ready_release(self):
        questions = self._approved_questions()
        with tempfile.TemporaryDirectory() as td:
            candidate = self._candidate_file(Path(td))
            with patch.object(gate, "inspect_environment", return_value=(["environment okay"], [], [])), \
                 patch.object(gate, "build_legal_report", return_value=self._ready_report(candidate)), \
                 patch.object(gate, "read_jsonl", return_value=questions):
                report = gate.evaluate_release(
                    env=self.clean_env,
                    candidate_paths=[candidate],
                    benchmark_path=Path("approved-benchmark.jsonl"),
                    reviewer_registry=self._reviewer_registry(),
                )
        self.assertFalse(report["ready"])
        self.assertFalse(report["database_operational_acceptance"]["ready"])
        self.assertIn(
            "database_operational_acceptance_incomplete",
            {item["code"] for item in report["blockers"]},
        )

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
