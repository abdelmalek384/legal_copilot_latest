-- Move the legal amendment/repeal relationship table out of the startup schema.
-- legal_document_versions is created by the legacy bootstrap before migrations run.
CREATE TABLE IF NOT EXISTS legal_version_relations(
    relation_id INTEGER PRIMARY KEY,
    from_version_id INTEGER NOT NULL REFERENCES legal_document_versions(version_id),
    to_version_id INTEGER NOT NULL REFERENCES legal_document_versions(version_id),
    relation_type TEXT NOT NULL CHECK(relation_type IN ('amends','repeals','consolidates','corrects','supersedes','implements')),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK(from_version_id <> to_version_id),
    UNIQUE(from_version_id, to_version_id, relation_type)
);
