-- One firm-scoped onboarding stopwatch. No user IDs or client/matter content are stored.
CREATE TABLE firm_onboarding_timing (
    firm_id INTEGER PRIMARY KEY REFERENCES firms(id) ON DELETE RESTRICT,
    started_at INTEGER NOT NULL CHECK(started_at > 0),
    completed_at INTEGER,
    completion_seconds INTEGER,
    CHECK(
        (completed_at IS NULL AND completion_seconds IS NULL)
        OR (completed_at IS NOT NULL AND completion_seconds IS NOT NULL
            AND completed_at >= started_at AND completion_seconds >= 0)
    )
);

CREATE TRIGGER firm_onboarding_started_at_immutable
BEFORE UPDATE OF started_at ON firm_onboarding_timing
WHEN NEW.started_at IS NOT OLD.started_at
BEGIN
    SELECT RAISE(ABORT, 'onboarding start time is immutable');
END;

CREATE TRIGGER firm_onboarding_completion_immutable
BEFORE UPDATE OF completed_at,completion_seconds ON firm_onboarding_timing
WHEN OLD.completed_at IS NOT NULL
 AND (NEW.completed_at IS NOT OLD.completed_at
      OR NEW.completion_seconds IS NOT OLD.completion_seconds)
BEGIN
    SELECT RAISE(ABORT, 'onboarding completion time is immutable');
END;

CREATE TRIGGER firm_onboarding_no_delete
BEFORE DELETE ON firm_onboarding_timing
BEGIN
    SELECT RAISE(ABORT, 'onboarding timing evidence is retained for audit');
END;
