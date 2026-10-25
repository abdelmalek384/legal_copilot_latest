"""Regression checks for the Arabic-first single-page frontend's accessibility contract."""
from pathlib import Path
import unittest

HTML = Path("static/index.html").read_text(encoding="utf-8")

class FrontendUXContractTests(unittest.TestCase):
    def test_skip_link_and_main_landmark_are_present(self):
        self.assertIn("className:'skip-link'", HTML)
        self.assertIn("id:'main',tabIndex:-1", HTML)
        self.assertIn("aria-label':navLabel('التنقل الرئيسي','Primary navigation')", HTML)

    def test_navigation_is_keyboard_operable_and_announces_current_page(self):
        self.assertIn("role:'button',tabIndex:0,'aria-current':PAGE===id?'page':null", HTML)
        self.assertIn("e.key==='Enter'||e.key===' '", HTML)

    def test_language_switch_rerenders_every_primary_workspace(self):
        switch = HTML[HTML.index("function switchLanguage()"):HTML.index("\nconst languageObserver")]
        for page in ("dash", "clients", "cases", "tasks", "calendar", "law", "review", "settings"):
            self.assertIn("PAGE==='" + page + "'", switch)
        self.assertIn("if(!ME.id){login(AUTH_MODE)", switch)

    def test_modal_escape_and_reduced_motion_support(self):
        self.assertIn("document.addEventListener('keydown'", HTML)
        self.assertIn("e.key==='Escape'", HTML)
        self.assertIn("@media(prefers-reduced-motion:reduce)", HTML)

    def test_research_scope_is_explicit_and_metadata_discovery_is_separate(self):
        self.assertIn("value:'verified_corpus'", HTML)
        self.assertIn("value:'firm_documents'", HTML)
        self.assertIn("value:'metadata_only'", HTML)
        self.assertIn("'/research/discover'", HTML)
        self.assertIn("Select a matter to search firm documents", HTML)

    def test_copy_fallback_checks_result_and_always_removes_temporary_textarea(self):
        self.assertIn("copied=document.execCommand('copy')===true", HTML)
        self.assertIn("finally{t.remove()}", HTML)
        self.assertIn("if(!copied)throw new Error('copy failed')", HTML)

    def test_source_inspector_exposes_status_pin_cites_copy_and_memo_actions(self):
        self.assertIn("source_status", HTML)
        self.assertIn("s.article", HTML)
        self.assertIn("Copy citation", HTML)
        self.assertIn("Copy exact passage", HTML)
        self.assertIn("highlightTerms", HTML)
        self.assertIn("document.createTextNode", HTML)
        self.assertIn("Export research memo", HTML)
        self.assertIn("setTimeout(()=>URL.revokeObjectURL(url),1000)", HTML)
        self.assertIn("save-to-matter", HTML)
        self.assertIn("No relevant verified legal text found in this scope", HTML)
        self.assertNotIn("matterSelect.disabled", HTML)

    def test_focus_and_small_screen_rules_exist(self):
        self.assertIn(":focus-visible", HTML)
        self.assertIn("@media(max-width:420px)", HTML)
        self.assertIn("@media(forced-colors:active)", HTML)

if __name__ == "__main__":
    unittest.main()
