import base64
import contextlib
import hashlib
import hmac
import io
import os
import struct
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from cryptography.fernet import Fernet

import app
import manage
from database_runtime import DatabaseRuntime
from tools.mfa_crypto import encrypt_totp_secret
from tools.mfa_primitives import generate_recovery_codes, generate_totp_secret, hash_recovery_code


def _code(secret: str, timestamp: int) -> str:
    raw = base64.b32decode(secret + "=" * ((8 - len(secret) % 8) % 8))
    digest = hmac.new(raw, struct.pack(">Q", timestamp // 30), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return f"{value % 1_000_000:06d}"


class MFABreakGlassCLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.names = ("COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB",
                      "MFA_ENCRYPTION_KEY", "MFA_ENFORCEMENT", "COPILOT_ENV")
        self.old = {name: os.environ.get(name) for name in self.names}
        os.environ["COPILOT_CONTROL_DB"] = str(self.root / "control.sqlite3")
        os.environ["COPILOT_TENANT_DB_ROOT"] = str(self.root / "tenants")
        os.environ["COPILOT_CORPUS_DB"] = str(self.root / "corpus.sqlite3")
        os.environ["MFA_ENCRYPTION_KEY"] = Fernet.generate_key().decode()
        os.environ["MFA_ENFORCEMENT"] = "admins_required"
        os.environ["COPILOT_ENV"] = "development"
        self.runtime = DatabaseRuntime.from_env()
        self.runtime.initialize()
        self.firm_id, _ = self.runtime.provision_firm("Break Glass Firm")
        self.actor_password = "Operator-Password-2026!"
        self.target_password = "Target-Password-2026!"
        self.actor_id = self.runtime.create_global_identity(
            "Platform Operator", "operator@example.test", app.hash_pw(self.actor_password)
        )
        self.target_id = self.runtime.create_global_identity(
            "Locked Out Admin", "target-admin@example.test", app.hash_pw(self.target_password)
        )
        c = self.runtime.control_connection()
        c.execute(
            "INSERT INTO user_platform_roles(user_id,role_name,granted_by_user_id) VALUES(?,'platform_admin',?)",
            (self.actor_id, self.actor_id),
        )
        self.runtime.create_firm_membership(self.target_id, self.firm_id, "admin")
        self.actor_secret = generate_totp_secret()
        target_secret = generate_totp_secret()
        now = int(time.time())
        for user_id, secret in ((self.actor_id, self.actor_secret), (self.target_id, target_secret)):
            c.execute(
                "INSERT INTO mfa_credentials(user_id,secret_ciphertext,status,enabled_at) "
                "VALUES(?,?,'enabled',datetime('now'))",
                (user_id, encrypt_totp_secret(secret)),
            )
        recovery = generate_recovery_codes()
        c.execute(
            "INSERT INTO mfa_recovery_codes(user_id,code_hash) VALUES(?,?)",
            (self.target_id, recovery["hashes"][0]),
        )
        c.execute(
            "INSERT INTO auth_sessions(token_hash,user_id,expires,mfa_verified,mfa_verified_at) VALUES(?,?,?,?,?)",
            (app.sha("target-session-token"), self.target_id, now + 3600, 1, now),
        )
        c.commit()

    def tearDown(self):
        self.runtime.close_current_thread()
        for name, value in self.old.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        self.temp.cleanup()

    def test_two_admin_break_glass_reset_revokes_sessions_and_audits_reason(self):
        now = int(time.time())
        args = SimpleNamespace(
            actor_email="operator@example.test",
            target_email="target-admin@example.test",
            reason="lost_device",
        )
        output = io.StringIO()
        with patch("getpass.getpass", side_effect=[
            self.actor_password, _code(self.actor_secret, now)
        ]), contextlib.redirect_stdout(output):
            manage.mfa_reset_cli(args)
        c = self.runtime.control_connection()
        self.assertIsNone(c.execute("SELECT 1 FROM mfa_credentials WHERE user_id=?", (self.target_id,)).fetchone())
        self.assertEqual(c.execute("SELECT COUNT(*) FROM auth_sessions WHERE user_id=?", (self.target_id,)).fetchone()[0], 0)
        self.assertTrue(c.execute(
            "SELECT used_at FROM mfa_recovery_codes WHERE user_id=?", (self.target_id,)
        ).fetchone()["used_at"])
        event = c.execute(
            "SELECT actor_user_id,target_user_id,event_type,detail_json FROM mfa_security_events "
            "WHERE event_type='administrator_reset'"
        ).fetchone()
        self.assertEqual(event["actor_user_id"], self.actor_id)
        self.assertEqual(event["target_user_id"], self.target_id)
        self.assertIn('"reason":"lost_device"', event["detail_json"])
        self.assertNotIn(self.actor_password, event["detail_json"])
        self.assertIn('"status": "mfa_reset"', output.getvalue())

    def test_break_glass_rejects_password_only_actor_without_resetting_target(self):
        args = SimpleNamespace(
            actor_email="operator@example.test",
            target_email="target-admin@example.test",
            reason="lost_device",
        )
        with patch("getpass.getpass", side_effect=["wrong-password", "000000"]):
            with self.assertRaises(SystemExit):
                manage.mfa_reset_cli(args)
        c = self.runtime.control_connection()
        self.assertIsNotNone(c.execute("SELECT 1 FROM mfa_credentials WHERE user_id=?", (self.target_id,)).fetchone())
        self.assertEqual(c.execute("SELECT COUNT(*) FROM auth_sessions WHERE user_id=?", (self.target_id,)).fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
