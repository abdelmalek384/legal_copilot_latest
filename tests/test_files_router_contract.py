"""Document read-route ownership contract."""

import unittest

import app


class FilesRouterContractTests(unittest.TestCase):
    def test_document_review_and_chunk_reads_are_registered_from_files_router(self):
        expected = {
            "/cases/{cid}/docs/{document_id}/reviews": {"GET"},
            "/cases/{cid}/docs/{document_id}/chunks": {"GET"},
        }
        routes = {r.path: r for r in app.app.routes if getattr(r, "path", None) in expected}
        self.assertEqual(set(routes), set(expected))
        self.assertTrue(all(routes[p].methods == methods and routes[p].endpoint.__module__ == "routers.files" for p, methods in expected.items()))


if __name__ == "__main__":
    unittest.main()
