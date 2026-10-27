-- Add explicit source classification and publication/text provenance fields.
-- Existing records remain unknown until evidence-backed reviewers classify them.
ALTER TABLE legal_sources
    ADD COLUMN source_class TEXT NOT NULL DEFAULT 'unknown';
ALTER TABLE legal_document_versions
    ADD COLUMN text_sha256 TEXT;
ALTER TABLE legal_document_versions
    ADD COLUMN publication_evidence_url TEXT;
CREATE INDEX idx_legal_sources_source_class
    ON legal_sources(source_class);
CREATE INDEX idx_legal_versions_review_legal_status
    ON legal_document_versions(review_status, legal_status);
