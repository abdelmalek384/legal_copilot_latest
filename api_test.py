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
A_IMPORT = {"Authorization": "Bearer " + c.post("/login", json={"email":"import-admin@x.eg","password":"password-ImportAdmin"}).json()["token"]}
def login(n): return {"Authorization": "Bearer " + c.post("/login", json={"email": n.lower() + "@x.eg", "password": "password-" + n}).json()["token"]}
L, J, O = login("Lead"), login("Junior"), login("Outsider")
assert c.get("/").headers.get("x-content-type-options") == "nosniff"
assert c.get("/").headers.get("x-frame-options") == "DENY"
assert c.get("/cases/999999999999999999999999999999999999", headers=L).status_code in (404, 422)
assert c.get("/cases").status_code == 401 and c.post("/login", json={"email": "lead@x.eg", "password": "bad"}).status_code == 401
rows = [json.loads(l) for l in open("sample_law.jsonl", encoding="utf-8")]
assert c.post("/law/import", json=rows, headers=L).status_code == 403
assert c.post("/law/import", json=rows, headers={"X-Admin-Token": "stage0-test-admin-token-please-use-a-long-random-secret"}).status_code == 401
assert c.post("/law/import", json=rows, headers={**A_IMPORT, "X-Admin-Token": "stage0-test-admin-token-please-use-a-long-random-secret"}).json()["imported"] == 3
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
S = {"Authorization": "Bearer " + c.post("/login", json={"email":"second@x.eg","password":"password-Second"}).json()["token"]}
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
A = {"Authorization": "Bearer " + c.post("/login", json={"email":"admin@x.eg","password":"password-Admin"}).json()["token"]}
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
assert c.post(f"/users/{new_uid}/disable", headers=A).status_code == 200
assert c.post("/login", json={"email":"disable@x.eg","password":"long-enough-password"}).status_code == 401
assert c.delete(f"/cases/{cid}", headers=J).status_code == 404 and c.delete(f"/cases/{cid}", headers=L).status_code == 200
# Authentication regression tests: malformed headers, expiry, reset revocation, role boundary, concurrent logins.
# Malformed or non-Bearer authorization values must never authenticate.
for malformed in ("", "garbage", "Bearer", "Basic abc", "Bearer not-a-real-token"):
    assert c.get("/cases", headers={"Authorization": malformed}).status_code == 401
# Expired sessions must be rejected even if their token is otherwise valid.
expired = login("Junior")
expired_token = expired["Authorization"].split(" ", 1)[1]
db.execute("UPDATE auth_sessions SET expires=? WHERE token_hash=?", (int(__import__("time").time()) - 1, app.sha(expired_token)))
db.commit()
assert c.get("/cases", headers=expired).status_code == 401
# Password reset must revoke all sessions for that account.
import manage
from types import SimpleNamespace
from unittest.mock import patch
reset_user = c.post("/users", json={"name":"Reset Test","email":"reset@x.eg","password":"old-password-Long","role":"lawyer"}, headers=A).json()
reset_token = {"Authorization":"Bearer "+c.post("/login",json={"email":"reset@x.eg","password":"old-password-Long"}).json()["token"]}
assert c.get("/cases", headers=reset_token).status_code == 200
with patch.object(manage, "read_password", return_value="new-password-Long"):
    manage.resetpw(SimpleNamespace(email="reset@x.eg"))
assert c.get("/cases", headers=reset_token).status_code == 401
assert c.post("/login",json={"email":"reset@x.eg","password":"old-password-Long"}).status_code == 401
assert c.post("/login",json={"email":"reset@x.eg","password":"new-password-Long"}).status_code == 200
# Non-admin users must not be able to invoke protected administrative law import.
assert c.post("/law/import", json=rows, headers={**L, "X-Admin-Token":"stage0-test-admin-token-please-use-a-long-random-secret"}).status_code == 403
# Concurrent successful login requests should not corrupt session state or spuriously lock the account.
from concurrent.futures import ThreadPoolExecutor
def concurrent_login(_):
    return c.post("/login", json={"email":"reset@x.eg","password":"new-password-Long"}).status_code
with ThreadPoolExecutor(max_workers=4) as pool:
    concurrent_statuses = list(pool.map(concurrent_login, range(4)))
assert concurrent_statuses == [200, 200, 200, 200], concurrent_statuses
# Logout revokes the server-side session, not just the browser token.
logout_headers = login("Junior")
assert c.get("/cases", headers=logout_headers).status_code == 200
assert c.post("/logout", headers=logout_headers).status_code == 200
assert c.get("/cases", headers=logout_headers).status_code == 401
for _ in range(5): c.post("/login", json={"email": "lead@x.eg", "password": "bad"})
assert c.post("/login", json={"email": "lead@x.eg", "password": "password-Lead"}).status_code == 429   # lockout persists
print("API OK")
