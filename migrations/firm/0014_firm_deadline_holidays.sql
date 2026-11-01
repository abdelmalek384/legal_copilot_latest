-- Firm-local dated holiday overrides and immutable change snapshots for deadline estimates.
CREATE TABLE firm_deadline_holidays (
    holiday_date TEXT PRIMARY KEY,
    name_ar TEXT NOT NULL CHECK(length(trim(name_ar)) BETWEEN 1 AND 120),
    updated_by INTEGER NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE firm_deadline_holiday_audit (
    id INTEGER PRIMARY KEY,
    actor_user_id INTEGER NOT NULL,
    action TEXT NOT NULL CHECK(action = 'replace_calendar'),
    before_json TEXT NOT NULL,
    after_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX firm_deadline_holiday_audit_created
    ON firm_deadline_holiday_audit(created_at DESC, id DESC);
