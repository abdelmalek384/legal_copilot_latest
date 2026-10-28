import unittest
from pathlib import Path

from tools.report_labour_law_evidence_cards import DEFAULT_INPUT, load_inventory


class LabourLawEvidenceManifestLoaderTests(unittest.TestCase):
    def test_report_loader_includes_all_manifest_supplements(self):
        data = load_inventory(DEFAULT_INPUT)
        self.assertEqual(len(data["cards"]), 250)
        ids = [card["card_id"] for card in data["cards"]]
        self.assertEqual(len(ids), len(set(ids)))
        for card in data["cards"]:
            self.assertIn("card_id", card)
            self.assertIn("pinpoint", card)
            self.assertIn("primary_evidence", card)
            self.assertIn("limitations", card)
        self.assertIn("Supplemental manifest loaded: 53 cards", data["source_method_note"])


if __name__ == "__main__":
    unittest.main()
