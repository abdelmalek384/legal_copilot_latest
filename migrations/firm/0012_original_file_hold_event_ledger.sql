-- Preserve the complete legal-hold history, including reason and actor, independently
-- of the mutable current-state columns on original_file_objects.
CREATE TABLE original_file_hold_events (
    id INTEGER PRIMARY KEY,
    object_id TEXT NOT NULL REFERENCES original_file_objects(object_id) ON DELETE RESTRICT,
    document_id INTEGER NOT NULL REFERENCES docs(id) ON DELETE RESTRICT,
    firm_id INTEGER NOT NULL CHECK(firm_id > 0),
    action TEXT NOT NULL CHECK(action IN ('set','release')),
    reason TEXT NOT NULL CHECK(length(trim(reason)) > 0),
    actor_user_id INTEGER NOT NULL CHECK(actor_user_id > 0),
    occurred_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX original_file_hold_events_object_idx
    ON original_file_hold_events(firm_id, object_id, id);

CREATE TRIGGER original_file_hold_events_tenant_insert
BEFORE INSERT ON original_file_hold_events
WHEN NOT EXISTS (
    SELECT 1
    FROM tenant_database_binding b
    JOIN original_file_objects o ON o.object_id = NEW.object_id
    JOIN docs d ON d.id = NEW.document_id
    WHERE b.singleton = 1
      AND b.firm_id = NEW.firm_id
      AND o.firm_id = NEW.firm_id
      AND o.document_id = NEW.document_id
      AND d.firm_id = NEW.firm_id
)
BEGIN
    SELECT RAISE(ABORT, 'original file hold event belongs to a different firm');
END;

CREATE TRIGGER original_file_hold_events_immutable_update
BEFORE UPDATE ON original_file_hold_events
BEGIN
    SELECT RAISE(ABORT, 'original file hold events are immutable');
END;

CREATE TRIGGER original_file_hold_events_immutable_delete
BEFORE DELETE ON original_file_hold_events
BEGIN
    SELECT RAISE(ABORT, 'original file hold events are immutable');
END;

CREATE TRIGGER original_file_hold_event_set
AFTER UPDATE OF legal_hold ON original_file_objects
WHEN OLD.legal_hold = 0 AND NEW.legal_hold = 1
BEGIN
    INSERT INTO original_file_hold_events(
        object_id,document_id,firm_id,action,reason,actor_user_id,occurred_at
    ) VALUES(
        NEW.object_id,NEW.document_id,NEW.firm_id,'set',NEW.hold_reason,
        NEW.hold_set_by,NEW.hold_set_at
    );
END;

CREATE TRIGGER original_file_hold_event_release
AFTER UPDATE OF legal_hold ON original_file_objects
WHEN OLD.legal_hold = 1 AND NEW.legal_hold = 0
BEGIN
    INSERT INTO original_file_hold_events(
        object_id,document_id,firm_id,action,reason,actor_user_id,occurred_at
    ) VALUES(
        NEW.object_id,NEW.document_id,NEW.firm_id,'release',NEW.hold_release_reason,
        NEW.hold_released_by,NEW.hold_released_at
    );
END;
