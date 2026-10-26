-- These triggers are installed before tenant_catalog writes the immutable binding.
-- SQLite resolves the binding table when the trigger executes, after provisioning.
CREATE TRIGGER cases_tenant_firm_insert
BEFORE INSERT ON cases
WHEN NOT EXISTS (
 SELECT 1 FROM tenant_database_binding b WHERE b.singleton=1 AND b.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'case firm scope mismatch'); END;
CREATE TRIGGER cases_tenant_firm_update
BEFORE UPDATE OF firm_id ON cases
WHEN NOT EXISTS (
 SELECT 1 FROM tenant_database_binding b WHERE b.singleton=1 AND b.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'case firm scope does not match tenant database'); END;

CREATE TRIGGER docs_tenant_firm_insert
BEFORE INSERT ON docs
WHEN NOT EXISTS (
 SELECT 1 FROM tenant_database_binding b WHERE b.singleton=1 AND b.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'document case/firm scope mismatch'); END;
CREATE TRIGGER docs_tenant_firm_update
BEFORE UPDATE OF firm_id ON docs
WHEN NOT EXISTS (
 SELECT 1 FROM tenant_database_binding b WHERE b.singleton=1 AND b.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'document firm scope does not match tenant database'); END;

CREATE TRIGGER reviews_tenant_firm_insert
BEFORE INSERT ON document_extraction_reviews
WHEN NOT EXISTS (
 SELECT 1 FROM tenant_database_binding b WHERE b.singleton=1 AND b.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'document extraction review scope mismatch'); END;
CREATE TRIGGER reviews_tenant_firm_update
BEFORE UPDATE OF firm_id ON document_extraction_reviews
WHEN NOT EXISTS (
 SELECT 1 FROM tenant_database_binding b WHERE b.singleton=1 AND b.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'review firm scope does not match tenant database'); END;

CREATE TRIGGER research_conversations_tenant_firm_insert
BEFORE INSERT ON research_conversations
WHEN NOT EXISTS (
 SELECT 1 FROM tenant_database_binding b WHERE b.singleton=1 AND b.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'research conversation firm scope mismatch'); END;
CREATE TRIGGER research_conversations_tenant_firm_update
BEFORE UPDATE OF firm_id ON research_conversations
WHEN NOT EXISTS (
 SELECT 1 FROM tenant_database_binding b WHERE b.singleton=1 AND b.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'research conversation firm scope does not match tenant database'); END;

CREATE TRIGGER case_deletion_audit_tenant_firm_insert
BEFORE INSERT ON case_deletion_audit
WHEN NOT EXISTS (
 SELECT 1 FROM tenant_database_binding b WHERE b.singleton=1 AND b.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'case deletion audit firm scope mismatch'); END;
CREATE TRIGGER case_deletion_audit_tenant_firm_update
BEFORE UPDATE OF firm_id ON case_deletion_audit
WHEN NOT EXISTS (
 SELECT 1 FROM tenant_database_binding b WHERE b.singleton=1 AND b.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'case deletion audit firm scope does not match tenant database'); END;
