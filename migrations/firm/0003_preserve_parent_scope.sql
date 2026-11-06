-- Fail closed on inconsistent document/case firm ownership, then preserve parent-child scope on updates.
CREATE TABLE _firm_parent_scope_guard (ok INTEGER NOT NULL CHECK(ok = 1));
INSERT INTO _firm_parent_scope_guard(ok)
SELECT CASE WHEN EXISTS (
 SELECT 1 FROM docs d LEFT JOIN cases c ON c.id=d.case_id
 WHERE c.id IS NULL OR d.firm_id IS NOT c.firm_id
) OR EXISTS (
 SELECT 1 FROM chunks ch JOIN docs d ON d.id=ch.document_id
 WHERE ch.document_id IS NOT NULL AND ch.case_id IS NOT d.case_id
) OR EXISTS (
 SELECT 1 FROM document_extraction_reviews r
 LEFT JOIN docs d ON d.id=r.document_id
 LEFT JOIN cases c ON c.id=r.case_id
 LEFT JOIN chunks ch ON ch.id=r.chunk_id
 WHERE d.id IS NULL OR c.id IS NULL OR ch.id IS NULL
 OR d.case_id IS NOT r.case_id OR ch.case_id IS NOT r.case_id
 OR ch.document_id IS NOT r.document_id OR d.firm_id IS NOT r.firm_id
 OR c.firm_id IS NOT r.firm_id
) THEN 0 ELSE 1 END;
DROP TABLE _firm_parent_scope_guard;

CREATE TRIGGER docs_firm_case_scope_insert
BEFORE INSERT ON docs
WHEN NOT EXISTS (
 SELECT 1 FROM cases c WHERE c.id=NEW.case_id AND c.firm_id IS NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'document case/firm scope mismatch'); END;

CREATE TRIGGER docs_firm_case_scope_update
BEFORE UPDATE OF case_id, firm_id ON docs
WHEN NOT EXISTS (
 SELECT 1 FROM cases c WHERE c.id=NEW.case_id AND c.firm_id IS NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'document case/firm scope mismatch'); END;

CREATE TRIGGER docs_child_scope_update
BEFORE UPDATE OF case_id, firm_id ON docs
WHEN EXISTS (
 SELECT 1 FROM chunks ch
 WHERE ch.document_id=OLD.id AND ch.case_id IS NOT NEW.case_id
) OR EXISTS (
 SELECT 1 FROM document_extraction_reviews r
 LEFT JOIN chunks ch ON ch.id=r.chunk_id
 WHERE r.document_id=OLD.id AND (
   r.case_id IS NOT NEW.case_id OR r.firm_id IS NOT NEW.firm_id
   OR ch.id IS NULL OR ch.case_id IS NOT NEW.case_id
   OR ch.document_id IS NOT OLD.id
 )
)
BEGIN SELECT RAISE(ABORT, 'document child scope mismatch'); END;

CREATE TRIGGER cases_firm_child_scope_update
BEFORE UPDATE OF firm_id ON cases
WHEN EXISTS (
 SELECT 1 FROM docs d WHERE d.case_id=OLD.id AND d.firm_id IS NOT NEW.firm_id
) OR EXISTS (
 SELECT 1 FROM document_extraction_reviews r
 WHERE r.case_id=OLD.id AND r.firm_id IS NOT NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'case firm scope mismatch'); END;
