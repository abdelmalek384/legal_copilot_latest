"""Regression contracts for the workspace navigation and visual fixes."""
from pathlib import Path
import unittest

HTML = (Path(__file__).resolve().parents[1] / "static" / "index.html").read_text(encoding="utf-8")


class WorkspaceUIFixTests(unittest.TestCase):
    def test_navigation_awaits_page_and_renders_visible_failure(self):
        self.assertIn("onclick:async e=>{", HTML)
        self.assertIn("PAGE=id;window.CASE_ID=null;window.DOCUMENT_REVIEW_TARGET=null;const main=$('main');try{await f()}catch(error)", HTML)
        self.assertIn("if(more&&window.innerWidth<=800){window.__lcMoreOpen=false;more.open=false}", HTML)
        self.assertIn("className:'card page-load-error',role:'alert'", HTML)
        self.assertIn("Try again", HTML)

    def test_brand_logo_has_a_visible_fallback(self):
        self.assertIn("src:'/static/app-icon.svg'", HTML)
        self.assertIn("className:'brand-mark brand-mark-fallback'", HTML)
        self.assertIn("#side .brand-mark-fallback", HTML)

    def test_sidebar_uses_high_contrast_navigation_states(self):
        self.assertIn("background:linear-gradient(180deg,#102746", HTML)
        self.assertIn("#side .primary-nav button.on{background:#e8f0ff", HTML)
        self.assertIn("#side .primary-nav button:focus-visible", HTML)

    def test_calendar_and_document_library_have_responsive_workspace_styles(self):
        self.assertIn("#main .calendar-month-grid{min-width:620px}", HTML)
        self.assertIn("#main .calendar-day.selected", HTML)
        self.assertIn("#main .document-library-list .workspace-list-item", HTML)


if __name__ == "__main__":
    unittest.main()
