"""Turn downloaded law PDFs (+ their .json metadata files) into article-level rows and a completeness report.
Usage: python tools/import_laws.py egypt_laws out_dir   (needs pymupdf; pytesseract + tesseract only for PDFs with a broken text layer)"""
import sys, re, io, json, pathlib, collections
import os
import pymupdf

NAMES = {
    "penal_code_58_1937_en": "Penal Code (Law No. 58 of 1937)",
    "banking_law_88_2003_en": "Central Bank, Banking Sector and Money Law (Law No. 88 of 2003)",
    "investment_law_72_2017": "Investment Law (Law No. 72 of 2017)",
    "companies_law_159_1981_en": "Companies Law (Law No. 159 of 1981)",
    "income_tax_law_91_2005_en": "Income Tax Law (Law No. 91 of 2005)",
    "env_regs_pm_decree_338_1995_en": "Executive Regulations of Environment Law 4/1994 (PM Decree 338 of 1995)",
}
HEAD = re.compile(r"(?m)^[ \t]*Article[ \t]*:?[ \t]*\(?[ \t]*(\d+)(?:[ \t]*(bis(?:[ \t]*\(?[A-Za-z]\)?)?))?[ \t]*\)?[ \t]*[:\-]?[ \t]*$")


def _ocr(a):
    import pytesseract
    from PIL import Image
    path, i = a
    return pytesseract.image_to_string(Image.open(io.BytesIO(pymupdf.open(path)[i].get_pixmap(dpi=130).tobytes("png"))), lang="eng")


def page_texts(path, cache):
    d = pymupdf.open(path); pages = [p.get_text() for p in d]; s = "".join(pages)
    if sum(0xE000 <= ord(ch) <= 0xF8FF for ch in s) > 0.2 * max(len(s), 1):  # broken font encoding -> OCR
        cache = cache / path.stem; cache.mkdir(parents=True, exist_ok=True); budget = int(os.environ.get("OCR_BATCH", 10 ** 9)); out = []
        for i in range(len(d)):  # resumable: finished pages are cached, so an interrupted run can simply be repeated
            f = cache / ("%d.txt" % i)
            if not f.exists():
                if budget <= 0: raise SystemExit("OCR in progress (%d/%d pages done): run again" % (i, len(d)))
                f.write_text(_ocr((str(path), i)), encoding="utf-8"); budget -= 1
            out.append(f.read_text(encoding="utf-8"))
        return out, True
    return pages, False


def clean(pages):
    lines = [l.strip() for t in pages for l in t.replace("\r", "\n").split("\n")]
    freq = collections.Counter(l for l in lines if l)
    drop = {l for l, n in freq.items() if n > 12 and 8 <= len(l) < 80 and not HEAD.match(l)}  # repeated page headers/footers
    keep = [l for l in lines if l not in drop and not re.fullmatch(r"(Page\s*\|\s*)?\d{1,4}|First draft", l)]
    return "\n".join(keep)


def split(text):
    ms = list(HEAD.finditer(text)); rows, block, prev = [], 1, 0
    if (text[:ms[0].start()] if ms else text).strip(): rows.append(("preamble", 0, text[:ms[0].start()] if ms else text))
    for i, m in enumerate(ms):
        n = int(m.group(1))
        if n < prev: block += 1  # numbering restarted: a new block (annex, regulations, amending law)
        prev = n
        rows.append((m.group(1) + (" " + m.group(2) if m.group(2) else ""), block, text[m.end():ms[i + 1].start() if i + 1 < len(ms) else len(text)]))
    return rows


def pieces(s, size=8000):
    s = re.sub(r"(?<!\n)\n(?!\n)", " ", s); s = re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n\n", s)).strip()
    while len(s) > size:
        k = s.rfind(" ", 0, size); k = k if k > 0 else size
        yield s[:k]; s = s[k:].lstrip()
    if s: yield s


def main(src, out):
    out = pathlib.Path(out); out.mkdir(exist_ok=True); allrows, rep = [], ["# Import report", ""]
    for mp in sorted(pathlib.Path(src).glob("*.json")):
        meta = json.loads(mp.read_text(encoding="utf-8")); did = meta["document_id"]
        pages, ocr = page_texts(mp.with_suffix(".pdf"), out / ".ocr_cache"); parts = split(clean(pages)); name = NAMES.get(did, did)
        source = "%s | English translation (not authoritative; the Arabic original governs) | retrieved %s | sha256 %s%s" % (
            meta["source_url"], meta["retrieved_at"][:10], meta["content_sha256"][:12], " | text recovered by OCR" if ocr else "")
        blocks, n_rows = collections.defaultdict(list), 0
        for art, block, body in parts:
            txt = list(pieces(body)); blocks[block].append(art)
            for t in txt:
                allrows.append({"law": name + ("" if block <= 1 else " [block %d]" % block), "article": art, "text": t, "as_of": None,
                                "in_force": 1, "verified": 0, "source": source}); n_rows += 1
        rep += ["## %s" % name, "- file: %s.pdf | pages: %d | OCR used: %s | rows: %d | review_status: %s" % (did, len(pages), ocr, n_rows, meta.get("review_status")), ""]
        rep += ["| block | first | last | articles found | missing numbers in range |", "|---|---|---|---|---|"]
        for b, arts in sorted(blocks.items()):
            nums = sorted({int(a.split()[0]) for a in arts if a[0].isdigit()})
            miss = sorted(set(range(nums[0], nums[-1] + 1)) - set(nums)) if nums else []
            rep.append("| %s | %s | %s | %d | %d %s |" % ("preamble" if b == 0 else b, nums[0] if nums else "-", nums[-1] if nums else "-", len(arts), len(miss), miss[:12] if miss else ""))
        short = sum(1 for r in allrows if r["source"] == source and len(r["text"]) < 40)
        rep += ["", "- very short rows (<40 chars, check for splitting errors): %d" % short, ""]
    (out / "law_rows.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in allrows) + "\n", encoding="utf-8")
    (out / "import_report.md").write_text("\n".join(rep), encoding="utf-8")
    print("rows:", len(allrows)); print("\n".join(rep))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
