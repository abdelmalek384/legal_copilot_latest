import os, json, tempfile
os.environ["COPILOT_DB"] = os.path.join(tempfile.mkdtemp(), "t.db")
import app
c = app.conn()
app.import_law(c, [json.loads(l) for l in open("sample_law.jsonl", encoding="utf-8")])
assert app.norm("المَادَّة") == app.norm("الماده") and app.norm("ﻻ") == app.norm("لا")  # diacritics, PDF ligatures
assert app.search(c, "اجازة سنوية")[0]["ref"].endswith("المادة 1")
assert app.search(c, "الإجازةُ السَّنَويّة")[0]["ref"].endswith("المادة 1")
assert app.search(c, "المادة ٢")[0]["ref"].endswith("المادة 2")
assert app.search(c, "للعاملين") and app.tokens("في من على") == []
assert app.ask(c, "qwerty zzz")["found"] is False
assert app.ask(c, "كيفية تسجيل علامة تجارية في الجمارك")["found"] is False
assert app.ask(c, "ما هي الاجازة السنوية للعامل؟")["found"] is True
app.LLM = lambda p: "تستحق اجازة [1]"; assert app.ask(c, "اجازة سنوية")["answer"]
app.LLM = lambda p: "اجابة بلا مصدر صالح [9]"; assert app.ask(c, "اجازة سنوية")["answer"] is None
assert app.ask(c, "المادة 3")["not_in_force"]
assert app.check_pw("correct horse 12", app.hash_pw("correct horse 12")) and not app.check_pw("x", app.hash_pw("y"))
print("ALL OK")
