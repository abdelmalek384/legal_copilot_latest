"""Download an Arabic law page and turn it into article-level rows (JSONL) plus a completeness report.
Run on a machine with internet access:  pip install requests ; python tools/fetch_arabic_law.py out_dir
Or use a page you saved yourself:       python tools/fetch_arabic_law.py out_dir --file saved_page.html"""
import sys, re, json, hashlib, pathlib, datetime
from html.parser import HTMLParser

LAWS = [{
    "id": "labor_law_14_2025_ar", "name": "قانون العمل رقم 14 لسنة 2025", "as_of": "2025-05-03",
    "url": "https://manshurat.org/node/76602", "blocks": {1: "مواد الإصدار", 2: "القانون المرافق"},
    "origin": "نص عربي منقول عن الجريدة الرسمية العدد 18 (تابع) في 3 مايو 2025، غير رسمي حتى تتم المطابقة مع الجريدة",
}]
TR = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
ORD = {w: i + 1 for i, w in enumerate(["الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة", "السابعة", "الثامنة", "التاسعة", "العاشرة",
                                      "الحادية عشرة", "الثانية عشرة", "الثالثة عشرة", "الرابعة عشرة", "الخامسة عشرة"])}
HEAD = re.compile(r"^[ \t]*\(?[ \t]*(?:ال)?مادة[ \t]*\(?[ \t]*(\d+|[\u0621-\u064a ]+?)[ \t]*\)?[ \t]*(مكررا?(?:[ \t]*\(?[\u0621-\u064a]\)?)?)?[ \t]*[:：]?[ \t]*\)?[ \t]*$")
SEC = re.compile(r"^[ \t]*\(?[ \t]*(الكتاب|الباب|الفصل|الفرع)[ \t]+[^\n]{1,25}?[ \t]*\)?[ \t]*$")


class Text(HTMLParser):
    BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "table", "section", "article"}
    SKIP = {"script", "style", "nav", "footer", "noscript"}

    def __init__(self): super().__init__(); self.out, self.skip = [], 0

    def handle_starttag(self, t, a):
        self.skip += t in self.SKIP
        if t in self.BLOCK: self.out.append("\n")

    def handle_endtag(self, t):
        if t in self.SKIP: self.skip = max(0, self.skip - 1)
        if t in self.BLOCK: self.out.append("\n")

    def handle_data(self, d):
        if not self.skip: self.out.append(d)


def to_lines(html):
    p = Text(); p.feed(html)
    return [re.sub(r"[ \t\u00a0\u200b\u200e\u200f]+", " ", l).strip() for l in "".join(p.out).translate(TR).split("\n")]


def split(lines):
    arts, cur, prev, block = [], None, 0, 1
    for l in lines:
        m = HEAD.match(l)
        n = int(m.group(1)) if m and m.group(1).isdigit() else ORD.get(m.group(1).strip()) if m else None
        if n:
            if cur: arts.append(cur)
            block += n < prev; prev = n
            cur = [str(n) + (" مكرر" if m.group(2) else ""), block, []]
        elif SEC.match(l): 
            if cur: arts.append(cur)
            cur = None  # a chapter heading ends the article; its title line is dropped
        elif cur and l: cur[2].append(l)
    if cur: arts.append(cur)
    return arts


def pieces(s, size=8000):
    while len(s) > size:
        k = s.rfind(" ", 0, size); k = k if k > 0 else size
        yield s[:k]; s = s[k:].lstrip()
    if s: yield s


def main(out, saved=None):
    out = pathlib.Path(out); out.mkdir(exist_ok=True); rows, rep = [], ["# Arabic import report", ""]
    for law in LAWS:
        if saved: raw = pathlib.Path(saved).read_bytes()
        else:
            import requests
            r = requests.get(law["url"], headers={"User-Agent": "EgyptLegalResearchPrototype/0.1"}, timeout=(10, 60)); r.raise_for_status(); raw = r.content
        arts = split(to_lines(raw.decode("utf-8", "replace")))
        src = "%s | %s | retrieved %s | sha256 %s" % (law["url"], law["origin"], datetime.date.today(), hashlib.sha256(raw).hexdigest()[:12])
        for art, block, body in arts:
            for t in pieces(" ".join(body)):
                rows.append({"law": law["name"] + " - " + law["blocks"].get(block, "جزء %d" % block), "article": art, "text": t,
                             "as_of": law["as_of"], "in_force": 1, "verified": 0, "source": src})
        rep += ["## " + law["name"], "", "| block | first | last | articles | missing numbers |", "|---|---|---|---|---|"]
        for b in sorted({a[1] for a in arts}):
            nums = sorted({int(a[0].split()[0]) for a in arts if a[1] == b}); miss = sorted(set(range(nums[0], nums[-1] + 1)) - set(nums))
            rep.append("| %s | %d | %d | %d | %d %s |" % (law["blocks"].get(b, b), nums[0], nums[-1], sum(a[1] == b for a in arts), len(miss), miss[:12]))
        short = [r["article"] for r in rows if len(r["text"]) < 40]
        rep += ["", "- very short rows (check): %s" % short[:20], "- END of last article (check there is no website footer text here):", "", "> " + (rows[-1]["text"][-300:] if rows else ""), ""]
    (out / "law_rows_ar.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    (out / "import_report_ar.md").write_text("\n".join(rep), encoding="utf-8"); print("rows:", len(rows)); print("\n".join(rep))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--file" else None)
