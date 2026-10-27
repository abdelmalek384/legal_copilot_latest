-- Durable, tenant-local reminder outbox. No reminder can cross firm databases.
-- SMTP acceptance is recorded as acceptance, not proof of inbox delivery.
CREATE TABLE reminder_deliveries (
    id INTEGER PRIMARY KEY,
    idempotency_key TEXT NOT NULL UNIQUE
        CHECK(length(idempotency_key) = 64),
    recipient_user_id INTEGER NOT NULL CHECK(recipient_user_id > 0),
    event_type TEXT NOT NULL CHECK(event_type IN ('task','deadline','session')),
    event_id TEXT NOT NULL CHECK(length(trim(event_id)) > 0),
    due_date TEXT NOT NULL CHECK(length(due_date) = 10),
    reminder_window TEXT NOT NULL CHECK(reminder_window IN ('due_soon','due_today','overdue')),
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK(status IN ('queued','sending','accepted_by_smtp','failed','ambiguous')),
    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK(attempt_count >= 0),
    next_attempt_at TEXT,
    lease_until TEXT,
    last_attempt_at TEXT,
    accepted_at TEXT,
    provider_message_id TEXT,
    last_error_code TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(recipient_user_id,event_type,event_id,due_date,reminder_window)
);
CREATE INDEX idx_reminder_deliveries_due
    ON reminder_deliveries(status,next_attempt_at,created_at);
CREATE INDEX idx_reminder_deliveries_recipient
    ON reminder_deliveries(recipient_user_id,created_at DESC);

-- Append-only outcome records preserve delivery attempts without message bodies or secrets.
CREATE TABLE reminder_delivery_attempts (
    id INTEGER PRIMARY KEY,
    delivery_id INTEGER NOT NULL REFERENCES reminder_deliveries(id) ON DELETE RESTRICT,
    attempt_number INTEGER NOT NULL CHECK(attempt_number > 0),
    smtp_attempts INTEGER NOT NULL DEFAULT 0 CHECK(smtp_attempts BETWEEN 0 AND 5),
    status TEXT NOT NULL CHECK(status IN ('accepted_by_smtp','failed','ambiguous')),
    error_code TEXT,
    provider_message_id TEXT,
    attempted_at TEXT NOT NULL,
    finished_at TEXT NOT NULL,
    UNIQUE(delivery_id,attempt_number)
);
CREATE INDEX idx_reminder_attempts_delivery
    ON reminder_delivery_attempts(delivery_id,attempt_number);

CREATE TRIGGER reminder_delivery_attempts_no_update
BEFORE UPDATE ON reminder_delivery_attempts
BEGIN SELECT RAISE(ABORT, 'reminder delivery attempts are append-only'); END;
CREATE TRIGGER reminder_delivery_attempts_no_delete
BEFORE DELETE ON reminder_delivery_attempts
BEGIN SELECT RAISE(ABORT, 'reminder delivery attempts are append-only'); END;
