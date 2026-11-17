"""Static regression contracts for the final workspace layout overrides."""
from pathlib import Path
import unittest

HTML = (Path(__file__).resolve().parents[1] / "static" / "index.html").read_text(encoding="utf-8")


class WorkspaceLayoutRegressionTests(unittest.TestCase):
    def test_main_content_uses_available_desktop_width(self):
        self.assertIn('#main:has(.research-layout){width:auto!important;flex:1 1 0%!important;min-width:0!important;max-width:none!important', HTML)

    def test_brand_asset_has_explicit_visible_dimensions_and_background(self):
        self.assertIn("#side .brand-mark{display:block!important;width:42px!important", HTML)
        self.assertIn("background:#14284b!important", HTML)

    def test_research_workspace_has_three_column_desktop_layout(self):
        self.assertIn('grid-template-columns:minmax(225px,245px) minmax(0,1fr) minmax(160px,180px)!important;', HTML)
        self.assertIn('#main .research-layout>.research-main>.research-composer', HTML)
        self.assertIn('#main .research-composer textarea{grid-column:1/-1!important;width:100%', HTML)

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
        self.assertIn('@media(max-width:800px){\n #main .research-layout{\n  grid-template-columns:minmax(0,1fr)!important;\n  grid-template-areas:"main" "history" "inspector"!important;', HTML)


    def test_legal_research_hides_global_search_and_uses_remaining_shell_width(self):
        self.assertIn('#main:has(.research-layout)>.workspace-topbar{display:none!important}', HTML)
        self.assertIn('#main:has(.research-layout){width:auto!important;flex:1 1 0%!important', HTML)
        self.assertIn('@media(max-width:1180px) and (min-width:801px){#main:has(.research-layout){width:auto!important;flex:1 1 0%!important}', HTML)
        self.assertIn('@media(max-width:800px){#main:has(.research-layout){width:100%!important;flex:1 1 auto!important}', HTML)

    def test_research_panes_keep_semantic_sides_in_ltr_and_rtl(self):
        self.assertIn('#main .research-layout:dir(ltr){grid-template-areas:"history main inspector"!important}', HTML)
        self.assertIn('@media(max-width:1180px){\n #main .research-layout:dir(ltr){grid-template-areas:"main main" "history inspector"!important}', HTML)

    def test_mobile_shell_media_query_is_a_real_css_rule(self):
        self.assertIn('}\n@media(max-width:800px){#main:has(.research-layout){width:100%!important;flex:1 1 auto!important}}', HTML)
        self.assertNotIn('}\\\\n@media(max-width:800px){#main:has(.research-layout)', HTML)

    def test_research_shell_navigation_rail_matches_reference_width(self):
        self.assertIn('#side{width:206px!important;min-width:206px!important;flex:0 0 206px!important', HTML)
        self.assertIn('@media(max-width:800px){#side{width:100%!important;min-width:0!important;flex:0 0 auto!important}}', HTML)

    def test_demo_safety_notice_remains_visible_but_compact_in_research(self):
        self.assertIn('#main:has(.research-layout)>.demo-banner{', HTML)
        self.assertIn('border-inline-start:3px solid #c48a35!important;', HTML)
        self.assertIn('font-size:10px!important;', HTML)
        self.assertNotIn('#main:has(.research-layout)>.demo-banner{display:none', HTML)

    def test_ltr_research_reverses_rail_track_widths_with_semantic_panes(self):
        self.assertIn('#main .research-layout:dir(ltr){grid-template-columns:minmax(160px,180px) minmax(0,1fr) minmax(225px,245px)!important}', HTML)

    def test_research_page_actions_have_separation_and_do_not_compress_labels(self):
        self.assertIn('#main:has(.research-layout)>.research-page-actions{', HTML)
        self.assertIn('flex-wrap:wrap!important;gap:8px!important', HTML)
        self.assertIn('min-width:max-content!important;min-height:36px!important', HTML)

    def test_duplicate_generic_empty_conversation_titles_are_not_repeated(self):
        self.assertIn('const seenPlaceholderTitles=new Set();', HTML)
        self.assertIn("['محادثة جديدة','محادثة جديدة (جديدة)','new conversation','new chat']", HTML)
        self.assertIn('if(seenPlaceholderTitles.has(normalized))return false;', HTML)

    def test_evidence_panel_explains_zero_source_state_and_hides_it_when_populated(self):
        self.assertIn('className:\'research-evidence-empty-state\'', HTML)
        self.assertIn('Sources will appear here when research returns supporting material.', HTML)
        self.assertIn('evidenceEmptyState.hidden=total>0;', HTML)
        self.assertIn('evidenceCoverage,evidenceFilters,evidenceFilterEmpty,evidenceEmptyState,evidenceCards,sourceInspector', HTML)

    def test_evidence_filters_and_scope_tabs_have_clear_spacing(self):
        self.assertIn('#main .research-evidence-filters{display:flex!important;flex-wrap:wrap!important;gap:6px!important}', HTML)
        self.assertIn('#main .research-composer-controls .research-scope-tabs{gap:6px!important;padding:5px!important}', HTML)

    def test_ltr_tablet_and_mobile_grids_override_desktop_track_widths(self):
        self.assertIn('@media(max-width:1180px){\n #main .research-layout:dir(ltr){grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;grid-template-areas:"main main" "history inspector"!important}', HTML)
        self.assertIn('@media(max-width:800px){\n #main .research-layout:dir(ltr){grid-template-columns:minmax(0,1fr)!important;grid-template-areas:"main" "history" "inspector"!important}', HTML)

    def test_side_rails_have_more_balanced_widths_and_consistent_spacing(self):
        self.assertIn('grid-template-columns:minmax(240px,260px) minmax(0,1fr) minmax(180px,200px)!important;', HTML)
        self.assertIn('grid-template-columns:minmax(180px,200px) minmax(0,1fr) minmax(240px,260px)!important;', HTML)
        self.assertIn('gap:14px!important;', HTML)
        self.assertIn('#main .research-layout>.research-list{\n display:flex!important;flex-direction:column!important;gap:12px!important;', HTML)
        self.assertIn('#main .research-layout>.research-evidence-panel{\n padding:15px!important;gap:11px!important;', HTML)

    def test_side_rail_widths_and_spacing_collapse_cleanly_on_smaller_screens(self):
        self.assertIn('@media(max-width:1180px){\n #main .research-layout{grid-template-columns:minmax(0,1fr) minmax(0,1fr)!important;gap:12px!important}', HTML)
        self.assertIn('@media(max-width:800px){\n #main .research-layout{grid-template-columns:minmax(0,1fr)!important;gap:10px!important}', HTML)

    def test_answer_tabs_share_the_available_width_evenly(self):
        self.assertIn('grid-template-columns:repeat(3,minmax(0,1fr))!important;', HTML)
        self.assertIn('width:100%!important;min-width:0!important;min-height:42px!important;', HTML)
        self.assertIn('justify-content:center!important;', HTML)
        self.assertIn('white-space:normal!important;', HTML)
        self.assertIn('#main .research-thread .research-answer-tabs [role=tab].active::after{display:none!important}', HTML)

    def test_answer_tabs_remain_balanced_on_small_screens(self):
        self.assertIn('@media(max-width:480px){\n #main .research-thread .research-answer-tabs{gap:4px!important;padding:3px!important}', HTML)
        self.assertIn('min-height:40px!important;padding:7px 4px!important;font-size:11px!important', HTML)


if __name__ == "__main__":
    unittest.main()
