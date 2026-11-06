"""Server-side case search and pagination tests."""
import unittest

from tests.invoice_test_support import InvoiceTestSupport


class CaseSearchPaginationTests(InvoiceTestSupport, unittest.TestCase):
    def test_admin_search_filters_and_paginates_without_duplicate_rows(self):
        for index in range(3):
            response = self.mutate(
                self.client_a, "post", "/cases",
                json={
                    "title": f"Pagination Matter {index}",
                    "client": "Pagination Client",
                    "case_number": f"PX-{index:03d}",
                    "case_year": "2026",
                    "court": "Cairo Court",
                    "opposing_party": f"Opposing Party {index}",
                },
            )
            self.assertEqual(response.status_code, 200, response.text)

        first = self.client_a.get("/cases/search", params={"limit": 2, "offset": 0})
        second = self.client_a.get("/cases/search", params={"limit": 2, "offset": 2})
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(second.status_code, 200, second.text)
        self.assertEqual(first.json()["total"], 4)
        self.assertEqual(second.json()["total"], 4)
        self.assertEqual(len(first.json()["items"]), 2)
        self.assertEqual(len(second.json()["items"]), 2)
        first_ids = {row["id"] for row in first.json()["items"]}
        second_ids = {row["id"] for row in second.json()["items"]}
        self.assertFalse(first_ids & second_ids)
        self.assertEqual(len(first_ids | second_ids), 4)

        by_title = self.client_a.get(
            "/cases/search", params={"q": "Pagination Matter 1", "limit": 50}
        )
        self.assertEqual(by_title.json()["total"], 1)
        self.assertEqual(by_title.json()["items"][0]["title"], "Pagination Matter 1")
        by_opponent = self.client_a.get(
            "/cases/search", params={"q": "Opposing Party 2"}
        )
        self.assertEqual(by_opponent.json()["total"], 1)
        self.assertEqual(by_opponent.json()["items"][0]["case_number"], "PX-002")

        self.assertEqual(self.client_a.get("/cases/search", params={"status": "closed"}).json()["total"], 0)
        self.assertEqual(self.client_a.get("/cases/search", params={"q": "%"}).json()["total"], 0)
        self.assertEqual(
            self.client_a.get("/cases/search", params={"q": "%' OR 1=1 --"}).json()["total"], 0
        )
        self.assertEqual(self.client_a.get("/cases/search", params={"status": "invalid"}).status_code, 422)

    def test_search_respects_firm_and_case_membership_boundaries(self):
        self.mutate(
            self.client_a, "post", "/cases",
            json={"title": "Firm A confidential matter", "client": "Client A"},
        )
        firm_b = self.client_b.get(
            "/cases/search", params={"q": "Firm A confidential matter"}
        )
        nonmember = self.client_nonmember.get(
            "/cases/search", params={"q": "Invoice matter"}
        )
        self.assertEqual(firm_b.status_code, 200, firm_b.text)
        self.assertEqual(firm_b.json()["total"], 0)
        self.assertEqual(firm_b.json()["items"], [])
        self.assertEqual(nonmember.status_code, 200, nonmember.text)
        self.assertEqual(nonmember.json()["total"], 0)
        self.assertEqual(nonmember.json()["items"], [])

    def test_search_enforces_page_bounds(self):
        for params in ({"limit": 0}, {"limit": 101}, {"offset": -1}, {"offset": 100001}):
            response = self.client_a.get("/cases/search", params=params)
            self.assertEqual(response.status_code, 422, (params, response.text))


if __name__ == "__main__":
    unittest.main()
