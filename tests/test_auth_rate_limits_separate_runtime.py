import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient
from starlette.requests import Request

import app
from database_runtime import DatabaseRuntime


class SeparateRuntimeAuthenticationRateLimitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env_names = (
            "COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB",
            "COPILOT_DB", "COPILOT_OBJECT_STORAGE_ROOT", "COPILOT_OBJECT_STORAGE_BACKEND",
            "COPILOT_ENV", "ADMIN_TOKEN",
        )
        self.old_env = {name: os.environ.get(name) for name in self.env_names}
        os.environ.pop("COPILOT_DB", None)
        os.environ["COPILOT_CONTROL_DB"] = str(self.root / "control.sqlite3")
        os.environ["COPILOT_TENANT_DB_ROOT"] = str(self.root / "tenants")
        os.environ["COPILOT_CORPUS_DB"] = str(self.root / "corpus.sqlite3")
        os.environ["COPILOT_OBJECT_STORAGE_ROOT"] = str(self.root / "objects")
        os.environ["COPILOT_OBJECT_STORAGE_BACKEND"] = "local"
        os.environ["COPILOT_ENV"] = "development"
        os.environ["ADMIN_TOKEN"] = "separate-runtime-rate-limit-test-token"
        app._database_runtime = None

        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        app._database_runtime = self.runtime
        self.firm_id, _ = self.runtime.provision_firm("Rate Limit Firm")
        self.password = "SeparateRuntimeRateLimitPassphrase-2026!"
        self.user_id = self.runtime.create_initial_firm_owner(
            self.firm_id, "Rate Limit Owner", "rate-limit-owner@example.test",
            app.hash_pw(self.password),
        )
        self.client = TestClient(app.app)

    def tearDown(self):
        self.client.close()
        try:
            self.runtime.close_current_thread()
        except Exception:
            pass
        app._database_runtime = None
        for name, value in self.old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        self.temp.cleanup()

    @staticmethod
    def _request(path, client_ip="198.51.100.40", method="POST"):
        return Request({
            "type": "http", "http_version": "1.1", "method": method,
            "scheme": "http", "path": path, "raw_path": path.encode(),
            "query_string": b"", "headers": [],
            "client": (client_ip, 1234), "server": ("testserver", 80),
        })

    def test_research_message_rate_limit_is_persisted_in_control_plane(self):
        control = self.runtime.control_connection()
        control.execute(
            "DELETE FROM api_rate_limit_windows WHERE bucket='__research_message__' "
            "AND client_key=?",
            ("198.51.100.40",),
        )
        control.commit()

        worker_two = DatabaseRuntime.from_env()
        worker_two.initialize()
        original_runtime = app._database_runtime
        try:
            for index in range(20):
                app._database_runtime = self.runtime if index % 2 == 0 else worker_two
                self.assertEqual(
                    app._rate_limit(self._request(f"/research/conversations/{index}/messages")),
                    0,
                )
            app._database_runtime = worker_two
            limited = app._rate_limit(self._request("/research/conversations/999/messages"))
            self.assertGreater(limited, 0)
        finally:
            app._database_runtime = original_runtime
            worker_two.close_current_thread()

        stored = control.execute(
            "SELECT hits FROM api_rate_limit_windows WHERE bucket='__research_message__' "
            "AND client_key=?",
            ("198.51.100.40",),
        ).fetchone()
        self.assertIsNotNone(stored)
        self.assertEqual(stored["hits"], 21)

    def test_active_email_or_ip_lockout_rejects_correct_password_before_login(self):
        control = self.runtime.control_connection()
        now = int(app.time.time())
        for identifier in ("rate-limit-owner@example.test", "ip:testclient"):
            control.execute(
                "INSERT INTO login_attempts(email,failures,window_start,locked_until) "
                "VALUES(?,?,?,?) ON CONFLICT(email) DO UPDATE SET "
                "failures=excluded.failures,window_start=excluded.window_start,"
                "locked_until=excluded.locked_until",
                (identifier, 5, now, now + 120),
            )
        control.commit()

        blocked = self.client.post("/login", json={
            "email": "rate-limit-owner@example.test", "password": self.password,
        })
        self.assertEqual(blocked.status_code, 429, blocked.text)
        self.assertGreater(int(blocked.headers.get("Retry-After", "0")), 0)

        control.execute(
            "DELETE FROM login_attempts WHERE email IN (?,?)",
            ("rate-limit-owner@example.test", "ip:testclient"),
        )
        control.commit()
        recovered = self.client.post("/login", json={
            "email": "rate-limit-owner@example.test", "password": self.password,
        })
        self.assertEqual(recovered.status_code, 200, recovered.text)


    def test_upload_throttle_runs_before_authentication_and_persists_in_control_plane(self):
        control = self.runtime.control_connection()
        now = int(app.time.time())
        window_start = int(now // 3600) * 3600
        control.execute(
            "DELETE FROM api_rate_limit_windows WHERE bucket='upload' "
            "AND client_key='testclient' AND window_start=?",
            (window_start,),
        )
        control.commit()

        original_limit = app._UPLOAD_RATE_LIMIT
        app._UPLOAD_RATE_LIMIT = (1, 3600)
        try:
            first = self.client.post(
                "/cases/1/upload", files={"file": ("rate-limit.docx", b"x")}
            )
            self.assertNotEqual(first.status_code, 429, first.text)
            second = self.client.post(
                "/cases/1/upload", files={"file": ("rate-limit.docx", b"x")}
            )
            self.assertEqual(second.status_code, 429, second.text)
            self.assertGreater(int(second.headers.get("Retry-After", "0")), 0)
        finally:
            app._UPLOAD_RATE_LIMIT = original_limit

        stored = control.execute(
            "SELECT hits FROM api_rate_limit_windows WHERE bucket='upload' "
            "AND client_key='testclient' AND window_start=?",
            (window_start,),
        ).fetchone()
        self.assertIsNotNone(stored)
        self.assertEqual(stored["hits"], 2)


    def test_search_middleware_rate_limit_returns_retry_after_in_separate_runtime(self):
        control = self.runtime.control_connection()
        now = int(app.time.time())
        window_start = int(now // 60) * 60
        control.execute(
            "DELETE FROM api_rate_limit_windows WHERE bucket='/search' "
            "AND client_key='testclient' AND window_start=?",
            (window_start,),
        )
        control.commit()

        original_limit = app._RATE_LIMITS["/search"]
        app._RATE_LIMITS["/search"] = (1, 60)
        try:
            first = self.client.post("/search", json={"q": "rate-limit middleware test"})
            self.assertNotEqual(first.status_code, 429, first.text)
            second = self.client.post("/search", json={"q": "rate-limit middleware test"})
            self.assertEqual(second.status_code, 429, second.text)
            self.assertGreater(int(second.headers.get("Retry-After", "0")), 0)
            self.assertIn("rate limit", second.json()["detail"].lower())
        finally:
            app._RATE_LIMITS["/search"] = original_limit

        stored = control.execute(
            "SELECT hits FROM api_rate_limit_windows WHERE bucket='/search' "
            "AND client_key='testclient' AND window_start=?",
            (window_start,),
        ).fetchone()
        self.assertIsNotNone(stored)
        self.assertEqual(stored["hits"], 2)


if __name__ == "__main__":
    unittest.main()
