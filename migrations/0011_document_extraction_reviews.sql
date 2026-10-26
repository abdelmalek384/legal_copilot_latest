-- Extraction-review records are independent of the legacy bootstrap's
-- prerequisite-column compatibility work and belong in the versioned ledger.
CREATE TABLE IF NOT EXISTS document_extraction_reviews (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL,
    case_id INTEGER NOT NULL,
    firm_id INTEGER NOT NULL,
    chunk_id INTEGER NOT NULL,
    reviewer_user_id INTEGER NOT NULL,
    outcome TEXT NOT NULL CHECK(outcome IN ('accepted','corrected','needs_recheck')),
    original_text TEXT NOT NULL,
    reviewed_text TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    page_reference TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
