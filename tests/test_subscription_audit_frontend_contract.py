"""Contract checks for the firm subscription audit timeline."""
import unittest
from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / "static" / "index.html").read_text(encoding="utf-8")


class SubscriptionAuditFrontendContractTests(unittest.TestCase):
    def test_billing_ui_renders_subscription_activity_in_arabic_and_english(self):
        self.assertIn("Subscription activity history", HTML)
        self.assertIn("سجل نشاط الاشتراك", HTML)
        self.assertIn("data.subscription_events", HTML)
        self.assertIn("payment_approved", HTML)
        self.assertIn("payment_rejected", HTML)
        self.assertIn("actor_name", HTML)


if __name__ == "__main__":
    unittest.main()
