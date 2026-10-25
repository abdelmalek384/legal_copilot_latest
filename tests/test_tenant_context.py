"""Security tests for trusted firm-context resolution."""
import sqlite3
import unittest
from pathlib import Path

from schema_profiles import apply_profile_migrations
from tenant_context import FirmContext, FirmContextError, resolve_firm_context, sqlite_membership_lookup

MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"


class ResolveFirmContextTests(unittest.TestCase):
    def setUp(self):
        self.user = {"id": 7, "email": "lawyer@example.test"}
        self.memberships = {
            (7, 101): {"status": "active", "role": "lawyer"},
            (7, 202): {"status": "suspended", "role": "admin"},
            (8, 202): {"status": "active", "role": "owner"},
        }

    def lookup(self, user_id, firm_id):
        return self.memberships.get((user_id, firm_id))

    def test_resolves_active_membership_to_immutable_context(self):
        result = resolve_firm_context(self.user, 101, self.lookup)
        self.assertEqual(result, FirmContext(user_id=7, firm_id=101, role="lawyer"))
        with self.assertRaises((AttributeError, TypeError)):
            result.firm_id = 202

    def test_rejects_firm_without_membership(self):
        with self.assertRaises(FirmContextError):
            resolve_firm_context(self.user, 303, self.lookup)

    def test_rejects_suspended_membership_even_if_role_is_admin(self):
        with self.assertRaises(FirmContextError):
            resolve_firm_context(self.user, 202, self.lookup)

    def test_cannot_substitute_another_users_membership(self):
        with self.assertRaises(FirmContextError):
            resolve_firm_context(self.user, 202, self.lookup)

    def test_rejects_missing_or_malformed_authenticated_identity(self):
        for identity in (None, {}, {"id": 0}, {"id": True}, {"id": "7"}):
            with self.subTest(identity=identity), self.assertRaises(FirmContextError):
                resolve_firm_context(identity, 101, self.lookup)

    def test_rejects_client_supplied_firm_id_shapes(self):
        for firm_id in (None, 0, -1, True, "101", 101.0):
            with self.subTest(firm_id=firm_id), self.assertRaises(FirmContextError):
                resolve_firm_context(self.user, firm_id, self.lookup)

    def test_rejects_unknown_role_even_if_membership_is_active(self):
        for role in ("owner", "platform_admin", "", None, 7):
            with self.subTest(role=role), self.assertRaises(FirmContextError):
                resolve_firm_context(
                    self.user, 101,
                    lambda user_id, firm_id, role=role: {"status": "active", "role": role},
                )

    def test_fails_closed_when_membership_backend_errors(self):
        def broken_lookup(user_id, firm_id):
            raise RuntimeError("database unavailable")
        with self.assertRaises(FirmContextError):
            resolve_firm_context(self.user, 101, broken_lookup)

    def test_sqlite_membership_lookup_uses_control_plane_status_and_firm_role(self):
        db = sqlite3.connect(":memory:")
        db.execute("PRAGMA foreign_keys=ON")
        try:
            apply_profile_migrations(db, "control_plane", MIGRATIONS)
            db.execute("INSERT INTO firms(id,name) VALUES(101,'Firm A'),(202,'Firm B')")
            db.execute(
                "INSERT INTO users(id,name,email_display,email_normalized,password_hash) VALUES(7,'Lawyer','lawyer@example.test','lawyer@example.test','hash')"
            )
            db.execute(
                "INSERT INTO firm_memberships(user_id,firm_id,firm_role,status) VALUES(7,101,'lawyer','active'),(7,202,'admin','suspended')"
            )
            lookup = sqlite_membership_lookup(db)
            self.assertEqual(lookup(7, 101), {"status": "active", "role": "lawyer"})
            self.assertEqual(lookup(7, 202), {"status": "suspended", "role": "admin"})
            self.assertIsNone(lookup(7, 303))
            self.assertEqual(
                resolve_firm_context({"id": 7}, 101, lookup),
                FirmContext(user_id=7, firm_id=101, role="lawyer"),
            )
            with self.assertRaises(FirmContextError):
                resolve_firm_context({"id": 7}, 202, lookup)
        finally:
            db.close()

    def test_suspended_firm_denies_even_active_membership(self):
        db = sqlite3.connect(":memory:")
        db.execute("PRAGMA foreign_keys=ON")
        try:
            apply_profile_migrations(db, "control_plane", MIGRATIONS)
            db.execute("INSERT INTO firms(id,name,status) VALUES(303,'Suspended Firm','suspended')")
            db.execute(
                "INSERT INTO users(id,name,email_display,email_normalized,password_hash) VALUES(7,'Lawyer','lawyer@example.test','lawyer@example.test','hash')"
            )
            db.execute(
                "INSERT INTO firm_memberships(user_id,firm_id,firm_role,status) VALUES(7,303,'admin','active')"
            )
            lookup = sqlite_membership_lookup(db)
            with self.assertRaises(FirmContextError):
                resolve_firm_context({"id": 7}, 303, lookup)
        finally:
            db.close()

    def test_disabled_global_identity_denies_active_membership(self):
        db = sqlite3.connect(":memory:")
        db.execute("PRAGMA foreign_keys=ON")
        try:
            apply_profile_migrations(db, "control_plane", MIGRATIONS)
            db.execute("INSERT INTO firms(id,name) VALUES(101,'Firm A')")
            db.execute(
                "INSERT INTO users(id,name,email_display,email_normalized,password_hash,status) VALUES(7,'Lawyer','lawyer@example.test','lawyer@example.test','hash','disabled')"
            )
            db.execute(
                "INSERT INTO firm_memberships(user_id,firm_id,firm_role,status) VALUES(7,101,'admin','active')"
            )
            lookup = sqlite_membership_lookup(db)
            with self.assertRaises(FirmContextError):
                resolve_firm_context({"id": 7}, 101, lookup)
        finally:
            db.close()

    def test_sqlite_membership_lookup_requires_a_trusted_sqlite_connection(self):
        with self.assertRaises(TypeError):
            sqlite_membership_lookup("/client/supplied/database.sqlite3")

    def test_fails_closed_on_malformed_membership(self):
        for membership in (None, {"status": "active"}, {"status": "active", "role": ""}):
            with self.subTest(membership=membership), self.assertRaises(FirmContextError):
                resolve_firm_context(self.user, 101, lambda user_id, firm_id: membership)


if __name__ == "__main__":
    unittest.main()
