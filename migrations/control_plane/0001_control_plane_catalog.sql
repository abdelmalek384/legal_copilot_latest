-- Initial control-plane firm/catalog foundation. Global identity and membership tables are added by migration 0003.
CREATE TABLE firms (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','provisioning','suspended','disabled')),
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE tenant_database_catalog (
 firm_id INTEGER PRIMARY KEY CHECK(firm_id > 0), database_file TEXT UNIQUE,
 status TEXT NOT NULL CHECK(status IN ('provisioning','provisioned','failed','disabled')),
 created_at TEXT NOT NULL DEFAULT (datetime('now')),
 updated_at TEXT NOT NULL DEFAULT (datetime('now')), last_error_code TEXT
);
CREATE INDEX idx_tenant_database_catalog_status ON tenant_database_catalog(status, updated_at);
