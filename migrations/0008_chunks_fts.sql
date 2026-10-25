-- Move FTS5 index creation into versioned schema setup.
-- Existing chunks_fts virtual tables and their indexed rows are preserved.
-- As before, this migration does not rebuild missing/stale index contents.
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(norm);
