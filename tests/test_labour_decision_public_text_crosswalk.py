import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "candidates" / "labour_law_14_2025" / "related_instruments" / "public_text_crosswalk_2026-10-28.json"

class TestLabourDecisionPublicTextCrosswalk(unittest.TestCase):
    def test_working_time_and_holiday_decisions_keep_evidence_gates(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        records = {item["document_id"]: item for item in data["decisions"]}
        self.assertEqual(set(records), {"EG-LABOUR-DECISION-49-2026", "EG-LABOUR-WORK-REGULATION-RULES-2026", "EG-LABOUR-DECISION-187-2025", "EG-LABOUR-DECISION-214-2025", "EG-LABOUR-DECISION-290-2025", "EG-LABOUR-DECISION-291-2025", "EG-LABOUR-DECISION-292-2025", "EG-LABOUR-DECISION-294-2025"})
        self.assertFalse(data["search_eligible"])
        for item in records.values():
            self.assertEqual(item["reuse_rights"], "unknown")
            self.assertTrue(item["currentness"].startswith("not verified"), item["currentness"])
            self.assertTrue(item["primary_lead"]["url"].startswith("https://"))
            self.assertTrue(item["card_action"])
        self.assertIn(117, records["EG-LABOUR-DECISION-290-2025"]["related_law_articles"])
        self.assertIn(129, records["EG-LABOUR-DECISION-294-2025"]["related_law_articles"])
        self.assertEqual(records["EG-LABOUR-DECISION-290-2025"]["primary_lead"]["url"], "https://dspace.id.com.eg/items/32fa3458-c4a5-4a6a-950c-23c6c74d41c1")
        self.assertIn("request-a-copy restricted", records["EG-LABOUR-DECISION-290-2025"]["primary_lead"]["status"])
        self.assertEqual(records["EG-LABOUR-DECISION-290-2025"]["secondary_text"]["url"], "https://lawhub.info/eg/?p=17303")
        self.assertIn("not compared", records["EG-LABOUR-DECISION-290-2025"]["secondary_text"]["status"])
        self.assertEqual(records["EG-LABOUR-DECISION-291-2025"]["primary_lead"]["url"], "https://dspace.id.com.eg/items/32fa3458-c4a5-4a6a-950c-23c6c74d41c1")
        self.assertEqual(records["EG-LABOUR-DECISION-291-2025"]["secondary_text"]["url"], "https://lawhub.info/eg/?p=17302")
        self.assertIn("not checked", records["EG-LABOUR-DECISION-291-2025"]["secondary_text"]["status"])

if __name__ == "__main__":
    unittest.main()

    def test_inventory_keeps_secondary_text_distinct_from_primary_verification(self):
        inventory_path = ROOT / "docs" / "phase_2_document_inventory.json"
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        records = {item["document_id"]: item for item in inventory["documents"]}
        for document_id in ("EG-LABOUR-DECISION-290-2025", "EG-LABOUR-DECISION-292-2025", "EG-LABOUR-DECISION-294-2025"):
            with self.subTest(document_id=document_id):
                record = records[document_id]
                self.assertIn("secondary", record["source_status"])
                self.assertEqual(record["legal_status"], "unknown")
                self.assertEqual(record["collection_permission"], "unknown")
                self.assertTrue(any(item["url"].startswith("https://") for item in record["source_urls"]))

