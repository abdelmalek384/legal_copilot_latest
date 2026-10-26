import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "validate_legal_release_readiness.py"
SPEC = importlib.util.spec_from_file_location("validate_legal_release_readiness", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LegalReleaseReadinessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "originals").mkdir()
        original = self.root / "originals" / "law.pdf"
        original.write_bytes(b"synthetic original bytes")
        self.original_hash = hashlib.sha256(original.read_bytes()).hexdigest()
        self.source_id = "SRC-1"
        self.candidate = {
            "document": {"document_id": "LAW-1", "source_id": self.source_id, "official_title": "Test law",
                         "permission_scope_review": {
                             "status": "passed", "evidence": "AUTH-1 clauses 1-4", "reviewed_on": "2025-01-01",
                             "approved_uses": ["collection", "indexing", "commercial_product_use", "excerpt_display"],
                         }},
            "sources": [{
                "source_id": self.source_id, "source_page": "https://laws.example.gov/portal",
                "collection_permission": "allowed", "commercial_reuse_permission": "allowed",
                "permission_evidence": "Written permission AUTH-1", "terms_checked_on": "2025-01-01",
            }],
            "version": {
                "source_url": "https://laws.example.gov/law.pdf", "original_path": "originals/law.pdf",
                "original_sha256": self.original_hash, "retrieved_at": "2025-01-02",
                "publication_date": "2024-12-01", "effective_date": "2025-01-01",
                "gazette_issue": "Issue 1", "legal_status": "in_force", "review_status": "verified",
                "authenticity_verified": 1, "status_verified": 1, "amendment_history_verified": 1,
                "permission_evidence": "Scope checked under AUTH-1",
            },
            "reviews": [{
                "review_type": review_type, "outcome": "pass", "notes": "Reviewed against evidence.",
                "evidence_url": "https://laws.example.gov/evidence",
            } for review_type in sorted(MODULE.REQUIRED_REVIEWS)],
        }
        self.register = {"sources": [{
            "source_id": self.source_id, "source_page": "https://www.laws.example.gov/portal",
            "collection_permission": "allowed", "commercial_reuse_permission": "allowed",
            "permission_evidence": "Written permission AUTH-1", "terms_checked_on": "2025-01-01",
        }]}

    def tearDown(self):
        self.tmp.cleanup()

    def test_complete_synthetic_evidence_passes(self):
        result = MODULE.audit_candidate(self.candidate, self.register, self.root)
        self.assertTrue(result["ready"], result["blockers"])

    def test_current_labour_candidate_is_blocked_not_silently_promoted(self):
        candidate = json.loads((ROOT / "data/candidates/labour_law_14_2025/registry_candidate.json").read_text(encoding="utf-8"))
        register = json.loads((ROOT / "docs/source_permission_register.json").read_text(encoding="utf-8"))
        result = MODULE.audit_candidate(candidate, register, ROOT)
        self.assertFalse(result["ready"])
        codes = {item["code"] for item in result["blockers"]}
        self.assertIn("candidate_collection_permission_not_allowed", codes)
        self.assertIn("version_not_verified", codes)
        self.assertIn("original_file_missing", codes)

    def test_historical_version_can_pass_when_its_status_is_verified(self):
        self.candidate["version"]["legal_status"] = "historical"
        result = MODULE.audit_candidate(self.candidate, self.register, self.root)
        self.assertTrue(result["ready"], result["blockers"])

    def test_hash_mismatch_blocks_release(self):
        self.candidate["version"]["original_sha256"] = "0" * 64
        result = MODULE.audit_candidate(self.candidate, self.register, self.root)
        self.assertIn("original_hash_mismatch", {item["code"] for item in result["blockers"]})

    def test_future_terms_date_and_missing_legal_review_block_release(self):
        self.candidate["sources"][0]["terms_checked_on"] = "2999-01-01"
        self.candidate["reviews"] = [r for r in self.candidate["reviews"] if r["review_type"] != "lawyer_approval"]
        result = MODULE.audit_candidate(self.candidate, self.register, self.root)
        codes = {item["code"] for item in result["blockers"]}
        self.assertIn("candidate_terms_date_invalid", codes)
        self.assertIn("review_missing_or_duplicate", codes)

    def test_scope_review_must_explicitly_include_display_and_commercial_use(self):
        self.candidate["document"]["permission_scope_review"]["approved_uses"] = ["collection", "indexing"]
        result = MODULE.audit_candidate(self.candidate, self.register, self.root)
        self.assertIn("document_scope_uses_incomplete", {item["code"] for item in result["blockers"]})

    def test_unmatched_central_source_fails_closed(self):
        self.register["sources"][0]["source_page"] = "https://other.example.gov"
        result = MODULE.audit_candidate(self.candidate, self.register, self.root)
        self.assertIn("central_source_record_missing", {item["code"] for item in result["blockers"]})


    def test_report_summarizes_blockers_status_and_practice_area_without_claiming_coverage(self):
        self.candidate["document"]["practice_areas"] = ["Labour", "Employment"]
        self.candidate["version"]["legal_status"] = "under_review"
        self.candidate["version"]["review_status"] = "pending_source_review"
        self.candidate["sources"][0]["commercial_reuse_permission"] = "unknown"
        self.register["sources"][0]["commercial_reuse_permission"] = "unknown"
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            original = temp_root / "originals" / "law.pdf"
            original.parent.mkdir()
            original.write_bytes(b"synthetic original bytes")
            self.candidate["version"]["original_path"] = "originals/law.pdf"
            candidate_path = temp_root / "registry_candidate.json"
            candidate_path.write_text(json.dumps(self.candidate), encoding="utf-8")
            register_path = temp_root / "register.json"
            register_path.write_text(json.dumps(self.register), encoding="utf-8")
            report = MODULE.build_report([candidate_path], register_path, temp_root)
        self.assertEqual(report["candidate_count"], 1)
        self.assertEqual(report["blocked_count"], 1)
        self.assertGreater(report["blocker_counts"].get("central_commercial_permission_not_allowed", 0), 0)
        self.assertEqual(report["legal_status_counts"], {"under_review": 1})
        self.assertEqual(report["review_status_counts"], {"pending_source_review": 1})
        self.assertEqual(report["practice_area_coverage"]["Labour"]["candidate_count"], 1)
        self.assertEqual(report["practice_area_coverage"]["Employment"]["blocked_count"], 1)
        self.assertIn("not complete Egyptian-law coverage", report["warning"])

    def test_report_counts_malformed_candidate_as_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            candidate_path = root / "bad.json"
            candidate_path.write_text("{", encoding="utf-8")
            register_path = root / "register.json"
            register_path.write_text(json.dumps(self.register), encoding="utf-8")
            report = MODULE.build_report([candidate_path], register_path, root)
        self.assertEqual(report["candidate_count"], 1)
        self.assertEqual(report["blocked_count"], 1)
        self.assertEqual(report["blocker_counts"], {"candidate_unreadable": 1})

if __name__ == "__main__":
    unittest.main()
