import importlib.util
import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_source_permission_register", ROOT / "tools" / "validate_source_permission_register.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class SourcePermissionRegisterTests(unittest.TestCase):
    def test_committed_register_validates(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        self.assertEqual(MODULE.validate(data), [])

    def test_register_loader_rejects_duplicate_json_keys_at_every_depth(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "register.json"
            for raw in (
                '{"schema_version": "1.0", "sources": [], "sources": [{"source_id": "S"}]}',
                '{"schema_version": "1.0", "sources": [{"source_id": "S", "permission": {"state": "unknown", "state": "allowed"}}]}',
            ):
                with self.subTest(raw=raw):
                    path.write_text(raw, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "duplicate JSON key in source permission register"):
                        MODULE.load_register(path)

    def test_permission_claim_requires_evidence_and_date(self):
        item = {
            "source_id": "S1", "authority": "Example", "source_page": "https://example.gov/",
            "material_types": ["law"], "access_status": "public",
            "collection_permission": "allowed", "commercial_reuse_permission": "unknown",
            "required_next_action": "review"
        }
        errors = MODULE.validate({"sources": [item]})
        self.assertTrue(any("permission_evidence" in error for error in errors))

    def test_source_ids_require_bounded_ascii_identifier_syntax(self):
        import json
        base = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        invalid_ids = (" leading", "trailing ", "contains space", "slash/name", "semi;colon", "", "x" * 129, "قانون")
        for source_id in invalid_ids:
            data = json.loads(json.dumps(base))
            data["sources"][0]["source_id"] = source_id
            with self.subTest(source_id=source_id):
                self.assertTrue(any("source_id must be a 1-128 character ASCII identifier" in error
                                    for error in MODULE.validate(data)))
        data = json.loads(json.dumps(base))
        data["sources"][0]["source_id"] = "EG-LAW.14_2025-A"
        self.assertFalse(any("source_id must be a 1-128 character ASCII identifier" in error
                             for error in MODULE.validate(data)))

    def test_duplicate_source_ids_rejected(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        data["sources"].append(dict(data["sources"][0]))
        self.assertTrue(any("duplicate source_id" in error for error in MODULE.validate(data)))


    def test_commercial_reuse_state_is_validated_independently(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        data["sources"][0]["commercial_reuse_permission"] = "public_means_free"
        errors = MODULE.validate(data)
        self.assertTrue(any("commercial_reuse_permission has unsupported value" in error for error in errors))

    def test_explicit_restrictive_commercial_state_requires_evidence_and_date(self):
        item = {
            "source_id": "S1", "authority": "Example", "source_page": "https://example.gov/",
            "material_types": ["law"], "access_status": "public",
            "collection_permission": "unknown",
            "commercial_reuse_permission": "prior_written_permission_required_per_published_terms",
            "terms_url": "https://example.gov/terms",
            "permission_evidence": None, "terms_checked_on": None,
            "required_next_action": "Review terms",
        }
        errors = MODULE.validate({"schema_version": "1.0", "assessment_date": "2026-10-27", "sources": [item]})
        self.assertTrue(any("permission_evidence" in error for error in errors))
        self.assertTrue(any("terms_checked_on" in error for error in errors))

    def test_allowed_commercial_reuse_requires_its_own_evidence_and_date(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = data["sources"][0]
        source["commercial_reuse_permission"] = "allowed"
        source["permission_evidence"] = "Collection permission evidence"
        source["terms_checked_on"] = "2026-10-23"
        errors = MODULE.validate(data)
        self.assertTrue(any("separate commercial_reuse_evidence" in error for error in errors))
        self.assertTrue(any("commercial_terms_checked_on date" in error for error in errors))

        source["commercial_reuse_evidence"] = "Written commercial license AUTH-COMM-1"
        source["commercial_terms_checked_on"] = "2026-10-23"
        source["commercial_reuse_evidence_url"] = "https://example.gov/licenses/commercial"
        self.assertEqual(MODULE.validate(data), [])

    def test_allowed_collection_requires_direct_https_evidence_url(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = data["sources"][0]
        source["collection_permission"] = "allowed"
        source["permission_evidence"] = "Permission letter"
        source["terms_checked_on"] = "2026-10-23"
        errors = MODULE.validate(data)
        self.assertTrue(any("permission_evidence_url" in error for error in errors))
        source["permission_evidence_url"] = "https://example.gov/rights/collection"
        self.assertFalse(any("allowed collection requires permission_evidence_url" in error for error in MODULE.validate(data)))

    def test_invalid_rights_evidence_urls_are_rejected(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = data["sources"][0]
        source["permission_evidence_url"] = "https://user:secret@example.gov/permission"
        source["commercial_reuse_evidence_url"] = "http://example.gov/license"
        errors = MODULE.validate(data)
        self.assertTrue(any("permission_evidence_url must be an HTTPS URL" in error for error in errors))
        self.assertTrue(any("commercial_reuse_evidence_url must be an HTTPS URL" in error for error in errors))

    def test_signed_cloud_storage_urls_and_fragments_are_rejected(self):
        from tools.validate_source_permission_register import _https_url
        for url in (
            "https://example.gov/law.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256",
            "https://example.gov/law.pdf?X-Amz-Date=20261116T120000Z",
            "https://example.gov/law.pdf?GoogleAccessId=account",
            "https://example.gov/law.pdf?X-Goog-Algorithm=GOOG4-RSA-SHA256",
            "https://example.gov/law.pdf?X-Goog-Date=20261116T120000Z",
            "https://example.gov/law.pdf#page=4",
            "https://example.gov/law.pdf#",
        ):
            with self.subTest(url=url):
                self.assertFalse(_https_url(url))
        self.assertTrue(_https_url("https://example.gov/law.pdf"))

    def test_credentials_in_source_urls_are_rejected(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        for url in (
            "https://user:secret@example.gov/law",
            " https://example.gov/law",
            "https://example.gov/law file",
            "https://example.gov:99999/law",
            "https://example.gov:/law",
            "https://example.gov/\x00law",
            "https://example.gov/law\x7f",
            "https://example.gov\\law",
        ):
            data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
            data["sources"][0]["source_page"] = url
            errors = MODULE.validate(data)
            with self.subTest(url=url):
                self.assertTrue(any("source_page must be an HTTPS URL without credentials" in error for error in errors))

    def test_one_day_local_date_ahead_of_utc_is_accepted(self):
        import datetime as dt
        tomorrow = (dt.date.today() + dt.timedelta(days=1)).isoformat()
        self.assertTrue(MODULE._valid_review_date(tomorrow))

    def test_invalid_or_future_permission_review_dates_are_rejected(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        data["sources"][2]["terms_checked_on"] = "2099-01-01"
        errors = MODULE.validate(data)
        self.assertTrue(any(".terms_checked_on must be a valid ISO date or null" in error for error in errors))

    def test_empty_material_types_and_invalid_assessment_date_are_rejected(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        data["sources"][0]["material_types"] = []
        data["assessment_date"] = "2026-02-31"
        errors = MODULE.validate(data)
        self.assertTrue(any("material_types must be a non-empty list" in error for error in errors))
        self.assertTrue(any("assessment_date must be a valid ISO date" in error for error in errors))

    def test_article_141_does_not_override_court_portal_access_terms(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-COURT-CASSATION")
        self.assertEqual(source["collection_permission"], "not_allowed_without_explicit_exception_or_license")
        self.assertEqual(source["commercial_reuse_permission"], "prior_written_permission_required_per_published_terms")
        self.assertIn("Article 141", source["permission_evidence"])
        self.assertIn("does not authorize automated/bulk extraction", source["permission_evidence"])
        self.assertEqual(source["source_page"], "https://cc.gov.eg/judgments_search/")
        self.assertIn("advanced search", source["permission_evidence"])
        self.assertIn("last updated May 2026", source["permission_evidence"])
        self.assertIn("personal account", source["permission_evidence"])
        self.assertIn("even from a subscribed account", source["permission_evidence"])
        self.assertIn("manual lookup/link-out source only", source["permission_evidence"])
        self.assertEqual(source["terms_checked_on"], "2026-10-31")
        self.assertIn("do not ingest", source["required_next_action"])

    def test_cassation_heritage_library_remains_browse_only_without_reuse_permission(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-COURT-CASSATION-LEGAL-HERITAGE-LIBRARY")
        self.assertEqual(source["collection_permission"], "unknown")
        self.assertEqual(source["commercial_reuse_permission"], "unknown")
        self.assertIn("watermark", source["permission_evidence"])
        self.assertIn("https://cc.gov.eg/heritage/documents/199", source["permission_evidence"])
        self.assertIn("https://cc.gov.eg/heritage/books/31/read", source["permission_evidence"])
        self.assertIn("1899", source["permission_evidence"])
        self.assertIn("not established", source["bulk_download_or_api"])
        self.assertEqual(source["permission_evidence_url"], "https://cc.gov.eg/posts/739")
        self.assertEqual(MODULE.validate(data), [])

    def test_scc_public_api_discovery_does_not_clear_collection_rights(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-SCC")
        self.assertEqual(source["collection_permission"], "unknown")
        self.assertEqual(source["commercial_reuse_permission"], "unknown")
        self.assertIn("third-party claims only", source["permission_evidence"])
        self.assertIn("not successfully independently validated", source["permission_evidence"])
        self.assertIn("get-cases-basedon-casestatuscode", source["permission_evidence"])
        self.assertIn("no readable body text", source["permission_evidence"])
        self.assertIn("do not call endpoints", source["bulk_download_or_api"].casefold())
        self.assertEqual(source["source_page"], "https://www.sccourt.gov.eg/newportal/?a=cp3&id=829")
        self.assertEqual(MODULE.validate(data), [])

    def test_dataflare_egyptian_corpus_mit_claim_does_not_clear_underlying_records(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-DATAFLARE-LEGAL-CORPUS")
        self.assertEqual(source["collection_permission"], "unknown")
        self.assertEqual(source["commercial_reuse_permission"], "unknown")
        self.assertIn("MIT", source["permission_evidence"])
        self.assertIn("no record-level source URL", source["permission_evidence"])
        self.assertIn("date=null", source["permission_evidence"])
        self.assertEqual(source["permission_evidence_url"], "https://huggingface.co/datasets/dataflare/egypt-legal-corpus")
        self.assertEqual(source["terms_checked_on"], "2026-10-30")
        self.assertEqual(MODULE.validate(data), [])

    def test_mksegypt_archive_license_claim_is_recorded_without_overstating_permission(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-MKSEGYPT-LEGAL-REPOSITORY")
        self.assertEqual(source["collection_permission"], "unknown")
        self.assertEqual(source["commercial_reuse_permission"], "unknown")
        self.assertIn("CC BY 4.0", source["permission_evidence"])
        self.assertIn("Article 141", source["permission_evidence"])
        self.assertIn("collections", source["permission_evidence"])
        self.assertEqual(source["permission_evidence_url"], "https://www.mksegypt.org/ar/documents")
        self.assertEqual(source["terms_checked_on"], "2026-10-30")
        self.assertEqual(MODULE.validate(data), [])

    def test_riwaq_decision_250_secondary_transcription_stays_rights_unknown(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-RIWAQ-ALJAMAL-DECISION-250-2026")
        self.assertEqual(source["source_page"], "https://ahmedazimelgamel.blogspot.com/2026/10/250-2026.html")
        self.assertEqual(source["collection_permission"], "unknown")
        self.assertEqual(source["commercial_reuse_permission"], "unknown")
        self.assertIsNone(source["terms_checked_on"])
        self.assertIn("1–781", source["permission_evidence"])
        self.assertIn("not the Official Gazette PDF", source["permission_evidence"])
        self.assertIn("manual discovery", source["required_next_action"])
        self.assertIn("Do not bulk-copy", source["required_next_action"])
        self.assertEqual(MODULE.validate(data), [])

    def test_law_hub_decision_250_preview_respects_published_reuse_restriction(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-LAW-HUB-DECISION-250-2026")
        self.assertEqual(source["collection_permission"], "unknown")
        self.assertEqual(source["commercial_reuse_permission"], "not_allowed_without_explicit_exception_or_license")
        self.assertEqual(source["terms_url"], "https://lawhub.info/eg/?page_id=778")
        self.assertEqual(source["terms_checked_on"], "2026-10-31")
        self.assertIn("attribution", source["permission_evidence"])
        self.assertIn("profit", source["permission_evidence"])
        self.assertIn("no document bytes or pages inspected", source["access_status"])
        self.assertEqual(MODULE.validate(data), [])

    def test_secondary_sources_for_labour_decisions_remain_rights_unknown(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        records = {item["source_id"]: item for item in data["sources"]}
        for source_id in ("EG-ALMASDAR-SECONDARY-LEGAL-NEWS", "EG-EGYIN-SECONDARY-LEGAL-NEWS"):
            source = records[source_id]
            self.assertEqual(source["collection_permission"], "unknown")
            self.assertEqual(source["commercial_reuse_permission"], "unknown")
            self.assertIsNone(source["terms_checked_on"])
            self.assertTrue(source["permission_evidence_url"].startswith("https://"))
            self.assertIn("manual discovery", source["required_next_action"])
            self.assertIn("Do not bulk-copy" if source_id.startswith("EG-ALMASDAR") else "Do not bulk-copy", source["required_next_action"])
        self.assertIn("all rights reserved", records["EG-ALMASDAR-SECONDARY-LEGAL-NEWS"]["permission_evidence"])
        self.assertIn("copyright is reserved", records["EG-EGYIN-SECONDARY-LEGAL-NEWS"]["permission_evidence"])
        self.assertEqual(MODULE.validate(data), [])

    def test_labour_decision_secondary_publishers_remain_rights_unknown(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        records = {item["source_id"]: item for item in data["sources"]}
        for source_id in ("EG-ALMASDAR-SECONDARY-LEGAL-NEWS", "EG-EGYIN-SECONDARY-LEGAL-NEWS"):
            source = records[source_id]
            self.assertEqual(source["collection_permission"], "unknown")
            self.assertEqual(source["commercial_reuse_permission"], "unknown")
            self.assertIsNone(source["terms_checked_on"])
            self.assertTrue(source["permission_evidence_url"].startswith("https://"))
            self.assertIn("manual discovery", source["required_next_action"])
            self.assertIn("Do not bulk-copy", source["required_next_action"])
        self.assertIn("all rights reserved", records["EG-ALMASDAR-SECONDARY-LEGAL-NEWS"]["permission_evidence"])
        self.assertIn("copyright is reserved", records["EG-EGYIN-SECONDARY-LEGAL-NEWS"]["permission_evidence"])
        self.assertEqual(MODULE.validate(data), [])

    def test_third_party_dspace_gazette_original_and_license_bundle_are_request_copy_restricted(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-IDSC-DSPACE-GAZETTE")
        self.assertEqual(source["repository_brand"], "Ibrachy & Dermarkar Repository")
        self.assertIn("Ibrachy & Dermarkar", source["authority"])
        self.assertEqual(source["publisher_metadata"], "المطابع الاميرية")
        self.assertEqual(source["collection_permission"], "unknown")
        self.assertEqual(source["commercial_reuse_permission"], "unknown")
        self.assertIn("license.txt", source["permission_evidence"])
        self.assertIn("request-a-copy", source["permission_evidence"])
        self.assertIn("no bytes or license text", source["permission_evidence"])
        self.assertIn("Do not bypass request-copy restrictions", source["required_next_action"])
        self.assertEqual(MODULE.validate(data), [])


    def test_labour_issue_295_metadata_is_restricted_and_not_a_reuse_license(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-IDSC-GAZETTE-2025-295-SUPPLEMENT-D")
        self.assertEqual(source["collection_permission"], "not_allowed_without_explicit_exception_or_license")
        self.assertEqual(source["commercial_reuse_permission"], "prior_written_permission_required_per_published_terms")
        self.assertEqual(source["terms_url"], "https://dspace.id.com.eg/info/end-user-agreement")
        self.assertEqual(source["terms_checked_on"], "2026-10-31")
        self.assertIn("request-a-copy", source["access_status"])
        self.assertIn("license.txt", source["permission_evidence"])
        self.assertIn("license filename", source["permission_evidence"])
        self.assertIn("systematic retrieval", source["permission_evidence"])
        self.assertIn("personal, non-commercial use", source["permission_evidence"])
        self.assertEqual(MODULE.validate(data), [])


    def test_sis_gazette_public_viewing_metadata_does_not_clear_rights(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-SIS-GAZETTE-2025-295-SUPPLEMENT-D")
        self.assertEqual(source["collection_permission"], "unknown")
        self.assertEqual(source["commercial_reuse_permission"], "unknown")
        self.assertIn("public viewing", source["access_status"])
        self.assertIn("Direct opening of the item page failed", source["permission_evidence"])
        self.assertEqual(MODULE.validate(data), [])


    def test_eastlaws_secondary_transcriptions_do_not_clear_reuse_rights(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-EASTLAWS-LABOUR-DECISIONS-290-291-2025")
        self.assertEqual(source["collection_permission"], "unknown")
        self.assertEqual(source["commercial_reuse_permission"], "unknown")
        self.assertIn("HTTP 403", source["access_status"])
        self.assertIn("no EastLaws terms", source["permission_evidence"])
        self.assertEqual(MODULE.validate(data), [])


    def test_gazette_issue_291_license_file_is_itself_restricted(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-IDSC-GAZETTE-2025-291-SUPPLEMENT-LABOUR")
        self.assertEqual(source["collection_permission"], "not_allowed_without_explicit_exception_or_license")
        self.assertEqual(source["commercial_reuse_permission"], "prior_written_permission_required_per_published_terms")
        self.assertIn("834.25 KB PDF", source["access_status"])
        self.assertIn("1.71 KB item-specific license.txt", source["access_status"])
        self.assertIn("all files are in restricted access", source["permission_evidence"])
        self.assertEqual(MODULE.validate(data), [])


    def test_lawhub_gazette_page_image_reproduction_does_not_clear_reuse_rights(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-LAWHUB-GAZETTE-295-DECISION-291-PDF")
        self.assertEqual(source["collection_permission"], "unknown")
        self.assertEqual(source["commercial_reuse_permission"], "unknown")
        self.assertIn("pages 21–22", source["access_status"])
        self.assertIn("No licence", source["permission_evidence"])
        self.assertEqual(MODULE.validate(data), [])


    def test_ministry_hosted_decision_289_pdf_does_not_clear_reuse_rights(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-MOL-SIS-DECISION-289-2025-PDF")
        self.assertEqual(source["collection_permission"], "unknown")
        self.assertEqual(source["commercial_reuse_permission"], "unknown")
        self.assertIn("not treat this PDF as the Official Gazette itself", source["required_next_action"])
        self.assertIn("No local PDF bytes/hash", source["access_status"])
        self.assertEqual(MODULE.validate(data), [])


    def test_decision_288_meles_item_and_license_are_request_copy_restricted(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-MELES-DSpace-DECISION-288-2025")
        self.assertEqual(source["collection_permission"], "not_allowed_without_explicit_exception_or_license")
        self.assertEqual(source["commercial_reuse_permission"], "prior_written_permission_required_per_published_terms")
        self.assertIn("55-byte item-specific license.txt", source["access_status"])
        self.assertIn("all files are in restricted access", source["permission_evidence"])
        self.assertEqual(MODULE.validate(data), [])


    def test_ministry_hosted_decision_294_pdf_does_not_clear_reuse_rights(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-MOL-SIS-DECISION-294-2025-PDF")
        self.assertEqual(source["collection_permission"], "unknown")
        self.assertEqual(source["commercial_reuse_permission"], "unknown")
        self.assertIn("not treat this PDF as the Official Gazette itself", source["required_next_action"])
        self.assertIn("No local PDF bytes/hash", source["access_status"])
        self.assertEqual(MODULE.validate(data), [])

    def test_decision_290_meles_metadata_does_not_clear_reuse_rights(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-MELES-DSpace-DECISION-290-2025")
        self.assertEqual(source["collection_permission"], "not_allowed_without_explicit_exception_or_license")
        self.assertEqual(source["commercial_reuse_permission"], "prior_written_permission_required_per_published_terms")
        self.assertIn("English PDF (103.23 KB)", source["access_status"])
        self.assertIn("Arabic PDF (105.2 KB)", source["access_status"])
        self.assertIn("not the Official Gazette", source["permission_evidence"])
        self.assertIn("item page and file links were not opened", source["permission_evidence"])
        self.assertEqual(source["terms_checked_on"], "2026-10-31")
        self.assertEqual(MODULE.validate(data), [])

    def test_decision_249_ministry_clarification_does_not_clear_reuse_rights(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-MOL-DECISION-249-2026-CLARIFICATION")
        self.assertEqual(source["collection_permission"], "unknown")
        self.assertEqual(source["commercial_reuse_permission"], "unknown")
        self.assertIsNone(source["terms_checked_on"])
        self.assertIn("not the complete ministerial decision", source["material_types"][1])
        self.assertIn("HTTP 502", source["access_status"])
        self.assertIn("or a Gazette amendment", source["permission_evidence"])
        self.assertEqual(MODULE.validate(data), [])


    def test_unhashable_permission_states_return_validation_errors(self):
        import json
        original = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        cases = (
            ("collection_permission", []),
            ("commercial_reuse_permission", {}),
        )
        for field, value in cases:
            data = json.loads(json.dumps(original))
            data["sources"][0][field] = value
            with self.subTest(field=field):
                errors = MODULE.validate(data)
                self.assertTrue(errors)
                self.assertTrue(any("unsupported value" in error for error in errors))

    def test_register_loader_rejects_symlink_swap_between_check_and_open(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "register.json"
            target.write_text('{"schema_version":"1.0","sources":[]}', encoding="utf-8")
            outside = root / "outside.json"
            outside.write_text('{"schema_version":"1.0","sources":[]}', encoding="utf-8")
            real_open = MODULE.os.open
            swapped = False

            def replace_before_open(path, flags, *args, **kwargs):
                nonlocal swapped
                if Path(path) == target and not swapped:
                    swapped = True
                    target.unlink()
                    target.symlink_to(outside)
                return real_open(path, flags, *args, **kwargs)

            with patch.object(MODULE.os, "open", side_effect=replace_before_open):
                with self.assertRaises((OSError, ValueError)):
                    MODULE.load_register(target)
            self.assertTrue(swapped)

    def test_register_loader_rejects_fifo_and_oversized_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            if hasattr(os, "mkfifo"):
                fifo = root / "register.fifo"
                os.mkfifo(fifo)
                with self.assertRaises((OSError, ValueError)):
                    MODULE.load_register(fifo)
            oversized = root / "oversized.json"
            oversized.write_bytes(b" " * (16 * 1024 * 1024 + 1))
            with self.assertRaises((OSError, ValueError)):
                MODULE.load_register(oversized)

    def test_eta_official_gazette_pdf_provenance_does_not_imply_reuse_permission(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(
            item for item in data["sources"]
            if item["source_id"] == "EG-ETA-GAZETTE-LABOUR-14-2025-PDF"
        )
        self.assertEqual(source["source_checked_on"], "2026-10-31")
        self.assertEqual(source["official_gazette_issue"], "18 (تابع)")
        self.assertEqual(source["official_gazette_issue_date"], "2025-05-03")
        self.assertEqual(source["effective_date_candidate"], "2025-09-01")
        self.assertEqual(source["specialized_labour_courts_effective_date_candidate"], "2025-10-01")
        self.assertIs(source["effective_date_verified"], False)
        self.assertIs(source["local_pdf_downloaded"], False)
        self.assertIsNone(source["local_pdf_sha256"])
        self.assertEqual(
            [item["printed_page"] for item in source["visual_page_checks"]],
            [5, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
        )
        self.assertEqual(source["collection_permission"], "unknown")
        self.assertEqual(source["commercial_reuse_permission"], "unknown")
        self.assertIsNone(source["terms_checked_on"])
        self.assertIn("download attempt failed", source["permission_evidence"])
        self.assertEqual(MODULE.validate(data), [])
    def test_new_november_2026_gazette_sources_keep_access_and_reuse_gates(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        by_id = {item["source_id"]: item for item in data["sources"]}
        decision_3356 = by_id["EG-IDSC-GAZETTE-2026-44BIS-A-PM-DECISION3356"]
        self.assertIn("request-a-copy", decision_3356["access_status"])
        self.assertEqual(decision_3356["collection_permission"], "not_allowed_without_explicit_exception_or_license")
        self.assertEqual(decision_3356["commercial_reuse_permission"], "prior_written_permission_required_per_published_terms")
        self.assertEqual(decision_3356["terms_checked_on"], "2026-11-24")
        secondary_3356 = by_id["EG-LAWHUB-PM-DECISION3356-2026"]
        self.assertEqual(secondary_3356["collection_permission"], "unknown")
        self.assertEqual(secondary_3356["commercial_reuse_permission"], "unknown")
        self.assertIn("lawhub.info-eg-dec-3356-2026-.pdf", secondary_3356["related_source_pages"][0])
        decision_3561 = by_id["EG-IDSC-GAZETTE-2026-46BIS-C-PM-DECISION3561"]
        self.assertEqual(decision_3561["collection_permission"], "not_allowed_without_explicit_exception_or_license")
        self.assertEqual(decision_3561["commercial_reuse_permission"], "prior_written_permission_required_per_published_terms")
        self.assertEqual(decision_3561["terms_checked_on"], "2026-11-24")
        self.assertEqual(MODULE.validate(data), [])

    def test_legacy_labour_decision_sources_keep_official_and_secondary_rights_distinct(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        by_id = {item["source_id"]: item for item in data["sources"]}
        for source_id in ("EG-LABOUR-MINISTRY-DECISION215-2003", "EG-LABOUR-MINISTRY-DECISION217-2003"):
            source = by_id[source_id]
            self.assertEqual(source["collection_permission"], "unknown")
            self.assertEqual(source["commercial_reuse_permission"], "unknown")
            self.assertIn("labour.gov.eg/media/", source["source_page"])
        decision_215 = by_id["EG-HRDISCUSSION-DECISION215-2003"]
        self.assertEqual(decision_215["collection_permission"], "unknown")
        self.assertEqual(decision_215["commercial_reuse_permission"], "unknown")
        self.assertIn("preamble", decision_215["access_status"])
        for source_id in ("EG-LABOUR-MINISTRY-DECISION214-2003", "EG-LABOUR-MINISTRY-DECISION216-2003"):
            source = by_id[source_id]
            self.assertEqual(source["collection_permission"], "unknown")
            self.assertEqual(source["commercial_reuse_permission"], "unknown")
            self.assertIn("labour.gov.eg", source["source_page"])
        decision_16 = by_id["EG-LAWEG-DECISION16-2012"]
        self.assertEqual(decision_16["collection_permission"], "unknown")
        self.assertEqual(decision_16["commercial_reuse_permission"], "unknown")
        self.assertIn("ItemID=76003", decision_16["source_page"])
        secondary = by_id["EG-RAAFATELSHAER-LEGACY-LABOUR-FUNDS-PDF-2018"]
        self.assertEqual(secondary["collection_permission"], "unknown")
        self.assertEqual(secondary["commercial_reuse_permission"], "unknown")
        self.assertIn("217/2003", " ".join(secondary["material_types"]))
        self.assertEqual(MODULE.validate(data), [])

    def test_optional_source_locator_urls_reject_credentials_fragments_and_signed_tokens(self):
        import json
        fields = ("file_url", "item_page_url", "repository_homepage_url", "official_pdf_url")
        for field in fields:
            with self.subTest(field=field):
                data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
                data["sources"][0][field] = "https://user:secret@example.gov/document"
                self.assertTrue(any(f".{field} must be a clean HTTPS URL" in error for error in MODULE.validate(data)))
                data["sources"][0][field] = "https://example.gov/document#fragment"
                self.assertTrue(any(f".{field} must be a clean HTTPS URL" in error for error in MODULE.validate(data)))
                data["sources"][0][field] = "https://example.gov/document?X-Amz-Signature=secret"
                self.assertTrue(any(f".{field} must be a clean HTTPS URL" in error for error in MODULE.validate(data)))

    def test_secondary_metadata_lead_requires_safe_locator_and_summary(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if "secondary_metadata_lead" in item)
        source["secondary_metadata_lead"]["url"] = "https://user:secret@example.gov/lead"
        self.assertTrue(any("secondary_metadata_lead must contain a clean HTTPS url" in error for error in MODULE.validate(data)))
        source["secondary_metadata_lead"]["url"] = "https://example.gov/lead"
        source["secondary_metadata_lead"]["summary"] = ""
        self.assertTrue(any("secondary_metadata_lead must contain a clean HTTPS url" in error for error in MODULE.validate(data)))

    def test_related_source_pages_are_validated_as_clean_https_locators(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = data["sources"][0]
        source["related_source_pages"] = ["https://example.gov/related"]
        self.assertEqual(MODULE.validate(data), [])
        source["related_source_pages"] = ["https://user:secret@example.gov/related"]
        self.assertTrue(any("related_source_pages must be a list of clean HTTPS URLs" in error for error in MODULE.validate(data)))
        source["related_source_pages"] = "https://example.gov/related"
        self.assertTrue(any("related_source_pages must be a list of clean HTTPS URLs" in error for error in MODULE.validate(data)))

if __name__ == "__main__":
    unittest.main()
