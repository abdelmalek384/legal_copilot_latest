-- Preserve the legacy default-firm bootstrap without mutating data at startup.
-- INSERT OR IGNORE leaves any existing firm 1 record and name untouched.
INSERT OR IGNORE INTO firms(id, name) VALUES (1, 'Default Firm');
