-- Firm-private answer correction queue. Notes are not training data by default.
CREATE TABLE answer_correction_suggestions (
    id INTEGER PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id) ON DELETE SET NULL,
    answer_id TEXT NOT NULL DEFAULT '',
    question TEXT NOT NULL DEFAULT '',
    answer_excerpt TEXT NOT NULL CHECK(length(trim(answer_excerpt)) > 0),
    correction_note TEXT NOT NULL CHECK(length(trim(correction_note)) > 0),
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','accepted','rejected')),
    training_use TEXT NOT NULL DEFAULT 'none' CHECK(training_use='none'),
    created_by INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    reviewed_by INTEGER,
    reviewed_at TEXT,
    review_note TEXT NOT NULL DEFAULT ''
);
CREATE INDEX idx_answer_corrections_queue ON answer_correction_suggestions(status,created_at DESC,id DESC);
CREATE INDEX idx_answer_corrections_creator ON answer_correction_suggestions(created_by,created_at DESC);
CREATE TABLE answer_correction_events (
    id INTEGER PRIMARY KEY,
    suggestion_id INTEGER NOT NULL REFERENCES answer_correction_suggestions(id) ON DELETE RESTRICT,
    actor_user_id INTEGER NOT NULL,
    event_type TEXT NOT NULL CHECK(event_type IN ('submitted','accepted','rejected')),
    detail_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_answer_correction_events_suggestion ON answer_correction_events(suggestion_id,created_at,id);
