-- Private, tenant-local answer correction queue.
-- The answer itself remains in research_messages; this table stores only a bounded excerpt.
CREATE TABLE answer_corrections (
    id INTEGER PRIMARY KEY,
    firm_id INTEGER NOT NULL CHECK(firm_id > 0),
    conversation_id INTEGER NOT NULL CHECK(conversation_id > 0),
    answer_id TEXT NOT NULL CHECK(length(answer_id) BETWEEN 32 AND 96),
    reporter_user_id INTEGER NOT NULL CHECK(reporter_user_id > 0),
    category TEXT NOT NULL CHECK(category IN ('legal_accuracy','citation','completeness','clarity','other')),
    correction_text TEXT NOT NULL CHECK(length(trim(correction_text)) BETWEEN 5 AND 4000),
    answer_excerpt TEXT NOT NULL DEFAULT '' CHECK(length(answer_excerpt) <= 2000),
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','accepted','rejected')),
    review_note TEXT NOT NULL DEFAULT '' CHECK(length(review_note) <= 2000),
    reviewed_by_user_id INTEGER,
    reviewed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK(
      (status='open' AND reviewed_by_user_id IS NULL AND reviewed_at IS NULL)
      OR
      (status IN ('accepted','rejected') AND reviewed_by_user_id IS NOT NULL AND reviewed_at IS NOT NULL)
    )
);

CREATE UNIQUE INDEX answer_corrections_one_open_per_reporter
    ON answer_corrections(firm_id,conversation_id,answer_id,reporter_user_id)
    WHERE status='open';
CREATE INDEX answer_corrections_firm_queue
    ON answer_corrections(status,created_at DESC,id DESC);
CREATE INDEX answer_corrections_answer
    ON answer_corrections(conversation_id,answer_id,created_at DESC);

CREATE TABLE answer_correction_events (
    id INTEGER PRIMARY KEY,
    correction_id INTEGER NOT NULL REFERENCES answer_corrections(id) ON DELETE RESTRICT,
    firm_id INTEGER NOT NULL CHECK(firm_id > 0),
    actor_user_id INTEGER NOT NULL CHECK(actor_user_id > 0),
    action TEXT NOT NULL CHECK(action IN ('submitted','accepted','rejected')),
    note TEXT NOT NULL DEFAULT '' CHECK(length(note) <= 2000),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX answer_correction_events_firm
    ON answer_correction_events(firm_id,correction_id,id);

CREATE TRIGGER answer_correction_events_no_update
BEFORE UPDATE ON answer_correction_events
BEGIN SELECT RAISE(ABORT, 'answer correction events are append-only'); END;
CREATE TRIGGER answer_correction_events_no_delete
BEFORE DELETE ON answer_correction_events
BEGIN SELECT RAISE(ABORT, 'answer correction events are append-only'); END;
