-- Persistent firm-local client profiles; existing matters are linked by normalized client name.
CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK(length(trim(name)) BETWEEN 2 AND 200),
    normalized_name TEXT NOT NULL UNIQUE CHECK(length(trim(normalized_name)) BETWEEN 2 AND 200),
    phone TEXT NOT NULL DEFAULT '' CHECK(length(phone)<=30),
    email TEXT NOT NULL DEFAULT '' CHECK(length(email)<=200),
    address TEXT NOT NULL DEFAULT '' CHECK(length(address)<=300),
    notes TEXT NOT NULL DEFAULT '' CHECK(length(notes)<=4000),
    created_by INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

ALTER TABLE cases ADD COLUMN client_id INTEGER REFERENCES clients(id) ON DELETE SET NULL;

INSERT INTO clients(name,normalized_name,created_by,created_at,updated_at)
SELECT MIN(trim(client)),lower(trim(client)),MIN(created_by),MIN(created_at),MAX(created_at)
FROM cases
WHERE length(trim(COALESCE(client,''))) BETWEEN 2 AND 200
GROUP BY lower(trim(client));

UPDATE cases
SET client_id=(SELECT id FROM clients WHERE normalized_name=lower(trim(cases.client)))
WHERE length(trim(COALESCE(client,''))) BETWEEN 2 AND 200;

CREATE INDEX idx_cases_client_id ON cases(client_id,id);
