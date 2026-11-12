"""Contract checks for persistent matter document classifications."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DocumentClassificationContractTests(unittest.TestCase):
    def test_firm_migration_creates_versioned_current_state_and_append_only_events(self):
        migration = (ROOT / "migrations" / "firm" / "0002_document_classifications.sql").read_text(encoding="utf-8")
        self.assertIn("REFERENCES docs(id) ON DELETE CASCADE", migration)
        self.assertIn("REFERENCES cases(id) ON DELETE CASCADE", migration)
        self.assertIn("CHECK(category IN", migration)
        self.assertIn("document_classification_events", migration)
        self.assertIn("idx_document_classification_events_document", migration)

    def test_api_is_matter_scoped_lead_only_and_optimistic(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('@app.get("/cases/{cid}/docs/{document_id}/classification")', app)
        self.assertIn('@app.put("/cases/{cid}/docs/{document_id}/classification")', app)
        self.assertIn("need(c, u, cid, lead=True)", app)
        self.assertIn("body.expected_version != current_version", app)
        self.assertIn("expected_version", app)
        self.assertIn("document_classification_events", app)
        self.assertIn('"document_classifications.csv"', app)
        self.assertIn('"document_classification_events.csv"', app)
        self.assertIn("ON CONFLICT(document_id) DO NOTHING", app)

    def test_ui_loads_saved_classification_and_disables_unauthorized_edits(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        self.assertIn("classification=await api('/cases/'+caseId+'/docs/'+doc.document_id+'/classification')", html)
        self.assertIn("item.classification.can_edit===true", html)
        self.assertIn("classification','PUT'", html)
        self.assertIn("expected_version:persisted?persisted.version:0", html)
        self.assertIn("Classification change history", html)


if __name__ == "__main__":
    unittest.main()
