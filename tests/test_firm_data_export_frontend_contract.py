"""Frontend contract checks for the firm-admin data export action."""
import unittest
from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / "static" / "index.html").read_text(encoding="utf-8")


class FirmDataExportFrontendContractTests(unittest.TestCase):
    def test_export_action_is_admin_only_and_targets_the_active_firm(self):
        self.assertIn("if(ME.role==='admin')items.push", HTML)
        self.assertIn("/firm/data-export.zip?firm_id='+encodeURIComponent(ME.firm_id)", HTML)
        self.assertIn("Download firm data", HTML)
        self.assertIn("تنزيل بيانات المكتب", HTML)

    def test_export_explains_scope_and_audit(self):
        self.assertIn("limited to the current firm", HTML)
        self.assertIn("security audit log", HTML)
        self.assertIn("خاص بالمكتب الحالي", HTML)
        self.assertIn("سجل الأمان", HTML)


if __name__ == "__main__":
    unittest.main()
