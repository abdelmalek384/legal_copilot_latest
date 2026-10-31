import importlib.util
import unittest
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

    def test_permission_claim_requires_evidence_and_date(self):
        item = {
            "source_id": "S1", "authority": "Example", "source_page": "https://example.gov/",
            "material_types": ["law"], "access_status": "public",
            "collection_permission": "allowed", "commercial_reuse_permission": "unknown",
            "required_next_action": "review"
        }
        errors = MODULE.validate({"sources": [item]})
        self.assertTrue(any("permission_evidence" in error for error in errors))

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

    def test_credentials_in_source_urls_are_rejected(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        for url in (
            "https://user:secret@example.gov/law",
            " https://example.gov/law",
            "https://example.gov/law file",
            "https://example.gov:99999/law",
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
        self.assertTrue(any("valid terms_checked_on date" in error for error in errors))

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
        self.assertIn("Do not bypass", source["required_next_action"])
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

if __name__ == "__main__":
    unittest.main()

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
            [5, 105, 106, 107, 108, 109, 110, 111],
        )
        self.assertEqual(source["collection_permission"], "unknown")
        self.assertEqual(source["commercial_reuse_permission"], "unknown")
        self.assertIsNone(source["terms_checked_on"])
        self.assertIn("download attempt failed", source["permission_evidence"])
        self.assertEqual(MODULE.validate(data), [])
