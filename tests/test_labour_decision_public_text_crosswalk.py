import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "candidates" / "labour_law_14_2025" / "related_instruments" / "public_text_crosswalk_2026-10-28.json"
INVENTORY = ROOT / "docs" / "phase_2_document_inventory.json"


class TestLabourDecisionPublicTextCrosswalk(unittest.TestCase):
    def test_working_time_decisions_keep_primary_and_secondary_evidence_separate(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        records = {item["document_id"]: item for item in data["decisions"]}
        self.assertFalse(data["search_eligible"])
        d290 = records["EG-LABOUR-DECISION-290-2025"]
        d291 = records["EG-LABOUR-DECISION-291-2025"]
        for record in (d290, d291):
            self.assertEqual(record["primary_lead"]["url"], "https://dspace.id.com.eg/items/32fa3458-c4a5-4a6a-950c-23c6c74d41c1")
            self.assertIn("request-a-copy restricted", record["primary_lead"]["status"])
            self.assertEqual(record["gazette_date"], "2025-12-30 (official Amiri Press issue metadata; secondary EastLaws record independently states the same Gazette publication date)")
            self.assertEqual(record["effective_date"], "2025-12-31 (stated by EastLaws and derived from Article 4 in both secondary transcriptions; not primary-PDF verified)" if record is d290 else "2025-12-31 (stated by EastLaws and derived from Article 5 in both secondary transcriptions; not primary-PDF verified)")
            self.assertIn("Two public secondary full-text transcriptions", record["secondary_text"]["status"])
            self.assertIn("neither compared", record["secondary_text"]["status"])
            self.assertIn("unknown", record["reuse_rights"])
            self.assertTrue(record["currentness"].startswith("not fully verified"))
            self.assertFalse(record.get("search_eligible", False))
        self.assertIn("seven categories", d290["secondary_text"]["summary"])
        self.assertIn("35%", d291["secondary_text"]["summary"])
        self.assertIn("70%", d291["secondary_text"]["summary"])
        self.assertIn("annual overtime maximum", d291["secondary_text"]["summary"])
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        docs = {item["document_id"]: item for item in inventory["documents"]}
        for document_id, url in (("EG-LABOUR-DECISION-290-2025", "https://www.eastlaws.com/legislation-full-text/ar/egypt/labor/30-12-2025/no-290?id=5008505&type=1"), ("EG-LABOUR-DECISION-291-2025", "https://www.eastlaws.com/legislation-full-text/ar/egypt/labor/30-12-2025/no-291?id=5064176&type=1")):
            record = docs[document_id]
            self.assertEqual(record["legal_status"], "unknown")
            self.assertEqual(record["review_status"], "discovery_only")
            self.assertTrue(any(source["url"] == url and "secondary" in source["status"] for source in record["source_urls"]))



    def test_decisions_292_and_294_have_issue_metadata_and_secondary_text(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        records = {item["document_id"]: item for item in data["decisions"]}
        for document_id in ("EG-LABOUR-DECISION-292-2025", "EG-LABOUR-DECISION-294-2025"):
            item = records[document_id]
            self.assertEqual(item["primary_lead"]["url"], "https://dspace.id.com.eg/items/37add437-802d-4848-8a24-8e064db22fcc/full")
            self.assertIn("request-a-copy restricted", item["primary_lead"]["status"])
            self.assertIn("Two public secondary", item["secondary_text"]["status"])
            self.assertIn("neither compared", item["secondary_text"]["status"])
            self.assertTrue(item["currentness"].startswith("not fully verified"))
            self.assertIn("unknown", item["reuse_rights"])
        self.assertIn("48 hours", records["EG-LABOUR-DECISION-292-2025"]["secondary_text"]["summary"])
        self.assertIn("12 public holidays", records["EG-LABOUR-DECISION-294-2025"]["secondary_text"]["summary"])


    def test_decisions_288_and_289_have_secondary_crosswalks(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        records = {item["document_id"]: item for item in data["decisions"]}
        for document_id in ("EG-LABOUR-DECISION-288-2025", "EG-LABOUR-DECISION-289-2025"):
            item = records[document_id]
            self.assertEqual(item["primary_lead"]["url"], "https://dspace.id.com.eg/items/32fa3458-c4a5-4a6a-950c-23c6c74d41c1")
            self.assertIn("request-a-copy restricted", item["primary_lead"]["status"])
            self.assertIn("neither compared", item["secondary_text"]["status"])
            self.assertTrue(item["currentness"].startswith("not fully verified"))
            self.assertIn("unknown", item["reuse_rights"])
        self.assertIn("five consecutive hours", records["EG-LABOUR-DECISION-288-2025"]["secondary_text"]["summary"])
        self.assertIn("48 hours per week", records["EG-LABOUR-DECISION-289-2025"]["secondary_text"]["summary"])


if __name__ == "__main__":
    unittest.main()
