import unittest
from datetime import datetime, timedelta, timezone

from tools.subscription_policy import (
    PlanPolicy,
    can_transition_subscription,
    evaluate_subscription_status,
    seat_capacity_available,
    trial_end_at,
    validate_transfer_reference,
)


class SubscriptionPolicyTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)

    def test_plan_limits_are_explicit_and_validated(self):
        plan = PlanPolicy("solo", seat_limit=1, trial_days=14)
        self.assertEqual(plan.seat_limit, 1)
        self.assertEqual(plan.trial_days, 14)
        with self.assertRaises(ValueError):
            PlanPolicy("solo", seat_limit=0, trial_days=14)
        with self.assertRaises(ValueError):
            PlanPolicy("enterprise", seat_limit=20, trial_days=14)

    def test_trial_end_and_expiry_boundaries(self):
        end = trial_end_at(self.now, 14)
        self.assertEqual(end, self.now + timedelta(days=14))
        self.assertEqual(
            evaluate_subscription_status("trialing", self.now, trial_ends_at=end),
            "trialing",
        )
        self.assertEqual(
            evaluate_subscription_status("trialing", end, trial_ends_at=end),
            "expired",
        )
        with self.assertRaises(ValueError):
            trial_end_at(self.now.replace(tzinfo=None), 14)

    def test_active_subscription_becomes_past_due_at_paid_through(self):
        paid_through = self.now + timedelta(days=1)
        self.assertEqual(
            evaluate_subscription_status("active", self.now, paid_through=paid_through),
            "active",
        )
        self.assertEqual(
            evaluate_subscription_status("active", paid_through, paid_through=paid_through),
            "past_due",
        )

    def test_seat_capacity_enforces_configured_limit(self):
        self.assertTrue(seat_capacity_available(0, 1))
        self.assertFalse(seat_capacity_available(1, 1))
        self.assertTrue(seat_capacity_available(3, 5, 2))
        self.assertFalse(seat_capacity_available(4, 5, 2))
        with self.assertRaises(ValueError):
            seat_capacity_available(-1, 5)

    def test_subscription_transition_graph(self):
        self.assertTrue(can_transition_subscription("trialing", "pending_payment"))
        self.assertTrue(can_transition_subscription("pending_payment", "active"))
        self.assertTrue(can_transition_subscription("past_due", "active"))
        self.assertFalse(can_transition_subscription("canceled", "active"))
        self.assertFalse(can_transition_subscription("active", "trialing"))

    def test_transfer_reference_validation_rejects_credentials_and_controls(self):
        self.assertEqual(validate_transfer_reference("  InstaPay-2026/ABC123  "), "InstaPay-2026/ABC123")
        for value in ("", "abc", "123456\nInjected", "account number 123456", "123456 "):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_transfer_reference(value)


if __name__ == "__main__":
    unittest.main()
