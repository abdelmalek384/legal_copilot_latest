-- Move independent authentication and case-workspace tables out of startup DDL.
-- Existing databases keep their data; fresh databases create these tables here
-- before request handlers run. Earlier migrations do not depend on these tables.
CREATE TABLE IF NOT EXISTS auth_sessions(
    token_hash TEXT PRIMARY KEY,
    user_id INTEGER,
    expires INTEGER
);
CREATE TABLE IF NOT EXISTS notes(
    id INTEGER PRIMARY KEY,
    case_id INTEGER,
    created_by INTEGER,
    text TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS fees(
    id INTEGER PRIMARY KEY,
    case_id INTEGER,
    title TEXT,
    amount REAL DEFAULT 0,
    paid REAL DEFAULT 0,
    due TEXT,
    note TEXT DEFAULT '',
    created_by INTEGER
);
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY,
    case_id INTEGER,
    title TEXT,
    assignee INTEGER,
    due TEXT,
    status TEXT DEFAULT 'open',
    created_by INTEGER
);
CREATE TABLE IF NOT EXISTS events(
    id INTEGER PRIMARY KEY,
    case_id INTEGER,
    who TEXT,
    at TEXT,
    text TEXT
);
CREATE TABLE IF NOT EXISTS sessions(
    id INTEGER PRIMARY KEY,
    case_id INTEGER,
    date TEXT,
    note TEXT,
    done INTEGER DEFAULT 0
);
