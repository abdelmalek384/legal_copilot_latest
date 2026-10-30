import os, json, tempfile
from datetime import date, timedelta
os.environ.update(COPILOT_DB=os.path.join(tempfile.mkdtemp(), "a.db"), ADMIN_TOKEN="stage0-test-admin-token-please-use-a-long-random-secret", LEGAL_REVIEWER_EMAILS="import-admin@x.eg")
from fastapi.testclient import TestClient
import app

# iCalendar text values must not allow raw CR/LF to inject new content lines.
assert app._ics_escape("a\\b,c;d\r\ne\rf\ng") == "a\\\\b\\,c\\;d\\ne\\nf\\ng"
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
db.execute("INSERT OR IGNORE INTO firms(id,name) VALUES(2,?)", ("Other Firm",))
db.execute("INSERT INTO users(name,email,pw,role,firm_id) VALUES(?,?,?,?,?)", ("Other Firm Admin","other-admin@x.eg",app.hash_pw("password-OtherAdmin"),"admin",2))
db.commit()
B_ADMIN = login_creds("other-admin@x.eg", "password-OtherAdmin")
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
# Unassigned work is visible only to members of the case and can be claimed once.
assert c.post(f"/cases/{cid}/tasks", json={"title": "مهمة غير مسندة", "due": "2099-01-02"}, headers=L).status_code == 200
lead_dash = c.get("/dashboard", headers=L).json()
junior_dash = c.get("/dashboard", headers=J).json()
outsider_dash = c.get("/dashboard", headers=O).json()
unassigned = next(x for x in junior_dash["unassigned_tasks"] if x["title"] == "مهمة غير مسندة")
assert any(x["title"] == "مهمة غير مسندة" for x in lead_dash["unassigned_tasks"])
assert all(x["title"] != "مهمة غير مسندة" for x in outsider_dash["unassigned_tasks"])
assert c.post(f"/tasks/{unassigned['id']}/claim", headers=O).status_code == 404
assert c.post(f"/tasks/{unassigned['id']}/claim", headers=J).status_code == 200
assert c.post(f"/tasks/{unassigned['id']}/claim", headers=L).status_code == 409
assert any(x["title"] == "مهمة غير مسندة" for x in c.get("/dashboard", headers=J).json()["tasks"])
assert all(x["title"] != "مهمة غير مسندة" for x in c.get("/dashboard", headers=J).json()["unassigned_tasks"])
soon = (date.today() + timedelta(days=7)).isoformat()
assert c.post(f"/cases/{cid}/deadlines", json={"title":"استئناف","due":soon,"note":""}, headers=L).status_code == 200
assert c.post(f"/cases/{cid}/sessions", json={"date":soon,"note":"جلسة تجريبية"}, headers=L).status_code == 200
calendar_response = c.get("/calendar.ics", headers=J)
assert calendar_response.status_code == 200 and "text/calendar" in calendar_response.headers.get("content-type", "")
assert "BEGIN:VCALENDAR" in calendar_response.text and "END:VCALENDAR" in calendar_response.text
assert "Legal deadline: استئناف" in calendar_response.text and "Hearing:" in calendar_response.text
assert c.get("/calendar.ics", headers=O).status_code == 200 and "استئناف" not in c.get("/calendar.ics", headers=O).text
dash = c.get("/dashboard", headers=J).json()
assert any(x["title"] == "استئناف" for x in dash["deadlines"])
deadline = next(x for x in dash["deadlines"] if x["title"] == "استئناف")
assert c.post(f"/deadlines/{deadline['id']}/done", headers=J).status_code == 404
assert c.post(f"/deadlines/{deadline['id']}/done", headers=L).status_code == 200
assert all(x["id"] != deadline["id"] for x in c.get("/dashboard", headers=J).json()["deadlines"])
assert len(c.get("/dashboard", headers=J).json()["tasks"]) == 2  # original assignment plus the newly claimed task
tid = c.get("/dashboard", headers=J).json()["tasks"][0]["id"]
assert c.post(f"/tasks/{tid}/done", headers=O).status_code == 404 and c.post(f"/tasks/{tid}/done", headers=J).status_code == 200
assert c.post(f"/cases/{cid}/sessions", json={"date": "tomorrow"}, headers=L).status_code == 422
assert c.post("/ask", json={"q": "مدة العقد", "case_id": cid}, headers=O).status_code == 404 and c.get(f"/cases/{cid}", headers=O).status_code == 404
legacy_case_doc = c.post(f"/cases/{cid}/docs", json={"name":"case-source.txt","text":"مدة العقد سنتان ويجدد تلقائيا"}, headers=J)
assert legacy_case_doc.status_code == 200, legacy_case_doc.text
r = c.post("/ask", json={"q": "مدة العقد", "case_id": cid}, headers=J).json(); assert r["sources"][0]["source"] == "case-file"
info = c.get(f"/cases/{cid}", headers=J).json(); assert len(info["events"]) >= 4 and any(task["status"] == "done" for task in info["tasks"])
assert c.patch(f"/cases/{cid}", json={"case_number":"77","case_year":"2025","court":"محكمة","circuit":"دائرة 3","opposing_party":"خصم"}, headers=L).status_code == 200
assert c.post(f"/cases/{cid}/notes", json={"text":"ملاحظة اختبار"}, headers=J).status_code == 200
assert c.post(f"/cases/{cid}/deadlines", json={"title":"استئناف","due":"2099-02-01","note":"تجريبي"}, headers=J).status_code == 200
assert c.post(f"/cases/{cid}/fees", json={"title":"أتعاب","amount":1000,"paid":250,"due":"2099-02-01"}, headers=J).status_code == 200
finance = c.get("/finance/overview", headers=J)
assert finance.status_code == 200, finance.text
assert finance.json()["fee_count"] == 1
assert finance.json()["total_amount"] == 1000 and finance.json()["total_paid"] == 250
assert finance.json()["outstanding_amount"] == 750 and finance.json()["overdue_count"] == 0
assert c.get("/finance/overview", headers=O).json()["fee_count"] == 0
assert c.get("/finance/overview", headers=B_ADMIN).json()["fee_count"] == 0
assert c.post(f"/cases/{cid}/fees", json={"title":"أتعاب غير صحيحة","amount":100,"paid":101}, headers=J).status_code == 422
assert c.post(f"/cases/{cid}/fees", json={"title":"مبلغ سالب","amount":-1,"paid":0}, headers=J).status_code == 422
assert c.post(f"/cases/{cid}/fees", json={"title":"مدفوع سالب","amount":100,"paid":-1}, headers=J).status_code == 422
assert c.post("/conflicts", json={"q":"خصم"}, headers=L).json()["matches"][0]["id"] == cid
info = c.get(f"/cases/{cid}", headers=J).json()
assert info["case_number"] == "77" and info["notes"][0]["text"] == "ملاحظة اختبار"
assert info["deadlines"][0]["title"] == "استئناف" and info["fees"][0]["paid"] == 250
assert c.get("/cases", headers=O).json() == [] and len(c.get("/cases", headers=J).json()) == 1

# Firm isolation regression checks reuse the second-firm admin created during test setup.
# Do not insert firm id 2 again: the setup already creates it for the legal-review boundary tests.
S = B_ADMIN
# Firm-scoped audit APIs must not expose another firm's events or deletion snapshots.
security_audit_b = c.get("/audit/security-events", headers=S)
assert security_audit_b.status_code == 200, security_audit_b.text
assert all(row["firm_id"] == 2 for row in security_audit_b.json()["items"]), security_audit_b.json()
deletion_audit_b = c.get("/audit/case-deletions", headers=S)
assert deletion_audit_b.status_code == 200, deletion_audit_b.text
assert deletion_audit_b.json()["items"] == [], deletion_audit_b.json()
other_cid = c.post("/cases", json={"title":"Private second-firm matter","client":"Second Client"}, headers=S).json()["id"]
assert c.get("/cases", headers=S).status_code == 200
assert [x["id"] for x in c.get("/cases", headers=S).json()] == [other_cid]

# Research conversations are user-owned and firm-scoped, including child messages and matter export.
research_conversation = c.post("/research/conversations", headers=J)
assert research_conversation.status_code == 200, research_conversation.text
research_id = research_conversation.json()["id"]
db.execute("INSERT INTO research_messages(conversation_id,role,content) VALUES(?,?,?)",
           (research_id, "user", "Private research question sentinel"))
db.execute("INSERT INTO research_messages(conversation_id,role,content) VALUES(?,?,?)",
           (research_id, "assistant", "Private research answer sentinel"))
db.commit()
own_research = c.get(f"/research/conversations/{research_id}", headers=J)
assert own_research.status_code == 200
assert any(m["content"] == "Private research answer sentinel" for m in own_research.json()["messages"])
assert c.get(f"/research/conversations/{research_id}", headers=S).status_code == 404
assert c.get(f"/research/conversations/{research_id}", headers=L).status_code == 404
assert all(x["id"] != research_id for x in c.get("/research/conversations", headers=S).json())
assert c.patch(f"/research/conversations/{research_id}", json={"title":"stolen"}, headers=S).status_code == 404
assert c.delete(f"/research/conversations/{research_id}", headers=S).status_code == 404
assert c.post(f"/research/conversations/{research_id}/messages",
              json={"message":"attempted cross-firm access"}, headers=S).status_code == 404
assert c.post(f"/research/conversations/{research_id}/save-to-matter",
              json={"case_id":other_cid,"message_id":db.execute(
                  "SELECT id FROM research_messages WHERE conversation_id=? AND role='assistant'", (research_id,)
              ).fetchone()[0]}, headers=J).status_code == 404
assert c.get(f"/research/conversations/{research_id}", headers=J).status_code == 200
assert c.get(f"/cases/{cid}", headers=S).status_code == 404
cross_firm_upload = c.post(f"/cases/{cid}/upload", files={"file": ("leak.docx", b"cross-firm attempt")}, headers=S)
assert cross_firm_upload.status_code == 404, cross_firm_upload.text
assert db.execute("SELECT COUNT(*) FROM docs WHERE firm_id=2").fetchone()[0] == 0
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
# CLI password-reset behavior is covered by profile-separated tests in
# tests/test_platform_security_audit.py; this legacy API harness deliberately
# exercises only the explicit development compatibility app, not CLI writes.
c.post("/users", json={"name":"Login Concurrency Test","email":"reset@x.eg","password":"new-password-Long","role":"lawyer"}, headers=A)
# Isolate login-rate-limit assertions from earlier requests in this scenario.
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
def capture_research_ask(db_conn, question, case_id=None, firm_id=1, as_of=None, conversation_context=None, scope="all_permitted"):
    captured.update(question=question, context=conversation_context, firm_id=firm_id, scope=scope)
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
assert captured["scope"] == "verified_corpus"

# Search scopes are explicit; firm documents require a matter and never blend with the legal corpus.
scope_cid = c.post("/cases", json={"title":"Research scope test"}, headers=L).json()["id"]
app.add_doc(db, scope_cid, "Research scope fixture", "مدة العقد سنتان")
app.add_chunks(db, [{"ref":"Page pinpoint fixture","text":"مدة التقادم في المثال التشغيلي سبع سنوات","case_id":scope_cid,"source":"case-file","article":"12","page":"17"}])
db.commit()
scope_chat = c.post("/research/conversations", json={}, headers=L)
assert scope_chat.status_code == 200, scope_chat.text
scope_chat_id = scope_chat.json()["id"]
assert c.post(f"/research/conversations/{scope_chat_id}/messages",
              json={"message":"مدة العقد","scope":"firm_documents"}, headers=L).status_code == 422
firm_scope = c.post(f"/research/conversations/{scope_chat_id}/messages",
                    json={"message":"مدة العقد","scope":"firm_documents","case_id":scope_cid}, headers=L)
assert firm_scope.status_code == 200, firm_scope.text
assert firm_scope.json()["scope"] == "firm_documents"
assert firm_scope.json().get("sources"), firm_scope.json()
assert all(source.get("case_id") == scope_cid for source in firm_scope.json().get("sources", []))
assert all(source.get("source_status") == "user_supplied_unverified" for source in firm_scope.json().get("sources", []))
page_search = c.post("/search", json={"q":"التقادم المثال التشغيلي","case_id":scope_cid,"scope":"firm_documents"}, headers=L)
assert page_search.status_code == 200, page_search.text
page_hit = next(x for x in page_search.json() if x["ref"] == "Page pinpoint fixture")
assert page_hit["page"] == "17" and page_hit["article"] == "12"
assert "matched_terms" in page_hit and "التقادم" in page_hit["matched_terms"], page_hit
assert "Page 17" in page_hit["citation"] and "Article 12" in page_hit["citation"]
assert c.delete(f"/research/conversations/{scope_chat_id}", headers=L).status_code == 200

# Metadata discovery searches catalog fields only and returns no fabricated passage on a miss.
discovery = c.post("/research/discover", json={"q":"zz_no_catalog_match_2026"}, headers=L)
assert discovery.status_code == 200, discovery.text
assert discovery.json()["scope"] == "metadata_only"
assert discovery.json()["found"] is False and discovery.json()["results"] == []
assert "does not establish" in discovery.json()["message"]
assert "No source page was scraped or downloaded" in discovery.json()["warning"]
assert c.post("/research/discover", json={"q":"valid"}, headers=O).status_code == 200
# Whitespace-only search input must be rejected cleanly rather than generating an empty SQL WHERE clause.
assert c.post("/research/discover", json={"q":"   "}, headers=L).status_code == 422

# Positive metadata discovery must return catalog fields only, never legal passage text.
metadata_source_id = "SRC-METADATA-DISCOVERY-TEST"
metadata_document_id = "DOC-METADATA-DISCOVERY-TEST"
db.execute("INSERT INTO legal_sources(source_id,authority,source_page) VALUES(?,?,?)",
           (metadata_source_id, "Synthetic metadata discovery authority", "https://example.gov/synthetic"))
db.execute("INSERT INTO legal_documents(document_id,source_id,official_title,document_type,law_number,law_year) VALUES(?,?,?,?,?,?)",
           (metadata_document_id, metadata_source_id, "Synthetic metadata discovery fixture", "law", "MD-2026", 2026))
db.execute("INSERT INTO legal_document_versions(document_id,version_label,source_url,legal_status,review_status) VALUES(?,?,?,?,?)",
           (metadata_document_id, "synthetic-unreviewed", "https://example.gov/synthetic/version", "under_review", "pending_lawyer_review"))
db.commit()
metadata_match = c.post("/research/discover", json={"q":"Synthetic metadata discovery"}, headers=L)
assert metadata_match.status_code == 200, metadata_match.text
metadata_payload = metadata_match.json()
assert metadata_payload["scope"] == "metadata_only" and metadata_payload["found"] is True
metadata_row = next((row for row in metadata_payload["results"] if row["document_id"] == metadata_document_id), None)
assert metadata_row is not None, metadata_payload
assert metadata_row["status"] == "metadata_only" and metadata_row["text_available"] is False
assert "text" not in metadata_row and "passage" not in metadata_row and "chunks" not in metadata_row
assert "no current-law status is implied" in metadata_row["warning"]

# LIKE wildcards in a user query are literal characters, not a way to enumerate the registry.
wildcard_discovery = c.post("/research/discover", json={"q":"%%__catalog_wildcard_probe__"}, headers=L)
assert wildcard_discovery.status_code == 200, wildcard_discovery.text
assert wildcard_discovery.json()["results"] == [], wildcard_discovery.json()

# Saving a research answer preserves the as-of date, scope, citations, and caveats in the matter note.
assistant_message = chat_after_followup["messages"][-1]
saved = c.post(f"/research/conversations/{chat_id}/save-to-matter",
               json={"case_id":scope_cid,"message_id":assistant_message["id"]}, headers=L)
assert saved.status_code == 201, saved.text
saved_note = db.execute("SELECT text FROM notes WHERE id=?", (saved.json()["note_id"],)).fetchone()["text"]
assert "LEGAL RESEARCH MEMO" in saved_note and "As of:" in saved_note and "Search scope:" in saved_note
assert "not evidence that no applicable law exists" in saved_note

# Renaming a research conversation is validated and scoped to its owner and firm.
renamed = c.patch(f"/research/conversations/{chat_id}", json={"title":"  Labour contract research  "}, headers=L)
assert renamed.status_code == 200, renamed.text
assert renamed.json()["title"] == "Labour contract research"
assert c.patch(f"/research/conversations/{chat_id}", json={"title":"   "}, headers=L).status_code == 422
assert c.patch(f"/research/conversations/{chat_id}", json={"title":"Other user's title"}, headers=J).status_code == 404
assert c.patch(f"/research/conversations/{chat_id}", json={"title":"Other firm's title"}, headers=S).status_code == 404

# Deleting a conversation removes its message history and is restricted to its owner.
assert c.delete(f"/research/conversations/{chat_id}", headers=J).status_code == 404
assert c.delete(f"/research/conversations/{chat_id}", headers=L).status_code == 200
assert c.get(f"/research/conversations/{chat_id}", headers=L).status_code == 404
assert all(x["id"] != chat_id for x in c.get("/research/conversations", headers=L).json())
