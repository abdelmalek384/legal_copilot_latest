-- Weekly firm-level pilot metrics. Only aggregate counts are stored; no user,
-- matter, answer, invoice, or correction identifiers/content are persisted here.
CREATE TABLE firm_weekly_pilot_metrics (
    firm_id INTEGER NOT NULL REFERENCES firms(id) ON DELETE RESTRICT,
    week_start TEXT NOT NULL CHECK(week_start GLOB '????-??-??'),
    metric TEXT NOT NULL CHECK(metric IN (
        'active_users','cases_created','deadlines_created',
        'answers_requested','invoices_issued','corrections_submitted'
    )),
    count INTEGER NOT NULL CHECK(count >= 0 AND count <= 1000000000),
    updated_at INTEGER NOT NULL CHECK(updated_at > 0),
    PRIMARY KEY(firm_id,week_start,metric)
);
CREATE INDEX idx_firm_weekly_pilot_metrics_week
    ON firm_weekly_pilot_metrics(week_start,firm_id);
