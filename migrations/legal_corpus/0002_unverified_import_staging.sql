-- Unlinked bulk imports are quarantined as review candidates, never searchable corpus chunks.
CREATE TABLE legal_import_staging (
 id INTEGER PRIMARY KEY,
 law TEXT NOT NULL,
 article TEXT NOT NULL,
 text TEXT NOT NULL,
 norm TEXT NOT NULL,
 source TEXT,
 submitted_by_user_id INTEGER,
 status TEXT NOT NULL DEFAULT 'pending_review'
   CHECK(status IN ('pending_review','accepted','rejected')),
 created_at TEXT NOT NULL DEFAULT (datetime('now')),
 reviewed_at TEXT,
 reviewed_by_user_id INTEGER,
 review_note TEXT NOT NULL DEFAULT ''
);
CREATE INDEX idx_legal_import_staging_status ON legal_import_staging(status, id);
