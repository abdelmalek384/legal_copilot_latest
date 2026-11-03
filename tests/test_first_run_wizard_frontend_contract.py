"""Contract checks for the interactive first-run firm setup UI."""
import unittest
from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / "static" / "index.html").read_text(encoding="utf-8")


class FirstRunWizardFrontendContractTests(unittest.TestCase):
    def test_dashboard_offers_setup_to_firm_admins_until_checklist_is_complete(self):
        self.assertIn("ME.role==='admin'?await api('/setup/first-run')", HTML)
        self.assertIn("setup.completed<setup.total", HTML)
        self.assertIn("Continue setup checklist", HTML)
        self.assertIn("متابعة قائمة الإعداد", HTML)

    def test_all_six_checklist_actions_are_connected(self):
        self.assertIn("api('/setup/first-run')", HTML)
        self.assertIn("api('/firm/profile')", HTML)
        self.assertIn("api('/firm/profile','PUT'", HTML)
        self.assertIn("settingsPage", HTML)
        self.assertIn("newCase", HTML)
        self.assertIn("TAB='dead';view(data.first_case_id)", HTML)
        self.assertIn("api('/setup/test-reminder','POST')", HTML)

    def test_health_explanations_and_test_email_confirmation_are_visible(self):
        self.assertIn("data.health.checks", HTML)
        self.assertIn("check.message_ar", HTML)
        self.assertIn("check.message_en", HTML)
        self.assertIn("data.health.ready_for_test_reminder", HTML)
        self.assertIn("قبول SMTP لا يؤكد وصول الرسالة إلى صندوق الوارد", HTML)
        self.assertIn("SMTP acceptance does not confirm inbox delivery", HTML)


if __name__ == "__main__":
    unittest.main()
