"""Human-attested deadline-rule verification CLI tests."""
import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from manage import verify_deadline_rule_file


class VerifyDeadlineRuleCommandTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "deadline_rules.draft.json"
        self.original = {
            "status": "draft_unverified",
            "warning": "Keep this warning while any rule remains unverified.",
            "rules": [
                {"id": "civil_appeal", "amount": 40, "unit": "days",
                 "verified": False, "verified_by": None, "verified_on": None,
                 "source_article": None},
                {"id": "cassation", "amount": 60, "unit": "days",
                 "verified": False, "verified_by": None, "verified_on": None,
                 "source_article": None},
            ],
        }
        self.path.write_text(json.dumps(self.original), encoding="utf-8")
        self.valid = {
            "rule_id": "civil_appeal",
            "lawyer_name": "  Counsel Reviewer  ",
            "source_article": "Official Gazette No. 12, Article 40",
            "verified_on": date.today().isoformat(),
            "lawyer_role": "egyptian_lawyer",
            "review_evidence_url": "https://gazette.example.test/issue/12",
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_updates_only_selected_rule_and_preserves_draft_catalog_status(self):
        verify_deadline_rule_file(self.path, **self.valid)
        saved = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "draft_unverified")
        self.assertEqual(saved["warning"], self.original["warning"])
        selected = saved["rules"][0]
        self.assertTrue(selected["verified"])
        self.assertEqual(selected["verified_by"], "Counsel Reviewer")
        self.assertEqual(selected["verified_on"], self.valid["verified_on"])
        self.assertEqual(selected["source_article"], self.valid["source_article"])
        self.assertEqual(selected["verified_by_role"], "egyptian_lawyer")
        self.assertEqual(selected["review_evidence_url"], self.valid["review_evidence_url"])
        self.assertEqual(saved["rules"][1], self.original["rules"][1])

    def test_rejects_unknown_or_ambiguous_rule_id_without_writing(self):
        for rule_id in ("missing", "civil_appeal "):
            with self.subTest(rule_id=rule_id):
                before = self.path.read_bytes()
                with self.assertRaises(ValueError):
                    verify_deadline_rule_file(self.path, **dict(self.valid, rule_id=rule_id))
                self.assertEqual(self.path.read_bytes(), before)

    def test_rejects_missing_human_attestation_fields_without_writing(self):
        invalid = (
            {"lawyer_name": "  "},
            {"source_article": " "},
            {"verified_on": "tomorrow"},
            {"verified_on": (date.today() + timedelta(days=1)).isoformat()},
            {"lawyer_role": "operator"},
            {"review_evidence_url": "http://gazette.example.test/article"},
        )
        for change in invalid:
            with self.subTest(change=change):
                before = self.path.read_bytes()
                with self.assertRaises(ValueError):
                    verify_deadline_rule_file(self.path, **dict(self.valid, **change))
                self.assertEqual(self.path.read_bytes(), before)

    def test_rejects_malformed_catalog_without_writing(self):
        self.path.write_text('{"rules": []}', encoding="utf-8")
        before = self.path.read_bytes()
        with self.assertRaises(ValueError):
            verify_deadline_rule_file(self.path, **self.valid)
        self.assertEqual(self.path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
