import hashlib
import io
import importlib.util
import json
import tempfile
import unittest
from unittest.mock import patch
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
        (self.root / "extracted").mkdir()
        extracted = self.root / "extracted" / "law.txt"
        extracted.write_text("Article 1\\nArticle 2", encoding="utf-8")
        self.text_hash = hashlib.sha256(extracted.read_bytes()).hexdigest()
        self.source_id = "SRC-1"
        self.candidate = {
            "document": {"document_id": "LAW-1", "source_id": self.source_id, "official_title": "Test law", "document_type": "statute",
                         "release_priority": "P0", "practice_areas": ["Labour and social insurance"],
                         "permission_scope_review": {
                             "status": "passed", "evidence": "AUTH-1 clauses 1-4", "reviewed_on": "2025-01-01",
                             "approved_uses": ["collection", "storage", "text_extraction", "indexing", "commercial_product_use", "excerpt_display"],
                         }},
            "sources": [{
                "source_id": self.source_id, "authority": "Synthetic official authority", "source_class": "official_primary_candidate", "source_page": "https://laws.example.gov/portal",
                "collection_permission": "allowed", "commercial_reuse_permission": "allowed",
                "permission_evidence": "Written collection permission AUTH-1", "permission_evidence_url": "https://laws.example.gov/rights/collection", "terms_checked_on": "2025-01-01",
                "commercial_reuse_evidence": "Commercial license AUTH-COMM-1", "commercial_reuse_evidence_url": "https://laws.example.gov/rights/commercial", "commercial_terms_checked_on": "2025-01-01",
            }],
            "version": {
                "source_url": "https://laws.example.gov/law.pdf", "original_path": "originals/law.pdf",
                "original_sha256": self.original_hash, "retrieved_at": "2025-01-02T12:00:00Z",
                "extracted_text_path": "extracted/law.txt", "text_sha256": self.text_hash,
                "text_review_status": "text_checked", "text_review_evidence_url": "https://laws.example.gov/text-review",
                "article_identifiers": ["Article 1", "Article 2"],
                "expected_article_identifiers": ["Article 1", "Article 2"],
                "publication_date": "2024-12-01", "effective_date": "2025-01-01",
                "gazette_issue": "Issue 1", "gazette_pages": "1-10",
                "publication_evidence_url": "https://laws.example.gov/gazette/issue-1", "legal_status": "in_force", "review_status": "verified",
                "authenticity_verified": 1, "status_verified": 1, "amendment_history_verified": 1,
                "permission_evidence": "Scope checked under AUTH-1",
            },
            "reviews": [{
                "review_type": review_type, "outcome": "pass", "notes": "Reviewed against evidence.",
                "reviewer_id": "reviewer-test-01",
                "reviewer_role": "qualified_egyptian_counsel" if review_type == "lawyer_approval" else "legal_researcher",
                "reviewed_on": "2025-01-03",
                "evidence_url": "https://laws.example.gov/evidence",
            } for review_type in sorted(MODULE.REQUIRED_REVIEWS)],
        }
        self.register = {"sources": [{
            "source_id": self.source_id, "authority": "Synthetic official authority", "source_page": "https://www.laws.example.gov/portal",
            "collection_permission": "allowed", "commercial_reuse_permission": "allowed",
            "permission_evidence": "Written collection permission AUTH-1", "permission_evidence_url": "https://laws.example.gov/rights/collection", "terms_checked_on": "2025-01-01",
            "commercial_reuse_evidence": "Commercial license AUTH-COMM-1", "commercial_reuse_evidence_url": "https://laws.example.gov/rights/commercial", "commercial_terms_checked_on": "2025-01-01",
        }]}

    def tearDown(self):
        self.tmp.cleanup()

    def test_complete_synthetic_evidence_passes(self):
        result = MODULE.audit_candidate(self.candidate, self.register, self.root)
        self.assertTrue(result["ready"], result["blockers"])

    def test_collection_rights_require_inspectable_evidence_url(self):
        candidate = json.loads(json.dumps(self.candidate))
        candidate["sources"][0].pop("permission_evidence_url")
        result = MODULE.audit_candidate(candidate, self.register, self.root)
        self.assertIn("candidate_permission_evidence_url_invalid", {item["code"] for item in result["blockers"]})

    def test_commercial_rights_require_separate_inspectable_evidence_url(self):
        candidate = json.loads(json.dumps(self.candidate))
        candidate["sources"][0].pop("commercial_reuse_evidence_url")
        result = MODULE.audit_candidate(candidate, self.register, self.root)
        self.assertIn("candidate_commercial_permission_evidence_url_invalid", {item["code"] for item in result["blockers"]})

    def test_central_permission_register_must_link_rights_evidence(self):
        register = json.loads(json.dumps(self.register))
        register["sources"][0].pop("permission_evidence_url")
        register["sources"][0].pop("commercial_reuse_evidence_url")
        result = MODULE.audit_candidate(self.candidate, register, self.root)
        codes = {item["code"] for item in result["blockers"]}
        self.assertIn("central_permission_evidence_url_invalid", codes)
        self.assertIn("central_commercial_permission_evidence_url_invalid", codes)

    def test_retrieval_requires_timezone_aware_timestamp(self):
        candidate = json.loads(json.dumps(self.candidate))
        candidate["version"]["retrieved_at"] = "2025-01-02"
        result = MODULE.audit_candidate(candidate, self.register, self.root)
        self.assertIn("retrieved_at_invalid", {item["code"] for item in result["blockers"]})
        candidate["version"]["retrieved_at"] = "2025-01-02T12:00:00"
        result = MODULE.audit_candidate(candidate, self.register, self.root)
        self.assertIn("retrieved_at_invalid", {item["code"] for item in result["blockers"]})

    def test_gazette_pinpoint_and_publication_evidence_are_required(self):
        candidate = json.loads(json.dumps(self.candidate))
        candidate["version"].pop("gazette_pages")
        candidate["version"].pop("publication_evidence_url")
        result = MODULE.audit_candidate(candidate, self.register, self.root)
        codes = {item["code"] for item in result["blockers"]}
        self.assertIn("gazette_pages_missing", codes)
        self.assertIn("publication_evidence_url_invalid", codes)

    def test_permission_cannot_transfer_between_source_ids_on_same_host(self):
        candidate = json.loads(json.dumps(self.candidate))
        register = json.loads(json.dumps(self.register))
        register["sources"][0]["source_id"] = "DIFFERENT-SOURCE"
        result = MODULE.audit_candidate(candidate, register, self.root)
        self.assertIn("central_source_id_mismatch", {item["code"] for item in result["blockers"]})

    def test_duplicate_central_source_matches_are_ambiguous_and_block_release(self):
        register = json.loads(json.dumps(self.register))
        duplicate = json.loads(json.dumps(register["sources"][0]))
        register["sources"].append(duplicate)
        result = MODULE.audit_candidate(self.candidate, register, self.root)
        self.assertFalse(result["ready"])
        self.assertIn("central_source_record_ambiguous", {item["code"] for item in result["blockers"]})

    def test_allowed_commercial_permission_without_separate_evidence_blocks_release(self):
        candidate = json.loads(json.dumps(self.candidate))
        register = json.loads(json.dumps(self.register))
        candidate["sources"][0].pop("commercial_reuse_evidence")
        candidate["sources"][0].pop("commercial_terms_checked_on")
        register["sources"][0].pop("commercial_reuse_evidence")
        register["sources"][0].pop("commercial_terms_checked_on")
        result = MODULE.audit_candidate(candidate, register, self.root)
        codes = {item["code"] for item in result["blockers"]}
        self.assertIn("candidate_commercial_permission_evidence_missing", codes)
        self.assertIn("candidate_commercial_terms_date_invalid", codes)
        self.assertIn("central_commercial_permission_evidence_missing", codes)
        self.assertIn("central_commercial_terms_date_invalid", codes)

    def test_report_separates_candidate_coverage_from_verified_text_and_permission_states(self):
        candidate_path = self.root / "registry_candidate.json"
        register_path = self.root / "permission_register.json"
        coverage_path = self.root / "coverage.csv"
        candidate_path.write_text(json.dumps(self.candidate), encoding="utf-8")
        register_path.write_text(json.dumps(self.register), encoding="utf-8")
        coverage_path.write_text("practice_area,priority,status\\nLabour,P0,not_started\\n", encoding="utf-8")
        report = MODULE.build_report(
            [candidate_path], register_path, self.root, coverage_matrix_path=coverage_path
        )
        self.assertEqual(report["source_authority_counts"], {"Synthetic official authority": 1})
        self.assertEqual(report["release_priority_counts"], {"P0": 1})
        self.assertEqual(report["collection_permission_counts"], {"allowed": 1})
        self.assertEqual(report["commercial_reuse_permission_counts"], {"allowed": 1})
        self.assertEqual(report["coverage_semantics"]["candidate_inventory_count"], 1)
        self.assertEqual(report["coverage_semantics"]["evidence_ready_current_text_count"], 1)
        self.assertFalse(report["coverage_semantics"]["percentage_claims"])
        self.assertEqual(report["candidates"][0]["gazette_pages"], "1-10")

    def test_report_output_cannot_overwrite_candidate_input(self):
        candidate_path = self.root / "candidate.json"
        register_path = self.root / "register.json"
        coverage_path = self.root / "coverage.csv"
        original_candidate = json.dumps(self.candidate, sort_keys=True)
        candidate_path.write_text(original_candidate, encoding="utf-8")
        register_path.write_text(json.dumps(self.register), encoding="utf-8")
        with patch("sys.stdout", new_callable=io.StringIO):
            result = MODULE.main([
                "--candidate", str(candidate_path),
                "--register", str(register_path),
                "--coverage-matrix", str(coverage_path),
                "--root", str(self.root),
                "--out", str(candidate_path),
            ])
        self.assertEqual(result, 2)
        self.assertEqual(candidate_path.read_text(encoding="utf-8"), original_candidate)

    def test_current_labour_candidate_is_blocked_not_silently_promoted(self):
        candidate = json.loads((ROOT / "data/candidates/labour_law_14_2025/registry_candidate.json").read_text(encoding="utf-8"))
        register = json.loads((ROOT / "docs/source_permission_register.json").read_text(encoding="utf-8"))
        result = MODULE.audit_candidate(candidate, register, ROOT)
        self.assertFalse(result["ready"])
        codes = {item["code"] for item in result["blockers"]}
        self.assertIn("candidate_collection_permission_not_allowed", codes)
        self.assertIn("version_not_verified", codes)
        self.assertIn("original_file_missing", codes)

    def test_historical_version_can_pass_when_its_status_and_end_date_are_verified(self):
        self.candidate["version"]["legal_status"] = "historical"
        self.candidate["version"]["repeal_date"] = "2025-06-01"
        result = MODULE.audit_candidate(self.candidate, self.register, self.root)
        self.assertTrue(result["ready"], result["blockers"])

    def test_repealed_or_historical_version_without_end_date_is_blocked(self):
        for status in ("repealed", "historical"):
            candidate = json.loads(json.dumps(self.candidate))
            candidate["version"]["legal_status"] = status
            candidate["version"].pop("repeal_date", None)
            result = MODULE.audit_candidate(candidate, self.register, self.root)
            self.assertIn(
                "repeal_date_required_for_historical_status",
                {item["code"] for item in result["blockers"]},
            )

    def test_repeal_date_before_effective_date_is_blocked(self):
        candidate = json.loads(json.dumps(self.candidate))
        candidate["version"]["repeal_date"] = "2024-06-01"
        result = MODULE.audit_candidate(candidate, self.register, self.root)
        self.assertIn("repeal_before_effective", {item["code"] for item in result["blockers"]})

    def test_future_scheduled_repeal_date_is_valid_for_current_in_force_status(self):
        candidate = json.loads(json.dumps(self.candidate))
        candidate["version"]["repeal_date"] = "2099-06-01"
        result = MODULE.audit_candidate(candidate, self.register, self.root)
        self.assertNotIn("repeal_date_invalid", {item["code"] for item in result["blockers"]})

    def test_in_force_status_with_past_repeal_date_is_blocked(self):
        candidate = json.loads(json.dumps(self.candidate))
        candidate["version"]["repeal_date"] = (MODULE.dt.date.today() - MODULE.dt.timedelta(days=1)).isoformat()
        result = MODULE.audit_candidate(candidate, self.register, self.root)
        self.assertIn("in_force_after_repeal_date", {item["code"] for item in result["blockers"]})

    def test_hash_mismatch_blocks_release(self):
        self.candidate["version"]["original_sha256"] = "0" * 64
        result = MODULE.audit_candidate(self.candidate, self.register, self.root)
        self.assertIn("original_hash_mismatch", {item["code"] for item in result["blockers"]})


    def test_text_hash_and_article_completeness_are_required(self):
        candidate = json.loads(json.dumps(self.candidate))
        candidate["version"]["text_sha256"] = "0" * 64
        candidate["version"]["article_identifiers"] = ["Article 1"]
        result = MODULE.audit_candidate(candidate, self.register, self.root)
        codes = {item["code"] for item in result["blockers"]}
        self.assertIn("text_hash_mismatch", codes)
        self.assertIn("article_identifiers_missing", codes)

    def test_duplicate_and_unexpected_article_identifiers_block_release(self):
        candidate = json.loads(json.dumps(self.candidate))
        candidate["version"]["article_identifiers"] = ["Article 1", "Article 1", "Annex A"]
        result = MODULE.audit_candidate(candidate, self.register, self.root)
        codes = {item["code"] for item in result["blockers"]}
        self.assertIn("article_identifiers_duplicated", codes)
        self.assertIn("article_identifiers_unexpected", codes)


    def test_article_anchor_must_exist_in_extracted_text(self):
        candidate = json.loads(json.dumps(self.candidate))
        candidate["version"]["article_identifiers"] = ["Article 1", "Article 3"]
        candidate["version"]["expected_article_identifiers"] = ["Article 1", "Article 3"]
        result = MODULE.audit_candidate(candidate, self.register, self.root)
        self.assertIn("article_identifiers_not_in_text", {item["code"] for item in result["blockers"]})

    def test_missing_text_review_evidence_blocks_release(self):
        candidate = json.loads(json.dumps(self.candidate))
        candidate["version"]["text_review_status"] = "extracted"
        candidate["version"]["text_review_evidence_url"] = None
        result = MODULE.audit_candidate(candidate, self.register, self.root)
        codes = {item["code"] for item in result["blockers"]}
        self.assertIn("text_review_status_unchecked", codes)
        self.assertIn("text_review_evidence_url_invalid", codes)

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

    def test_document_identity_requires_safe_id_title_and_type(self):
        for mutate, expected in (
            (lambda item: item["document"].update({"document_id": "../LAW-1"}), "document_id_invalid"),
            (lambda item: item["document"].pop("official_title"), "official_title_missing"),
            (lambda item: item["document"].pop("document_type"), "document_type_missing"),
        ):
            candidate = json.loads(json.dumps(self.candidate))
            mutate(candidate)
            result = MODULE.audit_candidate(candidate, self.register, self.root)
            with self.subTest(expected=expected):
                self.assertIn(expected, {item["code"] for item in result["blockers"]})

    def test_https_url_validation_rejects_all_userinfo(self):
        for url in (
            "https://@laws.example.gov/portal",
            "https://user@laws.example.gov/portal",
            "https://user:password@laws.example.gov/portal",
            " https://laws.example.gov/portal",
            "https://laws.example.gov/portal with-space",
            "https://laws.example.gov:99999/portal",
        ):
            with self.subTest(url=url):
                self.assertIsNone(MODULE.https_host(url))

    def test_scope_review_must_explicitly_approve_storage_and_text_extraction(self):
        for use in ("storage", "text_extraction"):
            candidate = json.loads(json.dumps(self.candidate))
            candidate["document"]["permission_scope_review"]["approved_uses"].remove(use)
            result = MODULE.audit_candidate(candidate, self.register, self.root)
            with self.subTest(use=use):
                self.assertIn("document_scope_uses_incomplete", {item["code"] for item in result["blockers"]})

    def test_original_and_extracted_paths_must_use_designated_relative_directories(self):
        cases = [
            ("original_path", str(self.root / "originals" / "law.pdf"), "original_path_invalid"),
            ("original_path", "originals/../originals/law.pdf", "original_path_invalid"),
            ("extracted_text_path", "originals/law.txt", "extracted_text_path_invalid"),
            ("extracted_text_path", "../extracted/law.txt", "extracted_text_path_invalid"),
        ]
        for field, value, expected_code in cases:
            candidate = json.loads(json.dumps(self.candidate))
            candidate["version"][field] = value
            result = MODULE.audit_candidate(candidate, self.register, self.root)
            with self.subTest(field=field, value=value):
                self.assertIn(expected_code, {item["code"] for item in result["blockers"]})

    def test_release_gate_rejects_symlinked_original_and_extracted_text(self):
        original_link = self.root / "originals" / "linked.pdf"
        original_link.symlink_to(self.root / "originals" / "law.pdf")
        candidate = json.loads(json.dumps(self.candidate))
        candidate["version"]["original_path"] = "originals/linked.pdf"
        result = MODULE.audit_candidate(candidate, self.register, self.root)
        self.assertIn("original_path_symlinked", {item["code"] for item in result["blockers"]})

        extracted_link = self.root / "extracted" / "linked.txt"
        extracted_link.symlink_to(self.root / "extracted" / "law.txt")
        candidate = json.loads(json.dumps(self.candidate))
        candidate["version"]["extracted_text_path"] = "extracted/linked.txt"
        result = MODULE.audit_candidate(candidate, self.register, self.root)
        self.assertIn("extracted_text_path_symlinked", {item["code"] for item in result["blockers"]})

    def test_unmatched_central_source_fails_closed(self):
        self.register["sources"][0]["source_page"] = "https://other.example.gov"
        result = MODULE.audit_candidate(self.candidate, self.register, self.root)
        self.assertIn("central_source_record_missing", {item["code"] for item in result["blockers"]})



    def test_review_requires_attribution_date_and_qualified_lawyer_role(self):
        candidate = json.loads(json.dumps(self.candidate))
        lawyer_review = next(r for r in candidate["reviews"] if r["review_type"] == "lawyer_approval")
        lawyer_review.pop("reviewer_id")
        lawyer_review["reviewer_role"] = "legal_researcher"
        lawyer_review.pop("reviewed_on")
        result = MODULE.audit_candidate(candidate, self.register, self.root)
        codes = {item["code"] for item in result["blockers"]}
        self.assertIn("reviewer_identity_missing", codes)
        self.assertIn("lawyer_qualification_not_established", codes)
        self.assertIn("review_date_invalid", codes)

    def test_future_review_date_is_rejected(self):
        candidate = json.loads(json.dumps(self.candidate))
        candidate["reviews"][0]["reviewed_on"] = "2999-01-01"
        result = MODULE.audit_candidate(candidate, self.register, self.root)
        self.assertIn("review_date_invalid", {item["code"] for item in result["blockers"]})

    def test_duplicate_document_ids_block_all_duplicate_candidates(self):
        candidate_a = self.root / "candidate-a.json"
        candidate_b = self.root / "candidate-b.json"
        register_path = self.root / "register.json"
        candidate_a.write_text(json.dumps(self.candidate), encoding="utf-8")
        candidate_b.write_text(json.dumps(self.candidate), encoding="utf-8")
        register_path.write_text(json.dumps(self.register), encoding="utf-8")
        report = MODULE.build_report([candidate_a, candidate_b], register_path, self.root)
        self.assertEqual(report["candidate_count"], 2)
        self.assertEqual(report["ready_count"], 0)
        self.assertEqual(report["blocker_counts"]["document_id_duplicate"], 2)
        self.assertTrue(all(
            "document_id_duplicate" in {blocker["code"] for blocker in item["blockers"]}
            for item in report["candidates"]
        ))

    def test_report_separates_planning_matrix_from_current_and_historical_readiness(self):
        candidate_path = self.root / "candidate.json"
        register_path = self.root / "register.json"
        candidate_path.write_text(json.dumps(self.candidate), encoding="utf-8")
        register_path.write_text(json.dumps(self.register), encoding="utf-8")
        matrix_path = self.root / "coverage.csv"
        matrix_path.write_text(
            chr(10).join([
                "practice_area,priority,status",
                "Civil law,P0,not_started",
                "Labour,P0,in_progress",
                "Tax,P1,not_started",
            ]) + chr(10),
            encoding="utf-8",
        )
        report = MODULE.build_report([candidate_path], register_path, self.root, matrix_path)
        self.assertEqual(report["release_ready_current_count"], 1)
        self.assertEqual(report["release_ready_historical_count"], 0)
        self.assertEqual(report["coverage_matrix"]["practice_area_count"], 3)
        self.assertEqual(report["coverage_matrix"]["status_counts"], {"in_progress": 1, "not_started": 2})
        self.assertEqual(report["coverage_matrix"]["unstarted_practice_areas"], ["Civil law", "Tax"])
        self.assertIn("does not prove", report["coverage_matrix"]["warning"])

        self.candidate["version"]["legal_status"] = "historical"
        self.candidate["version"]["repeal_date"] = "2025-06-01"
        candidate_path.write_text(json.dumps(self.candidate), encoding="utf-8")
        historical = MODULE.build_report([candidate_path], register_path, self.root, matrix_path)
        self.assertEqual(historical["release_ready_current_count"], 0)
        self.assertEqual(historical["release_ready_historical_count"], 1)

    def test_missing_or_malformed_coverage_matrix_is_reported_without_promoting_coverage(self):
        report = MODULE.summarize_coverage_matrix(self.root / "missing.csv")
        self.assertFalse(report["available"])
        malformed = self.root / "bad.csv"
        malformed.write_text("practice_area,priority" + chr(10) + "Civil law,P0" + chr(10), encoding="utf-8")
        report = MODULE.summarize_coverage_matrix(malformed)
        self.assertFalse(report["available"])
        self.assertIn("must include", report["error"])

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
