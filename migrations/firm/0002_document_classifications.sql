-- Persistent, matter-scoped document classification with an append-only audit trail.
CREATE TABLE document_classifications(
  document_id INTEGER PRIMARY KEY REFERENCES docs(id) ON DELETE CASCADE,
  case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  firm_id INTEGER NOT NULL,
  category TEXT NOT NULL CHECK(category IN ('unclassified','court_judgment','contract','pleading','correspondence','evidence_or_receipt')),
  version INTEGER NOT NULL DEFAULT 1 CHECK(version > 0),
  updated_by_user_id INTEGER NOT NULL,
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE document_classification_events(
  id INTEGER PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES docs(id) ON DELETE CASCADE,
  case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  firm_id INTEGER NOT NULL,
  actor_user_id INTEGER NOT NULL,
  previous_category TEXT,
  new_category TEXT NOT NULL CHECK(new_category IN ('unclassified','court_judgment','contract','pleading','correspondence','evidence_or_receipt')),
  version INTEGER NOT NULL,
  note TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(document_id,version)
);
CREATE TRIGGER document_classification_events_no_update BEFORE UPDATE ON document_classification_events
BEGIN SELECT RAISE(ABORT, 'document classification events are append-only'); END;
CREATE TRIGGER document_classification_events_no_delete BEFORE DELETE ON document_classification_events
BEGIN SELECT RAISE(ABORT, 'document classification events are append-only'); END;
CREATE INDEX idx_document_classifications_case ON document_classifications(firm_id,case_id);
CREATE INDEX idx_document_classification_events_document ON document_classification_events(firm_id,document_id,id DESC);
