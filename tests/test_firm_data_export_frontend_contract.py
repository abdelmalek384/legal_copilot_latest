"""Frontend contract for the admin-only firm data export action."""
from pathlib import Path
import unittest

HTML = (Path(__file__).resolve().parents[1] / "static" / "index.html").read_text(encoding="utf-8")


class FirmDataExportFrontendContractTests(unittest.TestCase):
    def test_export_action_is_admin_only_and_uses_active_firm_route(self):
        self.assertIn("if(isAdmin)items.push(h('div',{className:'card'},h('h3',{textContent:LANG==='ar'?'تصدير بيانات المكتب':'Export firm data'})", HTML)
        self.assertIn("window.location.href='/firm/data-export.zip'", HTML)
        self.assertIn("Download firm data ZIP", HTML)
        self.assertIn("تنزيل بيانات المكتب ZIP", HTML)

    def test_export_explains_scope_and_audit(self):
        self.assertIn("includes only the active firm", HTML)
        self.assertIn("export is audited", HTML)
        self.assertIn("يشمل المكتب النشط فقط", HTML)
        self.assertIn("سجل أمان المكتب", HTML)


if __name__ == "__main__":
    unittest.main()
