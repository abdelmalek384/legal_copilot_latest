-- Guard firm-scoped chunk/document/review relationships before adding enforcement.
CREATE TABLE _firm_scope_guard (ok INTEGER NOT NULL CHECK(ok = 1));
INSERT INTO _firm_scope_guard(ok)
SELECT CASE WHEN EXISTS (
 SELECT 1 FROM chunks ch LEFT JOIN docs d ON d.id=ch.document_id
 WHERE ch.document_id IS NOT NULL AND (d.id IS NULL OR d.case_id IS NOT ch.case_id)
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
DROP TABLE _firm_scope_guard;
CREATE TRIGGER chunks_document_case_scope_insert
BEFORE INSERT ON chunks
WHEN NEW.document_id IS NOT NULL AND NOT EXISTS (
 SELECT 1 FROM docs d WHERE d.id=NEW.document_id AND d.case_id=NEW.case_id
)
BEGIN SELECT RAISE(ABORT, 'chunk document/case scope mismatch'); END;
CREATE TRIGGER chunks_document_case_scope_update
BEFORE UPDATE OF document_id, case_id ON chunks
WHEN NEW.document_id IS NOT NULL AND NOT EXISTS (
 SELECT 1 FROM docs d WHERE d.id=NEW.document_id AND d.case_id=NEW.case_id
)
BEGIN SELECT RAISE(ABORT, 'chunk document/case scope mismatch'); END;
CREATE TRIGGER document_review_scope_insert
BEFORE INSERT ON document_extraction_reviews
WHEN NOT EXISTS (
 SELECT 1 FROM docs d
 JOIN cases c ON c.id=d.case_id
 JOIN chunks ch ON ch.id=NEW.chunk_id
 WHERE d.id=NEW.document_id AND d.case_id=NEW.case_id
 AND ch.case_id=NEW.case_id AND ch.document_id=NEW.document_id
 AND d.firm_id=NEW.firm_id AND c.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'document extraction review scope mismatch'); END;
CREATE TRIGGER document_review_scope_update
BEFORE UPDATE OF document_id, case_id, chunk_id, firm_id ON document_extraction_reviews
WHEN NOT EXISTS (
 SELECT 1 FROM docs d
 JOIN cases c ON c.id=d.case_id
 JOIN chunks ch ON ch.id=NEW.chunk_id
 WHERE d.id=NEW.document_id AND d.case_id=NEW.case_id
 AND ch.case_id=NEW.case_id AND ch.document_id=NEW.document_id
 AND d.firm_id=NEW.firm_id AND c.firm_id=NEW.firm_id
)
BEGIN SELECT RAISE(ABORT, 'document extraction review scope mismatch'); END;
