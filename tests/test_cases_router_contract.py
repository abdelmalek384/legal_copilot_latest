"""Cases router ownership contract."""

import unittest

import app


class CasesRouterContractTests(unittest.TestCase):
    def test_case_list_and_search_are_registered_from_cases_router(self):
        expected = {"/cases": {"GET"}, "/cases/search": {"GET"}}
        routes = {r.path: r for r in app.app.routes if getattr(r, "path", None) in expected}
        self.assertEqual(set(routes), set(expected))
        self.assertTrue(all(routes[p].methods == methods and routes[p].endpoint.__module__ == "routers.cases" for p, methods in expected.items()))


if __name__ == "__main__":
    unittest.main()
