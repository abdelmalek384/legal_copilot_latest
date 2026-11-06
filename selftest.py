"""Small smoke test for the approved profile-separated runtime.

Detailed retrieval, citation, identity, and authorization cases live in tests/.
This smoke test must not revive the shared COPILOT_DB compatibility harness.
"""
import io
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

_tmp = tempfile.TemporaryDirectory(prefix="legal-copilot-selftest-")
_root = Path(_tmp.name)
os.environ.pop("COPILOT_DB", None)
os.environ["COPILOT_ENV"] = "development"
os.environ["COPILOT_CONTROL_DB"] = str(_root / "control.sqlite3")
os.environ["COPILOT_TENANT_DB_ROOT"] = str(_root / "tenants")
os.environ["COPILOT_CORPUS_DB"] = str(_root / "corpus.sqlite3")
os.environ["COPILOT_OBJECT_STORAGE_ROOT"] = str(_root / "objects")
os.environ["COPILOT_OBJECT_STORAGE_BACKEND"] = "local"
os.environ.pop("ALLOW_UNLINKED_LEGACY_LAW_SEARCH", None)

import app
from database_runtime import DatabaseRuntime

runtime = DatabaseRuntime.from_env()
runtime.initialize()
firm_id, _ = runtime.provision_firm("Selftest synthetic firm")
user_id = runtime.create_initial_firm_owner(
    firm_id, "Selftest Owner", "selftest-owner@example.test", app.hash_pw("Selftest-Unique-Passphrase-2026!")
)
context = runtime.resolve_context(user_id, firm_id)
context_token = app._active_firm_context.set(context)
try:
    matter = runtime.firm_connection(context)
    case_id = matter.execute(
        "INSERT INTO cases(title,firm_id) VALUES(?,?)",
        ("Synthetic matter retrieval fixture", firm_id),
    ).lastrowid
    app.add_doc(matter, case_id, "Synthetic matter document", "مدة العقد سنتان")
    hits = app.search(
        matter, "مدة العقد", case_id=case_id, firm_id=firm_id, scope="firm_documents"
    )
    assert hits and hits[0]["scope"] == "firm_documents"
    assert hits[0]["text"] == "مدة العقد سنتان"
    assert app.search(
        matter, "إجازة سنوية", firm_id=firm_id, scope="verified_corpus"
    ) == [], "an empty legal corpus must not return unreviewed or fictional authority"

    assert app.norm("المَادَّة") == app.norm("الماده")
    assert app.norm("ﻻ") == app.norm("لا")  # Arabic diacritics and compatibility ligatures
    assert app.stem(app.norm("إجازة")) in app.expanded_tokens("عطلة سنوية")
    assert app.tokens("في من على") == []
    assert app.search(matter, "qwerty zzz", case_id=case_id, firm_id=firm_id,
                      scope="firm_documents") == []

    # LLM transmission is fail-closed unless the deployment operator explicitly approves it.
    saved = {
        key: os.environ.get(key)
        for key in ("LLM_URL", "LLM_MODEL", "LLM_KEY", "LLM_DATA_PROCESSING_APPROVED")
    }
    try:
        os.environ["LLM_URL"] = "https://llm.example.test/v1/chat/completions"
        os.environ["LLM_MODEL"] = "test-model"
        os.environ["LLM_KEY"] = "test-key"
        os.environ.pop("LLM_DATA_PROCESSING_APPROVED", None)
        with patch("app._llm_open") as open_url:
            assert app.llm("CONFIDENTIAL-SENTINEL") is None
            open_url.assert_not_called()
        os.environ["LLM_DATA_PROCESSING_APPROVED"] = "1"
        fake_response = io.BytesIO(
            json.dumps({"choices": [{"message": {"content": "test answer"}}]}).encode()
        )
        with patch("app._llm_open", return_value=fake_response) as open_url:
            assert app.llm("CONFIDENTIAL-SENTINEL") == "test answer"
            sent_request = open_url.call_args.args[0]
            assert b"CONFIDENTIAL-SENTINEL" in sent_request.data
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    assert app.check_pw(
        "correct horse 12", app.hash_pw("correct horse 12")
    ) and not app.check_pw("x", app.hash_pw("y"))
    print("ALL OK")
finally:
    app._active_firm_context.reset(context_token)
    try:
        runtime.close_current_thread()
    finally:
        _tmp.cleanup()
