import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
_TEST_DB_DIR = tempfile.TemporaryDirectory(prefix="secure-cookie-mode-")
os.environ["COPILOT_DB"] = str(Path(_TEST_DB_DIR.name) / "test.db")
spec = importlib.util.spec_from_file_location("legal_copilot_app_secure_cookie_test", ROOT / "app.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class SecureCookieTransportTests(unittest.TestCase):
    def test_declared_body_size_limit_allows_upload_limit_and_rejects_oversize(self):
        request = lambda value: SimpleNamespace(headers={} if value is None else {"content-length": value})
        self.assertIsNone(app._declared_body_size_error(request(None)))
        self.assertIsNone(app._declared_body_size_error(request(str(app.MAX_REQUEST_BODY_BYTES))))
        self.assertEqual(app._declared_body_size_error(request(str(app.MAX_REQUEST_BODY_BYTES + 1))), (413, "request body exceeds 16 MB limit"))

    def test_declared_body_size_rejects_malformed_or_negative_lengths(self):
        request = lambda value: SimpleNamespace(headers={"content-length": value})
        for value in ("not-a-number", "-1"):
            with self.subTest(value=value):
                self.assertEqual(app._declared_body_size_error(request(value)), (400, "invalid content-length"))

    def test_llm_redirect_handler_refuses_redirect_targets(self):
        handler = app._RejectLLMRedirects()
        for code, target in ((301, "http://remote.example/"), (302, "https://other.example/"), (307, "http://127.0.0.1:11434/")):
            with self.subTest(code=code, target=target):
                self.assertIsNone(handler.redirect_request(None, None, code, "redirect", {}, target))

    def test_llm_endpoint_requires_https_remotely_and_allows_loopback_http(self):
        for url in ("https://llm.example.com/v1/chat/completions", "http://127.0.0.1:11434/v1/chat/completions", "http://[::1]:11434/v1/chat/completions", "http://localhost:11434/v1/chat/completions"):
            with self.subTest(url=url):
                self.assertTrue(app._safe_llm_endpoint(url))
        for url in ("http://llm.example.com/v1/chat/completions", "http://192.168.1.20:11434/v1", "https://user:pass@llm.example.com/v1", "https://llm.example.com/v1?api_key=secret", "https://llm.example.com/v1#fragment", "https://llm.example.com:99999/v1", "file:///tmp/model"):
            with self.subTest(url=url):
                self.assertFalse(app._safe_llm_endpoint(url))

    def test_unsafe_llm_endpoint_never_calls_network_even_with_processing_approval(self):
        with patch.dict(os.environ, {"LLM_URL": "http://remote.example/v1", "LLM_DATA_PROCESSING_APPROVED": "1"}):
            with patch.object(app.urllib.request, "urlopen") as open_url:
                self.assertIsNone(app.llm("CONFIDENTIAL-SENTINEL"))
                open_url.assert_not_called()

    def test_direct_https_always_marks_cookie_transport_secure(self):
        request = SimpleNamespace(url=SimpleNamespace(scheme="https", netloc="legal.example.com"))
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("COPILOT_SECURE_COOKIES", None)
            self.assertTrue(app._secure_cookie_transport(request))

    def test_explicit_proxy_mode_marks_http_backend_request_secure(self):
        request = SimpleNamespace(url=SimpleNamespace(scheme="http", netloc="internal:8000"))
        with patch.dict(os.environ, {"COPILOT_SECURE_COOKIES": "1"}):
            self.assertTrue(app._secure_cookie_transport(request))

    def test_proxy_mode_is_not_enabled_by_truthy_guess_or_missing_value(self):
        request = SimpleNamespace(url=SimpleNamespace(scheme="http", netloc="internal:8000"))
        for value in ("", "true", "yes", "0"):
            with self.subTest(value=value), patch.dict(os.environ, {"COPILOT_SECURE_COOKIES": value}):
                self.assertFalse(app._secure_cookie_transport(request))

    def test_public_origin_allows_only_configured_https_origin(self):
        request = SimpleNamespace(url=SimpleNamespace(scheme="http", netloc="internal:8000"))
        with patch.dict(os.environ, {"COPILOT_PUBLIC_ORIGIN": "https://legal.example.com"}):
            self.assertTrue(app._origin_matches_request("https://legal.example.com", request))
            self.assertFalse(app._origin_matches_request("https://attacker.example", request))
            self.assertFalse(app._origin_matches_request("http://legal.example.com", request))
            self.assertFalse(app._origin_matches_request("https://legal.example.com/evil", request))

    def test_invalid_configured_public_origin_fails_closed(self):
        request = SimpleNamespace(url=SimpleNamespace(scheme="https", netloc="legal.example.com"))
        with patch.dict(os.environ, {"COPILOT_PUBLIC_ORIGIN": "https://user:pass@legal.example.com"}):
            self.assertFalse(app._origin_matches_request("https://legal.example.com", request))


if __name__ == "__main__":
    unittest.main()
