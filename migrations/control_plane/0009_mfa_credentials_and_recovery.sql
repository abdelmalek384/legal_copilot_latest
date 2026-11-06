-- TOTP MFA state and one-time recovery codes live in the control plane.
-- TOTP secrets are encrypted by the application with a dedicated MFA_ENCRYPTION_KEY.
ALTER TABLE auth_sessions
    ADD COLUMN mfa_verified INTEGER NOT NULL DEFAULT 1 CHECK(mfa_verified IN (0,1));
ALTER TABLE auth_sessions
    ADD COLUMN mfa_verified_at INTEGER NOT NULL DEFAULT 0 CHECK(mfa_verified_at >= 0);

-- Existing privileged sessions must pass MFA again when enforcement is enabled.
UPDATE auth_sessions SET mfa_verified=0
WHERE user_id IN (
    SELECT user_id FROM firm_memberships
    WHERE status='active' AND firm_role='admin'
    UNION
    SELECT user_id FROM user_platform_roles
    WHERE role_name IN ('platform_admin','platform_reviewer')
);

CREATE TABLE mfa_credentials (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    secret_ciphertext TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending','enabled')),
    enrollment_expires INTEGER,
    last_accepted_step INTEGER CHECK(last_accepted_step IS NULL OR last_accepted_step >= 0),
    failed_attempts INTEGER NOT NULL DEFAULT 0 CHECK(failed_attempts >= 0),
    locked_until INTEGER NOT NULL DEFAULT 0 CHECK(locked_until >= 0),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    enabled_at TEXT
);
CREATE INDEX idx_mfa_credentials_status ON mfa_credentials(status,locked_until);

CREATE TABLE mfa_recovery_codes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    used_at TEXT,
    CHECK(used_at IS NULL OR length(used_at) > 0)
);
CREATE INDEX idx_mfa_recovery_codes_user_unused
    ON mfa_recovery_codes(user_id,used_at);

CREATE TABLE mfa_security_events (
    id INTEGER PRIMARY KEY,
    actor_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    target_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    event_type TEXT NOT NULL CHECK(event_type IN (
        'enrollment_started','enrollment_completed','login_verified',
        'recovery_code_used','recovery_codes_rotated','mfa_disabled','administrator_reset',
        'verification_failed','enrollment_failed'
    )),
    detail_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_mfa_security_events_target
    ON mfa_security_events(target_user_id,created_at DESC,id DESC);
CREATE TRIGGER mfa_security_events_no_update
BEFORE UPDATE ON mfa_security_events
BEGIN SELECT RAISE(ABORT, 'MFA security events are append-only'); END;
CREATE TRIGGER mfa_security_events_no_delete
BEFORE DELETE ON mfa_security_events
BEGIN SELECT RAISE(ABORT, 'MFA security events are append-only'); END;
