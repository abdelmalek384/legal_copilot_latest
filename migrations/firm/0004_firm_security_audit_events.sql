-- Firm activity audit records stay inside the firm database.
CREATE TABLE security_audit_events (
 id INTEGER PRIMARY KEY,
 firm_id INTEGER NOT NULL,
 user_id INTEGER,
 event TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_security_audit_firm_created ON security_audit_events(firm_id, id DESC);
