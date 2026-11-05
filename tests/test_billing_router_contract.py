"""Billing route ownership contract."""

import unittest

import app


class BillingRouterContractTests(unittest.TestCase):
    def test_firm_billing_routes_are_registered_from_billing_router(self):
        expected = {
            ("/billing", "GET"),
            ("/billing/subscribe", "POST"),
            ("/billing/payment-submissions", "POST"),
            ("/invoices/{invoice_id}", "GET"),
            ("/invoices/{invoice_id}", "PUT"),
            ("/invoices/{invoice_id}/issue", "POST"),
            ("/invoices/{invoice_id}/payments", "POST"),
            ("/invoices/{invoice_id}/void", "POST"),
            ("/invoices/{invoice_id}/payments/{payment_id}/receipt", "GET"),
            ("/invoices/{invoice_id}/print", "GET"),
        }
        actual = {
            (route.path, method): route.endpoint.__module__
            for route in app.app.routes
            if getattr(route, "path", None) in {path for path, _ in expected}
            for method in getattr(route, "methods", set())
            if (route.path, method) in expected
        }
        self.assertEqual(set(actual), expected)
        self.assertTrue(all(module == "routers.billing" for module in actual.values()))


if __name__ == "__main__":
    unittest.main()
