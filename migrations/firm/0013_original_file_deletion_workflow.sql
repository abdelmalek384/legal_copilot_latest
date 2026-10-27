-- Retain a tombstone and immutable audit history when an original is explicitly purged.
ALTER TABLE original_file_objects ADD COLUMN purged_at TEXT;
ALTER TABLE original_file_objects ADD COLUMN purged_by_user_id INTEGER;
ALTER TABLE original_file_objects ADD COLUMN purge_reason TEXT;

CREATE TABLE original_file_deletion_requests (
    id INTEGER PRIMARY KEY,
    object_id TEXT NOT NULL REFERENCES original_file_objects(object_id) ON DELETE RESTRICT,
    document_id INTEGER NOT NULL REFERENCES docs(id) ON DELETE RESTRICT,
    firm_id INTEGER NOT NULL CHECK(firm_id > 0),
    requested_by_user_id INTEGER NOT NULL CHECK(requested_by_user_id > 0),
    request_reason TEXT NOT NULL CHECK(length(trim(request_reason)) > 0),
    requested_at TEXT NOT NULL DEFAULT (datetime('now')),
    status TEXT NOT NULL DEFAULT 'requested'
        CHECK(status IN ('requested','approved','purging','completed','cancelled')),
    approved_by_user_id INTEGER,
    approved_at TEXT,
    approval_reason TEXT,
    purge_started_by_user_id INTEGER,
    purge_started_at TEXT,
    completed_by_user_id INTEGER,
    completed_at TEXT,
    cancellation_reason TEXT,
    cancelled_by_user_id INTEGER,
    cancelled_at TEXT,
    CHECK(approved_by_user_id IS NULL OR approved_by_user_id <> requested_by_user_id)
);

CREATE UNIQUE INDEX original_file_deletion_active_request_idx
    ON original_file_deletion_requests(object_id)
    WHERE status IN ('requested','approved','purging');

CREATE INDEX original_file_deletion_requests_firm_status_idx
    ON original_file_deletion_requests(firm_id,status,id);

CREATE TABLE original_file_deletion_events (
    id INTEGER PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES original_file_deletion_requests(id) ON DELETE RESTRICT,
    object_id TEXT NOT NULL REFERENCES original_file_objects(object_id) ON DELETE RESTRICT,
    document_id INTEGER NOT NULL REFERENCES docs(id) ON DELETE RESTRICT,
    firm_id INTEGER NOT NULL CHECK(firm_id > 0),
    action TEXT NOT NULL CHECK(action IN ('requested','approved','purging','completed','cancelled')),
    reason TEXT NOT NULL CHECK(length(trim(reason)) > 0),
    actor_user_id INTEGER NOT NULL CHECK(actor_user_id > 0),
    occurred_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX original_file_deletion_events_object_idx
    ON original_file_deletion_events(firm_id,object_id,id);

CREATE TRIGGER original_file_deletion_request_tenant_insert
BEFORE INSERT ON original_file_deletion_requests
WHEN NOT EXISTS (
    SELECT 1
    FROM tenant_database_binding b
    JOIN original_file_objects o ON o.object_id=NEW.object_id
    JOIN docs d ON d.id=NEW.document_id
    WHERE b.singleton=1
      AND b.firm_id=NEW.firm_id
      AND o.firm_id=NEW.firm_id
      AND o.document_id=NEW.document_id
      AND d.firm_id=NEW.firm_id
      AND o.legal_hold=0
      AND o.purged_at IS NULL
      AND o.state='ready'
)
BEGIN
    SELECT RAISE(ABORT, 'original file is not eligible for a deletion request');
END;

CREATE TRIGGER original_file_deletion_request_status_guard
BEFORE UPDATE OF status ON original_file_deletion_requests
WHEN NOT (
    (OLD.status='requested' AND NEW.status IN ('approved','cancelled'))
    OR (OLD.status='approved' AND NEW.status IN ('purging','cancelled'))
    OR (OLD.status='purging' AND NEW.status='completed')
)
BEGIN
    SELECT RAISE(ABORT, 'invalid original file deletion request transition');
END;

CREATE TRIGGER original_file_deletion_request_metadata_guard
BEFORE UPDATE OF status ON original_file_deletion_requests
WHEN
    (NEW.status='approved' AND (
        NEW.approved_by_user_id IS NULL OR NEW.approved_at IS NULL
        OR NEW.approval_reason IS NULL OR length(trim(NEW.approval_reason))=0
        OR NEW.approved_by_user_id=NEW.requested_by_user_id
    ))
    OR (NEW.status='purging' AND (
        NEW.purge_started_by_user_id IS NULL OR NEW.purge_started_at IS NULL
    ))
    OR (NEW.status='completed' AND (
        NEW.completed_by_user_id IS NULL OR NEW.completed_at IS NULL
        OR NOT EXISTS (
            SELECT 1 FROM original_file_objects o
            WHERE o.object_id=NEW.object_id AND o.firm_id=NEW.firm_id
              AND o.purged_at IS NOT NULL
        )
    ))
    OR (NEW.status='cancelled' AND (
        NEW.cancelled_by_user_id IS NULL OR NEW.cancelled_at IS NULL
        OR NEW.cancellation_reason IS NULL OR length(trim(NEW.cancellation_reason))=0
    ))
BEGIN
    SELECT RAISE(ABORT, 'original file deletion transition metadata is incomplete');
END;

CREATE TRIGGER original_file_deletion_request_hold_guard
BEFORE UPDATE OF status ON original_file_deletion_requests
WHEN NEW.status IN ('approved','purging')
 AND EXISTS (
    SELECT 1 FROM original_file_objects o
    WHERE o.object_id=NEW.object_id AND o.firm_id=NEW.firm_id
      AND (o.legal_hold=1 OR o.purged_at IS NOT NULL OR o.state<>'ready')
 )
BEGIN
    SELECT RAISE(ABORT, 'original file is held, purged, or not ready for deletion');
END;

CREATE TRIGGER original_file_hold_blocks_purged_object
BEFORE UPDATE OF legal_hold ON original_file_objects
WHEN NEW.legal_hold=1 AND NEW.purged_at IS NOT NULL
BEGIN
    SELECT RAISE(ABORT, 'a purged original cannot be placed under legal hold');
END;

CREATE TRIGGER original_file_hold_blocks_inflight_purge
BEFORE UPDATE OF legal_hold ON original_file_objects
WHEN NEW.legal_hold=1
 AND EXISTS (
    SELECT 1 FROM original_file_deletion_requests r
    WHERE r.object_id=NEW.object_id AND r.firm_id=NEW.firm_id
      AND r.status='purging'
 )
BEGIN
    SELECT RAISE(ABORT, 'an in-flight purge must finish or roll back before setting a legal hold');
END;

CREATE TRIGGER original_file_hold_cancels_pending_deletion
AFTER UPDATE OF legal_hold ON original_file_objects
WHEN OLD.legal_hold=0 AND NEW.legal_hold=1
BEGIN
    UPDATE original_file_deletion_requests
       SET status='cancelled',
           cancelled_by_user_id=NEW.hold_set_by,
           cancelled_at=NEW.hold_set_at,
           cancellation_reason='Automatically cancelled by legal hold'
     WHERE object_id=NEW.object_id AND firm_id=NEW.firm_id
       AND status IN ('requested','approved');
END;

CREATE TRIGGER original_file_purge_metadata_guard
BEFORE UPDATE OF purged_at,purged_by_user_id,purge_reason ON original_file_objects
WHEN NEW.purged_at IS NOT NULL
 AND (
    OLD.purged_at IS NOT NULL
    OR NEW.legal_hold=1
    OR NEW.purged_by_user_id IS NULL
    OR NEW.purge_reason IS NULL OR length(trim(NEW.purge_reason))=0
    OR NOT EXISTS (
        SELECT 1 FROM original_file_deletion_requests r
        WHERE r.object_id=NEW.object_id AND r.firm_id=NEW.firm_id
          AND r.status='purging'
          AND r.purge_started_by_user_id=NEW.purged_by_user_id
    )
 )
BEGIN
    SELECT RAISE(ABORT, 'original file purge requires an approved, unheld purge operation');
END;

CREATE TRIGGER original_file_purge_metadata_immutable
BEFORE UPDATE OF purged_at,purged_by_user_id,purge_reason ON original_file_objects
WHEN OLD.purged_at IS NOT NULL
 AND (
    NEW.purged_at IS NOT OLD.purged_at
    OR NEW.purged_by_user_id IS NOT OLD.purged_by_user_id
    OR NEW.purge_reason IS NOT OLD.purge_reason
 )
BEGIN
    SELECT RAISE(ABORT, 'purge tombstone metadata is immutable');
END;

CREATE TRIGGER original_file_purged_state_immutable
BEFORE UPDATE OF state ON original_file_objects
WHEN OLD.purged_at IS NOT NULL AND NEW.state IS NOT OLD.state
BEGIN
    SELECT RAISE(ABORT, 'purged original file state is immutable');
END;

CREATE TRIGGER original_file_deletion_request_identity_immutable
BEFORE UPDATE ON original_file_deletion_requests
WHEN NEW.object_id IS NOT OLD.object_id
 OR NEW.document_id IS NOT OLD.document_id
 OR NEW.firm_id IS NOT OLD.firm_id
 OR NEW.requested_by_user_id IS NOT OLD.requested_by_user_id
 OR NEW.request_reason IS NOT OLD.request_reason
 OR NEW.requested_at IS NOT OLD.requested_at
BEGIN
    SELECT RAISE(ABORT, 'original file deletion request identity is immutable');
END;

CREATE TRIGGER original_file_deletion_request_no_delete
BEFORE DELETE ON original_file_deletion_requests
BEGIN
    SELECT RAISE(ABORT, 'original file deletion requests are retained for audit');
END;

CREATE TRIGGER original_file_deletion_events_tenant_insert
BEFORE INSERT ON original_file_deletion_events
WHEN NOT EXISTS (
    SELECT 1 FROM tenant_database_binding b
    JOIN original_file_objects o ON o.object_id=NEW.object_id
    JOIN docs d ON d.id=NEW.document_id
    JOIN original_file_deletion_requests r ON r.id=NEW.request_id
    WHERE b.singleton=1
      AND b.firm_id=NEW.firm_id
      AND o.firm_id=NEW.firm_id
      AND o.document_id=NEW.document_id
      AND d.firm_id=NEW.firm_id
      AND r.firm_id=NEW.firm_id
      AND r.object_id=NEW.object_id
      AND r.document_id=NEW.document_id
)
BEGIN
    SELECT RAISE(ABORT, 'original file deletion event belongs to a different firm');
END;

CREATE TRIGGER original_file_deletion_events_immutable_update
BEFORE UPDATE ON original_file_deletion_events
BEGIN
    SELECT RAISE(ABORT, 'original file deletion events are immutable');
END;

CREATE TRIGGER original_file_deletion_events_immutable_delete
BEFORE DELETE ON original_file_deletion_events
BEGIN
    SELECT RAISE(ABORT, 'original file deletion events are immutable');
END;

CREATE TRIGGER original_file_deletion_event_requested
AFTER INSERT ON original_file_deletion_requests
BEGIN
    INSERT INTO original_file_deletion_events(
        request_id,object_id,document_id,firm_id,action,reason,actor_user_id,occurred_at
    ) VALUES(
        NEW.id,NEW.object_id,NEW.document_id,NEW.firm_id,'requested',
        NEW.request_reason,NEW.requested_by_user_id,NEW.requested_at
    );
END;

CREATE TRIGGER original_file_deletion_event_approved
AFTER UPDATE OF status ON original_file_deletion_requests
WHEN OLD.status<>'approved' AND NEW.status='approved'
BEGIN
    INSERT INTO original_file_deletion_events(
        request_id,object_id,document_id,firm_id,action,reason,actor_user_id,occurred_at
    ) VALUES(
        NEW.id,NEW.object_id,NEW.document_id,NEW.firm_id,'approved',
        NEW.approval_reason,NEW.approved_by_user_id,NEW.approved_at
    );
END;

CREATE TRIGGER original_file_deletion_event_purging
AFTER UPDATE OF status ON original_file_deletion_requests
WHEN OLD.status<>'purging' AND NEW.status='purging'
BEGIN
    INSERT INTO original_file_deletion_events(
        request_id,object_id,document_id,firm_id,action,reason,actor_user_id,occurred_at
    ) VALUES(
        NEW.id,NEW.object_id,NEW.document_id,NEW.firm_id,'purging',
        NEW.approval_reason,NEW.purge_started_by_user_id,NEW.purge_started_at
    );
END;

CREATE TRIGGER original_file_deletion_event_completed
AFTER UPDATE OF status ON original_file_deletion_requests
WHEN OLD.status<>'completed' AND NEW.status='completed'
BEGIN
    INSERT INTO original_file_deletion_events(
        request_id,object_id,document_id,firm_id,action,reason,actor_user_id,occurred_at
    )
    SELECT NEW.id,NEW.object_id,NEW.document_id,NEW.firm_id,'completed',
           o.purge_reason,NEW.completed_by_user_id,NEW.completed_at
    FROM original_file_objects o
    WHERE o.object_id=NEW.object_id AND o.firm_id=NEW.firm_id;
END;

CREATE TRIGGER original_file_deletion_event_cancelled
AFTER UPDATE OF status ON original_file_deletion_requests
WHEN OLD.status<>'cancelled' AND NEW.status='cancelled'
BEGIN
    INSERT INTO original_file_deletion_events(
        request_id,object_id,document_id,firm_id,action,reason,actor_user_id,occurred_at
    ) VALUES(
        NEW.id,NEW.object_id,NEW.document_id,NEW.firm_id,'cancelled',
        NEW.cancellation_reason,NEW.cancelled_by_user_id,NEW.cancelled_at
    );
END;
