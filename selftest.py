import os, json, tempfile
os.environ["COPILOT_DB"] = os.path.join(tempfile.mkdtemp(), "t.db")
# This self-test deliberately exercises the fictional legacy corpus during migration.
os.environ["ALLOW_UNLINKED_LEGACY_LAW_SEARCH"] = "1"
import app
c = app.conn()
app.import_law(c, [json.loads(l) for l in open("sample_law.jsonl", encoding="utf-8")])
# The search fixture is fictional test data; explicitly mark only its first two rows as reviewed.
c.execute("UPDATE chunks SET verified=1,in_force=1 WHERE case_id IS NULL AND source='FICTIONAL-TEST-DATA' AND article IN ('1','2')")
c.commit()
assert app.norm("المَادَّة") == app.norm("الماده") and app.norm("ﻻ") == app.norm("لا")  # diacritics, PDF ligatures
assert app.search(c, "اجازة سنوية")[0]["ref"].endswith("المادة 1")
assert app.search(c, "الإجازةُ السَّنَويّة")[0]["ref"].endswith("المادة 1")
# Curated synonym expansion improves paraphrase recall while retaining the source passage as evidence.
synonym_hits = app.search(c, "عطلة سنوية")
assert synonym_hits and synonym_hits[0]["ref"].endswith("المادة 1")
assert "literal_match" in synonym_hits[0] and "expanded_match" in synonym_hits[0]
assert app.stem(app.norm("إجازة")) in app.expanded_tokens("عطلة سنوية")

assert app.search(c, "المادة ٢")[0]["ref"].endswith("المادة 2")
assert app.search(c, "للعاملين") and app.tokens("في من على") == []
assert app.ask(c, "qwerty zzz")["found"] is False
assert app.ask(c, "كيفية تسجيل علامة تجارية في الجمارك")["found"] is False
assert app.ask(c, "ما هي الاجازة السنوية للعامل؟")["found"] is True
app.LLM = lambda p: "تستحق اجازة [1]"; assert app.ask(c, "اجازة سنوية")["answer"]
app.LLM = lambda p: "اجابة بلا مصدر صالح [9]"; assert app.ask(c, "اجازة سنوية")["answer"] is None
# Unverified article 3 must not be returned as legal authority.
assert app.ask(c, "المادة 3")["found"] is False
# LLM transmission is fail-closed unless the deployment operator explicitly approves it.
from unittest.mock import patch
import io
_saved_llm_env = {k: os.environ.get(k) for k in ("LLM_URL", "LLM_MODEL", "LLM_KEY", "LLM_DATA_PROCESSING_APPROVED")}
try:
    os.environ["LLM_URL"] = "https://llm.example.test/v1/chat/completions"
    os.environ["LLM_MODEL"] = "test-model"
    os.environ["LLM_KEY"] = "test-key"
    os.environ.pop("LLM_DATA_PROCESSING_APPROVED", None)
    with patch("app.urllib.request.urlopen") as open_url:
        assert app.llm("CONFIDENTIAL-SENTINEL") is None
        open_url.assert_not_called()
    os.environ["LLM_DATA_PROCESSING_APPROVED"] = "1"
    fake_response = io.BytesIO(json.dumps({"choices": [{"message": {"content": "test answer"}}]}).encode())
    with patch("app.urllib.request.urlopen", return_value=fake_response) as open_url:
        assert app.llm("CONFIDENTIAL-SENTINEL") == "test answer"
        sent_request = open_url.call_args.args[0]
        assert b"CONFIDENTIAL-SENTINEL" in sent_request.data
finally:
    for _key, _value in _saved_llm_env.items():
        if _value is None:
            os.environ.pop(_key, None)
        else:
            os.environ[_key] = _value
assert app.check_pw("correct horse 12", app.hash_pw("correct horse 12")) and not app.check_pw("x", app.hash_pw("y"))
print("ALL OK")
