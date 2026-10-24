import os, io, json, tempfile
from datetime import date, timedelta
os.environ.update(COPILOT_DB=os.path.join(tempfile.mkdtemp(), "a.db"), ADMIN_TOKEN="stage0-test-admin-token-please-use-a-long-random-secret")
from fastapi.testclient import TestClient
import app, docx
c = TestClient(app.app); db = app.conn()
for n, role in (("Lead", "lawyer"), ("Junior", "junior"), ("Outsider", "lawyer")):
    db.execute("INSERT INTO users(name,email,pw,role) VALUES(?,?,?,?)", (n, n.lower() + "@x.eg", app.hash_pw("password-" + n), role))
db.commit()
# Separate admin identity for protected law imports; ordinary case lead is not an admin.
db.execute("INSERT INTO users(name,email,pw,role) VALUES(?,?,?,?)",
           ("Import Admin","import-admin@x.eg",app.hash_pw("password-ImportAdmin"),"admin"))
db.commit()
def login_creds(email, password):
    response = c.post("/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    session = response.cookies["lc_session"]
    csrf = response.cookies["lc_csrf"]
    c.cookies.clear()  # Tests pass credentials explicitly; avoid leaking one login into later requests.
    return {"Cookie": f"lc_session={session}; lc_csrf={csrf}", "X-CSRF-Token": csrf}
A_IMPORT = login_creds("import-admin@x.eg", "password-ImportAdmin")
def login(n): return login_creds(n.lower() + "@x.eg", "password-" + n)
L, J, O = login("Lead"), login("Junior"), login("Outsider")
assert c.get("/").headers.get("x-content-type-options") == "nosniff"
assert c.get("/").headers.get("x-frame-options") == "DENY"
landing = c.get("/")
script_policy = landing.headers.get("content-security-policy", "").split("script-src", 1)[1].split(";", 1)[0]
assert "unsafe-inline" not in script_policy and "nonce-" in script_policy and "<script nonce=" in landing.text
assert c.get("/cases/999999999999999999999999999999999999", headers=L).status_code in (404, 422)
assert c.get("/cases").status_code == 401 and c.post("/login", json={"email": "lead@x.eg", "password": "bad"}).status_code == 401
rows = [json.loads(l) for l in open("sample_law.jsonl", encoding="utf-8")]
assert c.post("/law/import", json=rows, headers=L).status_code == 403
assert c.post("/law/import", json=rows, headers={"X-Admin-Token": "stage0-test-admin-token-please-use-a-long-random-secret"}).status_code == 401
assert c.post("/law/import", json=rows, headers={**A_IMPORT, "X-Admin-Token": "stage0-test-admin-token-please-use-a-long-random-secret"}).json()["imported"] == 3
# Legacy bulk import must ignore caller-supplied verification/current-law flags.
legacy_rows = [
    {"law":"Unreviewed import test", "article":"99", "text":"Synthetic legal passage for import safety test.",
     "as_of":"2024-01-01", "source":"UNVERIFIED-IMPORT-TEST", "verified":1, "in_force":1}
]
legacy_import = c.post("/law/import", json=legacy_rows,
                       headers={**A_IMPORT, "X-Admin-Token":"stage0-test-admin-token-please-use-a-long-random-secret"})
assert legacy_import.status_code == 200, legacy_import.text
legacy_payload = legacy_import.json()
assert legacy_payload["imported"] == 1
assert legacy_payload["review_required"] is True
assert legacy_payload["search_eligible"] is False
assert "unverified" in legacy_payload["warning"].lower()
legacy_chunk = db.execute("SELECT verified,in_force,document_version_id FROM chunks WHERE ref=?",
                          ("Unreviewed import test - المادة 99",)).fetchone()
assert tuple(legacy_chunk) == (0, 0, None), tuple(legacy_chunk)
legacy_search = c.post("/search", json={"q":"Synthetic legal passage"}, headers=L).json()
assert all(hit["ref"] != "Unreviewed import test - المادة 99" for hit in legacy_search), legacy_search
cid = c.post("/cases", json={"title": "<b>x</b>", "client": "عميل"}, headers=L).json()["id"]
jid = [u for u in c.get("/users", headers=L).json() if u["name"] == "Junior"][0]["id"]
assert c.post(f"/cases/{cid}/tasks", json={"title": "t", "assignee": jid}, headers=L).status_code == 422   # not a member yet
assert c.post(f"/cases/{cid}/members", json={"user_id": jid, "role": "junior"}, headers=J).status_code == 404  # junior cannot manage team
assert c.post(f"/cases/{cid}/members", json={"user_id": jid, "role": "junior"}, headers=L).status_code == 200
assert c.post(f"/cases/{cid}/tasks", json={"title": "مذكرة", "assignee": jid, "due": "2099-01-01"}, headers=L).status_code == 200
soon = (date.today() + timedelta(days=7)).isoformat()
assert c.post(f"/cases/{cid}/deadlines", json={"title":"استئناف","due":soon,"note":""}, headers=L).status_code == 200
dash = c.get("/dashboard", headers=J).json()
assert any(x["title"] == "استئناف" for x in dash["deadlines"])
deadline = next(x for x in dash["deadlines"] if x["title"] == "استئناف")
assert c.post(f"/deadlines/{deadline['id']}/done", headers=J).status_code == 404
assert c.post(f"/deadlines/{deadline['id']}/done", headers=L).status_code == 200
assert all(x["id"] != deadline["id"] for x in c.get("/dashboard", headers=J).json()["deadlines"])
assert len(c.get("/dashboard", headers=J).json()["tasks"]) == 1
tid = c.get("/dashboard", headers=J).json()["tasks"][0]["id"]
assert c.post(f"/tasks/{tid}/done", headers=O).status_code == 404 and c.post(f"/tasks/{tid}/done", headers=J).status_code == 200
assert c.post(f"/cases/{cid}/sessions", json={"date": "tomorrow"}, headers=L).status_code == 422
d = docx.Document(); d.add_paragraph("مدة العقد سنتان ويجدد تلقائيا"); b = io.BytesIO(); d.save(b)
assert c.post(f"/cases/{cid}/upload", files={"file": ("a.docx", b.getvalue())}, headers=J).status_code == 200
assert c.post(f"/cases/{cid}/upload", files={"file": ("a.txt", b"hello world")}, headers=J).status_code == 415
assert c.post(f"/cases/{cid}/upload", files={"file": ("a.docx", b"not a docx")}, headers=J).status_code == 422
# Verify the OCR route metadata without requiring Tesseract in the CI runner.
_original_extract = app.extract
_original_ocr = app.ocr_pdf_text
try:
    app.extract = lambda name, data: ""
    app.ocr_pdf_text = lambda data: "recognized scanned document text that needs human review"
    _ocr_response = c.post(f"/cases/{cid}/upload", files={"file": ("scan.pdf", b"pdf bytes")}, headers=J)
finally:
    app.extract = _original_extract
    app.ocr_pdf_text = _original_ocr
assert _ocr_response.status_code == 200, _ocr_response.text
assert _ocr_response.json()["ocr_used"] is True
assert _ocr_response.json()["text_status"] == "ocr_unverified"
assert _ocr_response.json()["chunks"] >= 1

assert c.post("/ask", json={"q": "مدة العقد", "case_id": cid}, headers=O).status_code == 404 and c.get(f"/cases/{cid}", headers=O).status_code == 404
r = c.post("/ask", json={"q": "مدة العقد", "case_id": cid}, headers=J).json(); assert r["sources"][0]["source"] == "case-file"
info = c.get(f"/cases/{cid}", headers=J).json(); assert len(info["events"]) >= 4 and info["tasks"][0]["status"] == "done"
assert c.patch(f"/cases/{cid}", json={"case_number":"77","case_year":"2025","court":"محكمة","circuit":"دائرة 3","opposing_party":"خصم"}, headers=L).status_code == 200
assert c.post(f"/cases/{cid}/notes", json={"text":"ملاحظة اختبار"}, headers=J).status_code == 200
assert c.post(f"/cases/{cid}/deadlines", json={"title":"استئناف","due":"2099-02-01","note":"تجريبي"}, headers=J).status_code == 200
assert c.post(f"/cases/{cid}/fees", json={"title":"أتعاب","amount":1000,"paid":250}, headers=J).status_code == 200
assert c.post(f"/cases/{cid}/fees", json={"title":"أتعاب غير صحيحة","amount":100,"paid":101}, headers=J).status_code == 422
assert c.post(f"/cases/{cid}/fees", json={"title":"مبلغ سالب","amount":-1,"paid":0}, headers=J).status_code == 422
assert c.post(f"/cases/{cid}/fees", json={"title":"مدفوع سالب","amount":100,"paid":-1}, headers=J).status_code == 422
assert c.post("/conflicts", json={"q":"خصم"}, headers=L).json()["matches"][0]["id"] == cid
info = c.get(f"/cases/{cid}", headers=J).json()
assert info["case_number"] == "77" and info["notes"][0]["text"] == "ملاحظة اختبار"
assert info["deadlines"][0]["title"] == "استئناف" and info["fees"][0]["paid"] == 250
assert c.get("/cases", headers=O).json() == [] and len(c.get("/cases", headers=J).json()) == 1

# Firm isolation regression checks: a second firm's admin must not see or mutate the first firm's data.
db.execute("INSERT INTO firms(id,name) VALUES(2,'Second Firm')")
db.execute("INSERT INTO users(name,email,pw,role,firm_id) VALUES(?,?,?,?,?)",
           ("Second Admin","second@x.eg",app.hash_pw("password-Second"),"admin",2))
db.commit()
S = login_creds("second@x.eg", "password-Second")
other_cid = c.post("/cases", json={"title":"Private second-firm matter","client":"Second Client"}, headers=S).json()["id"]
assert c.get("/cases", headers=S).status_code == 200
assert [x["id"] for x in c.get("/cases", headers=S).json()] == [other_cid]
assert c.get(f"/cases/{cid}", headers=S).status_code == 404
assert c.post("/search", json={"q":"مدة العقد","case_id":cid}, headers=S).status_code == 404
assert c.post("/ask", json={"q":"مدة العقد","case_id":cid}, headers=S).status_code == 404
assert all(u["name"] != "Lead" for u in c.get("/users", headers=S).json())
assert c.patch(f"/cases/{cid}", json={"status":"closed"}, headers=S).status_code == 404
assert c.delete(f"/cases/{cid}", headers=S).status_code == 404
assert c.post("/conflicts", json={"q":"عميل"}, headers=S).json()["matches"] == []
assert all(x.get("case_title") != "مذكرة" for x in c.get("/dashboard", headers=S).json()["tasks"])
# Same-firm user creation is admin-only and password validation is enforced.
db.execute("INSERT INTO users(name,email,pw,role,firm_id) VALUES(?,?,?,?,?)",
           ("First Firm Admin","admin@x.eg",app.hash_pw("password-Admin"),"admin",1))
db.commit()
A = login_creds("admin@x.eg", "password-Admin")
assert c.post("/users", json={"name":"Nope","email":"nope@x.eg","password":"long-enough-password","role":"lawyer"}, headers=J).status_code == 403
assert c.post("/users", json={"name":"New User","email":"new@x.eg","password":"short","role":"lawyer"}, headers=A).status_code == 422
assert c.post("/users", json={"name":"New User","email":"new@x.eg","password":"long-enough-password","role":"lawyer"}, headers=A).status_code == 200
hidden = c.post("/cases", json={"title":"Private Matter Zeta","client":"Hidden Client Zeta"}, headers=A)
assert hidden.status_code == 200
probe = c.post("/conflicts", json={"q":"Hidden Client Zeta"}, headers=L).json()
assert probe["matches"] == [] and probe["possible_conflict"] is True and probe["admin_review_required"] is True
new_user = c.post("/users", json={"name":"Disable Me","email":"disable@x.eg","password":"long-enough-password","role":"lawyer"}, headers=A)
assert new_user.status_code == 200
new_uid = new_user.json()["id"]
# A session issued before account disablement must stop authorizing requests immediately.
disabled_session = login_creds("disable@x.eg", "long-enough-password")
assert c.get("/cases", headers=disabled_session).status_code == 200
assert c.post(f"/users/{new_uid}/disable", headers=A).status_code == 200
assert c.get("/cases", headers=disabled_session).status_code == 401
assert c.post("/login", json={"email":"disable@x.eg","password":"long-enough-password"}).status_code == 401
assert c.delete(f"/cases/{cid}", headers=J).status_code == 404 and c.delete(f"/cases/{cid}", headers=L).status_code == 200
# Permanent deletion must leave an admin-readable audit snapshot in the same firm.
assert c.get("/audit/case-deletions", headers=L).status_code == 403
deletion_audit = c.get("/audit/case-deletions", headers=A_IMPORT)
assert deletion_audit.status_code == 200, deletion_audit.text
audit_rows = deletion_audit.json()["items"]
assert audit_rows and audit_rows[0]["case_id"] == cid
assert audit_rows[0]["actor_name"] == "Lead"
assert len(audit_rows[0]["events_snapshot"]) >= 4
assert audit_rows[0]["case_snapshot"]["firm_id"] == 1
assert c.get("/audit/case-deletions?limit=101", headers=A_IMPORT).status_code == 422
# Authentication regression tests: malformed headers, expiry, password-reset revocation, role boundary and concurrent logins.
for malformed in ("", "garbage", "Bearer", "Basic abc", "Bearer not-a-real-token"):
    assert c.get("/cases", headers={"Authorization": malformed}).status_code == 401
assert c.post("/cases", json={"title":"Missing CSRF"}, headers={"Cookie": L["Cookie"]}).status_code == 403
expired = login("Junior")
expired_token = expired["Cookie"].split("lc_session=",1)[1].split(";",1)[0]
db.execute("UPDATE auth_sessions SET expires=? WHERE token_hash=?", (int(__import__("time").time()) - 1, app.sha(expired_token)))
db.commit()
assert c.get("/cases", headers=expired).status_code == 401
from unittest.mock import patch
import sys, getpass
c.post("/users", json={"name":"Reset Test","email":"reset@x.eg","password":"old-password-Long","role":"lawyer"}, headers=A)
reset_token = login_creds("reset@x.eg", "old-password-Long")
assert c.get("/cases", headers=reset_token).status_code == 200
# manage.py is a CLI script; set its arguments and patch the terminal prompt before importing it.
sys.argv = ["manage.py", "resetpw", "reset@x.eg"]
with patch("getpass.getpass", return_value="new-password-Long"):
    import manage
assert c.get("/cases", headers=reset_token).status_code == 401
# Isolate credential-reset assertions from login attempts made by earlier tests;
# rate-limit behavior is exercised separately from password correctness.
if hasattr(app, "_rate_limit_state"):
    with app._rate_limit_lock:
        for key in list(app._rate_limit_state):
            if key[0] == "/login":
                app._rate_limit_state.pop(key, None)
assert c.post("/login",json={"email":"reset@x.eg","password":"old-password-Long"}).status_code == 401
assert c.post("/login",json={"email":"reset@x.eg","password":"new-password-Long"}).status_code == 200
assert c.post("/law/import", json=rows, headers={**L, "X-Admin-Token":"stage0-test-admin-token-please-use-a-long-random-secret"}).status_code == 403
from concurrent.futures import ThreadPoolExecutor
def concurrent_login(_):
    # Independent clients avoid sharing TestClient cookie/session state across threads.
    with TestClient(app.app) as client:
        return client.post("/login", json={"email":"reset@x.eg","password":"new-password-Long"}).status_code
with ThreadPoolExecutor(max_workers=4) as pool:
    concurrent_statuses = list(pool.map(concurrent_login, range(4)))
assert concurrent_statuses == [200, 200, 200, 200], concurrent_statuses
# Logout revokes the server-side session, not just the browser token.
logout_headers = login("Junior")
assert c.get("/cases", headers=logout_headers).status_code == 200
assert c.post("/logout", headers=logout_headers).status_code == 200
assert c.get("/cases", headers=logout_headers).status_code == 401
for _ in range(5): c.post("/login", json={"email": "lead@x.eg", "password": "bad"})
assert c.post("/login", json={"email": "lead@x.eg", "password": "password-Lead"}).status_code == 200   # correct credentials bypass throttling lock
print("API OK")

# Persistent legal-research chat: history is owned by one user and scoped to their firm.
chat = c.post("/research/conversations", json={}, headers=L)
assert chat.status_code == 200, chat.text
chat_id = chat.json()["id"]
first_message = c.post(f"/research/conversations/{chat_id}/messages",
                       json={"message":"مدة العقد"}, headers=L)
assert first_message.status_code == 200, first_message.text
chat_data = c.get(f"/research/conversations/{chat_id}", headers=L)
assert chat_data.status_code == 200 and len(chat_data.json()["messages"]) == 2
assert chat_data.json()["messages"][0]["role"] == "user"
assert chat_data.json()["messages"][1]["role"] == "assistant"
assert isinstance(chat_data.json()["messages"][1]["sources"], list)
assert c.get(f"/research/conversations/{chat_id}", headers=J).status_code == 404
assert c.get(f"/research/conversations/{chat_id}", headers=S).status_code == 404
assert c.post(f"/research/conversations/{chat_id}/messages",
              json={"message":"   "}, headers=L).status_code == 422
assert any(x["id"] == chat_id for x in c.get("/research/conversations", headers=L).json())
# Follow-ups preserve the current question separately and use prior user turns only as context.
# Prior assistant prose must never be fed back as if it were authoritative legal material.
from unittest.mock import patch as patch_ask
captured = {}
real_ask = app.ask
def capture_research_ask(db_conn, question, case_id=None, firm_id=1, as_of=None, conversation_context=None):
    captured.update(question=question, context=conversation_context, firm_id=firm_id)
    return {"found": False, "answer": None, "sources": [], "message": "لم أجد مصدرا ذا صلة، ولن أخمن."}
with patch_ask.object(app, "ask", side_effect=capture_research_ask):
    followup = c.post(f"/research/conversations/{chat_id}/messages",
                      json={"message":"وهل توجد استثناءات؟"}, headers=L)
assert followup.status_code == 200, followup.text
assert captured["question"] == "وهل توجد استثناءات؟"
assert "مدة العقد" in (captured["context"] or "")
assert "لم أجد مصدرا" not in (captured["context"] or "")
assert captured["firm_id"] == 1
chat_after_followup = c.get(f"/research/conversations/{chat_id}", headers=L).json()
assert [m["role"] for m in chat_after_followup["messages"]][-2:] == ["user", "assistant"]
assert chat_after_followup["messages"][-1]["sources"] == []



# Impossible calendar dates must fail validation, not just malformed date strings.
from pydantic import ValidationError
for model, field, valid, invalid in (
    (app.SessIn, "date", "2024-02-29", "2025-02-29"),
    (app.DeadlineIn, "due", "2026-10-23", "2026-02-30"),
    (app.TaskIn, "due", "2024-02-29", "2024-13-01"),
    (app.FeeIn, "due", "2024-02-29", "2024-04-31"),
    (app.LawRow, "as_of", "2024-02-29", "2024-02-30"),
):
    sample = {"date": valid} if model is app.SessIn else (
        {"title": "deadline", "due": valid} if model is app.DeadlineIn else
        {"title": "task", "due": valid} if model is app.TaskIn else
        {"title": "fee", "amount": 10, "paid": 0, "due": valid} if model is app.FeeIn else
        {"law": "test", "article": "1", "text": "test", "as_of": valid}
    )
    model(**sample)
    bad = dict(sample); bad[field] = invalid
    try:
        model(**bad)
    except ValidationError:
        pass
    else:
        raise AssertionError(f"{model.__name__} accepted impossible date {invalid}")


# Evidence-backed legal review events are admin-only and never auto-promote legal status.
review_source_id = "SRC-REVIEW-EVENT-TEST"
review_document_id = "DOC-REVIEW-EVENT-TEST"
db.execute("INSERT INTO legal_sources(source_id,authority,source_page) VALUES(?,?,?)",
           (review_source_id, "Test official authority", "https://example.gov/legal"))
db.execute("INSERT INTO legal_documents(document_id,source_id,official_title,document_type) VALUES(?,?,?,?)",
           (review_document_id, review_source_id, "Review workflow test instrument", "law"))
db.execute("INSERT INTO legal_document_versions(document_id,version_label,source_url,legal_status,review_status) VALUES(?,?,?,?,?)",
           (review_document_id, "initial", "https://example.gov/legal/test.pdf", "under_review", "pending_lawyer_review"))
review_version_id = db.execute("SELECT version_id FROM legal_document_versions WHERE document_id=?",
                               (review_document_id,)).fetchone()[0]
db.commit()
assert c.get(f"/legal-review/versions/{review_version_id}/events", headers=L).status_code == 403
assert c.post(f"/legal-review/versions/{review_version_id}/events",
              json={"review_type":"legal_status","outcome":"pass","evidence_url":"https://example.gov/status"},
              headers=L).status_code == 403
assert c.post(f"/legal-review/versions/{review_version_id}/events",
              json={"review_type":"legal_status","outcome":"pass"},
              headers=A_IMPORT).status_code == 422
assert c.post(f"/legal-review/versions/{review_version_id}/events",
              json={"review_type":"legal_status","outcome":"pass",
                    "evidence_url":"https://reviewer:secret@example.gov/status"},
              headers=A_IMPORT).status_code == 422
review_created = c.post(f"/legal-review/versions/{review_version_id}/events",
                        json={"review_type":"source_authenticity","outcome":"pass",
                              "evidence_url":"https://example.gov/gazette/issue-123",
                              "notes":"Evidence URL recorded for authorized human review."},
                        headers=A_IMPORT)
assert review_created.status_code == 201, review_created.text
assert review_created.json()["status_changed"] is False
db_review_state = db.execute(
    "SELECT review_status,legal_status,authenticity_verified,status_verified,amendment_history_verified "
    "FROM legal_document_versions WHERE version_id=?", (review_version_id,)).fetchone()
assert tuple(db_review_state) == ("pending_lawyer_review","under_review",0,0,0), tuple(db_review_state)
review_history = c.get(f"/legal-review/versions/{review_version_id}/events", headers=A_IMPORT)
assert review_history.status_code == 200 and len(review_history.json()["events"]) == 1
assert review_history.json()["events"][0]["reviewer"] == "Import Admin"
assert c.get(f"/legal-review/versions/999999/events", headers=A_IMPORT).status_code == 404


# Legal-source reviewer workbench queue is administrator-only and read-only.
assert c.get("/legal-review/queue", headers=L).status_code == 403
review_queue_response = c.get("/legal-review/queue", headers=A_IMPORT)
assert review_queue_response.status_code == 200, review_queue_response.text
assert "versions" in review_queue_response.json()
assert "warning" in review_queue_response.json()
if review_queue_response.json()["versions"]:
    queue_row = review_queue_response.json()["versions"][0]
    assert {"version_id", "official_title", "review_status", "legal_status", "event_count"} <= set(queue_row)


# Numeric legal claims must be supported by the text of the cited passages,
# not merely by the existence of a syntactically valid citation.
assert app._legal_quantities("The maximum is five years.") == {(5, "year")}
assert app._legal_quantities("The maximum is 5 years.") == {(5, "year")}
assert app._legal_quantities("المدة خمس سنوات") == {(5, "year")}
numeric_hits = [{"text": "The maximum contract duration is five years."}]
assert not app._answer_has_unsupported_quantities("The maximum is five years [1].", numeric_hits, {1})
assert app._answer_has_unsupported_quantities("The maximum is ten years [1].", numeric_hits, {1})
assert app._answer_has_unsupported_quantities("The maximum is ten years [1].", numeric_hits, set())


# Persistent research-chat messages share one SQLite-backed per-IP budget
# across conversation IDs and worker processes.
from starlette.requests import Request as StarletteRequest
db.execute("DELETE FROM api_rate_limit_windows WHERE bucket='__research_message__' AND client_key='rate-limit-test'")
db.commit()
def rate_request(path, method="POST"):
    return StarletteRequest({
        "type": "http", "http_version": "1.1", "method": method,
        "scheme": "http", "path": path, "raw_path": path.encode(),
        "query_string": b"", "headers": [], "client": ("rate-limit-test", 1234),
        "server": ("testserver", 80),
    })
for n in range(20):
    assert app._rate_limit(rate_request(f"/research/conversations/{n}/messages")) == 0
stored = db.execute("SELECT hits FROM api_rate_limit_windows WHERE bucket='__research_message__' AND client_key='rate-limit-test'").fetchone()
assert stored and stored["hits"] == 20, "request counts must be stored outside process-local memory"
retry_after = app._rate_limit(rate_request("/research/conversations/999/messages"))
assert retry_after > 0, "research chat must return a retry delay after 20 requests/minute per IP"
assert app._rate_limit(rate_request("/research/conversations/999/messages", method="GET")) == 0
assert c.get("/openapi.json").status_code == 404
