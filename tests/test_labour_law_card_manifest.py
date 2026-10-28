import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "candidates" / "labour_law_14_2025" / "provision_evidence_cards_manifest.json"

class LabourLawCardManifestTests(unittest.TestCase):
    def test_manifest_covers_main_and_split_inventories(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(data["combined_expected_cards"], 240)
        self.assertFalse(data["authoritative_search_eligible"])
        self.assertEqual(len(data["inventory_files"]), 3)
        self.assertEqual(sum(item["expected_cards"] for item in data["inventory_files"]), 240)
        self.assertEqual(data["inventory_files"][1]["article_range"], [256, 274])
        self.assertEqual(data["inventory_files"][2]["article_range"], [275, 298])

if __name__ == "__main__":
    unittest.main()
