-- Platform-level events are distinct from firm-scoped matter audit records.
-- CLI-driven password resets are recorded in the same transaction as session revocation.
CREATE TABLE platform_security_events (
 id INTEGER PRIMARY KEY,
 actor_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
 target_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
 firm_id INTEGER REFERENCES firms(id) ON DELETE RESTRICT,
 event_type TEXT NOT NULL CHECK(event_type IN (
   'password_reset_cli',
   'firm_provisioned',
   'firm_disabled',
   'membership_created',
   'initial_owner_bootstrapped',
   'platform_role_granted',
   'platform_role_revoked'
 )),
 detail_json TEXT NOT NULL DEFAULT '{}',
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_platform_security_events_created ON platform_security_events(created_at,id);
CREATE INDEX idx_platform_security_events_target ON platform_security_events(target_user_id,created_at);
CREATE TRIGGER platform_security_events_no_update
BEFORE UPDATE ON platform_security_events
BEGIN
 SELECT RAISE(ABORT, 'platform security events are append-only');
END;
CREATE TRIGGER platform_security_events_no_delete
BEFORE DELETE ON platform_security_events
BEGIN
 SELECT RAISE(ABORT, 'platform security events are append-only');
END;
