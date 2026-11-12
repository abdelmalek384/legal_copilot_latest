"""Contract checks for the split Legal Research workspace."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "static" / "index.html").read_text(encoding="utf-8")


class ResearchWorkspaceInspectorContractTests(unittest.TestCase):
    def test_research_workspace_has_history_thread_and_source_inspector(self):
        self.assertIn("const sourcePanel=h('aside',{className:'research-inspector card'", HTML)
        self.assertIn("h('div',{className:'research-layout'},sidebar,h('section',{className:'research-main'},researchStatus,thread,composerArea),sourcePanel)", HTML)

    def test_source_inspector_preserves_exact_passages_and_provenance_cards(self):
        self.assertIn("sourcePanelContent.append(src)", HTML)
        self.assertIn("research-exact-passage", HTML)
        self.assertIn("research-source-actions", HTML)
        self.assertNotIn("bubble.append(src);", HTML)

    def test_metadata_discovery_remains_explicitly_metadata_only(self):
        self.assertIn("Metadata-only results — this view contains no legal text.", HTML)
        self.assertIn("sourcePanelContent.append(card.cloneNode(true))", HTML)
        self.assertIn("No legal text was retrieved. This result does not establish current status or reuse permission.", HTML)

    def test_research_layout_has_desktop_tablet_and_phone_breakpoints(self):
        self.assertIn(".research-layout{grid-template-columns:minmax(205px,238px) minmax(360px,1fr) minmax(285px,330px)", HTML)
        self.assertIn("@media(max-width:1180px)", HTML)
        self.assertIn("@media(max-width:800px)", HTML)
        self.assertIn("@media(max-width:420px)", HTML)

    def test_source_inspector_is_accessibly_named(self):
        self.assertIn("'aria-label':LANG==='ar'?'فحص المصادر':'Source inspector'", HTML)
        self.assertIn("className:'research-inspector-heading'", HTML)


if __name__ == "__main__":
    unittest.main()
