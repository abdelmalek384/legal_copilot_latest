"""Contract checks for persistent matter document classifications."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DocumentClassificationContractTests(unittest.TestCase):
    def test_firm_migration_creates_versioned_current_state_and_append_only_events(self):
        migration = (ROOT / "migrations" / "firm" / "0014_document_classifications.sql").read_text(encoding="utf-8")
        self.assertIn("REFERENCES docs(id) ON DELETE CASCADE", migration)
        self.assertIn("REFERENCES cases(id) ON DELETE CASCADE", migration)
        self.assertIn("CHECK(category IN", migration)
        self.assertIn("document_classification_events", migration)
        self.assertIn("UNIQUE(document_id,version)", migration)
        self.assertIn("idx_document_classification_events_document", migration)

    def test_api_is_matter_scoped_lead_only_and_optimistic(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('@app.get("/cases/{cid}/docs/{document_id}/classification")', app)
        self.assertIn('@app.put("/cases/{cid}/docs/{document_id}/classification")', app)
        self.assertIn("need(c, u, cid, lead=True)", app)
        self.assertIn("body.expected_version != current_version", app)
        self.assertIn("expected_version", app)
        self.assertIn("document_classification_events", app)
        self.assertIn("actor_ids = sorted({int(row[\"actor_user_id\"]) for row in events})", app)
        self.assertIn("item[\"actor_name\"] = names.get", app)
        self.assertIn("item[\"reviewer_name\"] = names.get", app)
        self.assertIn("control_conn().execute", app)
        self.assertIn('"document_classifications.csv"', app)
        self.assertIn('"document_classification_events.csv"', app)
        self.assertIn("ON CONFLICT(document_id) DO NOTHING", app)

    def test_ui_loads_saved_classification_and_disables_unauthorized_edits(self):
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        self.assertIn("const [data,classification]=await Promise.all([api('/cases/'+caseId+'/docs/'+doc.document_id+'/chunks'),api('/cases/'+caseId+'/docs/'+doc.document_id+'/classification').catch(()=>null)])", html)
        self.assertIn("item.classification.can_edit===true", html)
        self.assertIn("classification','PUT'", html)
        self.assertIn("expected_version:persisted?persisted.version:0", html)
        self.assertIn("Classification change history", html)


    def test_case_document_listing_includes_saved_classification_without_cross_case_join(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("dc.category AS saved_classification", app)
        self.assertIn("dc.case_id=d.case_id AND dc.firm_id=c.firm_id", app)
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        self.assertIn("doc.saved_classification", html)
        self.assertIn("No saved classification", html)

    def test_document_library_only_offers_download_for_retained_ready_originals(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("original_available_expr", app)
        self.assertIn("if _separate_runtime_enabled() else \"0\"", app)
        self.assertIn("o.state='ready' AND o.purged_at IS NULL", app)
        html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
        self.assertIn("doc.original_available", html)
        self.assertIn("'/docs/'+doc.document_id+'/original'", html)

    def test_classification_migration_follows_existing_firm_migration_sequence(self):
        migrations = sorted(path.name for path in (ROOT / "migrations" / "firm").glob("*.sql"))
        self.assertIn("0013_original_file_deletion_workflow.sql", migrations)
        self.assertIn("0014_document_classifications.sql", migrations)
        self.assertNotIn("0002_document_classifications.sql", migrations)

    def test_integrity_migration_guards_scope_and_makes_audit_events_immutable(self):
        migration = (ROOT / "migrations" / "firm" / "0015_document_classification_integrity.sql").read_text(encoding="utf-8")
        for trigger in (
            "document_classifications_scope_insert",
            "document_classifications_scope_update",
            "document_classification_events_scope_insert",
            "document_classification_events_no_update",
            "document_classification_events_no_delete",
        ):
            self.assertIn(trigger, migration)
        self.assertIn("classification audit event does not match current state", migration)
        self.assertIn("document classification audit events are immutable", migration)

    def test_legacy_schema_has_equivalent_classification_integrity_guards(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("CREATE TRIGGER IF NOT EXISTS document_classifications_scope_insert", app)
        self.assertIn("CREATE TRIGGER IF NOT EXISTS document_classification_events_no_update", app)
        self.assertIn("CREATE TRIGGER IF NOT EXISTS document_classification_events_no_delete", app)

if __name__ == "__main__":
    unittest.main()
