import base64
import hashlib
import hmac
import os
import sqlite3
import struct
import tempfile
import time
import unittest
from pathlib import Path

from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

import app
from database_runtime import DatabaseRuntime


def totp_code(secret: str, timestamp: int | None = None) -> str:
    stamp = int(time.time()) if timestamp is None else int(timestamp)
    step = stamp // 30
    raw = base64.b32decode(secret + "=" * ((8 - len(secret) % 8) % 8))
    digest = hmac.new(raw, struct.pack(">Q", step), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return f"{value % 1_000_000:06d}"


class MFAAccountSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        names = (
            "COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB",
            "ADMIN_TOKEN", "MFA_ENFORCEMENT", "MFA_ENCRYPTION_KEY", "COPILOT_ENV",
        )
        self.old_env = {name: os.environ.get(name) for name in names}
        os.environ["COPILOT_CONTROL_DB"] = str(self.root / "control.sqlite3")
        os.environ["COPILOT_TENANT_DB_ROOT"] = str(self.root / "tenants")
        os.environ["COPILOT_CORPUS_DB"] = str(self.root / "corpus.sqlite3")
        os.environ["ADMIN_TOKEN"] = "test-only-mfa-admin-token-2026-abcdef"
        os.environ["MFA_ENFORCEMENT"] = "admins_required"
        os.environ["MFA_ENCRYPTION_KEY"] = Fernet.generate_key().decode("ascii")
        os.environ["COPILOT_ENV"] = "development"
        app._database_runtime = None
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_id, _ = self.runtime.provision_firm("MFA Firm")
        self.password = "MfaTestPassphrase-2026-Strong!"
        self.user_id = self.runtime.create_initial_firm_owner(
            self.firm_id, "MFA Owner", "mfa-owner@example.test", app.hash_pw(self.password)
        )
        self.client = TestClient(app.app)

    def tearDown(self):
        self.client.close()
        try:
            self.runtime.close_current_thread()
        except Exception:
            pass
        for name, value in self.old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        self.temp.cleanup()

    def mutate(self, method, path, **kwargs):
        headers = dict(kwargs.pop("headers", {}) or {})
        headers["X-CSRF-Token"] = self.client.cookies.get("lc_csrf") or ""
        return getattr(self.client, method)(path, headers=headers, **kwargs)

    def login(self):
        return self.client.post(
            "/login", json={"email": "MFA-OWNER@example.test", "password": self.password}
        )

    def enroll(self):
        login = self.login()
        self.assertEqual(login.status_code, 200, login.text)
        self.assertTrue(login.json()["mfa_enrollment_required"])
        blocked = self.client.get("/cases")
        self.assertEqual(blocked.status_code, 403)
        started = self.mutate(
            "post", "/account/mfa/enroll", json={"current_password": self.password}
        )
        self.assertEqual(started.status_code, 200, started.text)
        secret = started.json()["secret"]
        control = self.runtime.control_connection()
        stored = control.execute(
            "SELECT secret_ciphertext,status FROM mfa_credentials WHERE user_id=?", (self.user_id,)
        ).fetchone()
        self.assertEqual(stored["status"], "pending")
        self.assertNotEqual(stored["secret_ciphertext"], secret)
        return secret

    def confirm(self, secret):
        current_step = (int(time.time()) // 30) * 30
        response = self.mutate(
            "post", "/account/mfa/confirm",
            json={"current_password": self.password, "code": totp_code(secret, current_step)},
        )
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["recovery_codes"]

    def test_admin_must_enroll_and_recovery_codes_are_shown_once_as_hashes(self):
        secret = self.enroll()
        codes = self.confirm(secret)
        self.assertEqual(len(codes), 10)
        control = self.runtime.control_connection()
        credential = control.execute(
            "SELECT status,secret_ciphertext,last_accepted_step FROM mfa_credentials WHERE user_id=?",
            (self.user_id,),
        ).fetchone()
        self.assertEqual(credential["status"], "enabled")
        self.assertNotIn(secret, credential["secret_ciphertext"])
        hashes = [row["code_hash"] for row in control.execute(
            "SELECT code_hash FROM mfa_recovery_codes WHERE user_id=?", (self.user_id,)
        ).fetchall()]
        self.assertEqual(len(hashes), 10)
        self.assertTrue(all(code not in hashes for code in codes))
        self.assertTrue(all(value.startswith("scrypt$") for value in hashes))
        self.assertEqual(self.client.get("/cases").status_code, 200)

    def test_login_requires_totp_and_replayed_step_is_rejected(self):
        secret = self.enroll()
        self.confirm(secret)
        login = self.login()
        self.assertEqual(login.status_code, 200, login.text)
        self.assertTrue(login.json()["mfa_verification_required"])
        credential = self.runtime.control_connection().execute(
            "SELECT last_accepted_step FROM mfa_credentials WHERE user_id=?",
            (self.user_id,),
        ).fetchone()
        last_accepted_step = credential["last_accepted_step"]
        self.assertIsNotNone(last_accepted_step)

        # Replay the exact step accepted during enrollment confirmation. Do not
        # derive this code from wall-clock time: a 30-second boundary between
        # confirm() and login verification otherwise makes this test flaky.
        replay = self.mutate(
            "post", "/account/mfa/verify",
            json={"code": totp_code(secret, last_accepted_step * 30)},
        )
        self.assertEqual(replay.status_code, 401, replay.text)

        current_step = int(time.time()) // 30
        next_step = max(current_step, last_accepted_step + 1)
        accepted = self.mutate(
            "post", "/account/mfa/verify",
            json={"code": totp_code(secret, next_step * 30)},
        )
        self.assertEqual(accepted.status_code, 200, accepted.text)
        self.assertTrue(accepted.json()["mfa_verified"])
        self.assertEqual(self.client.get("/cases").status_code, 200)

    def test_recovery_code_is_single_use(self):
        secret = self.enroll()
        codes = self.confirm(secret)
        login = self.login()
        self.assertTrue(login.json()["mfa_verification_required"])
        used = codes[0]
        first = self.mutate("post", "/account/mfa/verify", json={"recovery_code": used})
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(first.json()["factor"], "recovery")
        self.login()
        second = self.mutate("post", "/account/mfa/verify", json={"recovery_code": used})
        self.assertEqual(second.status_code, 401, second.text)
        control = self.runtime.control_connection()
        row = control.execute(
            "SELECT used_at FROM mfa_recovery_codes WHERE user_id=? ORDER BY id LIMIT 1",
            (self.user_id,),
        ).fetchone()
        self.assertIsNotNone(row["used_at"])

    def test_five_invalid_mfa_attempts_are_throttled(self):
        secret = self.enroll()
        self.confirm(secret)
        login = self.login()
        self.assertTrue(login.json()["mfa_verification_required"])
        statuses = []
        for _ in range(5):
            response = self.mutate("post", "/account/mfa/verify", json={"code": "000000"})
            statuses.append(response.status_code)
        self.assertEqual(statuses[-1], 429)
        self.assertTrue(all(code in (401, 429) for code in statuses))

    def test_recovery_code_rotation_invalidates_old_codes_and_is_not_cached(self):
        secret = self.enroll()
        old_codes = self.confirm(secret)
        # Confirmation establishes a recent, verified MFA session.
        rotate = self.mutate(
            "post", "/account/mfa/recovery-codes/rotate",
            json={
                "current_password": self.password,
                "code": totp_code(secret, (int(time.time()) // 30 + 1) * 30),
            },
        )
        self.assertEqual(rotate.status_code, 200, rotate.text)
        self.assertEqual(len(rotate.json()["recovery_codes"]), 10)
        self.assertIn("no-store", rotate.headers.get("cache-control", "").lower())
        new_codes = rotate.json()["recovery_codes"]
        self.assertNotEqual(old_codes, new_codes)

        control = self.runtime.control_connection()
        rows = control.execute(
            "SELECT code_hash,used_at FROM mfa_recovery_codes WHERE user_id=? ORDER BY id",
            (self.user_id,),
        ).fetchall()
        self.assertEqual(len(rows), 20)
        self.assertTrue(all(row["code_hash"].startswith("scrypt$") for row in rows))
        self.assertTrue(all(row["used_at"] is not None for row in rows[:10]))
        self.assertTrue(all(row["used_at"] is None for row in rows[10:]))
        self.assertFalse(any(code in [row["code_hash"] for row in rows] for code in new_codes))

        self.login()
        old_code_attempt = self.mutate(
            "post", "/account/mfa/verify", json={"recovery_code": old_codes[0]}
        )
        self.assertEqual(old_code_attempt.status_code, 401, old_code_attempt.text)

    def test_lost_authenticator_reenrollment_requires_recent_mfa_and_current_password(self):
        old_secret = self.enroll()
        self.confirm(old_secret)
        # A valid recent MFA session is required, even when the password is correct.
        reenroll = self.mutate(
            "post", "/account/mfa/re-enroll",
            json={"current_password": "incorrect-password"},
        )
        self.assertEqual(reenroll.status_code, 403, reenroll.text)
        control = self.runtime.control_connection()
        current = control.execute(
            "SELECT status,secret_ciphertext FROM mfa_credentials WHERE user_id=?",
            (self.user_id,),
        ).fetchone()
        self.assertEqual(current["status"], "enabled")
        self.assertNotEqual(current["secret_ciphertext"], old_secret)

        # Correct password and recent MFA verification can start a new pending
        # enrollment, but the replacement is not enabled until explicitly confirmed.
        reenroll = self.mutate(
            "post", "/account/mfa/re-enroll",
            json={"current_password": self.password},
        )
        self.assertEqual(reenroll.status_code, 200, reenroll.text)
        new_secret = reenroll.json()["secret"]
        self.assertNotEqual(new_secret, old_secret)
        current = control.execute(
            "SELECT status,secret_ciphertext,enrollment_expires FROM mfa_credentials WHERE user_id=?",
            (self.user_id,),
        ).fetchone()
        self.assertEqual(current["status"], "pending")
        self.assertNotEqual(current["secret_ciphertext"], new_secret)
        self.assertGreater(current["enrollment_expires"], int(time.time()))
        self.assertIn("no-store", reenroll.headers.get("cache-control", "").lower())

    def test_lost_authenticator_reenrollment_rejects_stale_mfa_verification(self):
        secret = self.enroll()
        self.confirm(secret)
        control = self.runtime.control_connection()
        control.execute(
            "UPDATE auth_sessions SET mfa_verified_at=? WHERE user_id=?",
            (int(time.time()) - 601, self.user_id),
        )
        control.commit()

        response = self.mutate(
            "post", "/account/mfa/re-enroll",
            json={"current_password": self.password},
        )
        self.assertEqual(response.status_code, 403, response.text)
        self.assertIn("recent MFA verification is required", response.text)
        credential = control.execute(
            "SELECT status FROM mfa_credentials WHERE user_id=?", (self.user_id,)
        ).fetchone()
        self.assertEqual(credential["status"], "enabled")

    def test_required_policy_prevents_privileged_admin_from_disabling_mfa(self):
        secret = self.enroll()
        self.confirm(secret)
        response = self.mutate(
            "post", "/account/mfa/disable",
            json={"current_password": self.password, "code": totp_code(secret, (int(time.time()) // 30 + 1) * 30)},
        )
        self.assertEqual(response.status_code, 403, response.text)
        self.assertIsNotNone(self.runtime.control_connection().execute(
            "SELECT 1 FROM mfa_credentials WHERE user_id=? AND status='enabled'", (self.user_id,)
        ).fetchone())


    def test_mfa_enrollment_audit_failure_rolls_back_pending_credential(self):
        failure_client = TestClient(app.app, raise_server_exceptions=False)
        try:
            login = failure_client.post(
                "/login", json={"email": "MFA-OWNER@example.test", "password": self.password}
            )
            self.assertEqual(login.status_code, 200, login.text)
            control = self.runtime.control_connection()
            control.execute("""
                CREATE TRIGGER reject_mfa_enrollment_audit
                BEFORE INSERT ON mfa_security_events
                WHEN NEW.event_type='enrollment_started'
                BEGIN SELECT RAISE(ABORT, 'injected MFA audit failure'); END
            """)
            control.commit()
            response = failure_client.post(
                "/account/mfa/enroll",
                json={"current_password": self.password},
                headers={"X-CSRF-Token": failure_client.cookies.get("lc_csrf") or ""},
            )
            self.assertEqual(response.status_code, 500, response.text)
            self.assertIsNone(control.execute(
                "SELECT user_id FROM mfa_credentials WHERE user_id=?", (self.user_id,)
            ).fetchone())
            self.assertEqual(control.execute(
                "SELECT COUNT(*) FROM mfa_security_events WHERE actor_user_id=? AND event_type='enrollment_started'",
                (self.user_id,),
            ).fetchone()[0], 0)
        finally:
            failure_client.close()

    def test_mfa_confirmation_audit_failure_preserves_pending_state_and_session(self):
        self.enroll()
        failure_client = TestClient(app.app, raise_server_exceptions=False)
        try:
            login = failure_client.post(
                "/login", json={"email": "MFA-OWNER@example.test", "password": self.password}
            )
            self.assertEqual(login.status_code, 200, login.text)
            control = self.runtime.control_connection()
            credential = control.execute(
                "SELECT secret_ciphertext,status FROM mfa_credentials WHERE user_id=?",
                (self.user_id,),
            ).fetchone()
            self.assertEqual(credential["status"], "pending")
            secret = app.decrypt_totp_secret(credential["secret_ciphertext"])
            control.execute("""
                CREATE TRIGGER reject_mfa_confirmation_audit
                BEFORE INSERT ON mfa_security_events
                WHEN NEW.event_type='enrollment_completed'
                BEGIN SELECT RAISE(ABORT, 'injected MFA audit failure'); END
            """)
            control.commit()
            session_token = failure_client.cookies.get("lc_session")
            response = failure_client.post(
                "/account/mfa/confirm",
                json={
                    "current_password": self.password,
                    "code": totp_code(secret, (int(time.time()) // 30) * 30),
                },
                headers={"X-CSRF-Token": failure_client.cookies.get("lc_csrf") or ""},
            )
            self.assertEqual(response.status_code, 500, response.text)
            current = control.execute(
                "SELECT status,last_accepted_step FROM mfa_credentials WHERE user_id=?",
                (self.user_id,),
            ).fetchone()
            self.assertEqual(current["status"], "pending")
            self.assertIsNone(current["last_accepted_step"])
            self.assertEqual(control.execute(
                "SELECT COUNT(*) FROM mfa_recovery_codes WHERE user_id=?", (self.user_id,)
            ).fetchone()[0], 0)
            session = control.execute(
                "SELECT mfa_verified FROM auth_sessions WHERE token_hash=?", (app.sha(session_token),)
            ).fetchone()
            self.assertEqual(session["mfa_verified"], 0)
            self.assertEqual(control.execute(
                "SELECT COUNT(*) FROM mfa_security_events WHERE actor_user_id=? AND event_type='enrollment_completed'",
                (self.user_id,),
            ).fetchone()[0], 0)
        finally:
            failure_client.close()


if __name__ == "__main__":
    unittest.main()
