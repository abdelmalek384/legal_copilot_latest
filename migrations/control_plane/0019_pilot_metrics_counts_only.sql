-- Replace identity-linked pilot event rows with count-only weekly aggregates.
-- Preserve historical counts, then discard user-level metric records.
CREATE TABLE pilot_metrics_weekly_counts (
    firm_id INTEGER NOT NULL REFERENCES firms(id) ON DELETE RESTRICT,
    week_start TEXT NOT NULL CHECK(length(week_start)=10),
    metric TEXT NOT NULL CHECK(metric IN (
        'active_users','cases_created','deadlines_created',
        'answers_requested','invoices_issued','corrections_submitted'
    )),
    count INTEGER NOT NULL CHECK(count >= 0),
    updated_at INTEGER NOT NULL CHECK(updated_at > 0),
    PRIMARY KEY(firm_id,week_start,metric)
);

INSERT INTO pilot_metrics_weekly_counts(firm_id,week_start,metric,count,updated_at)
SELECT
    firm_id,
    week_start,
    CASE metric
        WHEN 'active_user' THEN 'active_users'
        WHEN 'case_created' THEN 'cases_created'
        WHEN 'deadline_created' THEN 'deadlines_created'
        WHEN 'answer_requested' THEN 'answers_requested'
        WHEN 'invoice_issued' THEN 'invoices_issued'
        WHEN 'correction_submitted' THEN 'corrections_submitted'
    END,
    CASE WHEN metric='active_user' THEN COUNT(DISTINCT user_id) ELSE COUNT(*) END,
    MAX(occurred_at)
FROM pilot_metrics_events
GROUP BY firm_id,week_start,metric;

DROP TRIGGER pilot_metrics_events_no_update;
DROP TRIGGER pilot_metrics_events_no_delete;
DROP INDEX idx_pilot_metrics_firm_week;
DROP INDEX idx_pilot_metrics_active_user_week;
DROP TABLE pilot_metrics_events;

CREATE INDEX idx_pilot_metrics_week_firm
    ON pilot_metrics_weekly_counts(week_start,firm_id);
