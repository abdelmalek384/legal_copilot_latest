"""Platform router endpoint ownership contract."""

import unittest

import app


class PlatformRouterContractTests(unittest.TestCase):
    def test_metrics_and_payment_review_routes_are_registered_from_platform_router(self):
        expected = {
            ("/platform/pilot-metrics", "GET"),
            ("/platform/pilot-metrics/export.csv", "GET"),
            ("/platform/billing/payment-submissions", "GET"),
            ("/platform/billing/payment-submissions/{submission_id}/approve", "POST"),
            ("/platform/billing/payment-submissions/{submission_id}/reject", "POST"),
        }
        actual = {
            (route.path, method): route.endpoint.__module__
            for route in app.app.routes
            if getattr(route, "path", None) in {path for path, _ in expected}
            for method in getattr(route, "methods", set())
            if (route.path, method) in expected
        }
        self.assertEqual(set(actual), expected)
        self.assertTrue(all(module == "routers.platform" for module in actual.values()))


if __name__ == "__main__":
    unittest.main()
