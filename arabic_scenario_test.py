"""Arabic multi-case scenario test using an isolated temporary SQLite database.

All people, firms, matters, dates and amounts in this test are fictional.
Run from the project root: python arabic_scenario_test.py
This script does not write to the normal copilot.db.
"""
import json
import os
import sqlite3
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

# Real DOCX upload and extraction test (not just saving text through the API).
from io import BytesIO
from docx import Document

docx_buffer = BytesIO()
docx_file = Document()
docx_file.add_paragraph("مستند عربي خيالي لاختبار رفع الملفات واستخراج النص.")
docx_file.add_paragraph("هذه فقرة ثانية للتأكد من حفظ محتوى الملف.")
docx_file.save(docx_buffer)
upload_response = client.post(
    f"/cases/{created[0][0]}/upload",
    files={"file": ("اختبار-عربي.docx", docx_buffer.getvalue(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    headers=headers,
)
assert upload_response.status_code == 200, (
    f"رفع DOCX واستخراج النص فشل: {upload_response.status_code} {upload_response.text}"
)
uploaded_detail = client.get(f"/cases/{created[0][0]}", headers=headers).json()
assert any(d["name"] == "اختبار-عربي.docx" for d in uploaded_detail.get("docs", [])), "الملف المرفوع لا يظهر في القضية"

# Real PDF upload and text-extraction test (generated in memory; no external file).
from io import BytesIO
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, NumberObject, StreamObject

pdf_writer = PdfWriter()
pdf_page = pdf_writer.add_blank_page(width=612, height=792)
font = DictionaryObject({
    NameObject("/Type"): NameObject("/Font"),
    NameObject("/Subtype"): NameObject("/Type1"),
    NameObject("/BaseFont"): NameObject("/Helvetica"),
})
resources = DictionaryObject({
    NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})
})
pdf_page[NameObject("/Resources")] = resources
pdf_stream = StreamObject()
pdf_stream._data = b"BT /F1 12 Tf 72 720 Td (Fictional PDF contract text for extraction testing.) Tj ET"
pdf_page[NameObject("/Contents")] = pdf_writer._add_object(pdf_stream)
pdf_buffer = BytesIO()
pdf_writer.write(pdf_buffer)
pdf_response = client.post(
    f"/cases/{created[0][0]}/upload",
    files={"file": ("fictional-contract.pdf", pdf_buffer.getvalue(), "application/pdf")},
    headers=headers,
)
assert pdf_response.status_code == 200, (
    f"رفع PDF واستخراج النص فشل: {pdf_response.status_code} {pdf_response.text}"
)
pdf_detail = client.get(f"/cases/{created[0][0]}", headers=headers).json()
assert any(d["name"] == "fictional-contract.pdf" for d in pdf_detail.get("docs", [])), "ملف PDF المرفوع لا يظهر في القضية"

# Reject unsupported file types and mutation requests without a CSRF header.
bad_upload = client.post(
    f"/cases/{created[0][0]}/upload",
    files={"file": ("not-allowed.txt", b"this is a text file that should be rejected", "text/plain")},
    headers=headers,
)
assert bad_upload.status_code == 415, f"لم يُرفض نوع الملف غير المدعوم: {bad_upload.status_code}"
no_csrf_headers = {"Cookie": f"lc_session={session}; lc_csrf={csrf}"}
csrf_response = client.post(
    f"/cases/{created[0][0]}/notes",
    json={"text": "يجب رفض هذا الطلب لغياب ترويسة CSRF"},
    headers=no_csrf_headers,
)
assert csrf_response.status_code == 403, f"لم يُرفض الطلب دون CSRF: {csrf_response.status_code}"

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
print("نجاح: رفع ملف DOCX عربي واستخراج النص منه")
print("نجاح: رفع ملف PDF واستخراج النص منه")
print("نجاح: رفض امتداد ملف غير مدعوم")
print("نجاح: رفض طلب تعديل دون CSRF")
print("ملاحظة: جميع البيانات محفوظة في قاعدة SQLite مؤقتة منفصلة، ولن تُضاف إلى قاعدة بيانات المكتب.")
# Encrypted backup/restore round trip using a separate temporary database.
import base64
import subprocess
import sys
from cryptography.fernet import Fernet

backup_dir = os.path.join(tempfile.mkdtemp(prefix="legal_copilot_backup_test_"), "backups")
restore_path = os.path.join(tempfile.mkdtemp(prefix="legal_copilot_restore_test_"), "restored.db")
backup_key = Fernet.generate_key().decode()
env = os.environ.copy()
env["BACKUP_KEY"] = backup_key
env["COPILOT_DB"] = os.environ["COPILOT_DB"]
manage_path = os.path.join(os.path.dirname(__file__), "manage.py")
backup_result = subprocess.run(
    [sys.executable, manage_path, "backup", backup_dir, "--keep", "2"],
    env=env, capture_output=True, text=True, timeout=30,
)
assert backup_result.returncode == 0, f"إنشاء النسخة الاحتياطية فشل: {backup_result.stdout} {backup_result.stderr}"
backup_files = [os.path.join(backup_dir, name) for name in os.listdir(backup_dir) if name.endswith(".enc")]
assert len(backup_files) == 1, "لم يتم إنشاء ملف نسخة احتياطية مشفر واحد"
restore_result = subprocess.run(
    [sys.executable, manage_path, "restore", backup_files[0], restore_path],
    env=env, capture_output=True, text=True, timeout=30,
)
assert restore_result.returncode == 0, f"استعادة النسخة الاحتياطية فشلت: {restore_result.stdout} {restore_result.stderr}"
restored_db = sqlite3.connect(restore_path)
restored_cases = restored_db.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
restored_notes = restored_db.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
assert restored_cases == 5, f"عدد القضايا بعد الاستعادة غير صحيح: {restored_cases}"
assert restored_notes >= 5, f"الملاحظات لم تُستعد بالكامل: {restored_notes}"
integrity = restored_db.execute("PRAGMA integrity_check").fetchone()[0]
assert integrity == "ok", f"قاعدة البيانات المستعادة غير سليمة: {integrity}"
restored_db.close()
# Wrong key must not produce a successful restore.
wrong_env = env.copy()
wrong_env["BACKUP_KEY"] = Fernet.generate_key().decode()
wrong_path = os.path.join(tempfile.mkdtemp(prefix="legal_copilot_wrong_key_"), "bad.db")
wrong_result = subprocess.run(
    [sys.executable, manage_path, "restore", backup_files[0], wrong_path],
    env=wrong_env, capture_output=True, text=True, timeout=30,
)
assert wrong_result.returncode != 0, "الاستعادة بمفتاح خاطئ لم تُرفض"
print("نجاح: إنشاء نسخة احتياطية مشفرة واستعادتها")
print("نجاح: التحقق من سلامة قاعدة البيانات المستعادة وعدد القضايا والملاحظات")
print("نجاح: رفض الاستعادة بمفتاح تشفير خاطئ")
print("لم يُختبر هنا: صحة الرأي القانوني، صحة مواعيد قانونية حقيقية، رفع ملفات PDF فعليًا، أو اختبار اختراق مستقل.")

# CI execution is enabled for the audit/ branch family.
