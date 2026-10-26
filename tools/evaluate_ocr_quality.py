#!/usr/bin/env python3
"""Measure OCR transcription error against human-approved text, without scoring legal correctness.

Input JSONL rows require id, reference_text, and ocr_text; document_id and page are optional.
Reports raw and Arabic-normalized character/word error rates, including per-document metrics.
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

MAX_EDIT_CELLS = 4_000_000
DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
INVISIBLE = re.compile(r"[\u200b-\u200f\u202a-\u202e\ufeff]")


class OCREvaluationError(ValueError):
    pass


def normalize_arabic(text):
    text = unicodedata.normalize("NFKC", text).translate(DIGITS)
    text = DIACRITICS.sub("", text)
    text = text.replace("\u0640", "")
    text = re.sub(r"[أإآٱ]", "ا", text).replace("ى", "ي")
    text = INVISIBLE.sub("", text)
    return re.sub(r"\s+", " ", text).strip()


def _contains_token_sequence(text, phrase):
    """Match an exact normalized token/phrase sequence, not a substring inside another word."""
    haystack = normalize_arabic(text).split()
    needle = normalize_arabic(phrase).split()
    if not needle:
        return False
    return any(haystack[index:index + len(needle)] == needle
               for index in range(len(haystack) - len(needle) + 1))


def _sequence_edit_distance(reference_units, hypothesis_units):
    if len(reference_units) * len(hypothesis_units) > MAX_EDIT_CELLS:
        raise OCREvaluationError(
            "text pair is too large for exact edit-distance evaluation; split input into page-level rows"
        )
    if len(reference_units) < len(hypothesis_units):
        reference_units, hypothesis_units = hypothesis_units, reference_units
    previous = list(range(len(hypothesis_units) + 1))
    for i, ref_unit in enumerate(reference_units, 1):
        current = [i]
        for j, hyp_unit in enumerate(hypothesis_units, 1):
            current.append(min(
                current[j - 1] + 1,
                previous[j] + 1,
                previous[j - 1] + (ref_unit != hyp_unit),
            ))
        previous = current
    return previous[-1]


def edit_distance(reference, hypothesis):
    if not isinstance(reference, str) or not isinstance(hypothesis, str):
        raise OCREvaluationError("reference and OCR hypothesis must be strings")
    return _sequence_edit_distance(list(reference), list(hypothesis))

def _rates(reference, hypothesis, word_mode=False):
    ref = reference.split() if word_mode else list(reference)
    hyp = hypothesis.split() if word_mode else list(hypothesis)
    distance = _sequence_edit_distance(ref, hyp)
    denominator = max(1, len(ref))
    return {"edits": distance, "reference_units": len(ref), "error_rate": round(distance / denominator, 6)}


def _validate_rows(rows):
    seen = set()
    clean = []
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise OCREvaluationError(f"row {index}: expected a JSON object")
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id.strip():
            raise OCREvaluationError(f"row {index}: id must be a non-empty string")
        if row_id in seen:
            raise OCREvaluationError(f"row {index}: duplicate id {row_id}")
        seen.add(row_id)
        if not isinstance(row.get("reference_text"), str) or not isinstance(row.get("ocr_text"), str):
            raise OCREvaluationError(f"{row_id}: reference_text and ocr_text must be strings")
        critical_tokens = row.get("critical_tokens", [])
        if not isinstance(critical_tokens, list) or any(
            not isinstance(token, str) or not token.strip() for token in critical_tokens
        ):
            raise OCREvaluationError(f"{row_id}: critical_tokens must be a list of non-empty strings")
        critical_tokens = [token.strip() for token in critical_tokens]
        normalized_critical_tokens = [normalize_arabic(token) for token in critical_tokens]
        if any(not token for token in normalized_critical_tokens):
            raise OCREvaluationError(f"{row_id}: critical_tokens cannot normalize to empty text")
        if len(normalized_critical_tokens) != len(set(normalized_critical_tokens)):
            raise OCREvaluationError(f"{row_id}: critical_tokens contains duplicates after normalization")
        missing_from_reference = [
            token for token, normalized in zip(critical_tokens, normalized_critical_tokens)
            if not _contains_token_sequence(row["reference_text"], normalized)
        ]
        if missing_from_reference:
            raise OCREvaluationError(
                f"{row_id}: critical_tokens must appear in reference_text: {missing_from_reference}"
            )
        clean.append({
            "id": row_id,
            "document_id": str(row.get("document_id") or "unspecified"),
            "page": row.get("page"),
            "reference_text": row["reference_text"],
            "ocr_text": row["ocr_text"],
            "critical_tokens": critical_tokens,
        })
    if not clean:
        raise OCREvaluationError("no OCR comparison rows found")
    return clean


def evaluate(rows):
    rows = _validate_rows(rows)
    page_results = []
    per_document = defaultdict(list)
    for row in rows:
        reference, hypothesis = row["reference_text"], row["ocr_text"]
        normalized_reference = normalize_arabic(reference)
        normalized_hypothesis = normalize_arabic(hypothesis)
        result = {
            "id": row["id"],
            "document_id": row["document_id"],
            "page": row["page"],
            "raw_cer": _rates(reference, hypothesis),
            "raw_wer": _rates(reference, hypothesis, word_mode=True),
            "normalized_cer": _rates(normalized_reference, normalized_hypothesis),
            "normalized_wer": _rates(normalized_reference, normalized_hypothesis, word_mode=True),
        }
        missing_critical_tokens = [
            token for token in row["critical_tokens"]
            if not _contains_token_sequence(hypothesis, token)
        ]
        result.update({
            "critical_tokens_expected_count": len(row["critical_tokens"]),
            "critical_tokens_found_count": len(row["critical_tokens"]) - len(missing_critical_tokens),
            "critical_token_recall": (
                round((len(row["critical_tokens"]) - len(missing_critical_tokens)) / len(row["critical_tokens"]), 6)
                if row["critical_tokens"] else None
            ),
            "missing_critical_tokens": missing_critical_tokens,
        })
        page_results.append(result)
        per_document[row["document_id"]].append(result)

    def aggregate(items, key):
        edits = sum(item[key]["edits"] for item in items)
        units = sum(item[key]["reference_units"] for item in items)
        return {"edits": edits, "reference_units": units,
                "error_rate": round(edits / max(1, units), 6)}

    def critical_summary(items):
        expected = sum(item["critical_tokens_expected_count"] for item in items)
        found = sum(item["critical_tokens_found_count"] for item in items)
        pages_with_tokens = [item for item in items if item["critical_tokens_expected_count"] > 0]
        pages_with_missing = sum(bool(item["missing_critical_tokens"]) for item in pages_with_tokens)
        return {
            "pages_with_critical_tokens": len(pages_with_tokens),
            "critical_tokens_expected_count": expected,
            "critical_tokens_found_count": found,
            "critical_token_recall": round(found / expected, 6) if expected else None,
            "pages_with_missing_critical_tokens": pages_with_missing,
            "critical_token_page_failure_rate": (
                round(pages_with_missing / len(pages_with_tokens), 6) if pages_with_tokens else None
            ),
        }

    return {
        "schema_version": 1,
        "evaluation_scope": "ocr_transcription_quality_only",
        "legal_correctness_scored": False,
        "rows_scored": len(page_results),
        "overall": {
            **{
                metric: aggregate(page_results, metric)
                for metric in ("raw_cer", "raw_wer", "normalized_cer", "normalized_wer")
            },
            **critical_summary(page_results),
        },
        "by_document": {
            doc_id: {
                "pages_scored": len(items),
                **{metric: aggregate(items, metric)
                   for metric in ("raw_cer", "raw_wer", "normalized_cer", "normalized_wer")},
                **critical_summary(items),
            }
            for doc_id, items in sorted(per_document.items())
        },
        "pages": page_results,
        "limitations": [
            "Metrics measure text transcription only, not legal correctness or source authenticity.",
            "Normalized scores ignore selected Arabic orthographic distinctions; raw scores are retained.",
            "Reference text must be checked by a human against the original scan.",
        ],
    }


def read_jsonl(path):
    rows = []
    for line_no, raw in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            rows.append(json.loads(raw))
        except json.JSONDecodeError as exc:
            raise OCREvaluationError(f"{path}:{line_no}: invalid JSON: {exc.msg}") from exc
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="JSONL with human-checked reference_text and OCR ocr_text")
    parser.add_argument("--out", help="Write JSON report to this path; default is stdout")
    args = parser.parse_args(argv)
    try:
        report = evaluate(read_jsonl(args.input))
    except (OSError, OCREvaluationError) as exc:
        print(f"OCR evaluation refused: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
