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
