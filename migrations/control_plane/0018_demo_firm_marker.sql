-- Mark synthetic onboarding firms so they are unmistakable and excluded from pilot usage metrics.
ALTER TABLE firms ADD COLUMN is_demo INTEGER NOT NULL DEFAULT 0 CHECK(is_demo IN (0,1));
