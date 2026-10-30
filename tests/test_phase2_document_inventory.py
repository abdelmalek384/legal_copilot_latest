import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.validate_phase2_document_inventory import DEFAULT_PATH, validate_inventory


class Phase2DocumentInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = json.loads(DEFAULT_PATH.read_text(encoding="utf-8"))

    def test_current_inventory_is_metadata_only_and_structurally_valid(self):
        self.assertEqual(validate_inventory(self.inventory), [])
        self.assertEqual(len(self.inventory["documents"]), 79)
        self.assertTrue(all(d["review_status"] != "verified" for d in self.inventory["documents"]))
        self.assertTrue(all(d["legal_status"] in {"unknown", "not_applicable"} for d in self.inventory["documents"]))
        register = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        register_ids = {source["source_id"] for source in register["sources"]}
        self.assertIn("EG-MINISTRY-LABOUR-LAWS", register_ids)
        self.assertIn("EG-MINISTRY-LABOUR-LAWS", self.inventory["source_ids"])
        self.assertNotIn("EG-MINISTRY-OF-LABOUR", self.inventory["source_ids"])
        for document_id in (
            "EG-LABOUR-WORK-REGULATION-RULES-2026",
            "EG-LABOUR-DECISION-49-2026",
            "EG-LABOUR-DECISION-294-2025",
        ):
            record = next(d for d in self.inventory["documents"] if d["document_id"] == document_id)
            self.assertEqual(record["source_id"], "EG-MINISTRY-LABOUR-LAWS")

    def test_2026_labour_work_regulation_rules_remain_discovery_only(self):
        record = next(
            d for d in self.inventory["documents"]
            if d["document_id"] == "EG-LABOUR-WORK-REGULATION-RULES-2026"
        )
        self.assertEqual(record["source_id"], "EG-MINISTRY-LABOUR-LAWS")
        self.assertEqual(record["source_status"], "official_index_discovered_primary_text_pending")
        self.assertEqual(record["collection_permission"], "unknown")
        self.assertEqual(record["legal_status"], "unknown")
        self.assertEqual(record["review_status"], "discovery_only")
        self.assertTrue(any(a["id"] == "ACT-LABOUR-DECISION-49-2026-VERIFY" for a in self.inventory["next_actions"]))
        self.assertIsNone(record["instrument_number"])
        self.assertIn("official Gazette text/pages", record["notes"])
        self.assertEqual(validate_inventory(self.inventory), [])

    def test_decision_264_has_2026_followup_without_claiming_text_or_status_verified(self):
        record = next(
            d for d in self.inventory["documents"]
            if d["document_id"] == "EG-LABOUR-DECISION-264-2025"
        )
        self.assertTrue(any("sis.gov.eg" in item["url"] for item in record["source_urls"]))
        self.assertEqual(record["review_status"], "discovery_only")
        self.assertEqual(record["legal_status"], "unknown")
        self.assertEqual(record["collection_permission"], "permission_pending")
        self.assertTrue(any(a["id"] == "ACT-LABOUR-DECISION-264-2026-STANDARDS-VERIFY" for a in self.inventory["next_actions"]))
        self.assertTrue(any("exact standards text" in item for item in record["required_related_records"]))
        self.assertEqual(validate_inventory(self.inventory), [])

    def test_2026_labour_decision_49_remains_discovery_only(self):
        record = next(
            d for d in self.inventory["documents"]
            if d["document_id"] == "EG-LABOUR-DECISION-49-2026"
        )
        self.assertEqual(record["instrument_number"], 49)
        self.assertEqual(record["instrument_year"], 2026)
        self.assertEqual(record["source_id"], "EG-MINISTRY-LABOUR-LAWS")
        self.assertEqual(record["collection_permission"], "unknown")
        self.assertEqual(record["legal_status"], "unknown")
        self.assertEqual(record["review_status"], "discovery_only")
        self.assertTrue(any("labour.gov.eg" in item["url"] for item in record["source_urls"]))
        self.assertEqual(validate_inventory(self.inventory), [])

    def test_2025_labour_decision_294_remains_discovery_only(self):
        record = next(
            d for d in self.inventory["documents"]
            if d["document_id"] == "EG-LABOUR-DECISION-294-2025"
        )
        self.assertEqual(record["instrument_number"], 294)
        self.assertEqual(record["instrument_year"], 2025)
        self.assertEqual(record["collection_permission"], "unknown")
        self.assertEqual(record["legal_status"], "unknown")
        self.assertEqual(record["review_status"], "discovery_only")
        self.assertTrue(any("labour.gov.eg" in item["url"] for item in record["source_urls"]))
        self.assertTrue(any(a["id"] == "ACT-LABOUR-DECISION-294-2025-VERIFY" for a in self.inventory["next_actions"]))
        self.assertEqual(validate_inventory(self.inventory), [])

    def test_labour_executive_regulations_gap_is_an_action_not_a_claim_of_nonexistence(self):
        law = next(d for d in self.inventory["documents"] if d["document_id"] == "EG-LABOUR-LAW-14-2025")
        self.assertTrue(any("Ministry of Labour laws-and-legislations index" in law["notes"] for _ in [0]))
        action = next(a for a in self.inventory["next_actions"] if a["id"] == "ACT-LABOUR-LAW-14-2025-EXEC-REGS-VERIFY")
        self.assertIn("not proof of non-existence", action["action"])
        self.assertEqual(action["status"], "not_started")
        self.assertEqual(validate_inventory(self.inventory), [])

    def test_2026_labour_remote_work_and_wages_decisions_are_separate_discovery_records(self):
        expected = {
            "EG-LABOUR-PM-DECISION-982-2026": "official_text_candidate",
            "EG-LABOUR-PM-DECISION-1305-2026": "official_text_candidate",
            "EG-LABOUR-PM-DECISION-1572-2026": "later_official_citation_only",
            "EG-LABOUR-PM-DECISION-2033-2026": "later_official_citation_only",
            "EG-LABOUR-PM-DECISION-2377-2026": "official_text_candidate",
            "EG-LABOUR-PM-DECISION-2590-2026": "official_text_candidate",
            "EG-LABOUR-PM-DECISION-3165-2026": "official_text_candidate",
        }
        law = next(d for d in self.inventory["documents"] if d["document_id"] == "EG-LABOUR-LAW-14-2025")
        related_ids = {item["document_id"] for item in law["related_instruments"]}
        for document_id, expected_source_status in expected.items():
            record = next(d for d in self.inventory["documents"] if d["document_id"] == document_id)
            self.assertIn(document_id, related_ids)
            self.assertEqual(record["source_id"], "EG-AMIRI-PRESS")
            self.assertEqual(record["source_status"], expected_source_status)
            self.assertEqual(record["collection_permission"], "unknown")
            self.assertEqual(record["legal_status"], "unknown")
            self.assertEqual(record["review_status"], "discovery_only")
            self.assertTrue(record["required_related_records"])
            self.assertTrue(record["source_urls"])
        self.assertTrue(any("dspace.id.com.eg/items/90a235e2" in u["url"] for u in next(d for d in self.inventory["documents"] if d["document_id"] == "EG-LABOUR-PM-DECISION-1305-2026")["source_urls"]))
        self.assertTrue(any("dspace.id.com.eg/items/3ce63ac9" in u["url"] for u in next(d for d in self.inventory["documents"] if d["document_id"] == "EG-LABOUR-PM-DECISION-1572-2026")["source_urls"]))
        self.assertTrue(any("dspace.id.com.eg/items/080b6ab2" in u["url"] for u in next(d for d in self.inventory["documents"] if d["document_id"] == "EG-LABOUR-PM-DECISION-2033-2026")["source_urls"]))
        self.assertTrue(any(u["status"].endswith("requires_DSpace_login") for u in next(d for d in self.inventory["documents"] if d["document_id"] == "EG-LABOUR-PM-DECISION-1305-2026")["source_urls"] if "dspace.id.com.eg" in u["url"]))
        for document_id in ("EG-LABOUR-PM-DECISION-1572-2026", "EG-LABOUR-PM-DECISION-2033-2026"):
            record = next(d for d in self.inventory["documents"] if d["document_id"] == document_id)
            self.assertTrue(any(u["status"].endswith("request_copy_restricted") for u in record["source_urls"] if "dspace.id.com.eg" in u["url"]))
        self.assertEqual(validate_inventory(self.inventory), [])

    def test_unknown_source_and_duplicate_instrument_ids_are_rejected(self):
        data = copy.deepcopy(self.inventory)
        data["documents"][0]["source_id"] = "EG-NOT-REGISTERED"
        data["documents"][1]["document_id"] = data["documents"][0]["document_id"]
        errors = validate_inventory(data)
        self.assertTrue(any("unknown source_id" in e for e in errors))
        self.assertTrue(any("duplicate document_id" in e for e in errors))

    def test_inventory_rejects_embedded_legal_text_and_non_https_urls(self):
        data = copy.deepcopy(self.inventory)
        data["documents"][0]["full_text"] = "must never be embedded"
        data["documents"][0]["source_urls"] = [{"url": "http://example.invalid/law"}]
        errors = validate_inventory(data)
        self.assertTrue(any("content field full_text" in e for e in errors))
        self.assertTrue(any("must be HTTPS or null" in e for e in errors))

    def test_in_force_and_verified_states_require_evidence(self):
        data = copy.deepcopy(self.inventory)
        data["documents"][0]["legal_status"] = "in_force"
        data["documents"][0]["review_status"] = "verified"
        data["documents"][0]["effective_date"] = "2020-01-01"
        errors = validate_inventory(data)
        self.assertTrue(any("explicit collection permission" in e for e in errors))
        self.assertTrue(any("explicit commercial reuse permission" in e for e in errors))
        self.assertTrue(any("permission evidence" in e for e in errors))

    def test_source_permission_state_is_validated_independently(self):
        data = copy.deepcopy(self.inventory)
        data["source_ids"]["EG-PRESIDENCY"]["permission"] = "allowed_because_public"
        errors = validate_inventory(data)
        self.assertTrue(any("source_ids.EG-PRESIDENCY has unsupported permission state" in e for e in errors))

    def test_source_record_requires_explicit_permission_metadata(self):
        data = copy.deepcopy(self.inventory)
        del data["source_ids"]["EG-PRESIDENCY"]["permission"]
        errors = validate_inventory(data)
        self.assertTrue(any("source_ids.EG-PRESIDENCY missing permission" in e for e in errors))

    def test_source_url_must_be_https_or_null(self):
        data = copy.deepcopy(self.inventory)
        data["source_ids"]["EG-PRESIDENCY"]["source_url"] = "http://example.invalid"
        errors = validate_inventory(data)
        self.assertTrue(any("source_ids.EG-PRESIDENCY.source_url must be HTTPS or null" in e for e in errors))

    def test_source_permissions_do_not_promote_document_permissions(self):
        data = copy.deepcopy(self.inventory)
        data["source_ids"]["EG-PRESIDENCY"]["permission"] = "allowed"
        self.assertEqual(data["documents"][0]["collection_permission"], "unknown")
        self.assertEqual(data["documents"][0]["review_status"], "discovery_only")
        self.assertEqual(validate_inventory(data), [])


if __name__ == "__main__":
    unittest.main()
