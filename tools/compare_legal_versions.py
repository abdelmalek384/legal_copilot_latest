#!/usr/bin/env python3
"""Read-only, provision-label-based comparison of two registered legal versions.

This reports differences between extracted chunks only. It does not establish legal
amendment effect, completeness, authenticity, or the operative law.
"""
import argparse
import difflib
import json
import os
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote


def _normalized_text(value):
    value = unicodedata.normalize("NFC", value or "")
    return re.sub(r"\s+", " ", value).strip()


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def compare_version_chunks(left_chunks, right_chunks):
    """Compare extracted passages by exact article label without inferring renumbering."""
    def group(rows):
        grouped = {}
        unmapped = []
        malformed_count = 0
        uncertain_articles = set()
        for row in rows:
            if not isinstance(row, dict):
                malformed_count += 1
                unmapped.append({
                    "chunk_id": None,
                    "page": None,
                    "text": None,
                    "unmapped_reason": "invalid_chunk_record",
                })
                continue
            article = row.get("article")
            raw_text = row.get("text")
            text = raw_text if isinstance(raw_text, str) else None
            page = row.get("page")
            chunk = {
                "chunk_id": row.get("id"),
                "page": page if _nonempty(page) else None,
                "text": text,
            }
            if text is None or not text.strip():
                malformed_count += 1
                chunk["unmapped_reason"] = "missing_or_invalid_text"
                unmapped.append(chunk)
                if _nonempty(article):
                    uncertain_articles.add(article.strip())
                continue
            if not _nonempty(article):
                chunk["unmapped_reason"] = "missing_article_label"
                unmapped.append(chunk)
                continue
            grouped.setdefault(article.strip(), []).append(chunk)
        return grouped, unmapped, malformed_count, uncertain_articles

    left_by_article, left_unmapped, left_malformed, left_uncertain = group(left_chunks)
    right_by_article, right_unmapped, right_malformed, right_uncertain = group(right_chunks)
    provisions = []
    counts = {
        "added_in_right": 0,
        "removed_from_right": 0,
        "changed": 0,
        "unchanged": 0,
        "uncomparable_incomplete_text": 0,
    }
    for article in sorted(set(left_by_article) | set(right_by_article) | left_uncertain | right_uncertain):
        left_parts = left_by_article.get(article, [])
        right_parts = right_by_article.get(article, [])
        left_text = "\n\n".join(part["text"] for part in left_parts)
        right_text = "\n\n".join(part["text"] for part in right_parts)
        if article in left_uncertain or article in right_uncertain:
            change = "uncomparable_incomplete_text"
        elif not left_parts:
            change = "added_in_right"
        elif not right_parts:
            change = "removed_from_right"
        elif _normalized_text(left_text) == _normalized_text(right_text):
            change = "unchanged"
        else:
            change = "changed"
        counts[change] += 1
        item = {
            "article": article,
            "change": change,
            "left_pages": list(dict.fromkeys(part["page"] for part in left_parts if part["page"])),
            "right_pages": list(dict.fromkeys(part["page"] for part in right_parts if part["page"])),
            "left_text": left_text if left_parts else None,
            "right_text": right_text if right_parts else None,
        }
        if change == "changed":
            item["unified_diff"] = "\n".join(difflib.unified_diff(
                left_text.splitlines(),
                right_text.splitlines(),
                fromfile="left version",
                tofile="right version",
                lineterm="",
            ))
        provisions.append(item)

    if left_malformed or right_malformed:
        extra_warning = (
            "Malformed or empty extracted passages were found; inspect the unmapped_passages lists "
            "before relying on any article-level result."
        )
    else:
        extra_warning = None

    warnings = [
        "This is a comparison of extracted chunks, not a legal conclusion about amendment, repeal, or legal effect.",
        "Matching uses exact article labels; renumbered or restructured provisions may appear as removed/added and are not automatically mapped.",
        "Missing provisions may reflect incomplete extraction rather than a change in the legal instrument.",
        "Passages with missing/invalid text are excluded from text comparison; any article label affected on either side is marked uncomparable rather than added, removed, changed, or unchanged.",
        "Verify both texts against their authoritative source pages and have qualified Egyptian counsel review the legal effect.",
    ]
    if extra_warning:
        warnings.append(extra_warning)

    return {
        "comparison_type": "extracted_chunk_text_diff",
        "summary": {
            **counts,
            "unmapped_left_passages": len(left_unmapped),
            "unmapped_right_passages": len(right_unmapped),
            "malformed_left_passages": left_malformed,
            "malformed_right_passages": right_malformed,
        },
        "provisions": provisions,
        "unmapped_passages": {"left": left_unmapped, "right": right_unmapped},
        "warnings": warnings,
    }


def _connect_read_only(db_path):
    path = Path(db_path).expanduser().resolve()
    if not path.is_file():
        raise ValueError(f"database file does not exist: {path}")
    uri = "file:" + quote(str(path), safe="/") + "?mode=ro"
    try:
        connection = sqlite3.connect(uri, uri=True)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only=ON")
        return connection
    except sqlite3.Error as exc:
        raise ValueError(f"could not open database read-only: {exc}") from exc


def compare_registered_versions(db_path, left_version_id, right_version_id):
    """Read registry metadata and chunks using a read-only SQLite connection."""
    if left_version_id == right_version_id:
        raise ValueError("choose two different version IDs")
    connection = _connect_read_only(db_path)
    try:
        tables = {row["name"] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        required = {"legal_document_versions", "legal_documents", "chunks"}
        missing = sorted(required - tables)
        if missing:
            raise ValueError("database is missing required tables: " + ", ".join(missing))
        version_sql = (
            "SELECT v.version_id,v.document_id,v.version_label,v.source_url,"
            "v.publication_date,v.effective_date,v.repeal_date,v.legal_status,v.review_status,"
            "v.authenticity_verified,v.status_verified,v.amendment_history_verified,"
            "v.gazette_issue,v.gazette_pages,d.official_title,d.law_number,d.law_year "
            "FROM legal_document_versions v JOIN legal_documents d ON d.document_id=v.document_id "
            "WHERE v.version_id=?"
        )
        left_row = connection.execute(version_sql, (left_version_id,)).fetchone()
        right_row = connection.execute(version_sql, (right_version_id,)).fetchone()
        if left_row is None or right_row is None:
            missing_ids = []
            if left_row is None:
                missing_ids.append(str(left_version_id))
            if right_row is None:
                missing_ids.append(str(right_version_id))
            raise ValueError("version ID not found: " + ", ".join(missing_ids))
        left = dict(left_row)
        right = dict(right_row)
        if left["document_id"] != right["document_id"]:
            raise ValueError("versions belong to different legal documents; cross-document comparison is not supported")
        chunk_sql = "SELECT id,article,page,text FROM chunks WHERE document_version_id=? ORDER BY id"
        left_chunks = [dict(row) for row in connection.execute(chunk_sql, (left_version_id,)).fetchall()]
        right_chunks = [dict(row) for row in connection.execute(chunk_sql, (right_version_id,)).fetchall()]
        result = compare_version_chunks(left_chunks, right_chunks)
        result["document"] = {
            "document_id": left["document_id"],
            "official_title": left["official_title"],
            "law_number": left["law_number"],
            "law_year": left["law_year"],
        }
        result["left_version"] = left
        result["right_version"] = right
        if not left_chunks or not right_chunks:
            result["warnings"].append("One or both versions have no linked chunks; this comparison cannot establish text completeness.")
        for side, metadata in (("left", left), ("right", right)):
            if (metadata["review_status"] != "verified"
                    or metadata["authenticity_verified"] != 1
                    or metadata["status_verified"] != 1
                    or metadata["amendment_history_verified"] != 1):
                result["warnings"].append(
                    f"{side} version is not fully marked as reviewed/verified in registry metadata."
                )
        return result
    except sqlite3.Error as exc:
        raise ValueError(f"could not read version comparison data: {exc}") from exc
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=Path(os.environ.get("COPILOT_DB", "copilot.db")))
    parser.add_argument("--left-version-id", type=int, required=True, help="baseline version ID")
    parser.add_argument("--right-version-id", type=int, required=True, help="version to compare against baseline")
    args = parser.parse_args()
    try:
        result = compare_registered_versions(args.db, args.left_version_id, args.right_version_id)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
