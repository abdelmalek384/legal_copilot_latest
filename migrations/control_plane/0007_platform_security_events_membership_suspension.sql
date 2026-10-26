-- Extend the platform audit event vocabulary for per-firm membership suspension.
-- Preserve existing event IDs and records; no membership state is changed by this migration.
DROP TRIGGER platform_security_events_no_update;
DROP TRIGGER platform_security_events_no_delete;
DROP INDEX idx_platform_security_events_created;
DROP INDEX idx_platform_security_events_target;
ALTER TABLE platform_security_events RENAME TO platform_security_events_v6;
CREATE TABLE platform_security_events (
 id INTEGER PRIMARY KEY,
 actor_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
 target_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
 firm_id INTEGER REFERENCES firms(id) ON DELETE RESTRICT,
 event_type TEXT NOT NULL CHECK(event_type IN (
   'password_reset_cli',
   'password_changed_web',
   'firm_provisioned',
   'firm_disabled',
   'membership_created',
   'membership_suspended',
   'initial_owner_bootstrapped',
   'platform_role_granted',
   'platform_role_revoked'
 )),
 detail_json TEXT NOT NULL DEFAULT '{}',
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT INTO platform_security_events(id,actor_user_id,target_user_id,firm_id,event_type,detail_json,created_at)
SELECT id,actor_user_id,target_user_id,firm_id,event_type,detail_json,created_at
FROM platform_security_events_v6;
DROP TABLE platform_security_events_v6;
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
