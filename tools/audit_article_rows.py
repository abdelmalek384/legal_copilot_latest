#!/usr/bin/env python3
"""Structural and text-quality audit of a JSONL corpus of article rows (fields: law, article, text).

    python tools/audit_article_rows.py --input law_rows_ar.jsonl --out-dir audit_report

Checks (all offline, evidence only, nothing is imported or marked verified):
  * numbering per law/group: gaps, duplicates, order, non-numeric labels;
  * empty or very short text, hidden/replacement characters, mixed digit systems, double spaces,
    Latin fragments, Gazette header/page artifacts, repeated words;
  * texts that do not end in punctuation (reported with their last words, since a citation such as
    "...الصادر بالقانون رقم 15 لسنة 2017" is a natural ending, not necessarily truncation);
  * exact duplicate article texts;
  * numeric cross-references that point past the last article;
  * orthography outliers: when one spelling style dominates (for example the Gazette's typographic
    "فى/التى/الذى") the few rows that use the other style are listed, because they may have been
    re-typed or taken from a different version and deserve the first look;
  * an inventory of articles that state periods, amounts, percentages or counts, exported as a
    checklist for a lawyer to tick against the official text;
  * the embedded verified / in_force / as_of flags, which are reported but never trusted.

A clean audit says the file is internally consistent. It does not prove the text matches the
Official Gazette, that it is in force, or that reuse is permitted.
"""
import argparse
import collections
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

AD = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
UNITS = r"(?:يوم\w*|أيام|ايام|شهر\w*|أشهر|اشهر|سنة|سنوات|سنه|جنيه\w*|ساعة|ساعات|في المائة|بالمائة|فى المائة|%|٪)"
WORDS = (r"(?:واحد|اثنين|اثنان|ثلاث\w*|أربع\w*|اربع\w*|خمس\w*|ست\w*|سبع\w*|ثمان\w*|تسع\w*|عشر\w*|ثلاثين|أربعين|خمسين|"
         r"ستين|سبعين|ثمانين|تسعين|مائة|مئة|مائتي|ألف|مليون|نصف|ثلث|ربع)")
QUANTITY = re.compile(rf"(\d+(?:[\.,]\d+)?\s*(?:%|٪)|\d+(?:[\.,]\d+)?(?=\s*{UNITS})|{WORDS}(?=\s+{UNITS}))")
LIST_MARKER_AFTER = re.compile(r"^\s*[-–\)]")
REF_PRECEDES = re.compile(r"(?:رقم|لسنة|المادة|المواد|مادة|مادتي|بند|البند|الفقرة)\s*\(?\s*$")
STYLE_PAIRS = [("فى", "في"), ("التى", "التي"), ("الذى", "الذي")]
ARABIC_LETTER = "ء-ي"


def norm(text):
    return unicodedata.normalize("NFKC", text).translate(AD)


def load_rows(path):
    rows, malformed = [], 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                malformed += 1
                continue
            if isinstance(row, dict) and isinstance(row.get("text"), str):
                rows.append(row)
            else:
                malformed += 1
    return rows, malformed


def word_re(word):
    return re.compile(rf"(?<![{ARABIC_LETTER}]){word}(?![{ARABIC_LETTER}])")


def audit(rows, min_len=40):
    findings = collections.defaultdict(list)
    groups = collections.OrderedDict()
    for row in rows:
        groups.setdefault(row.get("law", ""), []).append(row)
    numbering = {}
    for group, items in groups.items():
        labels = [norm(str(r.get("article", ""))).strip() for r in items]
        ints = [int(x) for x in labels if x.isdigit()]
        numbering[group] = {
            "rows": len(labels),
            "first": min(ints) if ints else None,
            "last": max(ints) if ints else None,
            "non_numeric_labels": [x for x in labels if not x.isdigit()],
            "duplicates": sorted({x for x, c in collections.Counter(labels).items() if c > 1}),
            "gaps": sorted(set(range(1, max(ints) + 1)) - set(ints)) if ints else [],
            "in_order": ints == sorted(ints),
        }
    global_last = max([v["last"] for v in numbering.values() if v["last"]] or [0])
    for row in rows:
        text, label = row["text"], f"{row.get('law', '')[:40]} / {row.get('article')}"
        if not text.strip():
            findings["empty_text"].append(label)
            continue
        if len(text.strip()) < min_len:
            findings["very_short_text"].append(label)
        if re.search(r"[\ufffd\u200b-\u200f\u202a-\u202e\ufeff]", text):
            findings["hidden_or_replacement_characters"].append(label)
        if re.search(r"[٠-٩]", text) and re.search(r"[0-9]", text):
            findings["mixed_digit_systems"].append(label)
        if re.search(r"  +", text):
            findings["double_spaces"].append(label)
        if re.search(r"[A-Za-z]{3,}", text):
            findings["latin_fragments"].append(label)
        if re.search(r"(الوقائع المصرية|العدد\s*\d+\s*\(?تابع|صفحة\s*\d+)", text):
            findings["gazette_header_or_page_artifacts"].append(label)
        if re.search(r"(\S+)\s+\1\s+\1", text):
            findings["triple_repeated_word"].append(label)
        if not re.search(r"[\.\:;؛!؟\?]\s*$", text.strip()):
            findings["no_terminal_punctuation"].append({"row": label, "last_words": text.strip()[-70:]})
    seen, duplicates = {}, []
    for row in rows:
        key = re.sub(r"\W+", "", norm(row["text"]))
        if key in seen:
            duplicates.append({"first": seen[key], "again": f"{row.get('law', '')[:40]} / {row.get('article')}"})
        else:
            seen[key] = f"{row.get('law', '')[:40]} / {row.get('article')}"
    bad_refs, total_refs = [], 0
    for row in rows:
        for match in re.finditer(r"(?:المادة|المواد|مادة|مادتي)\s*\(?\s*(\d+)\s*\)?(?:\s*(?:و|،|,|إلى|الى)\s*\(?\s*(\d+)\s*\)?)*", norm(row["text"])):
            for number in re.findall(r"\d+", match.group(0)):
                total_refs += 1
                if global_last and int(number) > global_last:
                    bad_refs.append({"row": f"{row.get('law', '')[:40]} / {row.get('article')}", "ref": number})
    outliers, styles = [], {}
    corpus = " ".join(r["text"] for r in rows)
    for classic, modern in STYLE_PAIRS:
        c, m = len(word_re(classic).findall(corpus)), len(word_re(modern).findall(corpus))
        styles[f"{classic} vs {modern}"] = [c, m]
        total = c + m
        if total >= 20 and max(c, m) / total >= 0.9:
            minority = modern if c >= m else classic
            for row in rows:
                match = word_re(minority).search(row["text"])
                if match:
                    s = row["text"]
                    outliers.append({"row": f"{row.get('law', '')[:40]} / {row.get('article')}", "word": minority,
                                     "context": s[max(0, match.start() - 30): match.end() + 30]})
    return {
        "rows": len(rows),
        "numbering": numbering,
        "findings": {k: v for k, v in findings.items()},
        "exact_duplicate_texts": duplicates,
        "cross_references": {"total_numeric_references": total_refs, "beyond_highest_article_in_file": bad_refs},
        "orthography": {"counts_classic_vs_modern": styles, "minority_style_rows": outliers},
        "embedded_flags": {k: dict(collections.Counter(str(r.get(k)) for r in rows)) for k in ("verified", "in_force", "as_of")},
    }


def quantity_checklist(rows, outlier_rows=()):
    items = []
    outlier_rows = set(outlier_rows)
    for row in rows:
        text = norm(row["text"])
        snippets = []
        for match in QUANTITY.finditer(text):
            if LIST_MARKER_AFTER.match(text[match.end(): match.end() + 3]) and match.group(0).strip().isdigit():
                continue
            if REF_PRECEDES.search(text[max(0, match.start() - 25): match.start()]):
                continue
            snippets.append(text[max(0, match.start() - 30): match.end() + 30].strip())
        if snippets:
            label = f"{row.get('law', '')[:40]} / {row.get('article')}"
            items.append({"law": row.get("law", ""), "article": row.get("article"), "snippets": snippets,
                          "orthography_outlier": label in outlier_rows})
    return items


def write_outputs(report, checklist, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    report = dict(report, quantity_articles=len(checklist))
    (out / "audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    with open(out / "quantity_checklist.csv", "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["law", "article", "orthography_outlier (check first)", "numbers_periods_amounts_found",
                         "matches_gazette (yes/no)", "reviewer_notes"])
        for item in checklist:
            writer.writerow([item["law"], item["article"], "yes" if item["orthography_outlier"] else "",
                             " | ".join(item["snippets"][:6]) + (" | ..." if len(item["snippets"]) > 6 else ""), "", ""])
    lines = ["# Article-rows audit (evidence only)", "",
             "A clean audit means the file is internally consistent. It does not prove the text matches the Official Gazette, is in force, or may be reused.", "",
             f"- Rows audited: {report['rows']}", f"- Articles stating periods, amounts or percentages: {len(checklist)} (see quantity_checklist.csv)", "", "## Numbering"]
    for group, info in report["numbering"].items():
        lines.append(f"- {group}: {info['rows']} rows, {info['first']}..{info['last']}, gaps {info['gaps'] or 'none'}, duplicates {info['duplicates'] or 'none'}, in order {info['in_order']}")
    lines += ["", "## Findings"]
    if not report["findings"]:
        lines.append("- none")
    for name, items in report["findings"].items():
        lines.append(f"- {name}: {len(items)}")
    lines += ["", f"- exact duplicate texts: {len(report['exact_duplicate_texts'])}",
              f"- numeric references beyond the last article: {len(report['cross_references']['beyond_highest_article_in_file'])}",
              f"- orthography outliers: {len(report['orthography']['minority_style_rows'])} (check these articles first against the official text)",
              f"- embedded flags (never trusted): {json.dumps(report['embedded_flags'], ensure_ascii=False)}", ""]
    (out / "audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True)
    ap.add_argument("--out-dir", default="audit_report")
    args = ap.parse_args(argv)
    rows, malformed = load_rows(args.input)
    if not rows:
        print("No usable rows found.", file=sys.stderr)
        return 2
    report = audit(rows)
    report["malformed_lines"] = malformed
    outlier_labels = {o["row"] for o in report["orthography"]["minority_style_rows"]}
    checklist = quantity_checklist(rows, outlier_labels)
    write_outputs(report, checklist, args.out_dir)
    print(json.dumps({"rows": report["rows"], "malformed_lines": malformed,
                      "numbering_gaps": {g: v["gaps"] for g, v in report["numbering"].items()},
                      "findings": {k: len(v) for k, v in report["findings"].items()},
                      "orthography_outliers": len(outlier_labels), "quantity_articles": len(checklist),
                      "report": str(Path(args.out_dir) / "audit.md")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
