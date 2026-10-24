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
        self.assertEqual(len(self.inventory["documents"]), 69)
        self.assertTrue(all(d["review_status"] != "verified" for d in self.inventory["documents"]))
        self.assertTrue(all(d["legal_status"] in {"unknown", "not_applicable"} for d in self.inventory["documents"]))

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


if __name__ == "__main__":
    unittest.main()
