-- Enforce matter/document consistency and append-only classification audit history.
CREATE TRIGGER document_classifications_scope_insert
BEFORE INSERT ON document_classifications
WHEN NOT EXISTS (
  SELECT 1 FROM docs d JOIN cases c ON c.id=d.case_id
  WHERE d.id=NEW.document_id AND d.case_id=NEW.case_id AND c.firm_id=NEW.firm_id
)
BEGIN
  SELECT RAISE(ABORT, 'document classification scope mismatch');
END;

CREATE TRIGGER document_classifications_scope_update
BEFORE UPDATE ON document_classifications
WHEN NOT EXISTS (
  SELECT 1 FROM docs d JOIN cases c ON c.id=d.case_id
  WHERE d.id=NEW.document_id AND d.case_id=NEW.case_id AND c.firm_id=NEW.firm_id
)
BEGIN
  SELECT RAISE(ABORT, 'document classification scope mismatch');
END;

CREATE TRIGGER document_classification_events_scope_insert
BEFORE INSERT ON document_classification_events
WHEN NOT EXISTS (
  SELECT 1 FROM document_classifications dc
  JOIN docs d ON d.id=dc.document_id AND d.case_id=dc.case_id
  JOIN cases c ON c.id=d.case_id
  WHERE dc.document_id=NEW.document_id
    AND dc.case_id=NEW.case_id
    AND dc.firm_id=NEW.firm_id
    AND c.firm_id=NEW.firm_id
    AND dc.category=NEW.new_category
    AND dc.version=NEW.version
)
BEGIN
  SELECT RAISE(ABORT, 'classification audit event does not match current state');
END;

CREATE TRIGGER document_classification_events_no_update
BEFORE UPDATE ON document_classification_events
BEGIN
  SELECT RAISE(ABORT, 'document classification audit events are immutable');
END;

CREATE TRIGGER document_classification_events_no_delete
BEFORE DELETE ON document_classification_events
BEGIN
  SELECT RAISE(ABORT, 'document classification audit events are immutable');
END;
