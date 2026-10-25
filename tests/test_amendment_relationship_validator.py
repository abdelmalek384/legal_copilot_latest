import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_amendment_relationships", ROOT / "tools" / "validate_amendment_relationships.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AmendmentRelationshipValidatorTests(unittest.TestCase):
    def test_committed_register_reports_unresolved_relationships(self):
        relationships = json.loads(
            (ROOT / "docs" / "phase_2_amendment_relationships.json").read_text(encoding="utf-8")
        )
        inventory = json.loads(
            (ROOT / "docs" / "phase_2_document_inventory.json").read_text(encoding="utf-8")
        )
        report = MODULE.validate(relationships, inventory)
        self.assertEqual(report["relationships_checked"], len(relationships["relationships"]))
        self.assertGreater(report["warning_count"], 0)
        self.assertTrue(any(item["code"] == "relationship_not_reviewed_confirmed" for item in report["warnings"]))

    def test_non_base_relationship_requires_known_target(self):
        report = MODULE.validate(
            {"relationships": [{
                "relationship_id": "REL-1",
                "source_instrument_id": "LAW-A",
                "target_instrument_id": "MISSING-LAW",
                "relationship_type": "amends_specified_provisions",
                "status": "provision_mapping_pending",
                "source_url": "https://gazette.example.gov/law.pdf",
                "required_evidence": ["Official Gazette text"],
                "affected_provisions": ["Article 3"],
            }]},
            {"documents": [{"document_id": "LAW-A"}]},
        )
        self.assertTrue(any(item["code"] == "target_instrument_missing_from_inventory" for item in report["errors"]))

    def test_base_instrument_can_have_null_target(self):
        report = MODULE.validate(
            {"relationships": [{
                "relationship_id": "REL-BASE",
                "source_instrument_id": "LAW-A",
                "target_instrument_id": None,
                "relationship_type": "base_instrument",
                "status": "later_official_citation_only",
                "source_url": "https://gazette.example.gov/law.pdf",
                "required_evidence": ["Original Gazette text"],
            }]},
            {"documents": [{"document_id": "LAW-A"}]},
        )
        self.assertEqual(report["error_count"], 0)

    def test_duplicate_and_missing_relationship_ids_are_reported(self):
        base = {
            "source_instrument_id": "LAW-A",
            "target_instrument_id": None,
            "relationship_type": "base_instrument",
            "status": "under_review",
            "source_url": "https://gazette.example.gov/law.pdf",
            "required_evidence": ["Original Gazette text"],
        }
        report = MODULE.validate(
            {"relationships": [
                {**base, "relationship_id": "REL-DUP"},
                {**base, "relationship_id": "REL-DUP"},
                {**base, "relationship_id": "   "},
            ]},
            {"documents": [{"document_id": "LAW-A"}]},
        )
        codes = [item["code"] for item in report["errors"]]
        self.assertIn("duplicate_relationship_id", codes)
        self.assertIn("missing_relationship_id", codes)

    def test_https_source_url_with_embedded_credentials_is_rejected(self):
        report = MODULE.validate(
            {"relationships": [{
                "relationship_id": "REL-CREDENTIALS",
                "source_instrument_id": "LAW-A",
                "target_instrument_id": None,
                "relationship_type": "base_instrument",
                "status": "under_review",
                "source_url": "https://reviewer:secret@gazette.example.gov/law.pdf",
                "required_evidence": ["Original Gazette text"],
            }]},
            {"documents": [{"document_id": "LAW-A"}]},
        )
        self.assertTrue(any(item["code"] == "missing_or_invalid_https_source_url" for item in report["errors"]))

    def test_effective_date_must_be_a_real_iso_calendar_date(self):
        base = {
            "relationship_id": "REL-DATE",
            "source_instrument_id": "LAW-A",
            "target_instrument_id": None,
            "relationship_type": "base_instrument",
            "status": "under_review",
            "source_url": "https://gazette.example.gov/law.pdf",
            "required_evidence": ["Original Gazette text"],
        }
        inventory = {"documents": [{"document_id": "LAW-A"}]}
        for value in ("2026-13-01", "2026-02-30", "26-01-01", "20261025", 20261025, True):
            with self.subTest(effective_date=value):
                report = MODULE.validate(
                    {"relationships": [{**base, "instrument_effective_date": value}]}, inventory
                )
                self.assertTrue(any(
                    item["code"] == "invalid_effective_date_value" for item in report["errors"]
                ))
        for value in ("2024-02-29", "2026-10-25", None, "unknown_pending_gazette_verification"):
            with self.subTest(effective_date=value):
                report = MODULE.validate(
                    {"relationships": [{**base, "instrument_effective_date": value}]}, inventory
                )
                self.assertFalse(any(
                    item["code"] == "invalid_effective_date_value" for item in report["errors"]
                ))

    def test_duplicate_and_missing_document_ids_are_reported(self):
        base_relationship = {
            "relationship_id": "REL-BASE",
            "source_instrument_id": "LAW-A",
            "target_instrument_id": None,
            "relationship_type": "base_instrument",
            "status": "under_review",
            "source_url": "https://gazette.example.gov/law.pdf",
            "required_evidence": ["Original Gazette text"],
        }
        report = MODULE.validate(
            {"relationships": [base_relationship]},
            {"documents": [
                {"document_id": "LAW-A"},
                {"document_id": "LAW-A"},
                {"title": "Missing ID"},
                None,
            ]},
        )
        codes = [item["code"] for item in report["errors"]]
        self.assertIn("duplicate_document_id", codes)
        self.assertIn("missing_document_id", codes)
        self.assertIn("invalid_document_entry", codes)

    def test_invalid_document_schema_is_reported_without_crashing(self):
        report = MODULE.validate({"relationships": []}, {"documents": {}})
        self.assertIn("schema_error", report)
        self.assertEqual(report["relationships_checked"], 0)

    def test_invalid_or_missing_source_url_is_error(self):
        report = MODULE.validate(
            {"relationships": [{
                "relationship_id": "REL-BASE",
                "source_instrument_id": "LAW-A",
                "target_instrument_id": None,
                "relationship_type": "base_instrument",
                "status": "later_official_citation_only",
                "source_url": "http://gazette.example.gov/law.pdf",
                "required_evidence": ["Original Gazette text"],
            }]},
            {"documents": [{"document_id": "LAW-A"}]},
        )
        self.assertTrue(any(item["code"] == "missing_or_invalid_https_source_url" for item in report["errors"]))


if __name__ == "__main__":
    unittest.main()
