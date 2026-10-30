"""HTTP-level smoke tests for the public installable PWA shell."""
import os
import tempfile
from pathlib import Path
import unittest

from fastapi.testclient import TestClient

_TMP = tempfile.TemporaryDirectory(prefix="legal-copilot-pwa-")
_ROOT = Path(_TMP.name)
os.environ["COPILOT_ENV"] = "development"
os.environ.pop("COPILOT_DB", None)
os.environ["COPILOT_CONTROL_DB"] = str(_ROOT / "control.sqlite3")
os.environ["COPILOT_TENANT_DB_ROOT"] = str(_ROOT / "tenants")
os.environ["COPILOT_CORPUS_DB"] = str(_ROOT / "corpus.sqlite3")

import app  # noqa: E402


class PwaHttpRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_context = TestClient(app.app)
        cls.client = cls.client_context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client_context.__exit__(None, None, None)
        _TMP.cleanup()

    def test_manifest_route_has_install_metadata_and_no_store(self):
        response = self.client.get("/manifest.webmanifest")
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/manifest+json", response.headers.get("content-type", ""))
        self.assertIn('"lang": "ar"', response.text)
        self.assertEqual(response.headers.get("cache-control"), "no-store")

    def test_service_worker_route_has_root_scope_and_no_store(self):
        response = self.client.get("/service-worker.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn("javascript", response.headers.get("content-type", ""))
        self.assertEqual(response.headers.get("service-worker-allowed"), "/")
        self.assertEqual(response.headers.get("cache-control"), "no-store")

    def test_offline_and_icon_routes_return_only_static_assets(self):
        offline = self.client.get("/offline.html")
        icon = self.client.get("/app-icon.svg")
        self.assertEqual(offline.status_code, 200)
        self.assertIn("not stored for offline use", offline.text.lower())
        self.assertEqual(icon.status_code, 200)
        self.assertIn("image/svg+xml", icon.headers.get("content-type", ""))
        self.assertIn("<svg", icon.text)

    def test_home_injects_manifest_registration_and_worker_csp(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn('rel="manifest" href="/manifest.webmanifest"', response.text)
        self.assertIn('navigator.serviceWorker.register("/service-worker.js")', response.text)
        self.assertIn("worker-src 'self'", response.headers.get("content-security-policy", ""))
        self.assertEqual(response.headers.get("cache-control"), "no-store")


if __name__ == "__main__":
    unittest.main()
