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

    def test_dataflare_egyptian_corpus_mit_claim_does_not_clear_underlying_records(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in data["sources"] if item["source_id"] == "EG-DATAFLARE-LEGAL-CORPUS")
        self.assertEqual(source["collection_permission"], "unknown")
        self.assertEqual(source["commercial_reuse_permission"], "unknown")
        self.assertIn("MIT", source["permission_evidence"])
        self.assertIn("no record-level source URL", source["permission_evidence"])
        self.assertIn("date=None", source["permission_evidence"])
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

if __name__ == "__main__":
    unittest.main()
