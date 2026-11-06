-- Append-only, firm-scoped usage ledger. Store event type and units only; never query text or matter identifiers.
CREATE TABLE firm_usage_events (
    id INTEGER PRIMARY KEY,
    firm_id INTEGER NOT NULL REFERENCES firms(id) ON DELETE RESTRICT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    event_type TEXT NOT NULL CHECK(event_type IN (
        'research_query','document_upload','ocr_processing','draft_generation'
    )),
    units INTEGER NOT NULL CHECK(units > 0 AND units <= 1000000),
    occurred_at INTEGER NOT NULL
);
CREATE INDEX idx_firm_usage_events_period
    ON firm_usage_events(firm_id, occurred_at DESC, event_type);
CREATE INDEX idx_firm_usage_events_user
    ON firm_usage_events(firm_id, user_id, occurred_at DESC);
CREATE TRIGGER firm_usage_events_no_update
BEFORE UPDATE ON firm_usage_events
BEGIN
    SELECT RAISE(ABORT, 'firm usage events are immutable');
END;
CREATE TRIGGER firm_usage_events_no_delete
BEFORE DELETE ON firm_usage_events
BEGIN
    SELECT RAISE(ABORT, 'firm usage events are immutable');
END;
