-- User-configurable reminder delivery preferences and lead-day metadata.
ALTER TABLE reminder_deliveries
    ADD COLUMN lead_days INTEGER NOT NULL DEFAULT 1
    CHECK(lead_days BETWEEN 0 AND 30);

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
