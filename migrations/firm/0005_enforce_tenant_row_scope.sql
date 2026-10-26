-- Every firm-scoped row must agree with this database's immutable tenant binding.
-- Fail closed on pre-existing ambiguous rows; do not silently rewrite ownership.
CREATE TABLE _tenant_row_scope_guard (ok INTEGER NOT NULL CHECK(ok = 1));
INSERT INTO _tenant_row_scope_guard(ok)
SELECT CASE WHEN
 EXISTS (SELECT 1 FROM cases c WHERE c.firm_id IS NOT (SELECT firm_id FROM tenant_database_binding WHERE singleton=1))
 OR EXISTS (SELECT 1 FROM docs d WHERE d.firm_id IS NOT (SELECT firm_id FROM tenant_database_binding WHERE singleton=1))
 OR EXISTS (SELECT 1 FROM document_extraction_reviews r WHERE r.firm_id IS NOT (SELECT firm_id FROM tenant_database_binding WHERE singleton=1))
 OR EXISTS (SELECT 1 FROM research_conversations rc WHERE rc.firm_id IS NOT (SELECT firm_id FROM tenant_database_binding WHERE singleton=1))
 OR EXISTS (SELECT 1 FROM case_deletion_audit a WHERE a.firm_id IS NOT (SELECT firm_id FROM tenant_database_binding WHERE singleton=1))
 THEN 0 ELSE 1 END;
DROP TABLE _tenant_row_scope_guard;

CREATE TRIGGER cases_tenant_firm_insert
BEFORE INSERT ON cases
WHEN NOT EXISTS (
 SELECT 1 FROM tenant_database_binding b WHERE b.singleton=1 AND b.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'case firm scope does not match tenant database'); END;
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
BEGIN SELECT RAISE(ABORT, 'document firm scope does not match tenant database'); END;
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
BEGIN SELECT RAISE(ABORT, 'review firm scope does not match tenant database'); END;
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
BEGIN SELECT RAISE(ABORT, 'research conversation firm scope does not match tenant database'); END;
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
BEGIN SELECT RAISE(ABORT, 'case deletion audit firm scope does not match tenant database'); END;
