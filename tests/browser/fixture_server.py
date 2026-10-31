"""Disposable, synthetic-only application server for browser acceptance tests."""
from __future__ import annotations

import json
import os
from pathlib import Path

import uvicorn

import app
from database_runtime import DatabaseRuntime


PASSWORD = "Synthetic-Browser-Only-Passphrase-2026!"


def bootstrap() -> None:
    """Create isolated databases and fixtures; never reads production paths or data."""
    runtime = DatabaseRuntime.from_env()
    runtime.initialize()
    firm_a, _ = runtime.provision_firm("Synthetic Acceptance Firm A")
    firm_b, _ = runtime.provision_firm("Synthetic Acceptance Firm B")

    owner_a = runtime.create_initial_firm_owner(
        firm_a, "Synthetic Firm A Owner", "owner-a@example.test", app.hash_pw(PASSWORD)
    )
    owner_b = runtime.create_initial_firm_owner(
        firm_b, "Synthetic Firm B Owner", "owner-b@example.test", app.hash_pw(PASSWORD)
    )
    reviewer_id = runtime.create_global_identity(
        "Synthetic Platform Reviewer", "reviewer@example.test", app.hash_pw(PASSWORD)
    )
    runtime.create_firm_membership(reviewer_id, firm_a, "lawyer")
    control = runtime.control_connection()
    control.execute(
        "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,?)",
        (reviewer_id, "platform_reviewer"),
    )
    control.commit()

    firm_b_context = runtime.resolve_context(owner_b, firm_b)
    firm_b_db = runtime.firm_connection(firm_b_context)
    cursor = firm_b_db.execute(
        "INSERT INTO cases(title,created_by,firm_id) VALUES(?,?,?)",
        ("CROSS_FIRM_PRIVATE_SENTINEL_7D3A", owner_b, firm_b),
    )
    case_b_id = int(cursor.lastrowid)
    firm_b_db.commit()

    corpus = runtime.legal_corpus_connection()
    corpus.execute(
        """INSERT INTO legal_sources(
               source_id,authority,source_page,collection_permission,commercial_reuse_permission
           ) VALUES(?,?,?,?,?)""",
        (
            "SYNTHETIC-BROWSER-SOURCE-2026",
            "Synthetic Browser Authority",
            "https://example.invalid/synthetic-source",
            "unknown",
            "unknown",
        ),
    )
    corpus.execute(
        """INSERT INTO legal_documents(
               document_id,source_id,official_title,document_type,practice_area,law_number,law_year
           ) VALUES(?,?,?,?,?,?,?)""",
        (
            "SYNTHETIC-BROWSER-DOC-2026",
            "SYNTHETIC-BROWSER-SOURCE-2026",
            "SYNTHETIC METADATA ONLY INSTRUMENT 2026",
            "law",
            "synthetic_test_only",
            "999",
            2026,
        ),
    )
    corpus.commit()

    Path(os.environ["BROWSER_FIXTURE_STATE"]).write_text(
        json.dumps(
            {
                "owner_a_email": "owner-a@example.test",
                "owner_b_email": "owner-b@example.test",
                "reviewer_email": "reviewer@example.test",
                "password": PASSWORD,
                "firm_a_id": firm_a,
                "firm_b_id": firm_b,
                "firm_b_case_id": case_b_id,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    runtime.close_current_thread()


if __name__ == "__main__":
    bootstrap()
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=int(os.environ["BROWSER_FIXTURE_PORT"]),
        log_level="warning",
    )
