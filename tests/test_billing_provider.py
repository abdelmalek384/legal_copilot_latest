import unittest

from tools.billing_provider import FakeBillingProvider


class FakeBillingProviderTests(unittest.TestCase):
    def setUp(self):
        self.provider = FakeBillingProvider()

    def test_creates_pending_request_in_integer_minor_units(self):
        request = self.provider.create_payment_request(
            merchant_reference="FIRM-7-2026-11",
            amount_minor=12500,
            currency="egp",
            metadata={"firm_id": "7", "plan": "solo"},
        )
        self.assertEqual(request.status, "pending")
        self.assertEqual(request.amount_minor, 12500)
        self.assertEqual(request.currency, "EGP")
        self.assertEqual(self.provider.get_payment_request(request.provider_reference), request)

    def test_fake_confirmation_changes_only_pending_request(self):
        request = self.provider.create_payment_request(
            merchant_reference="SUB-42", amount_minor=9900, currency="EGP"
        )
        paid = self.provider.mark_paid_for_test(request.provider_reference)
        self.assertEqual(paid.status, "paid")
        self.assertEqual(self.provider.get_payment_request(request.provider_reference).status, "paid")
        with self.assertRaises(ValueError):
            self.provider.mark_paid_for_test(request.provider_reference)

    def test_rejects_invalid_amount_currency_and_reference(self):
        invalid = (
            {"merchant_reference": "", "amount_minor": 100, "currency": "EGP"},
            {"merchant_reference": "x", "amount_minor": 0, "currency": "EGP"},
            {"merchant_reference": "x", "amount_minor": True, "currency": "EGP"},
            {"merchant_reference": "x", "amount_minor": 100, "currency": "EG"},
        )
        for kwargs in invalid:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.provider.create_payment_request(**kwargs)

    def test_rejects_cardholder_fields_in_metadata(self):
        with self.assertRaises(ValueError):
            self.provider.create_payment_request(
                merchant_reference="SUB-43",
                amount_minor=9900,
                currency="EGP",
                metadata={"card_number": "4111111111111111"},
            )

    def test_unknown_reference_is_not_found(self):
        self.assertIsNone(self.provider.get_payment_request("fake_missing"))
        with self.assertRaises(KeyError):
            self.provider.mark_paid_for_test("fake_missing")


if __name__ == "__main__":
    unittest.main()
