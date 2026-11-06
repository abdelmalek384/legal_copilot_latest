-- Firm-local lawyer ratings for generated research answers.
-- Ratings are quality labels, not training consent and not legal approval of the corpus.
CREATE TABLE answer_ratings (
    id INTEGER PRIMARY KEY,
    answer_message_id INTEGER NOT NULL
        REFERENCES research_messages(id) ON DELETE RESTRICT,
    answer_id TEXT NOT NULL CHECK(length(trim(answer_id)) BETWEEN 8 AND 128),
    rating TEXT NOT NULL
        CHECK(rating IN ('correct','partially_correct','wrong')),
    cited_article_accuracy TEXT NOT NULL
        CHECK(cited_article_accuracy IN ('right','wrong','not_applicable')),
    expected_article_ids_json TEXT NOT NULL DEFAULT '[]'
        CHECK(json_valid(expected_article_ids_json)
              AND json_type(expected_article_ids_json) = 'array'),
    answerable INTEGER
        CHECK(answerable IS NULL OR answerable IN (0,1)),
    notes TEXT NOT NULL DEFAULT '' CHECK(length(notes) <= 2000),
    rated_by INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(answer_message_id, rated_by)
);

CREATE INDEX idx_answer_ratings_answer
    ON answer_ratings(answer_id, created_at DESC, id DESC);
CREATE INDEX idx_answer_ratings_reviewer
    ON answer_ratings(rated_by, created_at DESC, id DESC);

CREATE TABLE answer_rating_events (
    id INTEGER PRIMARY KEY,
    rating_id INTEGER NOT NULL
        REFERENCES answer_ratings(id) ON DELETE RESTRICT,
    actor_user_id INTEGER NOT NULL,
    event_type TEXT NOT NULL
        CHECK(event_type IN ('created','updated')),
    detail_json TEXT NOT NULL DEFAULT '{}'
        CHECK(json_valid(detail_json) AND json_type(detail_json) = 'object'),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_answer_rating_events_rating
    ON answer_rating_events(rating_id, created_at, id);

CREATE TRIGGER answer_rating_events_no_update
BEFORE UPDATE ON answer_rating_events
BEGIN SELECT RAISE(ABORT, 'answer rating events are immutable'); END;

CREATE TRIGGER answer_rating_events_no_delete
BEFORE DELETE ON answer_rating_events
BEGIN SELECT RAISE(ABORT, 'answer rating events are immutable'); END;
