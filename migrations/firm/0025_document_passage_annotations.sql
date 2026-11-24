-- Persist lawyer-selected text highlights and notes inside the owning firm/matter/document.
CREATE TABLE document_passage_annotations (
  id INTEGER PRIMARY KEY,
  document_id INTEGER NOT NULL REFERENCES docs(id) ON DELETE CASCADE,
  case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
  firm_id INTEGER NOT NULL,
  chunk_id INTEGER NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
  created_by_user_id INTEGER NOT NULL,
  start_offset INTEGER NOT NULL CHECK(start_offset >= 0),
  end_offset INTEGER NOT NULL CHECK(end_offset > start_offset),
  selected_text TEXT NOT NULL CHECK(length(selected_text) BETWEEN 1 AND 2000),
  source_text_sha256 TEXT NOT NULL CHECK(length(source_text_sha256) = 64),
  note TEXT NOT NULL CHECK(length(note) BETWEEN 1 AND 2000),
  color TEXT NOT NULL DEFAULT 'yellow' CHECK(color IN ('yellow','blue','green','pink')),
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  deleted_at TEXT,
  deleted_by_user_id INTEGER
);

CREATE INDEX idx_document_passage_annotations_scope
  ON document_passage_annotations(firm_id,case_id,document_id,chunk_id,id);

CREATE TRIGGER document_passage_annotations_scope_insert
BEFORE INSERT ON document_passage_annotations
WHEN NOT EXISTS (
  SELECT 1 FROM docs d
  JOIN cases c ON c.id=d.case_id
  JOIN chunks ch ON ch.document_id=d.id AND ch.case_id=d.case_id
  WHERE d.id=NEW.document_id AND d.case_id=NEW.case_id
    AND c.firm_id=NEW.firm_id AND ch.id=NEW.chunk_id
)
BEGIN
  SELECT RAISE(ABORT, 'document passage annotation scope mismatch');
END;

CREATE TRIGGER document_passage_annotations_scope_update
BEFORE UPDATE ON document_passage_annotations
WHEN NOT EXISTS (
  SELECT 1 FROM docs d
  JOIN cases c ON c.id=d.case_id
  JOIN chunks ch ON ch.document_id=d.id AND ch.case_id=d.case_id
  WHERE d.id=NEW.document_id AND d.case_id=NEW.case_id
    AND c.firm_id=NEW.firm_id AND ch.id=NEW.chunk_id
)
BEGIN
  SELECT RAISE(ABORT, 'document passage annotation scope mismatch');
END;

-- Annotation content is immutable. The only permitted update is one soft-delete transition.
CREATE TRIGGER document_passage_annotations_immutable
BEFORE UPDATE ON document_passage_annotations
WHEN NOT (
  NEW.id=OLD.id
  AND NEW.document_id=OLD.document_id
  AND NEW.case_id=OLD.case_id
  AND NEW.firm_id=OLD.firm_id
  AND NEW.chunk_id=OLD.chunk_id
  AND NEW.created_by_user_id=OLD.created_by_user_id
  AND NEW.start_offset=OLD.start_offset
  AND NEW.end_offset=OLD.end_offset
  AND NEW.selected_text=OLD.selected_text
  AND NEW.source_text_sha256=OLD.source_text_sha256
  AND NEW.note=OLD.note
  AND NEW.color=OLD.color
  AND NEW.created_at=OLD.created_at
  AND OLD.deleted_at IS NULL
  AND NEW.deleted_at IS NOT NULL
  AND NEW.deleted_by_user_id IS NOT NULL
)
BEGIN
  SELECT RAISE(ABORT, 'document passage annotations are immutable except for soft deletion');
END;

-- Prevent bypassing the audited soft-delete route with direct SQL DELETE.
-- Parent-driven retention cascades remain possible after the owning row disappears.
CREATE TRIGGER document_passage_annotations_no_physical_delete
BEFORE DELETE ON document_passage_annotations
WHEN EXISTS (SELECT 1 FROM docs WHERE id=OLD.document_id)
 AND EXISTS (SELECT 1 FROM cases WHERE id=OLD.case_id)
 AND EXISTS (SELECT 1 FROM chunks WHERE id=OLD.chunk_id)
BEGIN
  SELECT RAISE(ABORT, 'document passage annotations require soft deletion');
END;
