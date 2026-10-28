-- One-time invitations and account-recovery tokens live only in the control plane.
-- Raw tokens are never stored; application writers persist SHA-256 token hashes.
CREATE TABLE identity_invitations (
    id INTEGER PRIMARY KEY,
    firm_id INTEGER NOT NULL REFERENCES firms(id) ON DELETE RESTRICT,
    email_normalized TEXT NOT NULL CHECK(length(trim(email_normalized)) > 0),
    email_display TEXT NOT NULL CHECK(length(trim(email_display)) > 0),
    invited_role TEXT NOT NULL CHECK(invited_role IN ('lawyer','junior')),
    token_hash TEXT NOT NULL UNIQUE CHECK(length(token_hash)=64),
    invited_by_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at INTEGER NOT NULL CHECK(created_at > 0),
    expires_at INTEGER NOT NULL CHECK(expires_at > created_at),
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending','sent','consumed','revoked','expired','delivery_failed')),
    consumed_by_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    consumed_at INTEGER,
    updated_at INTEGER NOT NULL CHECK(updated_at > 0),
    CHECK((status='consumed' AND consumed_by_user_id IS NOT NULL AND consumed_at IS NOT NULL)
       OR (status<>'consumed' AND consumed_by_user_id IS NULL AND consumed_at IS NULL))
);
CREATE UNIQUE INDEX identity_invitations_one_active_per_firm_email
    ON identity_invitations(firm_id,email_normalized)
    WHERE status IN ('pending','sent');
CREATE INDEX identity_invitations_expiry_idx ON identity_invitations(status,expires_at);
CREATE INDEX identity_invitations_inviter_idx ON identity_invitations(invited_by_user_id,created_at DESC);

CREATE TRIGGER identity_invitations_status_guard
BEFORE UPDATE OF status ON identity_invitations
WHEN NOT (
    (OLD.status='pending' AND NEW.status IN ('sent','revoked','expired','delivery_failed'))
 OR (OLD.status='sent' AND NEW.status IN ('consumed','revoked','expired'))
)
BEGIN
    SELECT RAISE(ABORT, 'invalid invitation status transition');
END;
CREATE TRIGGER identity_invitations_identity_immutable
BEFORE UPDATE ON identity_invitations
WHEN NEW.firm_id IS NOT OLD.firm_id
 OR NEW.email_normalized IS NOT OLD.email_normalized
 OR NEW.email_display IS NOT OLD.email_display
 OR NEW.invited_role IS NOT OLD.invited_role
 OR NEW.token_hash IS NOT OLD.token_hash
 OR NEW.invited_by_user_id IS NOT OLD.invited_by_user_id
 OR NEW.created_at IS NOT OLD.created_at
 OR NEW.expires_at IS NOT OLD.expires_at
BEGIN
    SELECT RAISE(ABORT, 'invitation identity is immutable');
END;
CREATE TRIGGER identity_invitations_no_delete
BEFORE DELETE ON identity_invitations
BEGIN
    SELECT RAISE(ABORT, 'invitation records are retained for audit');
END;

CREATE TABLE password_recovery_tokens (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    token_hash TEXT NOT NULL UNIQUE CHECK(length(token_hash)=64),
    created_at INTEGER NOT NULL CHECK(created_at > 0),
    expires_at INTEGER NOT NULL CHECK(expires_at > created_at),
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending','sent','consumed','revoked','expired','delivery_failed')),
    consumed_at INTEGER,
    updated_at INTEGER NOT NULL CHECK(updated_at > 0),
    CHECK((status='consumed' AND consumed_at IS NOT NULL)
       OR (status<>'consumed' AND consumed_at IS NULL))
);
CREATE UNIQUE INDEX password_recovery_one_active_per_user
    ON password_recovery_tokens(user_id)
    WHERE status IN ('pending','sent');
CREATE INDEX password_recovery_expiry_idx ON password_recovery_tokens(status,expires_at);

CREATE TRIGGER password_recovery_status_guard
BEFORE UPDATE OF status ON password_recovery_tokens
WHEN NOT (
    (OLD.status='pending' AND NEW.status IN ('sent','revoked','expired','delivery_failed'))
 OR (OLD.status='sent' AND NEW.status IN ('consumed','revoked','expired'))
)
BEGIN
    SELECT RAISE(ABORT, 'invalid password recovery status transition');
END;
CREATE TRIGGER password_recovery_identity_immutable
BEFORE UPDATE ON password_recovery_tokens
WHEN NEW.user_id IS NOT OLD.user_id
 OR NEW.token_hash IS NOT OLD.token_hash
 OR NEW.created_at IS NOT OLD.created_at
 OR NEW.expires_at IS NOT OLD.expires_at
BEGIN
    SELECT RAISE(ABORT, 'password recovery token identity is immutable');
END;
CREATE TRIGGER password_recovery_no_delete
BEFORE DELETE ON password_recovery_tokens
BEGIN
    SELECT RAISE(ABORT, 'password recovery token records are retained for audit');
END;

CREATE TABLE identity_lifecycle_events (
    id INTEGER PRIMARY KEY,
    actor_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    target_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    firm_id INTEGER REFERENCES firms(id) ON DELETE RESTRICT,
    invitation_id INTEGER REFERENCES identity_invitations(id) ON DELETE RESTRICT,
    recovery_token_id INTEGER REFERENCES password_recovery_tokens(id) ON DELETE RESTRICT,
    event_type TEXT NOT NULL CHECK(event_type IN (
        'invitation_created','invitation_sent','invitation_delivery_failed',
        'invitation_revoked','invitation_accepted','invitation_expired',
        'recovery_requested','recovery_sent','recovery_delivery_failed',
        'recovery_consumed','recovery_expired','recovery_revoked','recovery_rate_limited'
    )),
    detail_json TEXT NOT NULL DEFAULT '{}',
    created_at INTEGER NOT NULL CHECK(created_at > 0),
    CHECK(invitation_id IS NULL OR recovery_token_id IS NULL)
);
CREATE INDEX identity_lifecycle_events_created_idx ON identity_lifecycle_events(created_at,id);
CREATE INDEX identity_lifecycle_events_target_idx ON identity_lifecycle_events(target_user_id,created_at DESC,id DESC);
CREATE INDEX identity_lifecycle_events_firm_idx ON identity_lifecycle_events(firm_id,created_at DESC,id DESC);

CREATE TRIGGER identity_lifecycle_events_no_update
BEFORE UPDATE ON identity_lifecycle_events
BEGIN
    SELECT RAISE(ABORT, 'identity lifecycle events are append-only');
END;
CREATE TRIGGER identity_lifecycle_events_no_delete
BEFORE DELETE ON identity_lifecycle_events
BEGIN
    SELECT RAISE(ABORT, 'identity lifecycle events are append-only');
END;
