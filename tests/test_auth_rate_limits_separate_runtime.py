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
            "COPILOT_ENV", "ADMIN_TOKEN", "COPILOT_IDENTITY_RATE_LIMIT_KEY",
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
        os.environ["COPILOT_IDENTITY_RATE_LIMIT_KEY"] = "separate-runtime-login-rate-limit-hmac-test-secret-2026"
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
        identifiers = (
            app._identity_rate_limit_digest("rate-limit-owner@example.test", purpose="login_email"),
            app._identity_rate_limit_digest("testclient", purpose="login_ip"),
        )
        for identifier in identifiers:
            control.execute(
                "INSERT INTO login_attempts(email,failures,window_start,locked_until) "
                "VALUES(?,?,?,?) ON CONFLICT(email) DO UPDATE SET "
                "failures=excluded.failures,window_start=excluded.window_start,"
                "locked_until=excluded.locked_until",
                (identifier, 5, now, now + 120),
            )
        control.commit()

        worker_two = DatabaseRuntime.from_env()
        worker_two.initialize()
        original_runtime = app._database_runtime
        try:
            # The same HMAC pseudonyms must enforce one shared control-plane
            # budget even when a different application worker receives login.
            app._database_runtime = worker_two
            with self.assertRaises(app.HTTPException) as blocked:
                app._login_separate(
                    app.LoginIn(email="rate-limit-owner@example.test", password=self.password),
                    self._request("/login"),
                    app.Response(),
                )
            self.assertEqual(blocked.exception.status_code, 429)
            self.assertGreater(int(blocked.exception.headers.get("Retry-After", "0")), 0)
        finally:
            app._database_runtime = original_runtime
            worker_two.close_current_thread()

        control.execute(
            "DELETE FROM login_attempts WHERE email IN (?,?)",
            identifiers,
        )
        control.commit()
        recovered = self.client.post("/login", json={
            "email": "rate-limit-owner@example.test", "password": self.password,
        })
        self.assertEqual(recovered.status_code, 200, recovered.text)


    def test_failed_login_persists_only_hmac_pseudonyms_for_email_and_ip(self):
        response = self.client.post("/login", json={
            "email": "rate-limit-owner@example.test", "password": "incorrect-password",
        })
        self.assertEqual(response.status_code, 401, response.text)
        rows = self.runtime.control_connection().execute(
            "SELECT email FROM login_attempts ORDER BY email"
        ).fetchall()
        keys = [str(row["email"]) for row in rows]
        self.assertEqual(len(keys), 2)
        expected = {
            app._identity_rate_limit_digest("rate-limit-owner@example.test", purpose="login_email"),
            app._identity_rate_limit_digest("testclient", purpose="login_ip"),
        }
        self.assertEqual(set(keys), expected)
        self.assertNotEqual(
            app._identity_rate_limit_digest("rate-limit-owner@example.test", purpose="login_email"),
            app._identity_rate_limit_digest("rate-limit-owner@example.test", purpose="email"),
        )
        self.assertNotIn("rate-limit-owner@example.test", keys)
        self.assertFalse(any("testclient" in key or key.startswith("ip:") for key in keys))
        self.assertTrue(all(len(key) == 64 and all(ch in "0123456789abcdef" for ch in key) for key in keys))

    def test_production_api_middleware_stores_hmac_ip_keys_and_fails_closed_without_key(self):
        original_mode = app._environment_mode
        peer = "198.51.100.40"
        request = self._request("/search", client_ip=peer)
        expected = app._identity_rate_limit_digest(peer, purpose="middleware_ip:/search")
        try:
            app._environment_mode = "production"
            self.assertEqual(app._rate_limit(request), 0)
            row = self.runtime.control_connection().execute(
                "SELECT client_key FROM api_rate_limit_windows WHERE bucket='/search' "
                "ORDER BY window_start DESC LIMIT 1"
            ).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["client_key"], expected)
            self.assertNotEqual(row["client_key"], peer)

            saved_key = os.environ.pop("COPILOT_IDENTITY_RATE_LIMIT_KEY", None)
            try:
                blocked = self._request("/search", client_ip="198.51.100.41")
                retry_after = app._rate_limit(blocked)
                self.assertGreater(retry_after, 0)
                count = self.runtime.control_connection().execute(
                    "SELECT COUNT(*) FROM api_rate_limit_windows WHERE bucket='/search'"
                ).fetchone()[0]
                self.assertEqual(count, 1)
            finally:
                if saved_key is not None:
                    os.environ["COPILOT_IDENTITY_RATE_LIMIT_KEY"] = saved_key
        finally:
            app._environment_mode = original_mode

    def test_hmac_ip_budget_keeps_the_higher_twenty_attempt_threshold(self):
        for index in range(5):
            response = self.client.post("/login", json={
                "email": f"unknown-{index}@example.test", "password": "incorrect-password",
            })
            self.assertEqual(response.status_code, 401, response.text)
        ip_key = app._identity_rate_limit_digest("testclient", purpose="login_ip")
        row = self.runtime.control_connection().execute(
            "SELECT failures,locked_until FROM login_attempts WHERE email=?",
            (ip_key,),
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["failures"], 5)
        self.assertEqual(row["locked_until"], 0)

    def test_production_and_staging_login_fail_closed_without_dedicated_hmac_key(self):
        saved_key = os.environ.pop("COPILOT_IDENTITY_RATE_LIMIT_KEY", None)
        original_mode = app._environment_mode
        try:
            for mode in ("production", "staging"):
                with self.subTest(mode=mode):
                    app._environment_mode = mode
                    response = self.client.post("/login", json={
                        "email": "rate-limit-owner@example.test", "password": "incorrect-password",
                    })
                    self.assertEqual(response.status_code, 503, response.text)
                    count = self.runtime.control_connection().execute(
                        "SELECT COUNT(*) FROM login_attempts"
                    ).fetchone()[0]
                    self.assertEqual(count, 0)
        finally:
            app._environment_mode = original_mode
            if saved_key is not None:
                os.environ["COPILOT_IDENTITY_RATE_LIMIT_KEY"] = saved_key

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


    def test_logout_revokes_server_side_session_in_separate_runtime(self):
        login = self.client.post("/login", json={
            "email": "rate-limit-owner@example.test", "password": self.password,
        })
        self.assertEqual(login.status_code, 200, login.text)
        self.assertEqual(self.client.get("/cases").status_code, 200)

        csrf = self.client.cookies.get("lc_csrf") or ""
        logout = self.client.post("/logout", headers={"X-CSRF-Token": csrf})
        self.assertEqual(logout.status_code, 200, logout.text)
        self.assertEqual(self.client.get("/session").status_code, 401)
        self.assertEqual(self.client.get("/cases").status_code, 401)


    def test_password_strength_rejects_common_long_password_without_changing_credentials(self):
        login = self.client.post("/login", json={
            "email": "rate-limit-owner@example.test", "password": self.password,
        })
        self.assertEqual(login.status_code, 200, login.text)
        csrf = self.client.cookies.get("lc_csrf") or ""
        rejected = self.client.post(
            "/account/password",
            json={
                "current_password": self.password,
                "new_password": "password1234",
            },
            headers={"X-CSRF-Token": csrf},
        )
        self.assertEqual(rejected.status_code, 422, rejected.text)

        control = self.runtime.control_connection()
        account = control.execute(
            "SELECT password_hash FROM users WHERE id=?", (self.user_id,)
        ).fetchone()
        self.assertIsNotNone(account)
        self.assertTrue(app.check_pw(self.password, account["password_hash"]))
        self.assertEqual(
            self.client.post("/login", json={
                "email": "rate-limit-owner@example.test", "password": self.password,
            }).status_code,
            200,
        )


if __name__ == "__main__":
    unittest.main()
