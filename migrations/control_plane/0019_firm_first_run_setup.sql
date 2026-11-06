CREATE TABLE firm_profiles (
    firm_id INTEGER PRIMARY KEY REFERENCES firms(id) ON DELETE RESTRICT,
    phone TEXT NOT NULL DEFAULT '' CHECK(length(phone)<=30),
    address TEXT NOT NULL DEFAULT '' CHECK(length(address)<=300),
    updated_by_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE firm_setup_events (
    id INTEGER PRIMARY KEY,
    firm_id INTEGER NOT NULL REFERENCES firms(id) ON DELETE RESTRICT,
    actor_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    event_type TEXT NOT NULL CHECK(event_type IN ('test_reminder_accepted')),
    provider_status TEXT NOT NULL CHECK(provider_status IN ('accepted_by_smtp')),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_firm_setup_events_firm_type
    ON firm_setup_events(firm_id,event_type,created_at DESC);
CREATE TRIGGER firm_setup_events_no_update
BEFORE UPDATE ON firm_setup_events
BEGIN
    SELECT RAISE(ABORT, 'firm setup events are append-only');
END;
CREATE TRIGGER firm_setup_events_no_delete
BEFORE DELETE ON firm_setup_events
BEGIN
    SELECT RAISE(ABORT, 'firm setup events are append-only');
END;
