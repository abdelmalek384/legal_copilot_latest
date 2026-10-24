"""Regression tests for safe legacy firm-ownership classification."""
import sqlite3
import time
from unittest.mock import patch

from fastapi import HTTPException

import app


def test_legacy_rows_without_firm_columns_are_quarantined_not_assigned():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    try:
        # Simulate a pre-firm-aware database before app startup migrations.
        db.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE,
                pw TEXT, role TEXT DEFAULT 'lawyer'
            );
            CREATE TABLE cases (
                id INTEGER PRIMARY KEY, title TEXT, client TEXT, created_by INTEGER
            );
            INSERT INTO users(id, name, email, pw) VALUES
                (7, 'Legacy User', 'legacy@example.test', 'not-a-real-password');
            INSERT INTO cases(id, title, created_by) VALUES
                (19, 'Legacy Case', 7);
        """)

        app._ensure_legacy_firm_ownership(db)

        user_cols = {row[1]: row for row in db.execute("PRAGMA table_info(users)")}
        case_cols = {row[1]: row for row in db.execute("PRAGMA table_info(cases)")}
        assert user_cols["firm_id"][4] is None  # no DEFAULT 1
        assert case_cols["firm_id"][4] is None  # no DEFAULT 1
        assert db.execute("SELECT firm_id FROM users WHERE id=7").fetchone()[0] is None
        assert db.execute("SELECT firm_id FROM cases WHERE id=19").fetchone()[0] is None

        rows = db.execute(
            "SELECT entity_type, entity_id, observed_firm_id, reason "
            "FROM tenant_ownership_quarantine ORDER BY entity_type"
        ).fetchall()
        assert [(row["entity_type"], row["entity_id"], row["observed_firm_id"], row["reason"])
                for row in rows] == [
                    ("case", 19, None, "missing_firm_ownership"),
                    ("user", 7, None, "missing_firm_ownership"),
                ]

        # Startup may run repeatedly; quarantine evidence must not duplicate.
        app._ensure_legacy_firm_ownership(db)
        assert db.execute("SELECT COUNT(*) FROM tenant_ownership_quarantine").fetchone()[0] == 2
    finally:
        db.close()


def test_explicitly_owned_rows_are_not_quarantined():
    db = sqlite3.connect(":memory:")
    try:
        db.executescript("""
            CREATE TABLE firms(id INTEGER PRIMARY KEY, name TEXT);
            CREATE TABLE users(id INTEGER PRIMARY KEY, firm_id INTEGER DEFAULT 1);
            CREATE TABLE cases(id INTEGER PRIMARY KEY, firm_id INTEGER DEFAULT 1);
            INSERT INTO firms VALUES (1, 'Default Firm');
            INSERT INTO users VALUES (1, 1);
            INSERT INTO cases VALUES (1, 1);
        """)
        app._ensure_legacy_firm_ownership(db)
        assert db.execute("SELECT COUNT(*) FROM tenant_ownership_quarantine").fetchone()[0] == 0
    finally:
        db.close()



def test_existing_session_for_unclassified_user_is_revoked():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    token = "legacy-session-token"
    try:
        db.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY, firm_id INTEGER, active INTEGER
            );
            CREATE TABLE auth_sessions (
                token_hash TEXT PRIMARY KEY, user_id INTEGER, expires INTEGER
            );
        """)
        db.execute("INSERT INTO users(id, firm_id, active) VALUES(1, NULL, 1)")
        db.execute(
            "INSERT INTO auth_sessions(token_hash, user_id, expires) VALUES(?,?,?)",
            (app.sha(token), 1, int(time.time()) + 3600),
        )
        db.commit()

        with patch("app.conn", return_value=db):
            try:
                app.user(request=None, session_cookie=token)
            except HTTPException as exc:
                assert exc.status_code == 401
            else:
                raise AssertionError("unclassified legacy account session must be denied")

        assert db.execute("SELECT COUNT(*) FROM auth_sessions").fetchone()[0] == 0
    finally:
        db.close()
