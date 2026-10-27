-- Original binary metadata belongs to the isolated firm database.
-- Blob objects are not stored in the shared legal corpus.
CREATE TABLE original_file_objects (
    object_id TEXT PRIMARY KEY CHECK(length(object_id) = 32),
    document_id INTEGER NOT NULL UNIQUE REFERENCES docs(id) ON DELETE RESTRICT,
    firm_id INTEGER NOT NULL CHECK(firm_id > 0),
    storage_backend TEXT NOT NULL CHECK(storage_backend IN ('local')),
    sha256 TEXT NOT NULL CHECK(length(sha256) = 64),
    byte_size INTEGER NOT NULL CHECK(byte_size >= 0),
    content_type TEXT NOT NULL DEFAULT 'application/octet-stream',
    state TEXT NOT NULL DEFAULT 'staged' CHECK(state IN ('staged','ready','quarantined')),
    legal_hold INTEGER NOT NULL DEFAULT 0 CHECK(legal_hold IN (0,1)),
    hold_reason TEXT,
    hold_set_by INTEGER,
    hold_set_at TEXT,
    hold_released_by INTEGER,
    hold_released_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK(legal_hold = 0 OR (hold_reason IS NOT NULL AND length(trim(hold_reason)) > 0))
);

CREATE INDEX original_file_objects_state_idx
    ON original_file_objects(state, created_at);

CREATE TRIGGER original_file_objects_tenant_insert
BEFORE INSERT ON original_file_objects
WHEN NOT EXISTS (
    SELECT 1 FROM tenant_database_binding b
    JOIN docs d ON d.id = NEW.document_id
    WHERE b.singleton = 1
      AND b.firm_id = NEW.firm_id
      AND d.firm_id = NEW.firm_id
)
BEGIN
    SELECT RAISE(ABORT, 'original file object belongs to a different firm');
END;

CREATE TRIGGER original_file_objects_tenant_update
BEFORE UPDATE OF firm_id, document_id ON original_file_objects
WHEN NOT EXISTS (
    SELECT 1 FROM tenant_database_binding b
    JOIN docs d ON d.id = NEW.document_id
    WHERE b.singleton = 1
      AND b.firm_id = NEW.firm_id
      AND d.firm_id = NEW.firm_id
)
BEGIN
    SELECT RAISE(ABORT, 'original file object belongs to a different firm');
END;

CREATE TRIGGER original_file_objects_hold_delete
BEFORE DELETE ON original_file_objects
WHEN OLD.legal_hold = 1
BEGIN
    SELECT RAISE(ABORT, 'original file is under legal hold');
END;

CREATE TRIGGER original_file_objects_hold_state_change
BEFORE UPDATE OF state ON original_file_objects
WHEN OLD.legal_hold = 1 AND NEW.state = 'quarantined'
BEGIN
    SELECT RAISE(ABORT, 'original file is under legal hold');
END;
