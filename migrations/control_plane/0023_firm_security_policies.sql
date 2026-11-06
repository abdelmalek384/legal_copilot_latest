-- Per-firm MFA policy, enforced during authenticated request context resolution.
CREATE TABLE firm_security_policies (
    firm_id INTEGER PRIMARY KEY REFERENCES firms(id) ON DELETE RESTRICT,
    require_mfa_for_admins INTEGER NOT NULL DEFAULT 0 CHECK(require_mfa_for_admins IN (0,1)),
    require_mfa_for_everyone INTEGER NOT NULL DEFAULT 0 CHECK(require_mfa_for_everyone IN (0,1)),
    updated_by_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
    updated_at INTEGER NOT NULL
);
CREATE TABLE firm_security_policy_audit (
    id INTEGER PRIMARY KEY,
    firm_id INTEGER NOT NULL REFERENCES firms(id) ON DELETE RESTRICT,
    actor_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    before_json TEXT NOT NULL,
    after_json TEXT NOT NULL,
    created_at INTEGER NOT NULL
);
CREATE INDEX idx_firm_security_policy_audit ON firm_security_policy_audit(firm_id,created_at DESC,id);
