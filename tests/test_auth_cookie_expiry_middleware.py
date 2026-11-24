"""Regression for auth-cookie expiry surviving middleware exception conversion."""
import unittest
from unittest.mock import patch

import app


class AuthCookieExpiryMiddlewareTests(unittest.IsolatedAsyncioTestCase):
    async def test_expired_auth_cookies_are_attached_to_final_401_response(self):
        request = app.Request({
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/private",
            "raw_path": b"/private",
            "query_string": b"",
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 80),
        })

        async def rejected_dependency(_request):
            # A dependency can set cookies on its injected Response and then raise.
            _request.state.clear_auth_cookies = True
            raise app.HTTPException(401, "unauthorized")

        with (
            patch.object(app, "_separate_runtime_enabled", return_value=False),
            patch.object(app, "_rate_limit", return_value=None),
            patch.object(app, "_declared_body_size_error", return_value=None),
            patch.object(app, "_secure_cookie_transport", return_value=False),
        ):
            response = await app.security_headers(request, rejected_dependency)

        self.assertEqual(response.status_code, 401)
        cookies = response.headers.getlist("set-cookie")
        for name in ("lc_session", "lc_csrf", "lc_firm"):
            self.assertTrue(
                any(cookie.startswith(f"{name}=") and "Max-Age=0" in cookie for cookie in cookies),
                f"{name} expiry cookie missing from final response: {cookies!r}",
            )


if __name__ == "__main__":
    unittest.main()
