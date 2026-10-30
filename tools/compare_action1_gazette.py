#!/usr/bin/env python3
"""Compare supplied Action 1 article candidates with a local Gazette PDF text layer.

The report is metadata-only: it contains article labels, page indices, hashes,
character counts, and match classifications, never the source or extracted text.
It does not OCR, alter source files, determine printed page numbers, or verify law.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import re
import sys
import unicodedata
from collections import OrderedDict
from pathlib import Path
from typing import Any

_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
_ARABIC = str.maketrans({
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا",
    "ى": "ي", "ـ": "",
})


def require_regular_file(value: str | Path, label: str) -> Path:
    path = Path(value).expanduser()
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} must be an existing regular non-symlink file")
    return path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_arabic_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).translate(_DIGITS).translate(_ARABIC)
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = "".join(ch for ch in value if ch not in "\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069")
    return re.sub(r"\s+", " ", value).strip()


def load_article_candidates(path: Path) -> tuple[list[dict[str, Any]], str]:
    digest = sha256_file(path)
    grouped: OrderedDict[tuple[str, str], list[str]] = OrderedDict()
    for line_number, line in enumerate(path.open("r", encoding="utf-8-sig"), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"JSONL line {line_number} is invalid JSON: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"JSONL line {line_number} must be an object")
        law, article, text = row.get("law"), row.get("article"), row.get("text")
        if not isinstance(law, str) or not law.strip():
            raise ValueError(f"JSONL line {line_number} has no non-empty law label")
        if not isinstance(article, (str, int)) or isinstance(article, bool) or not str(article).strip():
            raise ValueError(f"JSONL line {line_number} has no valid article label")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"JSONL line {line_number} has no non-empty text chunk")
        key = (law.strip(), str(article).strip())
        grouped.setdefault(key, []).append(text.strip())

    candidates = []
    for (law, article), chunks in grouped.items():
        combined = " ".join(chunks)
        normalized = normalize_arabic_text(combined)
        candidates.append({
            "law": law,
            "article": article,
            "text": normalized,
            "text_sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
            "normalized_character_count": len(normalized),
            "source_chunk_count": len(chunks),
        })
    return candidates, digest


def read_pdf_text(path: Path) -> tuple[list[str], str]:
    with path.open("rb") as handle:
        if b"%PDF-" not in handle.read(1024):
            raise ValueError("Gazette input has no PDF signature in the first 1024 bytes")
    try:
        import pymupdf
    except ImportError as exc:
        raise SystemExit("PyMuPDF is required; install optional dependencies with: python -m pip install -r requirements-ocr.txt") from exc
    try:
        with pymupdf.open(path) as document:
            pages = [page.get_text("text") or "" for page in document]
    except Exception as exc:
        raise ValueError(f"Gazette PDF could not be read ({type(exc).__name__})") from exc
    return [normalize_arabic_text(page) for page in pages], sha256_file(path)


def _page_at(offset: int, starts: list[int]) -> int:
    return max(0, bisect.bisect_right(starts, offset) - 1)


def compare_articles(candidates: list[dict[str, Any]], pages: list[str]) -> dict[str, Any]:
    pages = [normalize_arabic_text(page) for page in pages]
    starts: list[int] = []
    cursor = 0
    for page in pages:
        starts.append(cursor)
        cursor += len(page) + 1
    joined = " ".join(pages)
    text_layer_pages = sum(bool(page) for page in pages)
    matches = []
    counts = {
        "exact_text_match": 0,
        "exact_text_match_multiple_occurrences": 0,
        "both_anchors_found_nonexact": 0,
        "start_anchor_only": 0,
        "end_anchor_only": 0,
        "not_found": 0,
        "no_pdf_text_layer": 0,
    }
    for candidate in candidates:
        text = candidate["text"]
        result: dict[str, Any] = {
            "law": candidate["law"],
            "article": candidate["article"],
            "candidate_text_sha256": candidate["text_sha256"],
            "normalized_character_count": candidate["normalized_character_count"],
            "source_chunk_count": candidate["source_chunk_count"],
            "status": "not_found",
            "pdf_page_indices_zero_based": [],
            "match_method": None,
        }
        if not text_layer_pages:
            result["status"] = "no_pdf_text_layer"
        else:
            positions = []
            start = 0
            while True:
                found = joined.find(text, start)
                if found < 0:
                    break
                positions.append(found)
                start = found + max(1, len(text))
                if len(positions) >= 10:
                    break
            if positions:
                result["status"] = (
                    "exact_text_match" if len(positions) == 1
                    else "exact_text_match_multiple_occurrences"
                )
                result["match_method"] = "normalized_full_text"
                pages_found = set()
                for position in positions:
                    first = _page_at(position, starts)
                    last = _page_at(position + len(text) - 1, starts)
                    pages_found.update(range(first, last + 1))
                result["pdf_page_indices_zero_based"] = sorted(pages_found)
            else:
                anchor_size = min(120, max(40, len(text) // 5))
                prefix, suffix = text[:anchor_size], text[-anchor_size:]
                first = joined.find(prefix)
                last = joined.rfind(suffix)
                if first >= 0 and last >= first:
                    result["status"] = "both_anchors_found_nonexact"
                    result["match_method"] = "normalized_prefix_and_suffix_anchors"
                    result["pdf_page_indices_zero_based"] = sorted({
                        _page_at(first, starts),
                        _page_at(last + len(suffix) - 1, starts),
                    })
                elif first >= 0:
                    result["status"] = "start_anchor_only"
                    result["match_method"] = "normalized_prefix_anchor"
                    result["pdf_page_indices_zero_based"] = [_page_at(first, starts)]
                elif last >= 0:
                    result["status"] = "end_anchor_only"
                    result["match_method"] = "normalized_suffix_anchor"
                    result["pdf_page_indices_zero_based"] = [_page_at(last, starts)]
        counts[result["status"]] += 1
        matches.append(result)
    return {
        "pdf_page_count": len(pages),
        "pdf_pages_with_text_layer": text_layer_pages,
        "candidate_article_count": len(candidates),
        "match_counts": counts,
        "matches": matches,
    }


def build_report(gazette_pdf: str | Path, law_rows_jsonl: str | Path) -> dict[str, Any]:
    pdf_path = require_regular_file(gazette_pdf, "Gazette PDF")
    rows_path = require_regular_file(law_rows_jsonl, "law_rows_ar.jsonl")
    if pdf_path.resolve() == rows_path.resolve():
        raise ValueError("PDF and JSONL inputs must be different files")
    candidates, rows_hash = load_article_candidates(rows_path)
    pages, pdf_hash = read_pdf_text(pdf_path)
    comparison = compare_articles(candidates, pages)
    exact = comparison["match_counts"]["exact_text_match"]
    comparison.update({
        "source_pdf_sha256": pdf_hash,
        "source_jsonl_sha256": rows_hash,
        "comparison_scope": "text_layer_only_normalized_candidate_comparison",
        "safety_boundary": {
            "source_text_in_report": False,
            "source_files_modified": False,
            "ocr_performed": False,
            "printed_page_numbers_inferred": False,
            "legal_authenticity_verified": False,
            "extraction_accuracy_verified": False,
            "currentness_or_amendment_status_verified": False,
            "reuse_permission_confirmed": False,
            "lawyer_review_completed": False,
            "retrieval_eligible": False,
        },
        "interpretation": (
            f"{exact} article candidate(s) have one exact normalized text-layer match. "
            "This is a matching aid only; all pages, tables, notes, source identity, "
            "and legal status still require human review."
        ),
    })
    return {
        "schema_version": 1,
        "purpose": "Action 1 local Gazette text-layer comparison",
        "pdf": {"filename": pdf_path.name, "size_bytes": pdf_path.stat().st_size, "sha256": pdf_hash},
        "jsonl": {"filename": rows_path.name, "size_bytes": rows_path.stat().st_size, "sha256": rows_hash},
        "comparison": comparison,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gazette-pdf", required=True, help="Original Gazette PDF, kept local")
    parser.add_argument("--law-rows-jsonl", required=True, help="Candidate article JSONL, kept local")
    parser.add_argument("--out", required=True, type=Path, help="Metadata-only JSON report path")
    args = parser.parse_args(argv)
    try:
        report = build_report(args.gazette_pdf, args.law_rows_jsonl)
        destination = args.out.expanduser()
        if destination.is_symlink():
            raise ValueError("Report output must not be a symbolic link")
        if destination.resolve() in {Path(args.gazette_pdf).expanduser().resolve(), Path(args.law_rows_jsonl).expanduser().resolve()}:
            raise ValueError("Report output must not overwrite either source input")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Action 1 comparison failed: {exc}", file=sys.stderr)
        return 2
    print(f"Metadata-only comparison report written: {destination}")
    print(json.dumps(report["comparison"]["match_counts"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
