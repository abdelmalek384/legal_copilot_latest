import copy
from urllib.parse import urlsplit
import json
import sys
import unittest
from pathlib import Path

def _has_https_host(url, expected_host):
    try:
        parsed = urlsplit(url)
    except ValueError:
        return False
    hostname = (parsed.hostname or "").lower()
    expected_host = expected_host.lower()
    return (
        parsed.scheme == "https"
        and not parsed.username
        and not parsed.password
        and (hostname == expected_host or hostname.endswith("." + expected_host))
    )


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.validate_phase2_document_inventory import DEFAULT_PATH, validate_inventory


class Phase2DocumentInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = json.loads(DEFAULT_PATH.read_text(encoding="utf-8"))

    def test_current_inventory_is_metadata_only_and_structurally_valid(self):
        self.assertEqual(validate_inventory(self.inventory), [])
        self.assertEqual(len(self.inventory["documents"]), 85)
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
        ):
            record = next(d for d in self.inventory["documents"] if d["document_id"] == document_id)
            self.assertEqual(record["source_id"], "EG-MINISTRY-LABOUR-LAWS")

    def test_2026_labour_work_regulation_rules_remain_discovery_only(self):
        record = next(
            d for d in self.inventory["documents"]
            if d["document_id"] == "EG-LABOUR-WORK-REGULATION-RULES-2026"
        )
        self.assertEqual(record["source_id"], "EG-MINISTRY-LABOUR-LAWS")
        self.assertEqual(record["source_status"], "official_Gazette_metadata_verified_primary_text_restricted_secondary_full_text_crosscheck_found")
        self.assertEqual(record["collection_permission"], "unknown")
        self.assertEqual(record["legal_status"], "unknown")
        self.assertEqual(record["review_status"], "discovery_only")
        self.assertTrue(any(a["id"] == "ACT-LABOUR-DECISION-49-2026-VERIFY" for a in self.inventory["next_actions"]))
        self.assertEqual(record["instrument_number"], 162)
        self.assertIn("request-a-copy form", record["notes"])
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
        self.assertEqual(record["source_id"], "EG-IDSC-GAZETTE-2025-291-SUPPLEMENT-LABOUR")
        self.assertEqual(record["collection_permission"], "not_allowed_without_explicit_exception_or_license")
        self.assertEqual(record["legal_status"], "unknown")
        self.assertEqual(record["review_status"], "discovery_only")
        self.assertTrue(any("dspace.id.com.eg/items/37add437" in item["url"] for item in record["source_urls"]))
        self.assertTrue(any(a["id"] == "ACT-LABOUR-DECISION-294-2025-VERIFY" for a in self.inventory["next_actions"]))
        self.assertEqual(validate_inventory(self.inventory), [])

    def test_labour_executive_regulations_gap_is_an_action_not_a_claim_of_nonexistence(self):
        law = next(d for d in self.inventory["documents"] if d["document_id"] == "EG-LABOUR-LAW-14-2025")
        self.assertTrue(any("Ministry of Labour laws-and-legislations index" in law["notes"] for _ in [0]))
        action = next(a for a in self.inventory["next_actions"] if a["id"] == "ACT-LABOUR-LAW-14-2025-EXEC-REGS-VERIFY")
        self.assertIn("not proof of non-existence", action["action"])
        self.assertEqual(action["status"], "not_started")
        self.assertEqual(validate_inventory(self.inventory), [])

    def test_later_labour_source_labels_remain_discovery_only(self):
        expected = {
            "EG-LABOUR-WORK-REGULATION-RULES-2026",
            "EG-LABOUR-DECISION-49-2026",
            "EG-LABOUR-DECISION-294-2025",
            "EG-LABOUR-DECISION-214-2025",
            "EG-LABOUR-DECISION-187-2025",
            "EG-LABOUR-DECISION-288-2025",
            "EG-LABOUR-DECISION-289-2025",
            "EG-LABOUR-DECISION-290-2025",
            "EG-LABOUR-DECISION-291-2025",
            "EG-LABOUR-DECISION-292-2025",
        }
        records = {d["document_id"]: d for d in self.inventory["documents"]}
        self.assertTrue(expected.issubset(records))
        for document_id in expected:
            record = records[document_id]
            self.assertNotEqual(record["source_status"], "verified")
            if document_id in {"EG-LABOUR-DECISION-288-2025", "EG-LABOUR-DECISION-289-2025", "EG-LABOUR-DECISION-290-2025", "EG-LABOUR-DECISION-291-2025"}:
                self.assertEqual(record["collection_permission"], "not_allowed_without_explicit_exception_or_license")
                self.assertEqual(record["source_id"], "EG-IDSC-GAZETTE-2025-295-SUPPLEMENT-D")
            elif document_id in {"EG-LABOUR-DECISION-292-2025", "EG-LABOUR-DECISION-294-2025"}:
                self.assertEqual(record["collection_permission"], "not_allowed_without_explicit_exception_or_license")
                self.assertEqual(record["source_id"], "EG-IDSC-GAZETTE-2025-291-SUPPLEMENT-LABOUR")
            else:
                self.assertEqual(record["collection_permission"], "unknown")
            self.assertEqual(record["legal_status"], "unknown")
            self.assertEqual(record["review_status"], "discovery_only")
        self.assertEqual(validate_inventory(self.inventory), [])

    def test_decision_50_2026_remains_discovery_only_scan_candidate(self):
        record = next(d for d in self.inventory["documents"] if d["document_id"] == "EG-LABOUR-DECISION-50-2026")
        self.assertEqual(record["source_status"], "third_party_hosted_gazette_scan_candidate")
        self.assertEqual(record["collection_permission"], "unknown")
        self.assertEqual(record["legal_status"], "unknown")
        self.assertEqual(record["review_status"], "discovery_only")
        self.assertTrue(any(_has_https_host(item["url"], "cairo24.com") for item in record["source_urls"]))
        self.assertTrue(any(a["id"] == "ACT-LABOUR-DECISION-50-2026-VERIFY" for a in self.inventory["next_actions"]))
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


    def test_labour_decisions_248_to_252_are_catalogue_backed_but_quarantined(self):
        records = {
            item["document_id"]: item
            for item in self.inventory["documents"]
            if item["document_id"] in {
                "EG-LABOUR-DECISION-248-2026",
                "EG-LABOUR-DECISION-249-2026",
                "EG-LABOUR-DECISION-250-2026",
                "EG-LABOUR-DECISION-251-2026",
                "EG-LABOUR-DECISION-252-2026",
            }
        }
        self.assertEqual(len(records), 5)
        for number in (248, 249, 250, 251, 252):
            record = records[f"EG-LABOUR-DECISION-{number}-2026"]
            self.assertEqual(record["instrument_number"], number)
            self.assertEqual(record["instrument_year"], 2026)
            self.assertIn(f"قرار رقم {number} لسنة 2026", record["official_title_ar"])
            self.assertEqual(record["source_id"], "EG-IDSC-DSPACE-GAZETTE")
            self.assertEqual(record["repository_brand"], "Ibrachy & Dermarkar Repository")
            self.assertEqual(record["source_status"], "third_party_repository_metadata_plus_secondary_indexed_text_found; primary_comparison_pending")
            self.assertEqual(record["publication_date"], "2026-10-12")
            self.assertEqual(record["official_gazette_issue"], "225 تابع (أ)")
            self.assertEqual(record["collection_permission"], "unknown")
            self.assertEqual(record["legal_status"], "unknown")
            self.assertEqual(record["review_status"], "discovery_only")
            self.assertTrue(any("dspace.id.com.eg/items/9cf7c0e9" in item["url"] for item in record["source_urls"]))
            self.assertTrue(record["required_related_records"])
            self.assertFalse(record.get("effective_date"))
        decision_250 = records["EG-LABOUR-DECISION-250-2026"]
        self.assertTrue(any("ahmedazimelgamel.blogspot.com/2026/10/250-2026.html" in item["url"] for item in decision_250["source_urls"]))
        self.assertTrue(any("lawhub.info/eg/?p=19706" in item["url"] for item in decision_250["source_urls"]))
        self.assertIn("0/781", decision_250["notes"])
        self.assertTrue(any(action["id"] == "ACT-LABOUR-DECISIONS-248-252-2026-ORIGINAL-GAZETTE-VERIFY" and action["status"] == "blocked" for action in self.inventory["next_actions"]))
        register = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        register_ids = {source["source_id"] for source in register["sources"]}
        dspace_source = next(source for source in register["sources"] if source["source_id"] == "EG-IDSC-DSPACE-GAZETTE")
        self.assertEqual(dspace_source["repository_brand"], "Ibrachy & Dermarkar Repository")
        self.assertEqual(dspace_source["collection_permission"], "unknown")
        self.assertEqual(dspace_source["commercial_reuse_permission"], "unknown")
        for source_id in (
            "EG-IDSC-DSPACE-GAZETTE",
            "EG-ALMASDAR-SECONDARY-LEGAL-NEWS",
            "EG-EGYIN-SECONDARY-LEGAL-NEWS",
            "EG-RIWAQ-ALJAMAL-DECISION-250-2026",
            "EG-LAW-HUB-DECISION-250-2026",
        ):
            self.assertIn(source_id, register_ids)
            self.assertIn(source_id, self.inventory["source_ids"])
        self.assertEqual(validate_inventory(self.inventory), [])


    def test_labour_law_gazette_repository_access_terms_are_restricted(self):
        register = json.loads(
            (ROOT / "docs" / "phase_2_source_evidence_register.json").read_text(encoding="utf-8")
        )
        source = next(
            item for item in register["sources"]
            if item["source_id"] == "EG-IDSC-GAZETTE-2025-18-LABOUR"
        )
        self.assertEqual(source["access_terms_state"], "reviewed_restricted")
        self.assertEqual(
            source["collection_permission"],
            "not_allowed_without_explicit_exception_or_license",
        )
        self.assertEqual(source["terms_checked_on"], "2026-10-31")
        self.assertIn("request-a-copy", source["notes"])
        self.assertIn("commercial reuse remains unapproved", source["notes"])


    def test_working_time_decisions_use_restricted_issue_295_metadata(self):
        records = {item["document_id"]: item for item in self.inventory["documents"]}
        source_id = "EG-IDSC-GAZETTE-2025-295-SUPPLEMENT-D"
        for document_id in ("EG-LABOUR-DECISION-290-2025", "EG-LABOUR-DECISION-291-2025"):
            record = records[document_id]
            self.assertEqual(record["source_id"], source_id)
            self.assertEqual(record["collection_permission"], "not_allowed_without_explicit_exception_or_license")
            self.assertEqual(record["legal_status"], "unknown")
            self.assertEqual(record["review_status"], "discovery_only")
            self.assertTrue(any("32fa3458-c4a5-4a6a-950c-23c6c74d41c1" in item["url"] for item in record["source_urls"]))
            self.assertTrue(any("lawhub.info" in item["url"] for item in record["source_urls"]))
        self.assertIn(source_id, self.inventory["source_ids"])
        register = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in register["sources"] if item["source_id"] == source_id)
        self.assertEqual(source["collection_permission"], "not_allowed_without_explicit_exception_or_license")
        self.assertEqual(source["commercial_reuse_permission"], "prior_written_permission_required_per_published_terms")
        sis_id = "EG-SIS-GAZETTE-2025-295-SUPPLEMENT-D"
        self.assertIn(sis_id, self.inventory["source_ids"])
        for document_id in ("EG-LABOUR-DECISION-290-2025", "EG-LABOUR-DECISION-291-2025"):
            self.assertTrue(any("mediadr.sis.gov.eg" in item["url"] for item in records[document_id]["source_urls"]))
        sis_source = next(item for item in register["sources"] if item["source_id"] == sis_id)
        self.assertEqual(sis_source["collection_permission"], "unknown")
        self.assertEqual(sis_source["commercial_reuse_permission"], "unknown")
        self.assertIn("public viewing", sis_source["access_status"])
        self.assertEqual(validate_inventory(self.inventory), [])


    def test_decisions_292_and_294_use_restricted_issue_291_metadata(self):
        records = {item["document_id"]: item for item in self.inventory["documents"]}
        source_id = "EG-IDSC-GAZETTE-2025-291-SUPPLEMENT-LABOUR"
        for document_id in ("EG-LABOUR-DECISION-292-2025", "EG-LABOUR-DECISION-294-2025"):
            record = records[document_id]
            self.assertEqual(record["source_id"], source_id)
            self.assertEqual(record["collection_permission"], "not_allowed_without_explicit_exception_or_license")
            self.assertEqual(record["legal_status"], "unknown")
            self.assertEqual(record["review_status"], "discovery_only")
            self.assertTrue(any("dspace.id.com.eg/items/37add437" in item["url"] for item in record["source_urls"]))
            self.assertTrue(any("lawhub.info" in item["url"] for item in record["source_urls"]))
        self.assertIn(source_id, self.inventory["source_ids"])
        register = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        source = next(item for item in register["sources"] if item["source_id"] == source_id)
        self.assertEqual(source["collection_permission"], "not_allowed_without_explicit_exception_or_license")
        self.assertEqual(source["commercial_reuse_permission"], "prior_written_permission_required_per_published_terms")
        self.assertEqual(validate_inventory(self.inventory), [])



    def test_decisions_288_and_289_use_restricted_issue_295_metadata(self):
        records = {item["document_id"]: item for item in self.inventory["documents"]}
        for document_id in ("EG-LABOUR-DECISION-288-2025", "EG-LABOUR-DECISION-289-2025"):
            record = records[document_id]
            self.assertEqual(record["source_id"], "EG-IDSC-GAZETTE-2025-295-SUPPLEMENT-D")
            self.assertEqual(record["collection_permission"], "not_allowed_without_explicit_exception_or_license")
            self.assertEqual(record["legal_status"], "unknown")
            self.assertEqual(record["review_status"], "discovery_only")
            self.assertTrue(any("dspace.id.com.eg/items/32fa3458" in item["url"] for item in record["source_urls"]))
            self.assertTrue(any("lawhub.info" in item["url"] for item in record["source_urls"]))
        self.assertEqual(validate_inventory(self.inventory), [])



    def test_decision_289_ministry_text_copy_is_discovery_only(self):
        record = next(d for d in self.inventory["documents"] if d["document_id"] == "EG-LABOUR-DECISION-289-2025")
        self.assertEqual(record["source_status"], "official_Gazette_metadata_and_secondary_full_text_found; primary_comparison_pending")
        self.assertEqual(record["legal_status"], "unknown")
        self.assertEqual(record["review_status"], "discovery_only")
        self.assertEqual(record["collection_permission"], "not_allowed_without_explicit_exception_or_license")
        self.assertTrue(any("MOM20251227_0415.pdf" in item["url"] for item in record["source_urls"]))
        self.assertEqual(validate_inventory(self.inventory), [])


    def test_decision_288_meles_item_is_metadata_only_and_restricted(self):
        record = next(d for d in self.inventory["documents"] if d["document_id"] == "EG-LABOUR-DECISION-288-2025")
        self.assertEqual(record["legal_status"], "unknown")
        self.assertEqual(record["review_status"], "discovery_only")
        self.assertTrue(any("ca54d3fa-04be-4e59-b9f0-6b3752711a6f" in item["url"] for item in record["source_urls"]))
        self.assertEqual(validate_inventory(self.inventory), [])

if __name__ == "__main__":
    unittest.main()
