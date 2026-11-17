"""Static regression contracts for the final workspace layout overrides."""
from pathlib import Path
import unittest

HTML = (Path(__file__).resolve().parents[1] / "static" / "index.html").read_text(encoding="utf-8")


class WorkspaceLayoutRegressionTests(unittest.TestCase):
    def test_main_content_uses_available_desktop_width(self):
        self.assertIn("#main{flex:1 1 auto!important;width:calc(100% - 248px)!important", HTML)
        self.assertIn("max-width:none!important", HTML)

    def test_brand_asset_has_explicit_visible_dimensions_and_background(self):
        self.assertIn("#side .brand-mark{display:block!important;width:42px!important", HTML)
        self.assertIn("background:#14284b!important", HTML)

    def test_research_workspace_has_three_column_desktop_layout(self):
        self.assertIn("#main .research-layout{display:grid!important;grid-template-columns:minmax(220px,270px)", HTML)
        self.assertIn("#main .research-composer textarea{width:100%", HTML)

    def test_research_layout_collapses_for_tablets_and_phones(self):
        self.assertIn("@media(max-width:1180px)", HTML)
        self.assertIn("@media(max-width:760px)", HTML)
        self.assertIn("#main .research-layout{grid-template-columns:minmax(0,1fr)!important}", HTML)


    def test_research_reference_layout_keeps_history_answer_and_evidence_visible(self):
        self.assertIn('grid-template-areas:"inspector main history"!important', HTML)
        self.assertIn('#main .research-layout>.research-list{', HTML)
        self.assertIn('display:block!important;visibility:visible!important', HTML)
        self.assertIn('#main .research-layout>.research-main>.research-thread', HTML)
        self.assertIn('#main .research-layout>.research-evidence-panel', HTML)
        self.assertIn('grid-template-areas:"main main" "inspector history"!important', HTML)
        self.assertIn('grid-template-areas:"main" "history" "inspector"!important', HTML)


    def test_legal_research_hides_global_search_and_uses_remaining_shell_width(self):
        self.assertIn('#main:has(.research-layout)>.workspace-topbar{display:none!important}', HTML)
        self.assertIn('#main:has(.research-layout){width:auto!important;flex:1 1 0%!important', HTML)
        self.assertIn('@media(max-width:1180px) and (min-width:801px){#main:has(.research-layout){width:auto!important;flex:1 1 0%!important}', HTML)
        self.assertIn('@media(max-width:800px){#main:has(.research-layout){width:100%!important;flex:1 1 auto!important}', HTML)


if __name__ == "__main__":
    unittest.main()
