-- Persistent, append-only lawyer annotations anchored to a precise extracted-text version.
CREATE TABLE document_annotations(
 id INTEGER PRIMARY KEY,
 document_id INTEGER NOT NULL REFERENCES docs(id) ON DELETE CASCADE,
 case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
 firm_id INTEGER NOT NULL,
 chunk_id INTEGER NOT NULL,
 author_user_id INTEGER NOT NULL,
 annotation_type TEXT NOT NULL CHECK(annotation_type IN ('highlight','note')),
 start_offset INTEGER NOT NULL CHECK(start_offset >= 0),
 end_offset INTEGER NOT NULL CHECK(end_offset > start_offset),
 quoted_text TEXT NOT NULL CHECK(length(quoted_text) BETWEEN 1 AND 2000),
 body TEXT NOT NULL DEFAULT '' CHECK(length(body) <= 5000),
 page_reference TEXT NOT NULL DEFAULT '' CHECK(length(page_reference) <= 100),
 text_sha256 TEXT NOT NULL CHECK(length(text_sha256)=64),
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_document_annotations_scope
 ON document_annotations(firm_id,case_id,document_id,chunk_id,id DESC);
CREATE TABLE document_annotation_events(
 id INTEGER PRIMARY KEY,
 annotation_id INTEGER NOT NULL REFERENCES document_annotations(id) ON DELETE CASCADE,
 firm_id INTEGER NOT NULL,
 case_id INTEGER NOT NULL,
 document_id INTEGER NOT NULL,
 actor_user_id INTEGER NOT NULL,
 action TEXT NOT NULL CHECK(action='created'),
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_document_annotation_events_annotation
 ON document_annotation_events(firm_id,annotation_id,id DESC);

-- Validate all three parent links and the immutable tenant binding at write time.
CREATE TRIGGER document_annotations_scope_insert
BEFORE INSERT ON document_annotations
WHEN NOT EXISTS (
 SELECT 1 FROM docs d
 JOIN cases c ON c.id=d.case_id
 JOIN chunks ch ON ch.id=NEW.chunk_id
 JOIN tenant_database_binding b ON b.singleton=1
 WHERE d.id=NEW.document_id AND d.case_id=NEW.case_id
 AND ch.document_id=NEW.document_id AND ch.case_id=NEW.case_id
 AND d.firm_id=NEW.firm_id AND c.firm_id=NEW.firm_id
 AND b.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'document annotation scope mismatch'); END;
CREATE TRIGGER document_annotations_no_update
BEFORE UPDATE ON document_annotations
BEGIN SELECT RAISE(ABORT, 'document annotations are append-only'); END;

CREATE TRIGGER document_annotation_events_scope_insert
BEFORE INSERT ON document_annotation_events
WHEN NOT EXISTS (
 SELECT 1 FROM document_annotations a
 JOIN tenant_database_binding b ON b.singleton=1
 WHERE a.id=NEW.annotation_id AND a.firm_id=NEW.firm_id
 AND a.case_id=NEW.case_id AND a.document_id=NEW.document_id
 AND b.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'document annotation event scope mismatch'); END;
CREATE TRIGGER document_annotation_events_no_update
BEFORE UPDATE ON document_annotation_events
BEGIN SELECT RAISE(ABORT, 'document annotation events are append-only'); END;

CREATE TRIGGER document_annotations_tenant_firm_insert
BEFORE INSERT ON document_annotations
WHEN NOT EXISTS (
 SELECT 1 FROM tenant_database_binding b
 WHERE b.singleton=1 AND b.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'document annotation tenant mismatch'); END;
CREATE TRIGGER document_annotation_events_tenant_firm_insert
BEFORE INSERT ON document_annotation_events
WHEN NOT EXISTS (
 SELECT 1 FROM tenant_database_binding b
 WHERE b.singleton=1 AND b.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'document annotation event tenant mismatch'); END;
