-- Finish moving index creation out of the startup schema string.
-- Legacy bootstrap still creates these tables and prerequisite columns before
-- apply_migrations() runs. Keep this migration additive and idempotent.
CREATE INDEX IF NOT EXISTS idx_login_attempts_window
    ON login_attempts(window_start, locked_until);
CREATE INDEX IF NOT EXISTS idx_case_deletion_audit_firm_id
    ON case_deletion_audit(firm_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_api_rate_limit_windows_start
    ON api_rate_limit_windows(window_start);
CREATE UNIQUE INDEX IF NOT EXISTS idx_legal_version_sha256
    ON legal_document_versions(original_sha256) WHERE original_sha256 IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_legal_versions_dates
    ON legal_document_versions(effective_date, repeal_date, legal_status);
CREATE INDEX IF NOT EXISTS idx_legal_versions_review
    ON legal_document_versions(review_status, status_verified);
CREATE INDEX IF NOT EXISTS idx_legal_review_events_version
    ON legal_review_events(version_id, reviewed_at);
CREATE INDEX IF NOT EXISTS idx_research_conversations_owner
    ON research_conversations(firm_id, user_id, updated_at);
CREATE INDEX IF NOT EXISTS idx_research_messages_conversation
    ON research_messages(conversation_id, id);
