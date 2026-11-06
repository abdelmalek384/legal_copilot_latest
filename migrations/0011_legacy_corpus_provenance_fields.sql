-- Keep the explicitly opt-in shared-database development path schema-compatible
-- with corpus provenance fields used by the review dashboard. This does not
-- migrate legacy customer data; it only upgrades the schema of the configured
-- local test/development database.
-- @add-column-if-missing legal_sources source_class
ALTER TABLE legal_sources ADD COLUMN source_class TEXT NOT NULL DEFAULT 'unknown';
-- @add-column-if-missing legal_document_versions text_sha256
ALTER TABLE legal_document_versions ADD COLUMN text_sha256 TEXT;
-- @add-column-if-missing legal_document_versions publication_evidence_url
ALTER TABLE legal_document_versions ADD COLUMN publication_evidence_url TEXT;
CREATE INDEX IF NOT EXISTS idx_legal_sources_source_class
    ON legal_sources(source_class);
CREATE INDEX IF NOT EXISTS idx_legal_versions_review_legal_status
    ON legal_document_versions(review_status, legal_status);
