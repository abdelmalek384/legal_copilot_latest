"""Cases router ownership contract."""

import unittest

import app


class CasesRouterContractTests(unittest.TestCase):
    def test_case_session_and_note_write_routes_are_registered_from_cases_router(self):
        expected = {
            ("/cases/{cid}/sessions", "POST"),
            ("/cases/{cid}/notes", "POST"),
        }
        actual = {
            (route.path, method): route.endpoint.__module__
            for route in app.app.routes
            if getattr(route, "path", None) in {path for path, _ in expected}
            for method in getattr(route, "methods", set())
            if (route.path, method) in expected
        }
        self.assertEqual(set(actual), expected)
        self.assertTrue(all(module == "routers.cases" for module in actual.values()))

    def test_case_read_and_update_routes_are_registered_from_cases_router(self):
        expected = {
            ("/cases", "GET"),
            ("/cases/{cid}", "PATCH"),
            ("/cases/{cid}/members", "POST"),
            ("/cases/{cid}/members/{uid}", "DELETE"),
            ("/cases", "POST"),
            ("/cases/search", "GET"),
            ("/cases/{cid}", "GET"),
            ("/cases/{cid}/draft-skeleton", "GET"),
            ("/cases/{cid}/communications", "GET"),
            ("/cases/{cid}/communications", "POST"),
        }
        actual = {
            (route.path, method): route.endpoint.__module__
            for route in app.app.routes
            if getattr(route, "path", None) in {path for path, _ in expected}
            for method in getattr(route, "methods", set())
            if (route.path, method) in expected
        }
        self.assertEqual(set(actual), expected)
        self.assertTrue(all(module == "routers.cases" for module in actual.values()))


if __name__ == "__main__":
    unittest.main()
