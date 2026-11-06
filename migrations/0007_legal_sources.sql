-- Legal document metadata references this table, which is created before requests
-- run. SQLite permits the referencing table to be declared during legacy
-- bootstrap; migration ordering ensures the referenced table exists before use.
CREATE TABLE IF NOT EXISTS legal_sources(
    source_id TEXT PRIMARY KEY,
    authority TEXT NOT NULL,
    source_page TEXT NOT NULL,
    access_status TEXT NOT NULL DEFAULT 'unknown',
    collection_permission TEXT NOT NULL DEFAULT 'unknown'
        CHECK(collection_permission IN ('unknown','allowed','allowed_limited','prohibited','not_allowed_without_explicit_exception_or_license')),
    commercial_reuse_permission TEXT NOT NULL DEFAULT 'unknown',
    terms_url TEXT,
    terms_checked_on TEXT,
    permission_evidence TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
