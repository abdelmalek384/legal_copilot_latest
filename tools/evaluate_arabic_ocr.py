#!/usr/bin/env python3
"""Legacy OCR evaluator retained for compatibility; prefer tools/evaluate_ocr_quality.py.

This older command does not implement the canonical evaluator schema or critical-token metrics.

Input is JSONL with one page per record:
  {"document_id":"scan-01","page":"1","reference_text":"...","ocr_text":"..."}

This tool measures transcription similarity only. It does not authenticate a document,
judge legal correctness, or decide whether OCR output is safe for legal use.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path


_TRANSLATION = str.maketrans({
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا",
    "ى": "ي", "ـ": "",
    **{chr(0x0660 + i): str(i) for i in range(10)},
    **{chr(0x06F0 + i): str(i) for i in range(10)},
})


def normalize_arabic(text):
    """Normalize common Arabic OCR variants while preserving punctuation and numbers."""
    text = unicodedata.normalize("NFKC", str(text or ""))
    text = re.sub(r"[\u064b-\u065f\u0670]", "", text)
    text = text.translate(_TRANSLATION)
    return " ".join(text.split())


def edit_distance(a, b):
    """Levenshtein distance using O(min(len(a), len(b))) memory."""
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(
                current[-1] + 1,
                previous[j] + 1,
                previous[j - 1] + (ca != cb),
            ))
        previous = current
    return previous[-1]


def score_page(record, line_number=1):
    """Validate and score one page record; scores are ratios, not percentages."""
    if not isinstance(record, dict):
        raise ValueError(f"line {line_number}: expected a JSON object")
    for field in ("document_id", "page", "reference_text", "ocr_text"):
        if field not in record:
            raise ValueError(f"line {line_number}: missing required field {field}")
    document_id = str(record["document_id"]).strip()
    page = str(record["page"]).strip()
    if not document_id or not page:
        raise ValueError(f"line {line_number}: document_id and page must be non-empty")
    reference = normalize_arabic(record["reference_text"])
    recognized = normalize_arabic(record["ocr_text"])
    if not reference:
        raise ValueError(f"line {line_number}: reference_text must not be empty")
    ref_words = reference.split()
    ocr_words = recognized.split()
    char_errors = edit_distance(reference, recognized)
    word_errors = edit_distance(ref_words, ocr_words)
    return {
        "document_id": document_id,
        "page": page,
        "reference_characters": len(reference),
        "reference_words": len(ref_words),
        "character_errors": char_errors,
        "word_errors": word_errors,
        "cer": char_errors / len(reference),
        "wer": word_errors / len(ref_words),
    }


def evaluate_records(records):
    pages = [score_page(record, i) for i, record in enumerate(records, 1)]
    if not pages:
        raise ValueError("input contains no page records")
    total_chars = sum(p["reference_characters"] for p in pages)
    total_words = sum(p["reference_words"] for p in pages)
    total_char_errors = sum(p["character_errors"] for p in pages)
    total_word_errors = sum(p["word_errors"] for p in pages)
    return {
        "metric_note": "CER/WER are normalized transcription-error ratios, not legal-accuracy scores.",
        "normalization": "NFKC; remove Arabic diacritics and tatweel; normalize alef variants, alef maksura, Arabic/Persian digits, and whitespace; preserve punctuation.",
        "page_count": len(pages),
        "aggregate": {
            "reference_characters": total_chars,
            "reference_words": total_words,
            "character_errors": total_char_errors,
            "word_errors": total_word_errors,
            "cer": total_char_errors / total_chars,
            "wer": total_word_errors / total_words,
        },
        "pages": pages,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", help="JSONL file with manually corrected reference text and OCR output")
    parser.add_argument("--output", help="write JSON report to this path instead of stdout")
    args = parser.parse_args(argv)
    records = []
    try:
        with Path(args.jsonl).open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"line {line_number}: invalid JSON: {exc.msg}") from exc
        report = evaluate_records(records)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
