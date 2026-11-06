-- Content-free weekly pilot activity events. Only approved metric categories and actor IDs are stored.
-- No case, client, question, answer, invoice, correction, or document content is recorded.
CREATE TABLE pilot_metrics_events (
    id INTEGER PRIMARY KEY,
    firm_id INTEGER NOT NULL REFERENCES firms(id) ON DELETE RESTRICT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    metric TEXT NOT NULL CHECK(metric IN (
        'active_user','case_created','deadline_created','answer_requested',
        'invoice_issued','correction_submitted'
    )),
    week_start TEXT NOT NULL CHECK(length(week_start)=10),
    occurred_at INTEGER NOT NULL
);
CREATE INDEX idx_pilot_metrics_firm_week
    ON pilot_metrics_events(firm_id, week_start, metric, user_id);
CREATE UNIQUE INDEX idx_pilot_metrics_active_user_week
    ON pilot_metrics_events(firm_id, week_start, user_id)
    WHERE metric='active_user';
CREATE TRIGGER pilot_metrics_events_no_update
BEFORE UPDATE ON pilot_metrics_events
BEGIN
    SELECT RAISE(ABORT, 'pilot metrics events are immutable');
END;
CREATE TRIGGER pilot_metrics_events_no_delete
BEFORE DELETE ON pilot_metrics_events
BEGIN
    SELECT RAISE(ABORT, 'pilot metrics events are immutable');
END;
