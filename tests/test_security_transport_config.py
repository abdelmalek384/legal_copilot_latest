import importlib.util
import asyncio
import os
import io
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("legal_copilot_app_secure_cookie_test", ROOT / "app.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class SecureCookieTransportTests(unittest.TestCase):
    def test_trusted_host_allowlist_rejects_wildcard_all_and_url_syntax(self):
        self.assertEqual(app._trusted_host_patterns("legal.example.com,*.example.org,127.0.0.1"),
                         ["legal.example.com", "*.example.org", "127.0.0.1"])
        for value in ("*", "https://legal.example.com", "legal.example.com/path", "*.127.0.0.1", "legal..example.com"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    app._trusted_host_patterns(value)

    def test_trusted_host_middleware_accepts_allowlisted_host_and_rejects_others(self):
        async def run(host):
            sent = []
            async def fake_app(scope, receive, send):
                await send({"type": "http.response.start", "status": 204, "headers": []})
                await send({"type": "http.response.body", "body": b""})
            async def receive():
                return {"type": "http.disconnect"}
            async def send(message):
                sent.append(message)
            middleware = app.TrustedHostMiddleware(fake_app, allowed_hosts=app._trusted_host_patterns("legal.example.com"))
            await middleware({"type": "http", "headers": [(b"host", host.encode("ascii"))], "method": "GET", "path": "/"}, receive, send)
            return sent[0]["status"]
        self.assertEqual(asyncio.run(run("legal.example.com")), 204)
        self.assertEqual(asyncio.run(run("attacker.example")), 400)

    def test_streamed_body_without_content_length_is_limited(self):
        async def run_case(chunks):
            sent = []
            events = list(chunks)

            async def fake_app(scope, receive, send):
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        break
                    if not message.get("more_body", False):
                        break
                await send({"type": "http.response.start", "status": 200, "headers": []})
                await send({"type": "http.response.body", "body": b"ok"})

            async def receive():
                return events.pop(0) if events else {"type": "http.disconnect"}

            async def send(message):
                sent.append(message)

            middleware = app.RequestBodyLimitMiddleware(fake_app, max_body_bytes=5)
            await middleware({"type": "http", "headers": []}, receive, send)
            return sent

        small = asyncio.run(run_case([
            {"type": "http.request", "body": b"abc", "more_body": True},
            {"type": "http.request", "body": b"de", "more_body": False},
        ]))
        self.assertEqual(small[0]["status"], 200)
        oversized = asyncio.run(run_case([
            {"type": "http.request", "body": b"abc", "more_body": True},
            {"type": "http.request", "body": b"def", "more_body": False},
        ]))
        self.assertEqual(oversized[0]["status"], 413)
        self.assertIn(b"request body exceeds", oversized[1]["body"])

    def test_request_body_middleware_rejects_ambiguous_or_invalid_content_length(self):
        async def run_case(headers):
            sent = []
            async def forbidden_app(scope, receive, send):
                raise AssertionError("invalid declared length must be rejected before application")
            async def receive():
                return {"type": "http.disconnect"}
            async def send(message):
                sent.append(message)
            middleware = app.RequestBodyLimitMiddleware(forbidden_app, max_body_bytes=5)
            await middleware({"type": "http", "headers": headers}, receive, send)
            return sent

        for headers, expected in (
            ([(b"content-length", b"1"), (b"content-length", b"1")], 400),
            ([(b"content-length", b"not-a-number")], 400),
            ([(b"content-length", b"-1")], 400),
            ([(b"content-length", b"6")], 413),
        ):
            with self.subTest(headers=headers):
                sent = asyncio.run(run_case(headers))
                self.assertEqual(sent[0]["status"], expected)
                body = sent[1]["body"]
                self.assertIn(b"detail", body)

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

    def test_llm_provider_response_is_bounded_and_malformed_payloads_fail_closed(self):
        settings = {
            "LLM_URL": "https://llm.example.test/v1/chat/completions",
            "LLM_MODEL": "test-model",
            "LLM_KEY": "test-key",
            "LLM_DATA_PROCESSING_APPROVED": "1",
        }
        valid = io.BytesIO(b'{"choices":[{"message":{"content":"safe answer"}}]}')
        with patch.dict(os.environ, settings), patch.object(app, "_llm_open", return_value=valid):
            self.assertEqual(app.llm("question"), "safe answer")

        oversized = io.BytesIO(b"x" * (app.MAX_LLM_RESPONSE_BYTES + 1))
        with patch.dict(os.environ, settings), patch.object(app, "_llm_open", return_value=oversized):
            self.assertIsNone(app.llm("question"))

        for raw in (
            b"not-json",
            b"[]",
            b'{"choices":[]}',
            b'{"choices":[{"message":{}}]}',
            b'{"choices":[{"message":{"content":42}}]}',
            b'{"choices":[{"message":{"content":"  "}}]}',
            b"\\xff",
        ):
            with self.subTest(payload=raw[:40]), patch.dict(os.environ, settings), patch.object(
                app, "_llm_open", return_value=io.BytesIO(raw)
            ):
                self.assertIsNone(app.llm("question"))

    def test_llm_response_reader_requests_only_limit_plus_one_bytes(self):
        class BoundedReadProbe:
            def __init__(self):
                self.requested = None
            def read(self, size=-1):
                self.requested = size
                return b'{"choices":[{"message":{"content":"answer"}}]}'

        probe = BoundedReadProbe()
        self.assertEqual(app._read_llm_response_content(probe), "answer")
        self.assertEqual(probe.requested, app.MAX_LLM_RESPONSE_BYTES + 1)

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
