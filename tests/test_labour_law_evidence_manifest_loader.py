import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.report_labour_law_evidence_cards as evidence_cards

from tools.report_labour_law_evidence_cards import DEFAULT_INPUT, load_inventory, render_report


class LabourLawEvidenceManifestLoaderTests(unittest.TestCase):
    def test_inventory_and_manifest_reject_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            inventory = root / "provision_evidence_cards.json"
            manifest = root / "provision_evidence_cards_manifest.json"
            inventory.write_text('{"instrument":{},"instrument":{},"cards":[]}', encoding="utf-8")
            with patch.object(evidence_cards, "DEFAULT_INPUT", inventory), patch.object(evidence_cards, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "duplicate JSON object key 'instrument'"):
                    load_inventory(inventory)
            inventory.write_text('{"instrument":{},"cards":[]}', encoding="utf-8")
            manifest.write_text('{"inventory_files":[],"inventory_files":[]}', encoding="utf-8")
            with patch.object(evidence_cards, "DEFAULT_INPUT", inventory), patch.object(evidence_cards, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "duplicate JSON object key 'inventory_files'"):
                    load_inventory(inventory)

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
        self.assertIn("Canonical manifest inventory loaded: 360 cards", data["source_method_note"])
        self.assertTrue(all(card["search_eligible"] is False for card in data["cards"]))
        self.assertIn("archived split snapshots are excluded", data["source_method_note"])
        report = render_report(data)
        self.assertIn("**Cards in this report:** 360", report)
        self.assertEqual(sum(1 for line in report.splitlines() if line.startswith("### ") and line[4:5].isdigit()), 360)


    def test_inventory_loader_rejects_symlink_swap_and_fifo(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            inventory = root / "cards.json"
            inventory.write_text('{"cards":[]}', encoding="utf-8")
            outside = root / "outside.json"
            outside.write_text('{"cards":[]}', encoding="utf-8")
            real_open = evidence_cards.os.open if hasattr(evidence_cards, "os") else __import__("os").open
            import os
            swapped = False

            def replace_before_open(path, flags, *args, **kwargs):
                nonlocal swapped
                if Path(path) == inventory and not swapped:
                    swapped = True
                    inventory.unlink()
                    inventory.symlink_to(outside)
                return real_open(path, flags, *args, **kwargs)

            with patch("tools.validate_source_permission_register.os.open", side_effect=replace_before_open):
                with self.assertRaises(OSError):
                    load_inventory(inventory)
            self.assertTrue(swapped)
            if hasattr(os, "mkfifo"):
                fifo = root / "cards.fifo"
                os.mkfifo(fifo)
                with self.assertRaises(OSError):
                    load_inventory(fifo)

if __name__ == "__main__":
    unittest.main()
