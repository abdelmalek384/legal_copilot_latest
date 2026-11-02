-- Firm-private product feedback. Feedback is operational input, never training data by default.
CREATE TABLE product_feedback (
    id INTEGER PRIMARY KEY,
    category TEXT NOT NULL CHECK(category IN ('bug','idea','usability','other')),
    title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 3 AND 160),
    message TEXT NOT NULL CHECK(length(trim(message)) BETWEEN 10 AND 4000),
    page_path TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','acknowledged','planned','declined')),
    created_by INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    reviewed_by INTEGER,
    reviewed_at TEXT,
    response TEXT NOT NULL DEFAULT ''
);
CREATE INDEX idx_product_feedback_queue ON product_feedback(status,created_at DESC,id DESC);
CREATE INDEX idx_product_feedback_creator ON product_feedback(created_by,created_at DESC);
CREATE TABLE product_feedback_events (
    id INTEGER PRIMARY KEY,
    feedback_id INTEGER NOT NULL REFERENCES product_feedback(id) ON DELETE RESTRICT,
    actor_user_id INTEGER NOT NULL,
    event_type TEXT NOT NULL CHECK(event_type IN ('submitted','acknowledged','planned','declined')),
    detail_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_product_feedback_events_feedback ON product_feedback_events(feedback_id,created_at,id);
CREATE TRIGGER product_feedback_events_no_update
BEFORE UPDATE ON product_feedback_events
BEGIN SELECT RAISE(ABORT, 'feedback events are immutable'); END;
CREATE TRIGGER product_feedback_events_no_delete
BEFORE DELETE ON product_feedback_events
BEGIN SELECT RAISE(ABORT, 'feedback events are immutable'); END;
