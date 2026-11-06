import asyncio
import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from starlette.requests import Request
from starlette.responses import Response

import app
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
        "path": "/ask",
        "raw_path": b"/ask",
        "query_string": b"",
        "headers": headers,
        "client": (peer, 12345),
        "server": ("testserver", 80),
    })


class FakeCursor:
    def fetchone(self):
        return {"hits": 1}

    def fetchall(self):
        return []


class FakeConnection:
    def __init__(self):
        self.arguments = []

    def execute(self, _sql, arguments):
        self.arguments.append(arguments)
        return FakeCursor()

    def commit(self):
        pass


class TrustedProxyClientIpTests(unittest.TestCase):
    def test_untrusted_peer_cannot_spoof_forwarded_for(self):
        with patch.dict(os.environ, {"COPILOT_TRUSTED_PROXIES": "10.0.0.0/8"}):
            request = make_request("198.51.100.20", "203.0.113.99")
            self.assertEqual(client_ip(request), "198.51.100.20")

    def test_trusted_proxy_uses_forwarded_client_address(self):
        with patch.dict(os.environ, {"COPILOT_TRUSTED_PROXIES": "10.0.0.0/8"}):
            request = make_request("10.0.0.8", "203.0.113.44")
            self.assertEqual(client_ip(request), "203.0.113.44")

    def test_rightmost_untrusted_hop_is_selected_through_proxy_chain(self):
        with patch.dict(os.environ, {"COPILOT_TRUSTED_PROXIES": "10.0.0.0/8"}):
            request = make_request("10.0.0.8", "203.0.113.44, 10.0.0.7")
            self.assertEqual(client_ip(request), "203.0.113.44")

    def test_clients_behind_same_trusted_proxy_get_distinct_rate_limit_buckets(self):
        with patch.dict(os.environ, {"COPILOT_TRUSTED_PROXIES": "10.0.0.0/8"}):
            connection = FakeConnection()
            with patch.object(app, "control_conn", return_value=connection):
                app._rate_limit(make_request("10.0.0.8", "203.0.113.44"))
                app._rate_limit(make_request("10.0.0.8", "203.0.113.45"))
            self.assertEqual(connection.arguments[0][0], "/ask")
            self.assertEqual(connection.arguments[1][0], "/ask")
            self.assertEqual(connection.arguments[0][1], "203.0.113.44")
            self.assertEqual(connection.arguments[1][1], "203.0.113.45")

    def test_malformed_forwarded_for_falls_back_to_peer(self):
        with patch.dict(os.environ, {"COPILOT_TRUSTED_PROXIES": "10.0.0.0/8"}):
            request = make_request("10.0.0.8", "203.0.113.44, not-an-ip")
            self.assertEqual(client_ip(request), "10.0.0.8")

    def test_wildcard_trusted_proxy_configuration_is_rejected(self):
        with patch.dict(os.environ, {"COPILOT_TRUSTED_PROXIES": "*"}):
            with self.assertRaises(ValueError):
                client_ip(make_request("198.51.100.20", "203.0.113.99"))

    def test_malformed_trusted_proxy_configuration_is_rejected(self):
        with patch.dict(os.environ, {"COPILOT_TRUSTED_PROXIES": "10.0.0.0/8,not-a-network"}):
            with self.assertRaises(ValueError):
                client_ip(make_request("10.0.0.8", "203.0.113.44"))


    def test_same_client_ip_has_separate_budgets_for_validated_firms(self):
        with patch.dict(os.environ, {"COPILOT_TRUSTED_PROXIES": "10.0.0.0/8"}):
            connection = FakeConnection()
            request = make_request("10.0.0.8", "203.0.113.44")
            first = app._active_firm_context.set(type("Firm", (), {"firm_id": 101})())
            try:
                with patch.object(app, "control_conn", return_value=connection):
                    app._rate_limit(request)
                second = app._active_firm_context.set(type("Firm", (), {"firm_id": 202})())
                try:
                    with patch.object(app, "control_conn", return_value=connection):
                        app._rate_limit(request)
                finally:
                    app._active_firm_context.reset(second)
            finally:
                app._active_firm_context.reset(first)
        self.assertEqual(connection.arguments[0][0], "/ask")
        self.assertEqual(connection.arguments[1][0], "/ask")
        self.assertEqual(connection.arguments[0][1], "101:203.0.113.44")
        self.assertEqual(connection.arguments[1][1], "202:203.0.113.44")

    def test_firm_rate_budgets_are_isolated_and_persist_across_db_reconnects(self):
        with tempfile.TemporaryDirectory(prefix="trusted-proxy-rate-limit-") as temp:
            database = os.path.join(temp, "control.sqlite3")
            connection = sqlite3.connect(database)
            connection.execute(
                "CREATE TABLE api_rate_limit_windows("
                "bucket TEXT NOT NULL, client_key TEXT NOT NULL, "
                "window_start INTEGER NOT NULL, hits INTEGER NOT NULL DEFAULT 0, "
                "PRIMARY KEY(bucket,client_key,window_start))"
            )
            connection.commit()
            connection.close()

            opened_connections = []

            def open_control():
                db = sqlite3.connect(database)
                db.row_factory = sqlite3.Row
                opened_connections.append(db)
                return db

            request = make_request("10.0.0.8", "203.0.113.44")
            with patch.object(app, "_RATE_LIMITS", {"/ask": (1, 3600)}):
                with patch.object(app, "control_conn", side_effect=open_control):
                    firm_a = app._active_firm_context.set(type("Firm", (), {"firm_id": 101})())
                    try:
                        self.assertEqual(app._rate_limit(request), 0)
                    finally:
                        app._active_firm_context.reset(firm_a)

                    firm_b = app._active_firm_context.set(type("Firm", (), {"firm_id": 202})())
                    try:
                        self.assertEqual(app._rate_limit(request), 0)
                    finally:
                        app._active_firm_context.reset(firm_b)

                    # New SQLite connections are opened for each call, simulating
                    # worker/database reconnection while retaining the control DB.
                    firm_a = app._active_firm_context.set(type("Firm", (), {"firm_id": 101})())
                    try:
                        self.assertGreater(app._rate_limit(request), 0)
                    finally:
                        app._active_firm_context.reset(firm_a)

                    firm_b = app._active_firm_context.set(type("Firm", (), {"firm_id": 202})())
                    try:
                        self.assertGreater(app._rate_limit(request), 0)
                    finally:
                        app._active_firm_context.reset(firm_b)
            for db in opened_connections:
                db.close()


    def test_middleware_sets_validated_firm_context_before_rate_limiting(self):
        async def exercise():
            context = type("Firm", (), {"firm_id": 303})()
            observed = {}

            def rate_limit(_request):
                active = app._active_firm_context.get()
                observed["rate_limit_firm_id"] = getattr(active, "firm_id", None)
                return 0

            async def call_next(_request):
                active = app._active_firm_context.get()
                observed["route_firm_id"] = getattr(active, "firm_id", None)
                return Response("ok")

            with patch.object(app, "_separate_runtime_enabled", return_value=True), \\
                 patch.object(app, "_request_firm_context", return_value=context), \\
                 patch.object(app, "_rate_limit", side_effect=rate_limit):
                response = await app.security_headers(make_request("10.0.0.8"), call_next)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(observed["rate_limit_firm_id"], 303)
            self.assertEqual(observed["route_firm_id"], 303)
            self.assertIsNone(app._active_firm_context.get())

        asyncio.run(exercise())


if __name__ == "__main__":
    unittest.main()
