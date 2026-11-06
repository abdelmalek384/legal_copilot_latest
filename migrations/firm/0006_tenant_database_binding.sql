-- Tenant identity binding is schema, while the bound firm ID is per-database data.
CREATE TABLE tenant_database_binding (
    singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
    firm_id INTEGER NOT NULL CHECK(firm_id > 0),
    bound_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TRIGGER tenant_database_binding_no_update
BEFORE UPDATE ON tenant_database_binding
BEGIN
    SELECT RAISE(ABORT, 'tenant database firm binding is immutable');
END;
CREATE TRIGGER tenant_database_binding_no_delete
BEFORE DELETE ON tenant_database_binding
BEGIN
    SELECT RAISE(ABORT, 'tenant database firm binding is immutable');
END;
