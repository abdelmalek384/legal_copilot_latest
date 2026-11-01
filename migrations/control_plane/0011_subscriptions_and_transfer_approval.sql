-- Subscription and bank-transfer approval state belongs to the control plane.
-- No card or bank credentials are stored; only user-supplied transfer references.
CREATE TABLE firm_subscriptions (
    firm_id INTEGER PRIMARY KEY REFERENCES firms(id) ON DELETE RESTRICT,
    plan_code TEXT NOT NULL CHECK(plan_code IN ('solo','small_firm')),
    status TEXT NOT NULL CHECK(status IN ('trialing','pending_payment','active','past_due','expired','canceled')),
    seat_limit INTEGER NOT NULL CHECK(seat_limit > 0),
    trial_started_at TEXT,
    trial_ends_at TEXT,
    paid_through TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK(
      (status='trialing' AND trial_started_at IS NOT NULL AND trial_ends_at IS NOT NULL)
      OR status!='trialing'
    )
);

CREATE TABLE subscription_payment_requests (
    id INTEGER PRIMARY KEY,
    firm_id INTEGER NOT NULL REFERENCES firms(id) ON DELETE RESTRICT,
    requested_by INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    plan_code TEXT NOT NULL CHECK(plan_code IN ('solo','small_firm')),
    amount_piasters INTEGER NOT NULL CHECK(amount_piasters > 0),
    transfer_reference TEXT NOT NULL UNIQUE CHECK(length(transfer_reference) BETWEEN 6 AND 80),
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
    reviewed_by INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    reviewed_at TEXT,
    review_note TEXT NOT NULL DEFAULT '' CHECK(length(review_note) <= 2000),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK(
      (status='pending' AND reviewed_by IS NULL AND reviewed_at IS NULL)
      OR
      (status IN ('approved','rejected') AND reviewed_by IS NOT NULL AND reviewed_at IS NOT NULL)
    )
);
CREATE INDEX subscription_payment_requests_queue
    ON subscription_payment_requests(status,created_at,id);
CREATE INDEX subscription_payment_requests_firm
    ON subscription_payment_requests(firm_id,created_at DESC);

CREATE TABLE subscription_events (
    id INTEGER PRIMARY KEY,
    firm_id INTEGER NOT NULL REFERENCES firms(id) ON DELETE RESTRICT,
    actor_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    event_type TEXT NOT NULL CHECK(event_type IN (
        'trial_started','payment_requested','payment_approved','payment_rejected',
        'subscription_expired','subscription_canceled'
    )),
    details_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX subscription_events_firm
    ON subscription_events(firm_id,created_at DESC,id DESC);

CREATE TRIGGER subscription_events_no_update
BEFORE UPDATE ON subscription_events
BEGIN SELECT RAISE(ABORT, 'subscription events are append-only'); END;
CREATE TRIGGER subscription_events_no_delete
BEFORE DELETE ON subscription_events
BEGIN SELECT RAISE(ABORT, 'subscription events are append-only'); END;
