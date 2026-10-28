import unittest

import httpx

# The app reads host policy and the database path at import time. Keep this test
# isolated from developer data and exercise the actual ASGI middleware stack.
os.environ["COPILOT_ENV"] = "development"
os.environ["COPILOT_ALLOWED_HOSTS"] = "legal.example.test"

import app as app_module


class TrustedHostMiddlewareTests(unittest.IsolatedAsyncioTestCase):
    async def test_actual_asgi_app_rejects_unlisted_host(self):
        host_middleware = [
            middleware for middleware in app_module.app.user_middleware
            if middleware.cls.__name__ == "TrustedHostMiddleware"
        ]
        self.assertEqual(len(host_middleware), 1)
        self.assertEqual(host_middleware[0].kwargs.get("allowed_hosts"), ["legal.example.test"])
        transport = httpx.ASGITransport(app=app_module.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://legal.example.test") as client:
            allowed = await client.get(
                "/__trusted_host_probe__",
                headers={"host": "legal.example.test"},
            )
            rejected = await client.get(
                "/__trusted_host_probe__",
                headers={"host": "evil.example.test"},
            )
        self.assertEqual(allowed.status_code, 404)
        self.assertEqual(rejected.status_code, 400)

    def test_host_pattern_parser_rejects_url_syntax_and_wildcard_all(self):
        for value in ("*", "https://legal.example.test", "legal.example.test/path", "user@legal.example.test"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                app_module._trusted_host_patterns(value)


if __name__ == "__main__":
    unittest.main()
