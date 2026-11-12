-- Firm-local approved document labels with immutable reviewer attribution.
CREATE TABLE document_classifications (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL UNIQUE REFERENCES docs(id) ON DELETE RESTRICT,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    firm_id INTEGER NOT NULL CHECK(firm_id > 0),
    category TEXT NOT NULL CHECK(category IN (
        'unclassified','court_judgment','contract','pleading',
        'correspondence','evidence_or_receipt'
    )),
    updated_by_user_id INTEGER NOT NULL CHECK(updated_by_user_id > 0),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX document_classifications_matter_idx
    ON document_classifications(firm_id, case_id, updated_at DESC);

CREATE TABLE document_classification_events (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES docs(id) ON DELETE RESTRICT,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    firm_id INTEGER NOT NULL CHECK(firm_id > 0),
    actor_user_id INTEGER NOT NULL CHECK(actor_user_id > 0),
    event_type TEXT NOT NULL CHECK(event_type IN ('created','updated')),
    previous_category TEXT CHECK(previous_category IS NULL OR previous_category IN (
        'unclassified','court_judgment','contract','pleading',
        'correspondence','evidence_or_receipt'
    )),
    new_category TEXT NOT NULL CHECK(new_category IN (
        'unclassified','court_judgment','contract','pleading',
        'correspondence','evidence_or_receipt'
    )),
    note TEXT NOT NULL DEFAULT '' CHECK(length(note) <= 1000),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK((event_type = 'created' AND previous_category IS NULL)
       OR (event_type = 'updated' AND previous_category IS NOT NULL))
);

CREATE INDEX document_classification_events_document_idx
    ON document_classification_events(firm_id, document_id, id DESC);

CREATE TRIGGER document_classifications_tenant_insert
BEFORE INSERT ON document_classifications
WHEN NOT EXISTS (
    SELECT 1 FROM tenant_database_binding b
    JOIN docs d ON d.id=NEW.document_id
    JOIN cases c ON c.id=NEW.case_id
    WHERE b.singleton=1 AND b.firm_id=NEW.firm_id
      AND d.firm_id=NEW.firm_id AND d.case_id=NEW.case_id
      AND c.firm_id=NEW.firm_id
)
BEGIN
    SELECT RAISE(ABORT, 'document classification belongs to a different firm or matter');
END;

CREATE TRIGGER document_classifications_tenant_update
BEFORE UPDATE ON document_classifications
WHEN NOT EXISTS (
    SELECT 1 FROM tenant_database_binding b
    JOIN docs d ON d.id=NEW.document_id
    JOIN cases c ON c.id=NEW.case_id
    WHERE b.singleton=1 AND b.firm_id=NEW.firm_id
      AND d.firm_id=NEW.firm_id AND d.case_id=NEW.case_id
      AND c.firm_id=NEW.firm_id
)
BEGIN
    SELECT RAISE(ABORT, 'document classification belongs to a different firm or matter');
END;

CREATE TRIGGER document_classifications_no_delete
BEFORE DELETE ON document_classifications
BEGIN
    SELECT RAISE(ABORT, 'document classifications must be retained with their audit history');
END;

CREATE TRIGGER document_classification_events_tenant_insert
BEFORE INSERT ON document_classification_events
WHEN NOT EXISTS (
    SELECT 1 FROM tenant_database_binding b
    JOIN docs d ON d.id=NEW.document_id
    JOIN cases c ON c.id=NEW.case_id
    WHERE b.singleton=1 AND b.firm_id=NEW.firm_id
      AND d.firm_id=NEW.firm_id AND d.case_id=NEW.case_id
      AND c.firm_id=NEW.firm_id
)
BEGIN
    SELECT RAISE(ABORT, 'document classification event belongs to a different firm or matter');
END;

CREATE TRIGGER document_classification_events_no_update
BEFORE UPDATE ON document_classification_events
BEGIN
    SELECT RAISE(ABORT, 'document classification events are immutable');
END;

CREATE TRIGGER document_classification_events_no_delete
BEFORE DELETE ON document_classification_events
BEGIN
    SELECT RAISE(ABORT, 'document classification events are immutable');
END;
