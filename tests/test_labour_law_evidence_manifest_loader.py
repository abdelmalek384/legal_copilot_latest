import unittest
from pathlib import Path

from tools.report_labour_law_evidence_cards import DEFAULT_INPUT, load_inventory, render_report


class LabourLawEvidenceManifestLoaderTests(unittest.TestCase):
    def test_report_loader_uses_reconciled_canonical_inventory(self):
        data = load_inventory(DEFAULT_INPUT)
        self.assertEqual(len(data["cards"]), 360)
        ids = [card["card_id"] for card in data["cards"]]
        self.assertEqual(len(ids), len(set(ids)))
        for card in data["cards"]:
            self.assertIn("card_id", card)
            self.assertIn("pinpoint", card)
            self.assertIn("primary_evidence", card)
            self.assertIn("limitations", card)
        self.assertIn("Canonical manifest inventory loaded: 360 cards", data["source_method_note"])\n        self.assertTrue(all(card["search_eligible"] is False for card in data["cards"]))
        self.assertIn("archived split snapshots are excluded", data["source_method_note"])
        report = render_report(data)
        self.assertIn("**Cards in this report:** 360", report)
        self.assertEqual(sum(1 for line in report.splitlines() if line.startswith("### ") and line[4:5].isdigit()), 360)


if __name__ == "__main__":
    unittest.main()
