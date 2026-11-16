"""Regression contracts for the app icon route and research API diagnostics."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "app.py").read_text(encoding="utf-8")
HTML = (ROOT / "static" / "index.html").read_text(encoding="utf-8")


class ResearchAssetDiagnosticsTests(unittest.TestCase):
    def test_app_icon_is_served_at_workspace_and_pwa_paths(self):
        self.assertIn('@app.get("/static/app-icon.svg")', APP)
        self.assertIn('@app.get("/app-icon.svg")', APP)
        self.assertIn('media_type="image/svg+xml"', APP)
        self.assertTrue((ROOT / "static" / "app-icon.svg").is_file())

    def test_research_api_errors_include_status_method_and_path(self):
        self.assertIn("p.startsWith('/research/')?' ['+r.status+' '+m+' '+p.split('?')[0]+']':''", HTML)
        self.assertIn("const detail=(message||('HTTP '+r.status))+diagnostic", HTML)

    def test_research_conversation_list_route_exists(self):
        self.assertIn('@app.get("/research/conversations")', APP)


if __name__ == "__main__":
    unittest.main()
