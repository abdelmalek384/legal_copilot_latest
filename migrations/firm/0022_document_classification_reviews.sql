-- Persistent, append-only human classification decisions for firm-owned case documents.
CREATE TABLE document_classification_reviews (
  id INTEGER PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES docs(id) ON DELETE CASCADE,
  case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  firm_id INTEGER NOT NULL,
  reviewer_user_id INTEGER NOT NULL,
  category TEXT NOT NULL CHECK(category IN (
    'unclassified','court_judgment','contract','pleading','correspondence','evidence_or_receipt'
  )),
  suggested_category TEXT NOT NULL CHECK(suggested_category IN (
    'unclassified','court_judgment','contract','pleading','correspondence','evidence_or_receipt'
  )),
  matched_terms_json TEXT NOT NULL DEFAULT '[]',
  note TEXT NOT NULL DEFAULT '' CHECK(length(note) <= 2000),
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX document_classification_reviews_scope_idx
  ON document_classification_reviews(firm_id,case_id,document_id,id DESC);

CREATE TRIGGER document_classification_reviews_scope_insert
BEFORE INSERT ON document_classification_reviews
WHEN NOT EXISTS (
  SELECT 1 FROM docs d
  JOIN cases c ON c.id=d.case_id
  JOIN tenant_database_binding b ON b.singleton=1
  WHERE d.id=NEW.document_id
    AND d.case_id=NEW.case_id
    AND d.firm_id=NEW.firm_id
    AND c.firm_id=NEW.firm_id
    AND b.firm_id=NEW.firm_id
)
BEGIN
  SELECT RAISE(ABORT, 'document classification scope mismatch');
END;

CREATE TRIGGER document_classification_reviews_no_update
BEFORE UPDATE ON document_classification_reviews
BEGIN
  SELECT RAISE(ABORT, 'document classification reviews are append-only');
END;
