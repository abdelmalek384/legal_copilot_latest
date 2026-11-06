-- Add a firm ownership constraint to the tenant catalog without rewriting migration 0001.
-- Existing orphaned catalog rows deliberately fail this migration and must be reconciled first.
DROP INDEX IF EXISTS idx_tenant_database_catalog_status;
CREATE TABLE tenant_database_catalog_new (
 firm_id INTEGER PRIMARY KEY CHECK(firm_id > 0) REFERENCES firms(id) ON DELETE RESTRICT,
 database_file TEXT UNIQUE,
 status TEXT NOT NULL CHECK(status IN ('provisioning','provisioned','failed','disabled')),
 created_at TEXT NOT NULL DEFAULT (datetime('now')),
 updated_at TEXT NOT NULL DEFAULT (datetime('now')),
 last_error_code TEXT
);
INSERT INTO tenant_database_catalog_new
 (firm_id, database_file, status, created_at, updated_at, last_error_code)
SELECT firm_id, database_file, status, created_at, updated_at, last_error_code
FROM tenant_database_catalog;
DROP TABLE tenant_database_catalog;
ALTER TABLE tenant_database_catalog_new RENAME TO tenant_database_catalog;
CREATE INDEX idx_tenant_database_catalog_status ON tenant_database_catalog(status, updated_at);
