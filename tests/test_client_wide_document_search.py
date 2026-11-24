"""Contract checks for client-scoped document intelligence search."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ClientWideDocumentSearchTests(unittest.TestCase):
    def test_text_search_accepts_client_filter_without_bypassing_matter_access(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        endpoint = app[
            app.index("def search_accessible_document_text("):
            app.index('@app.get("/documents/search")')
        ]
        self.assertIn("client_id: int | None = Query(default=None, ge=1)", endpoint)
        self.assertIn("AND (? IS NULL OR cs.client_id=?)", endpoint)
        self.assertIn("m.case_id=cs.id AND m.user_id=?", endpoint)
        self.assertIn("cs.firm_id=?", endpoint)
        self.assertIn("client_id, client_id", endpoint)

    def test_documents_workspace_offers_authorized_client_scoped_search(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        page = html[html.index("async function documentsPage(){"):html.index("\nasync function law(){")]
        self.assertIn("Limit search to a selected client", page)
        self.assertIn("api('/clients')", page)
        self.assertIn("searchParams.set('client_id',clientSearchFilter.value)", page)
        self.assertIn("clientSearchFilter.onchange", page)
