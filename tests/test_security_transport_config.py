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
