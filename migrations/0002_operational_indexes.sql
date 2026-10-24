-- Move operational indexes out of app.py startup DDL.
-- Required tables and columns are created/validated by the legacy bootstrap
-- before apply_migrations() runs. IF NOT EXISTS preserves older installations.
CREATE INDEX IF NOT EXISTS idx_cases_firm ON cases(firm_id);
CREATE INDEX IF NOT EXISTS idx_members_user_case ON members(user_id,case_id);
CREATE INDEX IF NOT EXISTS idx_deadlines_case_due ON deadlines(case_id,due,status);
CREATE INDEX IF NOT EXISTS idx_docs_case_added ON docs(case_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_doc_reviews_document
    ON document_extraction_reviews(firm_id,document_id,id DESC);
