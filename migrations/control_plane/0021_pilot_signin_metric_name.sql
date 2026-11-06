-- Rename the login-event counter so it cannot be mistaken for distinct weekly active users.
-- Historical active_users values were successful sign-in/context events, not unique people.
CREATE TABLE pilot_metrics_weekly_counts_new (
    firm_id INTEGER NOT NULL REFERENCES firms(id) ON DELETE RESTRICT,
    week_start TEXT NOT NULL CHECK(length(week_start)=10),
    metric TEXT NOT NULL CHECK(metric IN (
        'successful_sign_ins','cases_created','deadlines_created',
        'answers_requested','invoices_issued','corrections_submitted'
    )),
    count INTEGER NOT NULL CHECK(count >= 0),
    updated_at INTEGER NOT NULL CHECK(updated_at > 0),
    PRIMARY KEY(firm_id,week_start,metric)
);

INSERT INTO pilot_metrics_weekly_counts_new(firm_id,week_start,metric,count,updated_at)
SELECT firm_id,week_start,
       CASE WHEN metric='active_users' THEN 'successful_sign_ins' ELSE metric END,
       count,updated_at
FROM pilot_metrics_weekly_counts;

DROP INDEX IF EXISTS idx_pilot_metrics_week_firm;
DROP TABLE pilot_metrics_weekly_counts;
ALTER TABLE pilot_metrics_weekly_counts_new RENAME TO pilot_metrics_weekly_counts;
CREATE INDEX idx_pilot_metrics_week_firm
    ON pilot_metrics_weekly_counts(week_start,firm_id);
