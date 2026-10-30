"""Tests for the local-only manual capture provenance validator."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.validate_manual_capture_record import validate_capture_record


class ManualCaptureRecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.original = self.root / "gazette.txt"
        self.original.write_bytes("قانون تجريبي؛ ليس نصاً قانونياً حقيقياً".encode("utf-8"))
        self.record_path = self.root / "capture.json"
        self.record = {
            "document_id": "EG-TEST-1",
            "official_title": "قانون تجريبي (بيانات اختبار فقط)",
            "source_authority": "Example authority",
            "source_url": "https://example.gov/source",
            "retrieved_at": "2026-10-27T12:00:00Z",
            "acquisition_method": "manual",
            "original_file": "gazette.txt",
            "original_sha256": hashlib.sha256(self.original.read_bytes()).hexdigest(),
            "collection_permission": "unknown",
            "commercial_reuse_permission": "unknown",
            "terms_url": None,
            "terms_checked_on": None,
            "collection_permission_evidence_url": None,
            "commercial_reuse_evidence_url": None,
            "legal_status": "unknown",
            "review_status": "pending_source_review",
        }

    def test_claimed_verified_status_never_makes_capture_retrieval_eligible(self):
        self.record["legal_status"] = "in_force"
        self.record["review_status"] = "verified"
        result = validate_capture_record(self.record, self.record_path)
        self.assertTrue(result["valid"])
        self.assertFalse(result["retrieval_eligible"])
        self.assertTrue(any("never verifies legal authenticity" in warning for warning in result["warnings"]))

    def test_unsupported_legal_status_is_rejected(self):
        self.record["legal_status"] = "current_verified"
        result = validate_capture_record(self.record, self.record_path)
        self.assertFalse(result["valid"])
        self.assertIn("legal_status has an unsupported value", result["errors"])

    def test_valid_hash_proves_integrity_only_not_retrieval_eligibility(self):
        result = validate_capture_record(self.record, self.record_path)
        self.assertTrue(result["valid"])
        self.assertTrue(result["provenance_valid"])
        self.assertFalse(result["collection_ready"])
        self.assertFalse(result["commercial_product_use_ready"])
        self.assertFalse(result["retrieval_eligible"])

    def test_hash_mismatch_is_rejected(self):
        self.record["original_sha256"] = "0" * 64
        result = validate_capture_record(self.record, self.record_path)
        self.assertFalse(result["valid"])
        self.assertIn("original_sha256 does not match the original file bytes", result["errors"])

    def test_path_traversal_is_rejected(self):
        self.record["original_file"] = "../outside.txt"
        result = validate_capture_record(self.record, self.record_path)
        self.assertFalse(result["valid"])
        self.assertTrue(any("safe relative path" in error for error in result["errors"]))

    def test_symlink_original_is_rejected(self):
        link = self.root / "linked.txt"
        link.symlink_to(self.original)
        self.record["original_file"] = "linked.txt"
        self.record["original_sha256"] = hashlib.sha256(self.original.read_bytes()).hexdigest()
        result = validate_capture_record(self.record, self.record_path)
        self.assertFalse(result["valid"])
        self.assertTrue(any("symbolic links" in error for error in result["errors"]))

    def test_malformed_source_url_and_naive_timestamp_are_rejected(self):
        self.record["source_url"] = "https://user:pass@example.gov/source"
        self.record["retrieved_at"] = "2026-10-27T12:00:00"
        result = validate_capture_record(self.record, self.record_path)
        self.assertFalse(result["valid"])
        self.assertTrue(any("source_url" in error for error in result["errors"]))
        self.assertTrue(any("retrieved_at" in error for error in result["errors"]))

    def test_future_retrieval_and_terms_review_dates_are_rejected(self):
        self.record["retrieved_at"] = "2999-01-01T00:00:00Z"
        self.record["terms_checked_on"] = "2999-01-01"
        result = validate_capture_record(self.record, self.record_path)
        self.assertFalse(result["valid"])
        self.assertIn("retrieved_at must not be in the future", result["errors"])
        self.assertIn("terms_checked_on must not be in the future", result["errors"])

    def test_non_calendar_iso_date_formats_are_rejected(self):
        self.record["publication_date"] = "2026-W44-2"
        result = validate_capture_record(self.record, self.record_path)
        self.assertFalse(result["valid"])
        self.assertTrue(any("publication_date" in error for error in result["errors"]))

    def test_non_string_permission_states_are_rejected_without_crashing(self):
        self.record["collection_permission"] = []
        self.record["commercial_reuse_permission"] = {}
        result = validate_capture_record(self.record, self.record_path)
        self.assertFalse(result["valid"])
        self.assertTrue(any("collection_permission" in error for error in result["errors"]))
        self.assertTrue(any("commercial_reuse_permission" in error for error in result["errors"]))

    def test_limited_or_permission_required_states_never_pass_unrestricted_gates(self):
        self.record.update({
            "collection_permission": "allowed_limited",
            "commercial_reuse_permission": "prior_written_permission_required_per_published_terms",
            "terms_url": "https://example.gov/terms",
            "terms_checked_on": "2026-10-27",
            "collection_permission_evidence_url": "https://example.gov/permission/limited",
            "commercial_reuse_evidence_url": "https://example.gov/permission/request-required",
        })
        result = validate_capture_record(self.record, self.record_path)
        self.assertTrue(result["valid"])
        self.assertFalse(result["collection_ready"])
        self.assertFalse(result["commercial_product_use_ready"])
        self.assertFalse(result["retrieval_eligible"])

    def test_stale_terms_review_blocks_permission_readiness(self):
        self.record.update({
            "collection_permission": "allowed",
            "commercial_reuse_permission": "allowed",
            "terms_url": "https://example.gov/terms",
            "terms_checked_on": "2025-01-01",
            "collection_permission_evidence_url": "https://example.gov/permission/collection",
            "commercial_reuse_evidence_url": "https://example.gov/permission/commercial",
        })
        result = validate_capture_record(self.record, self.record_path)
        self.assertTrue(result["valid"])
        self.assertFalse(result["terms_review_fresh"])
        self.assertFalse(result["collection_ready"])
        self.assertFalse(result["commercial_product_use_ready"])
        self.assertTrue(any("source terms review is older than 180 days" in warning for warning in result["warnings"]))
        self.assertFalse(result["retrieval_eligible"])

    def test_permission_gates_need_terms_and_separate_evidence(self):
        self.record.update({
            "collection_permission": "allowed",
            "commercial_reuse_permission": "allowed",
            "terms_url": "https://example.gov/terms",
            "terms_checked_on": "2026-10-27",
            "collection_permission_evidence_url": "https://example.gov/permission/collection",
            "commercial_reuse_evidence_url": None,
        })
        result = validate_capture_record(self.record, self.record_path)
        self.assertTrue(result["collection_ready"])
        self.assertFalse(result["commercial_product_use_ready"])
        self.assertFalse(result["retrieval_eligible"])


if __name__ == "__main__":
    unittest.main()
