"""Unit tests for the read-only live deployment HTTP smoke probe."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import httpx

from tools.deployment_http_smoke import main, normalize_base_url, run_smoke


def fake_transport(*, omit_worker_csp=False, bad_status=None):
    def handler(request):
        path = request.url.path
        bodies = {
            "/": '<html><link rel="manifest" href="/manifest.webmanifest"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><script>navigator.serviceWorker.register("/service-worker.js")</script></html>',
            "/manifest.webmanifest": json.dumps({
                "lang": "ar", "dir": "rtl", "display": "standalone",
                "start_url": "/", "icons": [{"src": "/app-icon.svg"}],
            }),
            "/service-worker.js": (
                'const OFFLINE_URL = "/offline.html"; cache.add(OFFLINE_URL); '
                'if (request.mode === "navigate" && url.pathname === "/") { }'
            ),
            "/offline.html": "<p>Case files and account data are not stored for offline use.</p>",
            "/app-icon.svg": "<svg></svg>",
            "/apple-touch-icon.png": bytes([137, 80, 78, 71, 13, 10, 26, 10]),
        }
        headers = {
            "Content-Type": {
                "/": "text/html; charset=utf-8",
                "/manifest.webmanifest": "application/manifest+json",
                "/service-worker.js": "application/javascript",
                "/offline.html": "text/html; charset=utf-8",
                "/app-icon.svg": "image/svg+xml",
                "/apple-touch-icon.png": "image/png",
            }[path],
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "no-referrer",
            "Content-Security-Policy": "default-src 'self'; worker-src 'self'; script-src 'self'",
            "Strict-Transport-Security": "max-age=31536000",
            "Service-Worker-Allowed": "/",
        }
        if omit_worker_csp:
            headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'"
        status = bad_status if path == "/manifest.webmanifest" and bad_status else 200
        body = bodies[path]
        content = body if isinstance(body, bytes) else body.encode("utf-8")
        return httpx.Response(status, headers=headers, content=content, request=request)
    return httpx.MockTransport(handler)


class DeploymentHttpSmokeTests(unittest.TestCase):
    def test_requires_https_unless_loopback_is_explicit(self):
        with self.assertRaises(ValueError):
            normalize_base_url("http://example.com", allow_http_loopback=True)
        with self.assertRaises(ValueError):
            normalize_base_url("http://127.0.0.1:8000")
        self.assertEqual(
            normalize_base_url("http://127.0.0.1:8000", allow_http_loopback=True),
            "http://127.0.0.1:8000",
        )

    def test_rejects_credentials_paths_queries_and_fragments(self):
        for value in (
            "https://user:pass@example.com",
            "https://example.com/path",
            "https://example.com?token=x",
            "https://example.com/#fragment",
        ):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_base_url(value)

    def test_complete_public_shell_passes(self):
        with httpx.Client(transport=fake_transport(), base_url="https://legal.example.com") as client:
            report = run_smoke("https://legal.example.com", client=client)
        self.assertTrue(report["ready"], report)
        self.assertEqual(report["failed"], 0)

    def test_missing_worker_csp_fails_closed(self):
        with httpx.Client(transport=fake_transport(omit_worker_csp=True), base_url="https://legal.example.com") as client:
            report = run_smoke("https://legal.example.com", client=client)
        self.assertFalse(report["ready"])
        self.assertGreater(report["failed"], 0)

    def test_optional_report_creates_missing_parent_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "report.json"
            with mock.patch.object(sys, "argv", ["deployment_http_smoke.py", "--base-url", "https://legal.example.com", "--out", str(output)]):
                with mock.patch("tools.deployment_http_smoke.run_smoke", return_value={"ready": True, "checks": []}):
                    self.assertEqual(main(), 0)
            self.assertTrue(output.is_file())
            self.assertTrue(json.loads(output.read_text(encoding="utf-8"))["ready"])

    def test_non_200_public_asset_fails(self):
        with httpx.Client(transport=fake_transport(bad_status=503), base_url="https://legal.example.com") as client:
            report = run_smoke("https://legal.example.com", client=client)
        self.assertFalse(report["ready"])
        self.assertTrue(any(item["name"] == "GET /manifest.webmanifest" and not item["passed"] for item in report["checks"]))


if __name__ == "__main__":
    unittest.main()
