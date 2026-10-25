-- Fresh control-plane identity and membership schema only.
-- This migration intentionally does not import or reconcile legacy user rows.
-- Application writers must populate email_normalized using the shared canonical
-- normalizer (trim + Unicode casefold); the unique key is global to this database.
CREATE TABLE users (
 id INTEGER PRIMARY KEY,
 name TEXT NOT NULL CHECK(length(trim(name)) > 0),
 email_display TEXT NOT NULL CHECK(length(trim(email_display)) > 0),
 email_normalized TEXT NOT NULL COLLATE NOCASE UNIQUE
   CHECK(length(email_normalized) > 0 AND email_normalized = trim(email_normalized)),
 password_hash TEXT NOT NULL CHECK(length(password_hash) > 0),
 status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','disabled')),
 created_at TEXT NOT NULL DEFAULT (datetime('now')),
 updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE firm_memberships (
 id INTEGER PRIMARY KEY,
 user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
 firm_id INTEGER NOT NULL REFERENCES firms(id) ON DELETE RESTRICT,
 firm_role TEXT NOT NULL CHECK(firm_role IN ('admin','lawyer','junior')),
 status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','suspended','revoked')),
 created_at TEXT NOT NULL DEFAULT (datetime('now')),
 updated_at TEXT NOT NULL DEFAULT (datetime('now')),
 created_by_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
 UNIQUE(user_id, firm_id)
);
CREATE INDEX idx_firm_memberships_user_status ON firm_memberships(user_id, status);
CREATE INDEX idx_firm_memberships_firm_status ON firm_memberships(firm_id, status);
CREATE TABLE user_platform_roles (
 user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
 role_name TEXT NOT NULL CHECK(role_name IN ('platform_admin','platform_reviewer')),
 granted_at TEXT NOT NULL DEFAULT (datetime('now')),
 granted_by_user_id INTEGER REFERENCES users(id) ON DELETE RESTRICT,
 PRIMARY KEY(user_id, role_name)
);
CREATE INDEX idx_user_platform_roles_role ON user_platform_roles(role_name, user_id);
