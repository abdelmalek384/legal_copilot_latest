-- Firm-local client/matter communication history. Content never enters the global audit log.
CREATE TABLE case_communications (
 id INTEGER PRIMARY KEY,
 case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
 created_by INTEGER NOT NULL,
 channel TEXT NOT NULL CHECK(channel IN ('call','email','meeting','other')),
 subject TEXT NOT NULL,
 summary TEXT NOT NULL,
 occurred_at TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_case_communications_timeline
 ON case_communications(case_id,occurred_at DESC,id DESC);
