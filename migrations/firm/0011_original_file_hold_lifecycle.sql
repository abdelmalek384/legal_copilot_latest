-- Complete the audited legal-hold transition contract for retained original files.
-- The database enforces transition metadata and writes the audit event in the same transaction.
ALTER TABLE original_file_objects ADD COLUMN hold_release_reason TEXT;

CREATE TRIGGER original_file_hold_set_guard
BEFORE UPDATE OF legal_hold ON original_file_objects
WHEN OLD.legal_hold = 0 AND NEW.legal_hold = 1
 AND (
    NEW.hold_reason IS NULL OR length(trim(NEW.hold_reason)) = 0
    OR NEW.hold_set_by IS NULL OR NEW.hold_set_at IS NULL
    OR NEW.hold_released_by IS NOT NULL OR NEW.hold_released_at IS NOT NULL
    OR NEW.hold_release_reason IS NOT NULL
 )
BEGIN
    SELECT RAISE(ABORT, 'legal hold requires complete set metadata');
END;

CREATE TRIGGER original_file_hold_release_guard
BEFORE UPDATE OF legal_hold ON original_file_objects
WHEN OLD.legal_hold = 1 AND NEW.legal_hold = 0
 AND (
    NEW.hold_released_by IS NULL OR NEW.hold_released_at IS NULL
    OR NEW.hold_release_reason IS NULL OR length(trim(NEW.hold_release_reason)) = 0
 )
BEGIN
    SELECT RAISE(ABORT, 'legal hold release requires complete release metadata');
END;

CREATE TRIGGER original_file_hold_details_immutable
BEFORE UPDATE OF hold_reason, hold_set_by, hold_set_at ON original_file_objects
WHEN OLD.legal_hold = 1
 AND (
    NEW.hold_reason IS NOT OLD.hold_reason
    OR NEW.hold_set_by IS NOT OLD.hold_set_by
    OR NEW.hold_set_at IS NOT OLD.hold_set_at
 )
BEGIN
    SELECT RAISE(ABORT, 'active legal hold metadata is immutable');
END;

CREATE TRIGGER original_file_hold_set_audit
AFTER UPDATE OF legal_hold ON original_file_objects
WHEN OLD.legal_hold = 0 AND NEW.legal_hold = 1
BEGIN
    INSERT INTO security_audit_events(firm_id, user_id, event)
    VALUES(NEW.firm_id, NEW.hold_set_by, 'original_document_legal_hold_set:' || NEW.document_id);
END;

CREATE TRIGGER original_file_hold_release_audit
AFTER UPDATE OF legal_hold ON original_file_objects
WHEN OLD.legal_hold = 1 AND NEW.legal_hold = 0
BEGIN
    INSERT INTO security_audit_events(firm_id, user_id, event)
    VALUES(NEW.firm_id, NEW.hold_released_by, 'original_document_legal_hold_released:' || NEW.document_id);
END;
