"""Tests proving firm roles do not imply platform privileges."""
import sqlite3
import unittest
from pathlib import Path

from platform_access import has_platform_role
from schema_profiles import apply_profile_migrations

MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"


class PlatformRoleLookupTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        apply_profile_migrations(self.db, "control_plane", MIGRATIONS)
        self.db.execute("INSERT INTO firms(id,name) VALUES(1,'Firm A')")
        self.db.execute(
            "INSERT INTO users(id,name,email_display,email_normalized,password_hash) VALUES(1,'Admin','admin@example.test','admin@example.test','hash')"
        )
        self.db.execute(
            "INSERT INTO firm_memberships(user_id,firm_id,firm_role,status) VALUES(1,1,'admin','active')"
        )

    def tearDown(self):
        self.db.close()

    def test_firm_admin_does_not_implicitly_have_platform_role(self):
        self.assertFalse(has_platform_role(self.db, 1, "platform_admin"))
        self.assertFalse(has_platform_role(self.db, 1, "platform_reviewer"))

    def test_platform_role_is_explicit_and_revocable_independently(self):
        self.db.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(1,'platform_reviewer')"
        )
        self.assertTrue(has_platform_role(self.db, 1, "platform_reviewer"))
        self.assertFalse(has_platform_role(self.db, 1, "platform_admin"))
        self.db.execute(
            "DELETE FROM user_platform_roles WHERE user_id=1 AND role_name='platform_reviewer'"
        )
        self.assertFalse(has_platform_role(self.db, 1, "platform_reviewer"))

    def test_rejects_invalid_identity_or_role_inputs(self):
        for user_id in (0, -1, True, "1", None):
            with self.subTest(user_id=user_id), self.assertRaises(ValueError):
                has_platform_role(self.db, user_id, "platform_reviewer")
        with self.assertRaises(ValueError):
            has_platform_role(self.db, 1, "admin")
        with self.assertRaises(TypeError):
            has_platform_role("client-controlled-path", 1, "platform_reviewer")


if __name__ == "__main__":
    unittest.main()
