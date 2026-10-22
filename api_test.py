import os, io, json, tempfile
os.environ.update(COPILOT_DB=os.path.join(tempfile.mkdtemp(), "a.db"), ADMIN_TOKEN="adm")
from fastapi.testclient import TestClient
import app, docx
c = TestClient(app.app); db = app.conn()
for n, role in (("Lead", "lawyer"), ("Junior", "junior"), ("Outsider", "lawyer")):
    db.execute("INSERT INTO users(name,email,pw,role) VALUES(?,?,?,?)", (n, n.lower() + "@x.eg", app.hash_pw("password-" + n), role))
db.commit()
def login(n): return {"Authorization": "Bearer " + c.post("/login", json={"email": n.lower() + "@x.eg", "password": "password-" + n}).json()["token"]}
L, J, O = login("Lead"), login("Junior"), login("Outsider")
assert c.get("/cases").status_code == 401 and c.post("/login", json={"email": "lead@x.eg", "password": "bad"}).status_code == 401
rows = [json.loads(l) for l in open("sample_law.jsonl", encoding="utf-8")]
assert c.post("/law/import", json=rows, headers=L).status_code == 403
assert c.post("/law/import", json=rows, headers={"X-Admin-Token": "adm"}).json()["imported"] == 3
cid = c.post("/cases", json={"title": "<b>x</b>", "client": "عميل"}, headers=L).json()["id"]
jid = [u for u in c.get("/users", headers=L).json() if u["name"] == "Junior"][0]["id"]
assert c.post(f"/cases/{cid}/tasks", json={"title": "t", "assignee": jid}, headers=L).status_code == 422   # not a member yet
assert c.post(f"/cases/{cid}/members", json={"user_id": jid, "role": "junior"}, headers=J).status_code == 404  # junior cannot manage team
assert c.post(f"/cases/{cid}/members", json={"user_id": jid, "role": "junior"}, headers=L).status_code == 200
assert c.post(f"/cases/{cid}/tasks", json={"title": "مذكرة", "assignee": jid, "due": "2099-01-01"}, headers=L).status_code == 200
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
assert c.delete(f"/cases/{cid}", headers=J).status_code == 404 and c.delete(f"/cases/{cid}", headers=L).status_code == 200
for _ in range(5): c.post("/login", json={"email": "lead@x.eg", "password": "bad"})
assert c.post("/login", json={"email": "lead@x.eg", "password": "password-Lead"}).status_code == 429   # lockout
print("API OK")
