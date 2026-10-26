-- Runtime authentication and global abuse-throttle state belongs to the control plane.
CREATE TABLE auth_sessions (
 token_hash TEXT PRIMARY KEY,
 user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 expires INTEGER NOT NULL CHECK(expires > 0)
);
CREATE INDEX idx_auth_sessions_user_id ON auth_sessions(user_id);
CREATE INDEX idx_auth_sessions_expires ON auth_sessions(expires);
CREATE TABLE login_attempts (
 email TEXT PRIMARY KEY,
 failures INTEGER NOT NULL DEFAULT 0 CHECK(failures >= 0),
 window_start INTEGER NOT NULL DEFAULT 0,
 locked_until INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE api_rate_limit_windows (
 bucket TEXT NOT NULL,
 client_key TEXT NOT NULL,
 window_start INTEGER NOT NULL,
 hits INTEGER NOT NULL DEFAULT 0 CHECK(hits >= 0),
 PRIMARY KEY(bucket, client_key, window_start)
);
CREATE INDEX idx_api_rate_limit_window_start ON api_rate_limit_windows(window_start);
