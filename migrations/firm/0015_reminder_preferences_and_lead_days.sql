-- Expand the tenant-local reminder identity to support independent 7/3/1-day deliveries.
-- Rebuild the outbox and its append-only attempts so the uniqueness key includes lead_days.
ALTER TABLE reminder_delivery_attempts RENAME TO reminder_delivery_attempts_old;
ALTER TABLE reminder_deliveries RENAME TO reminder_deliveries_old;

CREATE TABLE reminder_deliveries (
    id INTEGER PRIMARY KEY,
    idempotency_key TEXT NOT NULL UNIQUE CHECK(length(idempotency_key) = 64),
    recipient_user_id INTEGER NOT NULL CHECK(recipient_user_id > 0),
    event_type TEXT NOT NULL CHECK(event_type IN ('task','deadline','session')),
    event_id TEXT NOT NULL CHECK(length(trim(event_id)) > 0),
    due_date TEXT NOT NULL CHECK(length(due_date) = 10),
    reminder_window TEXT NOT NULL CHECK(reminder_window IN ('due_soon','due_today','overdue')),
    lead_days INTEGER NOT NULL DEFAULT 1 CHECK(lead_days BETWEEN 0 AND 30),
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
    UNIQUE(recipient_user_id,event_type,event_id,due_date,reminder_window,lead_days)
);

INSERT INTO reminder_deliveries (
    id,idempotency_key,recipient_user_id,event_type,event_id,due_date,reminder_window,
    lead_days,status,attempt_count,next_attempt_at,lease_until,last_attempt_at,accepted_at,
    provider_message_id,last_error_code,created_at,updated_at
)
SELECT id,idempotency_key,recipient_user_id,event_type,event_id,due_date,reminder_window,
       1,status,attempt_count,next_attempt_at,lease_until,last_attempt_at,accepted_at,
       provider_message_id,last_error_code,created_at,updated_at
FROM reminder_deliveries_old;

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

INSERT INTO reminder_delivery_attempts
SELECT id,delivery_id,attempt_number,smtp_attempts,status,error_code,provider_message_id,
       attempted_at,finished_at
FROM reminder_delivery_attempts_old;

DROP TABLE reminder_delivery_attempts_old;
DROP TABLE reminder_deliveries_old;

CREATE INDEX idx_reminder_deliveries_due
    ON reminder_deliveries(status,next_attempt_at,created_at);
CREATE INDEX idx_reminder_deliveries_recipient
    ON reminder_deliveries(recipient_user_id,created_at DESC);
CREATE INDEX idx_reminder_attempts_delivery
    ON reminder_delivery_attempts(delivery_id,attempt_number);

CREATE TRIGGER reminder_delivery_attempts_no_update
BEFORE UPDATE ON reminder_delivery_attempts
BEGIN SELECT RAISE(ABORT, 'reminder delivery attempts are append-only'); END;
CREATE TRIGGER reminder_delivery_attempts_no_delete
BEFORE DELETE ON reminder_delivery_attempts
BEGIN SELECT RAISE(ABORT, 'reminder delivery attempts are append-only'); END;

CREATE TABLE reminder_preferences (
    user_id INTEGER PRIMARY KEY CHECK(user_id > 0),
    email_enabled INTEGER NOT NULL DEFAULT 1 CHECK(email_enabled IN (0,1)),
    deadline_7_days INTEGER NOT NULL DEFAULT 1 CHECK(deadline_7_days IN (0,1)),
    deadline_3_days INTEGER NOT NULL DEFAULT 1 CHECK(deadline_3_days IN (0,1)),
    deadline_1_day INTEGER NOT NULL DEFAULT 1 CHECK(deadline_1_day IN (0,1)),
    deadline_day_of INTEGER NOT NULL DEFAULT 1 CHECK(deadline_day_of IN (0,1)),
    deadline_overdue INTEGER NOT NULL DEFAULT 1 CHECK(deadline_overdue IN (0,1)),
    session_day_of INTEGER NOT NULL DEFAULT 1 CHECK(session_day_of IN (0,1)),
    task_reminders INTEGER NOT NULL DEFAULT 1 CHECK(task_reminders IN (0,1)),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
