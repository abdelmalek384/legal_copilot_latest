"""Contract checks for the current bilingual first-run firm setup UI."""
import unittest
from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / "static" / "index.html").read_text(encoding="utf-8")


class FirstRunWizardFrontendContractTests(unittest.TestCase):
    def test_dashboard_links_admins_to_the_setup_checklist(self):
        self.assertIn("ME.role==='admin'&&Array.isArray(ME.firms)?api('/setup/first-run')", HTML)
        self.assertIn("setup.completed<setup.total", HTML)
        self.assertIn("firstRunPage", HTML)
        self.assertIn("Continue setup", HTML)
        self.assertIn("متابعة الإعداد", HTML)

    def test_firm_profile_and_each_checklist_action_are_connected(self):
        self.assertIn("async function firstRunPage()", HTML)
        self.assertIn("api('/firm/profile','PUT'", HTML)
        self.assertIn("invite_colleague:()=>settingsPage()", HTML)
        self.assertIn("mfa:()=>settingsPage()", HTML)
        self.assertIn("first_case:()=>newCase()", HTML)
        self.assertIn("first_deadline:()=>data.first_case_id?view(data.first_case_id):newCase()", HTML)
        self.assertIn("test_reminder:data.health", HTML)
        self.assertIn("sendSetupTestReminder()", HTML)
        self.assertIn("setupHealthPage()", HTML)

    def test_progress_privacy_and_deadline_warning_are_visible(self):
        self.assertIn("role:'progressbar'", HTML)
        self.assertIn("'aria-valuenow':percent", HTML)
        self.assertIn("Do not rely on any legal deadline", HTML)
        self.assertIn("لا تعتمد على أي موعد قانوني", HTML)
        self.assertIn("no secret values", HTML)
        self.assertIn("دون عرض الأسرار", HTML)


if __name__ == "__main__":
    unittest.main()
