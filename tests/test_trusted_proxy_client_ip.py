import os
import unittest
from unittest.mock import patch

from starlette.requests import Request

from app import client_ip


def make_request(peer, forwarded_for=None):
    headers = []
    if forwarded_for is not None:
        headers.append((b"x-forwarded-for", forwarded_for.encode("ascii")))
    return Request({
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": headers,
        "client": (peer, 12345),
        "server": ("testserver", 80),
    })


class TrustedProxyClientIpTests(unittest.TestCase):
    def test_untrusted_peer_cannot_spoof_forwarded_for(self):
        with patch.dict(os.environ, {"COPILOT_TRUSTED_PROXIES": "10.0.0.0/8"}):
            request = make_request("198.51.100.20", "203.0.113.99")
            self.assertEqual(client_ip(request), "198.51.100.20")

    def test_trusted_proxy_uses_forwarded_client_address(self):
        with patch.dict(os.environ, {"COPILOT_TRUSTED_PROXIES": "10.0.0.0/8"}):
            request = make_request("10.0.0.8", "203.0.113.44")
            self.assertEqual(client_ip(request), "203.0.113.44")

    def test_clients_behind_same_trusted_proxy_get_distinct_keys(self):
        with patch.dict(os.environ, {"COPILOT_TRUSTED_PROXIES": "10.0.0.0/8"}):
            first = client_ip(make_request("10.0.0.8", "203.0.113.44"))
            second = client_ip(make_request("10.0.0.8", "203.0.113.45"))
            self.assertNotEqual(first, second)

    def test_malformed_forwarded_for_falls_back_to_peer(self):
        with patch.dict(os.environ, {"COPILOT_TRUSTED_PROXIES": "10.0.0.0/8"}):
            request = make_request("10.0.0.8", "203.0.113.44, not-an-ip")
            self.assertEqual(client_ip(request), "10.0.0.8")

    def test_malformed_trusted_proxy_configuration_is_rejected(self):
        with patch.dict(os.environ, {"COPILOT_TRUSTED_PROXIES": "10.0.0.0/8,not-a-network"}):
            with self.assertRaises(ValueError):
                client_ip(make_request("10.0.0.8", "203.0.113.44"))


if __name__ == "__main__":
    unittest.main()
