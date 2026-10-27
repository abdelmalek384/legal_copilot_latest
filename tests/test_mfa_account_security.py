import base64
import hashlib
import hmac
import os
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
        replay = self.mutate(
            "post", "/account/mfa/verify",
            json={"code": totp_code(secret, (int(time.time()) // 30 + 1) * 30)},
        )
        self.assertEqual(replay.status_code, 401, replay.text)
        next_step = (int(time.time()) // 30 + 1) * 30
        accepted = self.mutate(
            "post", "/account/mfa/verify",
            json={"code": totp_code(secret, next_step)},
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


if __name__ == "__main__":
    unittest.main()
