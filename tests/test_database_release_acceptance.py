import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from s3_original_file_storage import S3PrivateObjectStore
from tools.purge_approved_original_files import _validate_s3_apply_authorization
from tools.database_release_acceptance import (
    REQUIRED_GATES,
    load_acceptance_manifest,
    load_staging_purge_acceptance_manifest,
    original_storage_config_fingerprint,
    validate_acceptance_manifest,
)


class DatabaseReleaseAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
        stamp = self.now.isoformat()
        self.manifest = {
            "schema_version": 1,
            "gates": {
                "original_file_storage": {
                    "status": "passed", "evidence_ref": "private-evidence://storage",
                    "verified_at": stamp, "verified_by": "operator-a",
                    "storage_config_sha256": "a" * 64,
                },
                "backup_restore_rollback": {
                    "status": "passed", "evidence_ref": "private-evidence://restore",
                    "verified_at": stamp, "verified_by": "operator-a",
                    "witnessed_by": "witness-b",
                    "verified_scenarios": [
                        "staging_restore", "rollback", "staged_upload_recovery", "deletion_recovery",
                    ],
                },
                "retention_export_deletion_policy": {
                    "status": "passed", "evidence_ref": "private-evidence://policy",
                    "approved_at": stamp, "approved_by": "policy-owner",
                },
                "production_identity_email": {
                    "status": "passed", "evidence_ref": "private-evidence://email",
                    "verified_at": stamp, "verified_by": "operator-a",
                },
                "privileged_recovery_bootstrap": {
                    "status": "passed", "evidence_ref": "private-evidence://bootstrap",
                    "verified_at": stamp, "verified_by": "operator-a",
                    "witnessed_by": "witness-b",
                },
                "independent_security_review": {
                    "status": "passed", "evidence_ref": "private-evidence://security",
                    "reviewed_at": stamp, "reviewer": "independent-reviewer",
                    "unresolved_critical_high": 0,
                },
            },
        }

    def test_complete_manifest_passes(self):
        report = validate_acceptance_manifest(self.manifest, now=self.now)
        self.assertTrue(report["ready"], report["blockers"])
        self.assertEqual(report["passed_count"], len(REQUIRED_GATES))
        self.assertEqual(report["required_count"], len(REQUIRED_GATES))
        self.assertEqual(report["blockers"], [])

    def test_storage_config_fingerprint_is_stable_and_changes_with_target(self):
        config = {
            "COPILOT_OBJECT_STORAGE_BACKEND": "s3",
            "COPILOT_S3_BUCKET": "bucket-a",
            "COPILOT_S3_REGION": "us-east-1",
            "COPILOT_S3_KMS_KEY_ID": "key-a",
            "COPILOT_S3_ENDPOINT_URL": "",
        }
        first = original_storage_config_fingerprint(config)
        self.assertRegex(first or "", r"^[0-9a-f]{64}$")
        self.assertEqual(first, original_storage_config_fingerprint(dict(config)))
        changed = dict(config, COPILOT_S3_BUCKET="bucket-b")
        self.assertNotEqual(first, original_storage_config_fingerprint(changed))
        self.assertIsNone(original_storage_config_fingerprint({}))

    def test_storage_acceptance_is_bound_to_current_s3_kms_configuration(self):
        matched = validate_acceptance_manifest(
            self.manifest, now=self.now, expected_storage_config_sha256="a" * 64
        )
        self.assertTrue(matched["ready"], matched["blockers"])

        changed = validate_acceptance_manifest(
            self.manifest, now=self.now, expected_storage_config_sha256="b" * 64
        )
        self.assertFalse(changed["ready"])
        self.assertIn(
            ("original_file_storage", "storage_configuration_mismatch"),
            {(item["gate"], item["code"]) for item in changed["blockers"]},
        )

        unavailable = validate_acceptance_manifest(
            self.manifest, now=self.now, expected_storage_config_sha256=""
        )
        self.assertFalse(unavailable["ready"])
        self.assertIn(
            ("original_file_storage", "storage_configuration_unavailable"),
            {(item["gate"], item["code"]) for item in unavailable["blockers"]},
        )

    def test_staging_purge_requires_storage_and_retention_evidence_bound_to_target(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "acceptance.json"
            path.write_text(json.dumps(self.manifest), encoding="utf-8")
            report = load_staging_purge_acceptance_manifest(
                path, expected_storage_config_sha256="a" * 64, now=self.now
            )
            self.assertTrue(report["ready"], report["blockers"])
            self.assertEqual(report["passed_count"], 2)
            self.assertEqual(report["required_count"], 2)

            changed_target = load_staging_purge_acceptance_manifest(
                path, expected_storage_config_sha256="b" * 64, now=self.now
            )
            self.assertFalse(changed_target["ready"])
            self.assertIn(
                ("original_file_storage", "storage_target_mismatch"),
                {(item["gate"], item["code"]) for item in changed_target["blockers"]},
            )

    def test_staging_purge_rejects_missing_or_expired_policy_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "acceptance.json"
            manifest = json.loads(json.dumps(self.manifest))
            manifest["gates"]["retention_export_deletion_policy"]["status"] = "pending"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            pending = load_staging_purge_acceptance_manifest(
                path, expected_storage_config_sha256="a" * 64, now=self.now
            )
            self.assertFalse(pending["ready"])
            self.assertIn(
                ("retention_export_deletion_policy", "not_passed"),
                {(item["gate"], item["code"]) for item in pending["blockers"]},
            )

            path.write_text(json.dumps(self.manifest), encoding="utf-8")
            expired = load_staging_purge_acceptance_manifest(
                path, expected_storage_config_sha256="a" * 64,
                now=self.now + timedelta(days=366),
            )
            self.assertFalse(expired["ready"])
            self.assertIn(
                ("retention_export_deletion_policy", "evidence_expired"),
                {(item["gate"], item["code"]) for item in expired["blockers"]},
            )

    def test_staging_purge_rejects_boolean_schema_version(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "acceptance.json"
            manifest = json.loads(json.dumps(self.manifest))
            manifest["schema_version"] = True
            path.write_text(json.dumps(manifest), encoding="utf-8")
            report = load_staging_purge_acceptance_manifest(
                path, expected_storage_config_sha256="a" * 64, now=self.now
            )
        self.assertFalse(report["ready"])
        self.assertIn(
            ("manifest", "invalid_manifest"),
            {(item["gate"], item["code"]) for item in report["blockers"]},
        )

    def test_staging_purge_rejects_naive_current_time_without_exception(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "acceptance.json"
            path.write_text(json.dumps(self.manifest), encoding="utf-8")
            report = load_staging_purge_acceptance_manifest(
                path,
                expected_storage_config_sha256="a" * 64,
                now=datetime(2026, 10, 28, 12, 0),
            )
        self.assertFalse(report["ready"])
        self.assertIn(
            ("manifest", "current_time_must_be_timezone_aware"),
            {(item["gate"], item["code"]) for item in report["blockers"]},
        )

    def test_staging_purge_rejects_placeholder_evidence_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "acceptance.json"
            manifest = json.loads(json.dumps(self.manifest))
            manifest["gates"]["retention_export_deletion_policy"]["evidence_ref"] = "PENDING"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            report = load_staging_purge_acceptance_manifest(
                path, expected_storage_config_sha256="a" * 64, now=self.now
            )
        self.assertFalse(report["ready"])
        self.assertIn(
            ("retention_export_deletion_policy", "invalid_evidence_reference"),
            {(item["gate"], item["code"]) for item in report["blockers"]},
        )

    def test_staging_purge_rejects_invalid_expected_storage_fingerprint(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "acceptance.json"
            path.write_text(json.dumps(self.manifest), encoding="utf-8")
            report = load_staging_purge_acceptance_manifest(
                path, expected_storage_config_sha256="not-a-sha256", now=self.now
            )
        self.assertFalse(report["ready"])
        self.assertIn(
            ("manifest", "storage_configuration_unavailable"),
            {(item["gate"], item["code"]) for item in report["blockers"]},
        )

    def test_core_s3_purge_authorization_requires_production_manifest(self):
        key = "arn:aws:kms:eu-central-1:123456789012:key/test-key"

        class FakeKms:
            meta = SimpleNamespace(region_name="eu-central-1")

            def describe_key(self, **kwargs):
                return {"KeyMetadata": {"KeyId": key, "Arn": key}}

        client = SimpleNamespace(meta=SimpleNamespace(
            region_name="eu-central-1",
            endpoint_url="https://s3.eu-central-1.amazonaws.com",
        ))
        store = S3PrivateObjectStore(
            client, bucket="private-bucket", kms_key_id=key, kms_client=FakeKms()
        )
        environment = {
            "COPILOT_ENV": "production",
            "COPILOT_OBJECT_STORAGE_BACKEND": "s3",
            "COPILOT_S3_BUCKET": "private-bucket",
            "COPILOT_S3_REGION": "eu-central-1",
            "COPILOT_S3_KMS_KEY_ID": key,
            "COPILOT_S3_ENDPOINT_URL": "",
            "COPILOT_DATABASE_ACCEPTANCE_FILE": "/nonexistent/acceptance.json",
        }
        with patch.dict(os.environ, environment, clear=True):
            with self.assertRaisesRegex(RuntimeError, "incomplete or stale acceptance"):
                _validate_s3_apply_authorization(12, store, staging_drill=False)

    def test_core_s3_purge_authorization_rejects_development_and_wrong_staging_target(self):
        key = "arn:aws:kms:eu-central-1:123456789012:key/test-key"

        class FakeKms:
            meta = SimpleNamespace(region_name="eu-central-1")

            def describe_key(self, **kwargs):
                return {"KeyMetadata": {"KeyId": key, "Arn": key}}

        client = SimpleNamespace(meta=SimpleNamespace(
            region_name="eu-central-1",
            endpoint_url="https://s3.eu-central-1.amazonaws.com",
        ))
        store = S3PrivateObjectStore(
            client, bucket="private-bucket", kms_key_id=key, kms_client=FakeKms()
        )
        base = {
            "COPILOT_OBJECT_STORAGE_BACKEND": "s3",
            "COPILOT_S3_BUCKET": "private-bucket",
            "COPILOT_S3_REGION": "eu-central-1",
            "COPILOT_S3_KMS_KEY_ID": key,
            "COPILOT_S3_ENDPOINT_URL": "",
            "COPILOT_DATABASE_ACCEPTANCE_FILE": "/nonexistent/acceptance.json",
        }
        with patch.dict(os.environ, dict(base, COPILOT_ENV="development"), clear=True):
            with self.assertRaisesRegex(RuntimeError, "restricted to accepted production"):
                _validate_s3_apply_authorization(12, store, staging_drill=False)
        staging = dict(
            base,
            COPILOT_ENV="staging",
            COPILOT_S3_PURGE_STAGING_BUCKET="different-bucket",
            COPILOT_S3_PURGE_STAGING_FIRM_ID="12",
        )
        with patch.dict(os.environ, staging, clear=True):
            with self.assertRaisesRegex(RuntimeError, "explicit bucket/firm allowlist"):
                _validate_s3_apply_authorization(12, store, staging_drill=True)

    def test_missing_or_pending_gates_block_release(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["gates"]["backup_restore_rollback"]["status"] = "pending"
        del manifest["gates"]["production_identity_email"]
        report = validate_acceptance_manifest(manifest, now=self.now)
        self.assertFalse(report["ready"])
        codes = {(item["gate"], item["code"]) for item in report["blockers"]}
        self.assertIn(("backup_restore_rollback", "not_passed"), codes)
        self.assertIn(("production_identity_email", "evidence_missing"), codes)


    def test_backup_restore_gate_requires_each_recovery_scenario(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["gates"]["backup_restore_rollback"]["verified_scenarios"].remove(
            "staged_upload_recovery"
        )
        report = validate_acceptance_manifest(manifest, now=self.now)
        self.assertFalse(report["ready"])
        self.assertIn(
            ("backup_restore_rollback", "required_scenarios_missing"),
            {(item["gate"], item["code"]) for item in report["blockers"]},
        )

    def test_backup_restore_gate_rejects_malformed_scenario_evidence(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["gates"]["backup_restore_rollback"]["verified_scenarios"] = "all passed"
        report = validate_acceptance_manifest(manifest, now=self.now)
        self.assertFalse(report["ready"])
        self.assertIn(
            ("backup_restore_rollback", "invalid_verified_scenarios"),
            {(item["gate"], item["code"]) for item in report["blockers"]},
        )


    def test_witness_must_be_distinct_from_operator(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["gates"]["backup_restore_rollback"]["witnessed_by"] = "OPERATOR-A"
        report = validate_acceptance_manifest(manifest, now=self.now)
        self.assertFalse(report["ready"])
        self.assertIn(
            ("backup_restore_rollback", "independent_witness_required"),
            {(item["gate"], item["code"]) for item in report["blockers"]},
        )

    def test_security_review_requires_zero_unresolved_critical_or_high_findings(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["gates"]["independent_security_review"]["unresolved_critical_high"] = 1
        report = validate_acceptance_manifest(manifest, now=self.now)
        self.assertFalse(report["ready"])
        self.assertIn(
            ("independent_security_review", "unresolved_critical_or_high_findings"),
            {(item["gate"], item["code"]) for item in report["blockers"]},
        )

    def test_independent_security_reviewer_cannot_be_an_operator(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["gates"]["independent_security_review"]["reviewer"] = "OPERATOR-A"
        report = validate_acceptance_manifest(manifest, now=self.now)
        self.assertFalse(report["ready"])
        self.assertIn(
            ("independent_security_review", "reviewer_not_independent_of_operators"),
            {(item["gate"], item["code"]) for item in report["blockers"]},
        )

    def test_timestamps_must_have_timezone_and_cannot_be_in_future(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["gates"]["original_file_storage"]["verified_at"] = "2026-10-28T12:00:00"
        report = validate_acceptance_manifest(manifest, now=self.now)
        self.assertFalse(report["ready"])
        self.assertIn(
            ("original_file_storage", "invalid_or_timezone_free_timestamp"),
            {(item["gate"], item["code"]) for item in report["blockers"]},
        )

        manifest = json.loads(json.dumps(self.manifest))
        manifest["gates"]["original_file_storage"]["verified_at"] = "2026-11-01T12:00:00+00:00"
        report = validate_acceptance_manifest(manifest, now=self.now)
        self.assertIn(
            ("original_file_storage", "evidence_timestamp_in_future"),
            {(item["gate"], item["code"]) for item in report["blockers"]},
        )

    def test_stale_operational_evidence_blocks_release(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["gates"]["original_file_storage"]["verified_at"] = (
            self.now - timedelta(days=91)
        ).isoformat()
        manifest["gates"]["production_identity_email"]["verified_at"] = (
            self.now - timedelta(days=91)
        ).isoformat()
        manifest["gates"]["independent_security_review"]["reviewed_at"] = (
            self.now - timedelta(days=91)
        ).isoformat()
        # The approved policy has a longer but still finite review window.
        manifest["gates"]["retention_export_deletion_policy"]["approved_at"] = (
            self.now - timedelta(days=366)
        ).isoformat()
        report = validate_acceptance_manifest(manifest, now=self.now)
        codes = {(item["gate"], item["code"]) for item in report["blockers"]}
        self.assertIn(("original_file_storage", "evidence_expired"), codes)
        self.assertIn(("production_identity_email", "evidence_expired"), codes)
        self.assertIn(("independent_security_review", "evidence_expired"), codes)
        self.assertIn(("retention_export_deletion_policy", "evidence_expired"), codes)
        self.assertFalse(report["ready"])

    def test_operational_evidence_at_freshness_boundary_is_accepted(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["gates"]["original_file_storage"]["verified_at"] = (
            self.now - timedelta(days=90)
        ).isoformat()
        report = validate_acceptance_manifest(manifest, now=self.now)
        self.assertNotIn(
            ("original_file_storage", "evidence_expired"),
            {(item["gate"], item["code"]) for item in report["blockers"]},
        )

    def test_loader_fails_closed_for_missing_or_malformed_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            missing = load_acceptance_manifest(Path(td) / "missing.json", now=self.now)
            malformed_path = Path(td) / "malformed.json"
            malformed_path.write_text("{not json", encoding="utf-8")
            malformed = load_acceptance_manifest(malformed_path, now=self.now)
        self.assertFalse(missing["ready"])
        self.assertIn("manifest_not_found", {item["code"] for item in missing["blockers"]})
        self.assertFalse(malformed["ready"])
        self.assertIn(
            "manifest_unreadable_or_invalid_json",
            {item["code"] for item in malformed["blockers"]},
        )

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO creation is unavailable on this platform")
    def test_loader_rejects_fifo_manifest_without_blocking(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "acceptance.fifo"
            os.mkfifo(path)
            report = load_acceptance_manifest(path, now=self.now)
        self.assertFalse(report["ready"])
        self.assertIn(
            ("manifest", "manifest_not_regular_file"),
            {(item["gate"], item["code"]) for item in report["blockers"]},
        )

    def test_loader_rejects_symlinked_acceptance_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            real = root / "real.json"
            real.write_text(json.dumps(self.manifest), encoding="utf-8")
            link = root / "acceptance.json"
            try:
                link.symlink_to(real)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation is unavailable on this platform")
            report = load_acceptance_manifest(link, now=self.now)
        self.assertFalse(report["ready"])
        self.assertIn(
            ("manifest", "manifest_symlink_forbidden"),
            {(item["gate"], item["code"]) for item in report["blockers"]},
        )

    @unittest.skipUnless(os.name == "posix", "POSIX permission bits are not portable")
    def test_loader_rejects_group_or_other_writable_acceptance_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "acceptance.json"
            path.write_text(json.dumps(self.manifest), encoding="utf-8")
            path.chmod(0o664)
            report = load_acceptance_manifest(path, now=self.now)
        self.assertFalse(report["ready"])
        self.assertIn(
            ("manifest", "manifest_group_or_other_writable"),
            {(item["gate"], item["code"]) for item in report["blockers"]},
        )

    def test_loader_rejects_oversized_acceptance_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "acceptance.json"
            path.write_text(" " * 1_000_001, encoding="utf-8")
            report = load_acceptance_manifest(path, now=self.now)
        self.assertFalse(report["ready"])
        self.assertIn(
            ("manifest", "manifest_too_large"),
            {(item["gate"], item["code"]) for item in report["blockers"]},
        )

    def test_reports_never_echo_private_evidence_references(self):
        manifest = json.loads(json.dumps(self.manifest))
        manifest["gates"]["original_file_storage"]["evidence_ref"] = "SECRET-DO-NOT-ECHO"
        manifest["gates"]["original_file_storage"]["status"] = "pending"
        report = validate_acceptance_manifest(manifest, now=self.now)
        self.assertNotIn("SECRET-DO-NOT-ECHO", json.dumps(report))

    def test_template_is_pending_by_default(self):
        template = Path(__file__).resolve().parents[1] / "docs" / "database_release_acceptance.template.json"
        report = load_acceptance_manifest(template, now=self.now)
        self.assertFalse(report["ready"])
        self.assertEqual(report["passed_count"], 0)
        self.assertEqual(report["required_count"], len(REQUIRED_GATES))


if __name__ == "__main__":
    unittest.main()
