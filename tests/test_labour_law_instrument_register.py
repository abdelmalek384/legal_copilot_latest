import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data" / "candidates" / "labour_law_14_2025" / "related_instruments" / "implementing_decisions_inventory_2026-10-28.json"


class LabourLawInstrumentRegisterTests(unittest.TestCase):
    def test_register_has_expected_public_source_leads(self):
        payload = json.loads(REGISTER.read_text(encoding="utf-8"))
        self.assertEqual(payload["count"], 7)
        self.assertEqual(len(payload["items"]), 7)
        ids = [item["instrument_id"] for item in payload["items"]]
        self.assertEqual(len(ids), len(set(ids)))
        for item in payload["items"]:
            self.assertFalse(item["search_eligible"])
            self.assertTrue(item["source_leads"])
            self.assertTrue(item["articles_mapped"])
            self.assertIn("not_cleared", item["reuse_state"])
            for source in item["source_leads"]:
                self.assertTrue(source["url"].startswith("https://"))
        self.assertIn("EG-MOL-DEC-260-2025", ids)
        self.assertIn("EG-MOL-OSH-DECISIONS-248-252-2026", ids)


if __name__ == "__main__":
    unittest.main()
