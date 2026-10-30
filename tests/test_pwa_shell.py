"""Static contract tests for the installable PWA shell and privacy boundaries."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "app.py").read_text(encoding="utf-8")
SERVICE_WORKER = (ROOT / "static" / "service-worker.js").read_text(encoding="utf-8")
OFFLINE = (ROOT / "static" / "offline.html").read_text(encoding="utf-8")


class PwaShellTests(unittest.TestCase):
    def test_manifest_is_arabic_first_and_installable(self):
        manifest = json.loads((ROOT / "static" / "manifest.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual(manifest["lang"], "ar")
        self.assertEqual(manifest["dir"], "rtl")
        self.assertEqual(manifest["start_url"], "/")
        self.assertEqual(manifest["scope"], "/")
        self.assertEqual(manifest["display"], "standalone")
        self.assertEqual(manifest["icons"][0]["src"], "/app-icon.svg")
        self.assertTrue(any(icon.get("src") == "/apple-touch-icon.png" and icon.get("sizes") == "180x180" for icon in manifest["icons"]))

    def test_home_injects_manifest_and_nonce_protected_registration(self):
        self.assertIn('href="/manifest.webmanifest"', APP)
        self.assertIn('name="apple-mobile-web-app-capable" content="yes"', APP)
        self.assertIn('name="apple-mobile-web-app-title" content="المساعد القانوني"', APP)
        self.assertIn('navigator.serviceWorker.register("/service-worker.js")', APP)
        self.assertIn('page = page.replace("</html>", registration + "</html>", 1)', APP)
        self.assertIn("</html>", (ROOT / "static" / "index.html").read_text(encoding="utf-8"))
        self.assertIn('<script nonce="' + "' + request.state.csp_nonce + '" + '">', APP)
        self.assertIn("worker-src 'self'", APP)

    def test_public_routes_serve_only_fixed_assets(self):
        for route, asset in (
            ('@app.get("/manifest.webmanifest")', 'manifest.webmanifest'),
            ('@app.get("/service-worker.js")', 'service-worker.js'),
            ('@app.get("/offline.html")', 'offline.html'),
            ('@app.get("/app-icon.svg")', 'app-icon.svg'),
            ('@app.get("/apple-touch-icon.png")', 'apple-touch-icon.png.b64'),
        ):
            self.assertIn(route, APP)
            self.assertIn(f'_read_pwa_asset("{asset}")', APP)

    def test_service_worker_caches_only_the_static_offline_notice(self):
        self.assertIn('cache.add(OFFLINE_URL)', SERVICE_WORKER)
        self.assertNotIn("caches.put(", SERVICE_WORKER)
        self.assertNotIn("cache.addAll(", SERVICE_WORKER)
        self.assertNotIn("caches.match(OFFLINE_URL)", SERVICE_WORKER)
        self.assertIn("cache.match(OFFLINE_URL)", SERVICE_WORKER)
        self.assertIn('request.mode === "navigate" && url.pathname === "/"', SERVICE_WORKER)
        self.assertIn('if (request.method !== "GET") return;', SERVICE_WORKER)
        self.assertIn("request.mode === \"navigate\"", SERVICE_WORKER)
        self.assertNotIn("Authorization", SERVICE_WORKER)
        self.assertNotIn("localStorage", SERVICE_WORKER)

    def test_offline_notice_explicitly_says_matter_data_is_not_cached(self):
        self.assertIn("لا تُخزَّن ملفات القضايا", OFFLINE)
        self.assertIn("case files, research results, and account data are not stored", OFFLINE)


if __name__ == "__main__":
    unittest.main()
