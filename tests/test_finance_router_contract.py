"""Behavior-neutral router ownership contract for the finance overview route."""

import unittest

import app


class FinanceRouterContractTests(unittest.TestCase):
    def test_finance_overview_is_registered_from_finance_router(self):
        routes = [
            route for route in app.app.routes
            if getattr(route, "path", None) == "/finance/overview"
        ]
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0].methods, {"GET"})
        self.assertEqual(routes[0].endpoint.__module__, "routers.finance")
        invoice_overview = [
            route for route in app.app.routes
            if getattr(route, "path", None) == "/finance/invoices/overview"
        ]
        self.assertEqual(len(invoice_overview), 1)
        self.assertEqual(invoice_overview[0].endpoint.__module__, "routers.finance")
        fee_route = next(
            route for route in app.app.routes
            if getattr(route, "path", None) == "/cases/{cid}/fees"
            and "POST" in getattr(route, "methods", set())
        )
        self.assertEqual(fee_route.endpoint.__module__, "routers.finance")


if __name__ == "__main__":
    unittest.main()
