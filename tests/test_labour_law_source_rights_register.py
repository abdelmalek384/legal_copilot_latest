import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "data" / "candidates" / "labour_law_14_2025" / "related_instruments" / "source_rights_register_2026-10-28.json"

class LabourLawSourceRightsRegisterTests(unittest.TestCase):
    def test_sources_are_provenance_leads_not_permission_claims(self):
        data = json.loads(REGISTER.read_text(encoding="utf-8"))
        self.assertEqual(len(data["sources"]), 9)
        ids = [source["source_id"] for source in data["sources"]]
        self.assertEqual(len(ids), len(set(ids)))
        for source in data["sources"]:
            self.assertTrue(source["url"].startswith("https://"))
            if source["source_class"] != "community_transcription":
                self.assertIn(source.get("commercial_reuse_permission", "unknown_not_cleared"), {"unknown_not_cleared", "not_assumed"})
        gazette = next(source for source in data["sources"] if source["source_id"] == "SRC-ETA-OFFICIAL-GAZETTE-PDF")
        self.assertFalse(gazette["binary_obtained_and_hashed"])
        self.assertIn("Do not bypass access restrictions", data["policy"])

if __name__ == "__main__":
    unittest.main()
