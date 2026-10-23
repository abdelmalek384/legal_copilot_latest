import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_source_permission_register", ROOT / "tools" / "validate_source_permission_register.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class SourcePermissionRegisterTests(unittest.TestCase):
    def test_committed_register_validates(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        self.assertEqual(MODULE.validate(data), [])

    def test_permission_claim_requires_evidence_and_date(self):
        item = {
            "source_id": "S1", "authority": "Example", "source_page": "https://example.gov/",
            "material_types": ["law"], "access_status": "public",
            "collection_permission": "allowed", "commercial_reuse_permission": "unknown",
            "required_next_action": "review"
        }
        errors = MODULE.validate({"sources": [item]})
        self.assertTrue(any("permission_evidence" in error for error in errors))

    def test_duplicate_source_ids_rejected(self):
        import json
        data = json.loads((ROOT / "docs" / "source_permission_register.json").read_text(encoding="utf-8"))
        data["sources"].append(dict(data["sources"][0]))
        self.assertTrue(any("duplicate source_id" in error for error in MODULE.validate(data)))

if __name__ == "__main__":
    unittest.main()
