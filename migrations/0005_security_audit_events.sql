-- Move the security audit event table out of the startup schema.
-- Application routes write to this table only after conn() has applied migrations.
CREATE TABLE IF NOT EXISTS security_audit_events(
    id INTEGER PRIMARY KEY,
    firm_id INT NOT NULL,
    user_id INT NOT NULL,
    event TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
