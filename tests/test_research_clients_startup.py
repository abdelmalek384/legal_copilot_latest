"""Regression contracts for resilient Legal Research and Clients page startup."""
from pathlib import Path
import unittest

HTML = (Path(__file__).resolve().parents[1] / "static" / "index.html").read_text(encoding="utf-8")


class ResearchAndClientsStartupTests(unittest.TestCase):
    def test_research_page_mounts_before_history_load_and_reports_failure(self):
        law = HTML[HTML.index("async function law()"):HTML.index("function documentIntelligencePanel")]
        mount = law.index("shell(LANG==='ar'?'البحث القانوني':'Legal Research'")
        guarded = law.index("try{\n  await drawList();")
        self.assertLess(mount, guarded)
        self.assertIn("Could not load conversation history", law)
        self.assertIn("Retry", law)

    def test_clients_page_mounts_even_when_client_api_fails(self):
        clients = HTML[HTML.index("async function clients()"):HTML.index("\nasync function casesPage()")]
        self.assertIn("let profiles=[],profilesError=null", clients)
        self.assertIn("Could not load client profiles", clients)
        self.assertIn("shell(uiText('العملاء','Clients')", clients)

    def test_conflict_search_uses_backend_matches_contract(self):
        clients = HTML[HTML.index("async function clients()"):HTML.index("\nasync function casesPage()")]
        self.assertIn("api('/conflicts','POST',{q:cq.value.trim()})", clients)
        self.assertIn("r.matches.length", clients)


if __name__ == "__main__":
    unittest.main()
