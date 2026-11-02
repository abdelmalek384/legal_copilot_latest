-- Firm subscription state and manual bank-transfer/InstaPay review ledger.
CREATE TABLE firm_subscriptions (
    firm_id INTEGER PRIMARY KEY REFERENCES firms(id) ON DELETE RESTRICT,
    plan_code TEXT NOT NULL CHECK(plan_code IN ('solo','small_firm')),
    status TEXT NOT NULL CHECK(status IN ('trial','pending_payment','active','past_due','expired','cancelled')),
    seat_limit INTEGER NOT NULL CHECK(seat_limit > 0),
    trial_started_at INTEGER,
    trial_ends_at INTEGER,
    current_period_start INTEGER,
    current_period_end INTEGER,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);
CREATE TABLE subscription_payment_submissions (
    id INTEGER PRIMARY KEY,
    firm_id INTEGER NOT NULL REFERENCES firms(id) ON DELETE RESTRICT,
    amount_piasters INTEGER NOT NULL CHECK(amount_piasters > 0),
    method TEXT NOT NULL CHECK(method IN ('bank_transfer','instapay')),
    transfer_reference TEXT NOT NULL CHECK(length(trim(transfer_reference)) BETWEEN 3 AND 200),
    submitted_by_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
    reviewed_by_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    reviewed_at INTEGER,
    decision_note TEXT NOT NULL DEFAULT '',
    created_at INTEGER NOT NULL,
    UNIQUE(firm_id,method,transfer_reference)
);
CREATE INDEX idx_subscription_payment_review ON subscription_payment_submissions(status,created_at,id);
CREATE INDEX idx_subscription_payment_firm ON subscription_payment_submissions(firm_id,created_at DESC);
CREATE TABLE subscription_audit_events (
    id INTEGER PRIMARY KEY,
    firm_id INTEGER NOT NULL REFERENCES firms(id) ON DELETE RESTRICT,
    actor_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    event_type TEXT NOT NULL CHECK(event_type IN ('trial_started','plan_changed','payment_submitted','payment_approved','payment_rejected')),
    detail_json TEXT NOT NULL DEFAULT '{}',
    created_at INTEGER NOT NULL
);
CREATE INDEX idx_subscription_audit_firm ON subscription_audit_events(firm_id,created_at DESC,id);
