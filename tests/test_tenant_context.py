"""Security tests for trusted firm-context resolution."""
import unittest

from tenant_context import FirmContext, FirmContextError, resolve_firm_context


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

    def test_fails_closed_when_membership_backend_errors(self):
        def broken_lookup(user_id, firm_id):
            raise RuntimeError("database unavailable")
        with self.assertRaises(FirmContextError):
            resolve_firm_context(self.user, 101, broken_lookup)

    def test_fails_closed_on_malformed_membership(self):
        for membership in (None, {"status": "active"}, {"status": "active", "role": ""}):
            with self.subTest(membership=membership), self.assertRaises(FirmContextError):
                resolve_firm_context(self.user, 101, lambda user_id, firm_id: membership)


if __name__ == "__main__":
    unittest.main()
