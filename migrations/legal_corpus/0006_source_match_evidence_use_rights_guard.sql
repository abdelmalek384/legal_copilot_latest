-- An approved-use row must never contradict its parent evidence packet's rights flag.
-- Evidence rows are append-only; a later permissive assessment must be a new revision.
CREATE TRIGGER legal_source_match_evidence_use_requires_rights
BEFORE INSERT ON legal_source_match_evidence_uses
WHEN NOT EXISTS (
    SELECT 1
    FROM legal_source_match_evidence e
    WHERE e.evidence_id=NEW.evidence_id
      AND e.reuse_rights_allowed=1
)
BEGIN
    SELECT RAISE(ABORT, 'approved use requires affirmative reuse-rights evidence');
END;
