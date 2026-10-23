"""Arabic multi-case scenario test using an isolated temporary SQLite database.

All people, firms, matters, dates and amounts in this test are fictional.
Run from the project root: python arabic_scenario_test.py
This script does not write to the normal copilot.db.
"""
import json
import os
import tempfile
from datetime import date, timedelta

os.environ["COPILOT_DB"] = os.path.join(tempfile.mkdtemp(prefix="legal_copilot_arabic_test_"), "test.db")
os.environ["ADMIN_TOKEN"] = "arabic-scenario-test-token-long-enough-32-chars"
from fastapi.testclient import TestClient
import app

client = TestClient(app.app)
db = app.conn()
db.execute(
    "INSERT INTO users(name,email,pw,role,firm_id) VALUES(?,?,?,?,?)",
    ("مسؤول الاختبار", "arabic-test@example.invalid", app.hash_pw("Arabic-test-password-2026"), "admin", 1),
)
db.commit()

login = client.post("/login", json={
    "email": "arabic-test@example.invalid",
    "password": "Arabic-test-password-2026",
})
assert login.status_code == 200, f"تسجيل الدخول فشل: {login.status_code} {login.text}"
session = login.cookies.get("lc_session")
csrf = login.cookies.get("lc_csrf")
assert session and csrf, "لم تُنشأ جلسة آمنة أو رمز CSRF"
headers = {"Cookie": f"lc_session={session}; lc_csrf={csrf}", "X-CSRF-Token": csrf}

today = date.today()
scenarios = [
    {
        "title": "اختبار مدني — نزاع عقد توريد",
        "client": "أحمد محمود — اسم وهمي",
        "case_number": "١٠١", "case_year": "٢٠٢٦",
        "court": "محكمة افتراضية للاختبار", "circuit": "الدائرة المدنية",
        "opposing_party": "شركة النور — اسم وهمي",
        "deadline": today + timedelta(days=7),
        "note": "واقعة خيالية: خلاف على تنفيذ عقد توريد.",
    },
    {
        "title": "اختبار عمالي — مستحقات مالية",
        "client": "منى إبراهيم — اسم وهمي",
        "case_number": "٢٠٢", "case_year": "٢٠٢٦",
        "court": "محكمة افتراضية للاختبار", "circuit": "الدائرة العمالية",
        "opposing_party": "مؤسسة تجريبية",
        "deadline": today + timedelta(days=2),
        "note": "واقعة خيالية: مطالبة بمستحقات مالية.",
    },
    {
        "title": "اختبار إيجاري — التزامات عقد",
        "client": "خالد علي — اسم وهمي",
        "case_number": "٣٠٣", "case_year": "٢٠٢٦",
        "court": "محكمة افتراضية للاختبار", "circuit": "الدائرة المدنية",
        "opposing_party": "سمير حسن — اسم وهمي",
        "deadline": today + timedelta(days=10),
        "note": "واقعة خيالية: خلاف بشأن التزامات عقد إيجار.",
    },
    {
        "title": "اختبار تجاري — فواتير غير مسددة",
        "client": "شركة الأفق — اسم وهمي",
        "case_number": "٤٠٤", "case_year": "٢٠٢٦",
        "court": "محكمة افتراضية للاختبار", "circuit": "الدائرة التجارية",
        "opposing_party": "شركة المدار — اسم وهمي",
        "deadline": today + timedelta(days=4),
        "note": "واقعة خيالية: مطالبة بقيمة فواتير.",
    },
    {
        "title": "اختبار أحوال شخصية — ملف تجريبي",
        "client": "سارة يوسف — اسم وهمي",
        "case_number": "٥٠٥", "case_year": "٢٠٢٦",
        "court": "محكمة افتراضية للاختبار", "circuit": "دائرة افتراضية",
        "opposing_party": "طرف افتراضي",
        "deadline": today + timedelta(days=5),
        "note": "ملف خيالي لا يتضمن بيانات شخصية حقيقية.",
    },
]

created = []
for item in scenarios:
    payload = {k: item[k] for k in ("title", "client")}
    response = client.post("/cases", json=payload, headers=headers)
    assert response.status_code == 200, f"إنشاء القضية فشل ({item['title']}): {response.status_code} {response.text}"
    case_id = response.json()["id"]
    created.append((case_id, item))
    patch = {k: item[k] for k in ("case_number", "case_year", "court", "circuit", "opposing_party")}
    response = client.patch(f"/cases/{case_id}", json=patch, headers=headers)
    assert response.status_code == 200, f"حفظ بيانات القضية فشل: {response.status_code} {response.text}"
    response = client.post(f"/cases/{case_id}/notes", json={"text": item["note"]}, headers=headers)
    assert response.status_code == 200, f"حفظ الملاحظة فشل: {response.status_code} {response.text}"
    response = client.post(
        f"/cases/{case_id}/deadlines",
        json={"title": "موعد تجريبي — مراجعة الملف", "due": item["deadline"].isoformat(), "note": "موعد وهمي للاختبار"},
        headers=headers,
    )
    assert response.status_code == 200, f"إضافة الموعد فشلت: {response.status_code} {response.text}"

# Check list and detail retrieval, ensuring the five matters remain distinct.
response = client.get("/cases", headers=headers)
assert response.status_code == 200, f"قائمة القضايا فشلت: {response.status_code}"
case_list = response.json()
created_ids = {cid for cid, _ in created}
assert created_ids.issubset({row["id"] for row in case_list}), "بعض القضايا لا تظهر في القائمة"
assert len([row for row in case_list if row["id"] in created_ids]) == 5, "عدد القضايا التجريبية ليس خمسة"

for case_id, item in created:
    response = client.get(f"/cases/{case_id}", headers=headers)
    assert response.status_code == 200, f"فتح القضية فشل: {response.status_code}"
    detail = response.json()
    assert detail["title"] == item["title"], "اختلاط عنوان قضية بأخرى"
    assert detail["client"] == item["client"], "اختلاط بيانات الموكلين"
    assert detail["case_number"] == item["case_number"], "رقم القضية لم يُحفظ كما أُدخل"
    assert detail["opposing_party"] == item["opposing_party"], "بيانات الخصم لم تُحفظ"
    assert any(note["text"] == item["note"] for note in detail.get("notes", [])), "الملاحظة العربية غير موجودة"
    assert any(deadline["title"] == "موعد تجريبي — مراجعة الملف" for deadline in detail.get("deadlines", [])), "الموعد غير موجود"

# Fee calculations: one fictional commercial matter.
fee_case = next(cid for cid, item in created if item["case_number"] == "٤٠٤")
response = client.post(
    f"/cases/{fee_case}/fees",
    json={"title": "أتعاب تجريبية", "amount": 10000, "paid": 2500},
    headers=headers,
)
assert response.status_code == 200, f"إضافة الأتعاب فشلت: {response.status_code} {response.text}"
fee_detail = client.get(f"/cases/{fee_case}", headers=headers).json()
fee = next((x for x in fee_detail.get("fees", []) if x["title"] == "أتعاب تجريبية"), None)
assert fee is not None, "الأتعاب لا تظهر في القضية"
assert fee["amount"] == 10000 and fee["paid"] == 2500, "قيمة الأتعاب أو المدفوع غير صحيحة"
assert fee["amount"] - fee["paid"] == 7500, "حساب المتبقي غير صحيح"

# Arabic document text storage and retrieval smoke test.
doc_text = "مستند تجريبي خيالي: يوضح هذا النص شروط عقد التوريد محل الاختبار.\n\nفقرة ثانية باللغة العربية لاختبار حفظ النص."
doc_response = client.post(
    f"/cases/{created[0][0]}/docs",
    json={"name": "مستند عقد توريد تجريبي", "text": doc_text},
    headers=headers,
)
assert doc_response.status_code == 200, f"حفظ نص المستند فشل: {doc_response.status_code} {doc_response.text}"
doc_detail = client.get(f"/cases/{created[0][0]}", headers=headers).json()
assert any(d["name"] == "مستند عقد توريد تجريبي" for d in doc_detail.get("docs", [])), "المستند لا يظهر في ملف القضية"

# Cross-firm isolation: a user in another firm must not read this firm's case.
db.execute(
    "INSERT INTO firms(id,name) VALUES(?,?)",
    (2, "مكتب تجريبي ثانٍ"),
)
db.execute(
    "INSERT INTO users(name,email,pw,role,firm_id) VALUES(?,?,?,?,?)",
    ("محامٍ من مكتب آخر", "other-firm-test@example.invalid", app.hash_pw("Other-firm-test-password-2026"), "admin", 2),
)
db.commit()
other_client = TestClient(app.app)
other_login = other_client.post("/login", json={
    "email": "other-firm-test@example.invalid",
    "password": "Other-firm-test-password-2026",
})
assert other_login.status_code == 200, f"تسجيل دخول المكتب الثاني فشل: {other_login.status_code}"
other_session = other_login.cookies.get("lc_session")
other_csrf = other_login.cookies.get("lc_csrf")
assert other_session and other_csrf, "لم تُنشأ جلسة للمكتب الثاني"
other_headers = {"Cookie": f"lc_session={other_session}; lc_csrf={other_csrf}", "X-CSRF-Token": other_csrf}
cross_firm_response = other_client.get(f"/cases/{created[0][0]}", headers=other_headers)
assert cross_firm_response.status_code in (403, 404), (
    f"قد يتمكن مستخدم من مكتب آخر من قراءة القضية: {cross_firm_response.status_code}"
)

# Authorization and input-validation negative tests.
anonymous = TestClient(app.app)
anonymous_response = anonymous.get(f"/cases/{created[0][0]}")
assert anonymous_response.status_code == 401, f"الطلب دون تسجيل دخول لم يُرفض: {anonymous_response.status_code}"
bad_fee_response = client.post(
    f"/cases/{fee_case}/fees",
    json={"title": "اختبار مبلغ غير صحيح", "amount": 100, "paid": 150},
    headers=headers,
)
assert bad_fee_response.status_code == 422, f"لم يُرفض دفع أكبر من إجمالي الأتعاب: {bad_fee_response.status_code}"

# Conflict search should find the fictional client in its own case.
response = client.post("/conflicts", json={"q": "شركة الأفق"}, headers=headers)
assert response.status_code == 200, f"فحص تعارض المصالح فشل: {response.status_code} {response.text}"
assert any(m["id"] == fee_case for m in response.json().get("matches", [])), "لم يُعثر على موكل الاختبار في فحص التعارض"

# Search route smoke test. We only assert a valid API response, not legal correctness.
search_response = client.post("/search", json={"q": "عقد توريد", "case_id": created[0][0]}, headers=headers)
assert search_response.status_code == 200, f"اختبار البحث فشل: {search_response.status_code} {search_response.text}"

print("نجاح: تسجيل الدخول وإنشاء جلسة CSRF")
print("نجاح: إنشاء ٥ قضايا عربية تجريبية")
print("نجاح: حفظ واسترجاع بيانات القضية دون اختلاط")
print("نجاح: حفظ ٥ ملاحظات عربية و٥ مواعيد تجريبية")
print("نجاح: تسجيل الأتعاب وحساب المتبقي (٧٥٠٠)")
print("نجاح: فحص تعارض المصالح للموكل التجريبي")
print("نجاح: استجابة واجهة البحث")
print("نجاح: حفظ نص مستند عربي وظهوره في ملف القضية")
print("نجاح: رفض الوصول دون تسجيل دخول")
print("نجاح: منع مستخدم مكتب آخر من قراءة القضية")
print("نجاح: رفض تسجيل مبلغ مدفوع أكبر من إجمالي الأتعاب")
print("ملاحظة: جميع البيانات محفوظة في قاعدة SQLite مؤقتة منفصلة، ولن تُضاف إلى قاعدة بيانات المكتب.")
print("لم يُختبر هنا: صحة الرأي القانوني، صحة مواعيد قانونية حقيقية، رفع ملفات PDF/DOCX فعليًا، أو اختبار اختراق مستقل.")

# CI execution is enabled for the audit/ branch family.
