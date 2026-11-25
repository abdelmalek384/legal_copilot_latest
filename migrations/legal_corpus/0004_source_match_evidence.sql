-- Append-only, version-bound source-match evidence for isolated non-production tests.
-- This records machine evidence only; it does not confer legal verification or reuse rights.
CREATE TABLE legal_source_match_evidence (
    evidence_id INTEGER PRIMARY KEY,
    version_id INTEGER NOT NULL REFERENCES legal_document_versions(version_id),
    source_id TEXT NOT NULL REFERENCES legal_sources(source_id),
    evidence_revision INTEGER NOT NULL CHECK(evidence_revision > 0),
    validator_passed INTEGER NOT NULL CHECK(validator_passed IN (0,1)),
    original_capture_sha256 TEXT NOT NULL
        CHECK(length(original_capture_sha256)=64 AND lower(original_capture_sha256) NOT GLOB '*[^0-9a-f]*'),
    independent_copy_source_id TEXT NOT NULL REFERENCES legal_sources(source_id),
    independent_copy_sha256 TEXT NOT NULL
        CHECK(length(independent_copy_sha256)=64 AND lower(independent_copy_sha256) NOT GLOB '*[^0-9a-f]*'),
    publication_date TEXT NOT NULL CHECK(length(publication_date)=10 AND publication_date GLOB '????-??-??'),
    effective_date TEXT NOT NULL CHECK(length(effective_date)=10 AND effective_date GLOB '????-??-??'),
    reuse_rights_evidence TEXT NOT NULL CHECK(length(trim(reuse_rights_evidence)) > 0),
    reuse_rights_evidence_url TEXT NOT NULL CHECK(reuse_rights_evidence_url LIKE 'https://%'),
    article_inventory_complete INTEGER NOT NULL CHECK(article_inventory_complete IN (0,1)),
    differences_resolved_against_primary INTEGER NOT NULL CHECK(differences_resolved_against_primary IN (0,1)),
    publication_and_effective_dates_verified INTEGER NOT NULL CHECK(publication_and_effective_dates_verified IN (0,1)),
    reuse_rights_allowed INTEGER NOT NULL CHECK(reuse_rights_allowed IN (0,1)),
    recorded_by TEXT NOT NULL CHECK(length(trim(recorded_by)) > 0),
    recorded_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(version_id, evidence_revision),
    CHECK(source_id <> independent_copy_source_id)
);

CREATE TABLE legal_source_match_evidence_uses (
    evidence_id INTEGER NOT NULL REFERENCES legal_source_match_evidence(evidence_id),
    approved_use TEXT NOT NULL CHECK(approved_use IN (
        'collection','storage','text_extraction','indexing',
        'commercial_product_use','excerpt_display'
    )),
    PRIMARY KEY(evidence_id, approved_use)
);

CREATE TRIGGER legal_source_match_evidence_exact_version_insert
BEFORE INSERT ON legal_source_match_evidence
WHEN NOT EXISTS (
    SELECT 1
    FROM legal_document_versions v
    JOIN legal_documents d ON d.document_id=v.document_id
    WHERE v.version_id=NEW.version_id
      AND d.source_id=NEW.source_id
      AND v.publication_date=NEW.publication_date
      AND v.effective_date=NEW.effective_date
      AND lower(COALESCE(v.original_sha256,''))=lower(NEW.original_capture_sha256)
)
BEGIN
    SELECT RAISE(ABORT, 'source-match evidence does not match exact source/version');
END;

CREATE TRIGGER legal_source_match_evidence_no_update
BEFORE UPDATE ON legal_source_match_evidence
BEGIN
    SELECT RAISE(ABORT, 'source-match evidence is append-only');
END;
CREATE TRIGGER legal_source_match_evidence_no_delete
BEFORE DELETE ON legal_source_match_evidence
BEGIN
    SELECT RAISE(ABORT, 'source-match evidence is append-only');
END;
CREATE TRIGGER legal_source_match_evidence_uses_no_update
BEFORE UPDATE ON legal_source_match_evidence_uses
BEGIN
    SELECT RAISE(ABORT, 'source-match approved uses are append-only');
END;
CREATE TRIGGER legal_source_match_evidence_uses_no_delete
BEFORE DELETE ON legal_source_match_evidence_uses
BEGIN
    SELECT RAISE(ABORT, 'source-match approved uses are append-only');
END;

CREATE INDEX idx_legal_source_match_evidence_version_revision
    ON legal_source_match_evidence(version_id, evidence_revision DESC);
