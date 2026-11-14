#!/usr/bin/env python3
"""Import lawyer-supplied UTF-8 Gazette text into quarantined article-level candidate rows.

This is an offline transcription importer. It does not fetch sources, verify authenticity,
grant reuse permission, determine current force, or approve legal content.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import stat
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

try:
    from tools.import_laws import HEAD as NUMERIC_HEAD, pieces, split
except ModuleNotFoundError:  # direct execution from tools/
    from import_laws import HEAD as NUMERIC_HEAD, pieces, split

MAX_TEXT_BYTES = 20 * 1024 * 1024
MAX_METADATA_BYTES = 1024 * 1024
SENSITIVE_QUERY_KEYS = {
    "token", "access_token", "auth", "authorization", "password", "secret",
    "signature", "sig", "api_key", "apikey", "session", "sessionid",
    "credential", "api-key", "auth_token", "session_token",
    # Common cloud object-storage signed-URL parameters. The generic
    # signature/sig entries above catch the actual signature; these catch
    # companion identity/expiry fields that should not be retained either.
    "awsaccesskeyid", "googleaccessid", "key-pair-id",
    "x-amz-signature", "x-amz-credential", "x-amz-security-token",
    "x-amz-algorithm", "x-amz-date", "x-amz-expires", "x-amz-signedheaders",
    "x-goog-signature", "x-goog-credential", "x-goog-algorithm",
    "x-goog-date", "x-goog-expires", "x-goog-signedheaders",
}


# Law 14/2025's issuance provisions use Arabic ordinal headings, while the
# attached Labour Law restarts at numeric Article 1. Keep those sequences apart.
PROMULGATION_ORDINALS = {
    "الأولى": 1, "الاولى": 1,
    "الثانية": 2, "الثانيه": 2,
    "الثالثة": 3, "الثالثه": 3,
    "الرابعة": 4, "الرابعه": 4,
    "الخامسة": 5, "الخامسه": 5,
    "السادسة": 6, "السادسه": 6,
    "السابعة": 7,
    "الثامنة": 8, "الثامنه": 8,
    "التاسعة": 9, "التاسعه": 9,
    "العاشرة": 10, "العاشره": 10,
    "الحادية عشرة": 11, "الحاديه عشرة": 11, "الحاديه عشره": 11,
    "الحادية عشر": 11, "الحاديه عشر": 11,
    "الثانية عشرة": 12, "الثانيه عشرة": 12, "الثانيه عشره": 12,
    "الثانية عشر": 12, "الثانيه عشر": 12,
    "الثالثة عشرة": 13, "الثالثه عشرة": 13, "الثالثه عشره": 13,
    "الثالثة عشر": 13, "الثالثه عشر": 13,
}
_ORDINAL_ALTERNATION = "|".join(
    re.escape(value) for value in sorted(PROMULGATION_ORDINALS, key=len, reverse=True)
)
PROMULGATION_HEAD = re.compile(
    rf"(?m)^[ \t]*\(?[ \t]*(?:المادة|مادة)[ \t]+\(?[ \t]*"
    rf"(?P<ordinal>{_ORDINAL_ALTERNATION})[ \t]*\)?[ \t]*\)?"
    rf"[ \t]*(?:[:-][ \t]*|$)"
)


def split_gazette_text(text: str) -> list[tuple[str, int, str, str]]:
    """Split ordinal issuance provisions and numeric law articles separately."""
    ordinal_matches = list(PROMULGATION_HEAD.finditer(text))
    if not ordinal_matches:
        return [
            (article, block, body, "preamble" if article == "preamble" else "article")
            for article, block, body in split(text)
        ]

    matches = []
    for match in ordinal_matches:
        ordinal = " ".join(match.group("ordinal").split())
        number = PROMULGATION_ORDINALS[ordinal]
        matches.append((
            match.start(), match.end(), f"issuance_{number}", "promulgation", number
        ))
    for match in NUMERIC_HEAD.finditer(text):
        raw_number = match.group(1)
        number = int(raw_number.translate(str.maketrans(
            "٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789"
        )))
        matches.append((
            match.start(), match.end(), raw_number, "attached_law", number
        ))
    matches.sort(key=lambda item: item[0])

    parts = []
    preamble = text[:matches[0][0]]
    if preamble.strip():
        parts.append(("preamble", 0, preamble, "preamble"))

    block = 0
    current_kind = None
    previous_number = None
    for index, (start, end, article, kind, number) in enumerate(matches):
        if current_kind is None:
            block = 1
            current_kind = kind
            previous_number = None
        elif kind != current_kind:
            block += 1
            current_kind = kind
            previous_number = None
        elif previous_number is not None and number < previous_number:
            block += 1
        previous_number = number
        next_start = matches[index + 1][0] if index + 1 < len(matches) else len(text)
        parts.append((article, block, text[end:next_start], kind))
    return parts


def _read_regular(path: Path, label: str, limit: int) -> bytes:
    try:
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode):
            raise ValueError(f"{label} must be a regular file, not a symlink")
        if before.st_size > limit:
            raise ValueError(f"{label} exceeds {limit} bytes")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as handle:
            opened = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened.st_mode) or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
                raise ValueError(f"{label} changed identity while opening")
            data = handle.read(limit + 1)
            after = os.fstat(handle.fileno())
            if len(data) > limit or len(data) != after.st_size:
                raise ValueError(f"{label} changed or exceeded its size limit while reading")
            if (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise ValueError(f"{label} changed while being read")
            return data
    except OSError as exc:
        raise ValueError(f"cannot safely read {label}: {type(exc).__name__}") from exc


def _reject_duplicate_json_keys(pairs):
    """Build JSON objects without silently accepting duplicate keys at any depth."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key in metadata: {key}")
        result[key] = value
    return result


def _validate_metadata(meta: object, text_bytes: bytes) -> dict:
    if not isinstance(meta, dict):
        raise ValueError("metadata sidecar must be a JSON object")
    for field in ("document_id", "official_title", "language", "gazette_issue",
                  "publication_date", "retrieved_at", "captured_by", "capture_method",
                  "content_sha256"):
        if not isinstance(meta.get(field), str) or not meta[field].strip():
            raise ValueError(f"{field} is required and must be a non-empty string")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", meta["document_id"]):
        raise ValueError("document_id contains unsupported characters")
    if not isinstance(meta["language"], str) or meta["language"].strip().lower() != "ar":
        raise ValueError("language must be ar for the Arabic-first Gazette text importer")
    # These values are copied into provenance strings and reports. Reject
    # control characters so a sidecar cannot forge extra provenance lines.
    for field in (
        "official_title", "gazette_issue", "retrieved_at", "captured_by",
        "source_reference", "permission_evidence_reference",
    ):
        value = meta.get(field)
        if isinstance(value, str) and any(ord(char) < 32 or ord(char) == 127 for char in value):
            raise ValueError(f"{field} must not contain control characters")
    if not isinstance(meta.get("supplier_role"), str) or meta["supplier_role"] not in {"egyptian_lawyer", "qualified_egyptian_counsel"}:
        raise ValueError("supplier_role must identify an Egyptian lawyer or qualified counsel")
    if not isinstance(meta["capture_method"], str) or meta["capture_method"] not in {"lawyer_supplied_text", "manual_transcription"}:
        raise ValueError("capture_method must be lawyer_supplied_text or manual_transcription")
    try:
        publication = dt.date.fromisoformat(meta["publication_date"])
        if publication.isoformat() != meta["publication_date"]:
            raise ValueError
    except ValueError as exc:
        raise ValueError("publication_date must be YYYY-MM-DD") from exc
    try:
        dt.datetime.fromisoformat(meta["retrieved_at"].replace("Z", "+00:00"))
    except ValueError as exc:
        try:
            dt.date.fromisoformat(meta["retrieved_at"])
        except ValueError:
            raise ValueError("retrieved_at must be an ISO date or datetime") from exc
    expected = meta["content_sha256"].lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("content_sha256 must be a 64-character SHA-256")
    actual = hashlib.sha256(text_bytes).hexdigest()
    if actual != expected:
        raise ValueError("SHA-256 mismatch for supplied Gazette text")
    source_reference = meta.get("source_reference")
    if "source_reference" in meta and not (
            isinstance(source_reference, str) and source_reference.strip()):
        raise ValueError("source_reference must be a non-empty string when supplied")
    source_url = meta.get("source_url")
    if "source_url" in meta and source_url is not None:
        if (not isinstance(source_url, str) or not source_url
                or "\\" in source_url
                or any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in source_url)):
            raise ValueError("source_url must be a valid HTTPS URL without whitespace or control characters")
        try:
            parsed = urlsplit(source_url)
            port = parsed.port
        except (TypeError, ValueError) as exc:
            raise ValueError("source_url must be a valid HTTPS URL") from exc
        if (parsed.scheme.lower() != "https" or not parsed.hostname
                or "@" in parsed.netloc
                or parsed.username is not None or parsed.password is not None
                or "#" in source_url or parsed.netloc.endswith(":")
                or (port is not None and not 1 <= port <= 65535)):
            raise ValueError("source_url must be HTTPS without credentials or fragments and with a valid authority")
        query_keys = {key.casefold() for key, _ in parse_qsl(parsed.query, keep_blank_values=True)}
        if query_keys & SENSITIVE_QUERY_KEYS:
            raise ValueError("source_url must not contain signed or credential query parameters")
    elif not (isinstance(meta.get("source_reference"), str) and meta["source_reference"].strip()):
        raise ValueError("provide source_url or a non-empty source_reference")
    for field in ("expected_promulgation_provisions", "expected_attached_law_articles"):
        if field in meta:
            value = meta[field]
            if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 10000:
                raise ValueError(f"{field} must be an integer between 0 and 10000")
    permission = meta.get("collection_permission", "unknown")
    if not isinstance(permission, str) or permission not in {"unknown", "allowed", "not_allowed"}:
        raise ValueError("collection_permission must be unknown, allowed, or not_allowed")
    if permission == "not_allowed":
        raise ValueError("collection permission is marked not_allowed; refusing to create candidate rows")
    permission_evidence = meta.get("permission_evidence_reference")
    if permission == "allowed" and (
            not isinstance(permission_evidence, str) or not permission_evidence.strip()):
        raise ValueError("permission_evidence_reference is required when collection_permission is allowed")
    if permission_evidence is not None and (
            not isinstance(permission_evidence, str) or not permission_evidence.strip()):
        raise ValueError("permission_evidence_reference must be a non-empty string when supplied")
    return {**meta, "publication_date": publication.isoformat(), "actual_sha256": actual}


def _write_new_output_files(output_dir: Path, files: dict[str, bytes]) -> None:
    """Create output files exclusively; never follow or overwrite an existing file."""
    directory_fd = None
    created = []
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    binary = getattr(os, "O_BINARY", 0)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | nofollow | binary
    try:
        if os.open in getattr(os, "supports_dir_fd", set()) and hasattr(os, "O_DIRECTORY"):
            directory_fd = os.open(
                output_dir,
                os.O_RDONLY | os.O_DIRECTORY | nofollow,
            )
        for name, payload in files.items():
            if directory_fd is not None:
                fd = os.open(name, flags, 0o600, dir_fd=directory_fd)
            else:
                fd = os.open(output_dir / name, flags, 0o600)
            created.append(name)
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
    except FileExistsError as exc:
        for name in reversed(created):
            try:
                if directory_fd is not None:
                    os.unlink(name, dir_fd=directory_fd)
                else:
                    os.unlink(output_dir / name)
            except OSError:
                pass
        raise ValueError("output files already exist; use a new empty output directory") from exc
    except Exception:
        for name in reversed(created):
            try:
                if directory_fd is not None:
                    os.unlink(name, dir_fd=directory_fd)
                else:
                    os.unlink(output_dir / name)
            except OSError:
                pass
        raise
    finally:
        if directory_fd is not None:
            os.close(directory_fd)


def import_text(text_path: Path, metadata_path: Path, output_dir: Path) -> dict:
    text_path, metadata_path, output_dir = Path(text_path), Path(metadata_path), Path(output_dir)
    if text_path.resolve() == metadata_path.resolve():
        raise ValueError("text and metadata paths must be different")
    if output_dir.is_symlink():
        raise ValueError("output directory must not be a symlink")
    source_parent = text_path.resolve().parent
    output_resolved = output_dir.resolve()
    if output_resolved == source_parent or source_parent in output_resolved.parents:
        raise ValueError("output directory must be outside the source directory")
    # Use the resolved absolute path so a symlinked parent is not re-resolved at write time.
    output_dir = output_resolved
    if output_dir.exists() and not output_dir.is_dir():
        raise ValueError("output path must be a directory")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("output directory must be empty; use a new empty output directory")
    text_bytes = _read_regular(text_path, "Gazette text", MAX_TEXT_BYTES)
    meta_bytes = _read_regular(metadata_path, "metadata sidecar", MAX_METADATA_BYTES)
    try:
        text = text_bytes.decode("utf-8-sig")
        meta = json.loads(
            meta_bytes.decode("utf-8-sig"), object_pairs_hook=_reject_duplicate_json_keys
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("text must be UTF-8 and metadata must be valid UTF-8 JSON") from exc
    if "\x00" in text:
        raise ValueError("Gazette text contains NUL characters")
    metadata = _validate_metadata(meta, text_bytes)
    article_parts = split_gazette_text(text)
    preamble_parts = [part for part in article_parts if part[0] == "preamble"]
    articles = [part for part in article_parts if part[0] != "preamble"]
    if not articles:
        raise ValueError("no recognized Arabic/English article or promulgation headings were found")
    has_promulgation = any(part[3] == "promulgation" for part in articles)
    promulgation_count = sum(part[3] == "promulgation" for part in articles)
    attached_law_count = sum(part[3] in {"attached_law", "article"} for part in articles)
    preamble_characters = sum(len(part[2]) for part in preamble_parts)
    rows = []
    block_articles = {}
    block_provision_types = {}
    empty_articles = []
    title = metadata["official_title"].strip()
    source = (
        f"document_id {metadata['document_id']} | "
        f"source_url {metadata.get('source_url') or 'not_supplied'} | "
        f"source_reference {metadata.get('source_reference') or 'not_supplied'} | "
        f"{metadata['gazette_issue']} | published {metadata['publication_date']} | "
        f"retrieved {metadata['retrieved_at']} | sha256 {metadata['actual_sha256']} | "
        f"supplied by {metadata['captured_by']} ({metadata['supplier_role']}) | "
        f"capture_method {metadata['capture_method']} | "
        f"collection_permission {metadata.get('collection_permission', 'unknown')} | "
        f"permission_evidence_reference {metadata.get('permission_evidence_reference') or 'not_supplied'}"
    )
    for article, block, body, provision_type in article_parts:
        if provision_type == "preamble":
            continue
        if provision_type == "promulgation":
            label = title + " [promulgation]"
        elif has_promulgation and block == 2:
            label = title + " [attached law]"
        elif has_promulgation and block > 2:
            label = title + f" [attached law block {block - 1}]"
        else:
            label = title + ("" if block <= 1 else f" [block {block}]")
        chunks = list(pieces(body))
        if not chunks:
            empty_articles.append(article)
        for chunk in chunks:
            rows.append({
                "law": label,
                "article": article,
                "provision_type": provision_type,
                "text": chunk,
                "as_of": None,
                "in_force": 0,
                "verified": 0,
                "source": source,
                "document_id": metadata["document_id"],
                "gazette_issue": metadata["gazette_issue"],
                "publication_date": metadata["publication_date"],
                "content_sha256": metadata["actual_sha256"],
                "retrieved_at": metadata["retrieved_at"],
                "captured_by": metadata["captured_by"],
                "supplier_role": metadata["supplier_role"],
                "capture_method": metadata["capture_method"],
                "source_url": metadata.get("source_url"),
                "source_reference": metadata.get("source_reference"),
                "collection_permission": metadata.get("collection_permission", "unknown"),
                "permission_evidence_reference": metadata.get("permission_evidence_reference"),
            })
        block_articles.setdefault(block, []).append(article)
        block_provision_types.setdefault(block, provision_type)
    if not rows:
        raise ValueError("recognized headings contained no importable text")
    output_dir.mkdir(parents=True, exist_ok=True)
    if output_dir.is_symlink() or not output_dir.is_dir():
        raise ValueError("output directory must be a real directory, not a symlink")
    jsonl = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n"
    report = [
        "# Gazette text import report", "",
        "**Status:** candidate transcription only; not verified, authoritative, current, or retrieval-eligible.", "",
        f"- Document: {title}",
        f"- Document ID: {metadata['document_id']}",
        f"- Capture method: {metadata['capture_method']}",
        f"- Gazette issue: {metadata['gazette_issue']}",
        f"- Publication date: {metadata['publication_date']}",
        f"- Retrieved at: {metadata['retrieved_at']}",
        f"- Source URL: {metadata.get('source_url') or 'not supplied'}",
        f"- Source reference: {metadata.get('source_reference') or 'not supplied'}",
        f"- Supplied by: {metadata['captured_by']} ({metadata.get('supplier_role', 'role not recorded')})",
        f"- Exact text SHA-256: {metadata['actual_sha256']}",
        f"- Article/provision headings recognized: {len(articles)}",
        f"- Promulgation provisions recognized: {promulgation_count}",
        f"- Attached-law article headings recognized: {attached_law_count}",
        f"- Expected article headings recognized: {metadata.get('expected_promulgation_provisions', 'not supplied')} promulgation; {metadata.get('expected_attached_law_articles', 'not supplied')} attached-law",
        f"- Unparsed preamble characters excluded from candidate rows: {preamble_characters}",
        f"- Output candidate chunks: {len(rows)}",
        f"- Empty article bodies requiring review: {len(empty_articles)}",
        f"- Collection permission: {metadata.get('collection_permission', 'unknown')}",
        f"- Permission evidence reference: {metadata.get('permission_evidence_reference') or 'not supplied'}",
        "- Every row is emitted with verified=0, in_force=0, and as_of=null.",
        "- No legal currentness, source authenticity, or reuse rights are inferred.", "",
        "| numbering block | first label | last label | headings | expected |",
        "|---|---|---|---:|---:|",
    ]
    numbering_gaps = {}
    duplicate_numbers = {}
    out_of_range_numbers = {}
    for block, labels in sorted(block_articles.items()):
        numeric = []
        for label in labels:
            match = re.match(r"^issuance_(\d+)$", str(label))
            if not match:
                match = re.match(r"^\s*([0-9٠-٩۰-۹]+)", str(label))
            if match:
                try:
                    numeric.append(int(match.group(1).translate(str.maketrans(
                        "٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789"
                    ))))
                except ValueError:
                    pass
        provision_type = block_provision_types.get(block)
        expected = (
            metadata.get("expected_promulgation_provisions")
            if provision_type == "promulgation"
            else metadata.get("expected_attached_law_articles")
            if provision_type in {"attached_law", "article"}
            else None
        )
        upper_bound = expected if expected is not None else max(numeric, default=0)
        present = set(numeric)
        missing = sorted(set(range(1, upper_bound + 1)) - present)
        duplicates = sorted({number for number in numeric if numeric.count(number) > 1})
        out_of_range = sorted({number for number in numeric if expected is not None and number > expected})
        if missing:
            numbering_gaps[str(block)] = missing
        if duplicates:
            duplicate_numbers[str(block)] = duplicates
        if out_of_range:
            out_of_range_numbers[str(block)] = out_of_range
        expected_label = str(expected) if expected is not None else "not supplied"
        report.append(f"| {block} | {labels[0]} | {labels[-1]} | {len(labels)} | {expected_label} |")

    # An expected block that is wholly absent must not disappear from the audit.
    # The per-block loop above can only report gaps inside blocks that were observed.
    observed_kinds = set(block_provision_types.values())
    expected_blocks = (
        ("promulgation", metadata.get("expected_promulgation_provisions")),
        ("attached_law", metadata.get("expected_attached_law_articles")),
    )
    for kind, expected_count in expected_blocks:
        has_kind = (
            kind in observed_kinds
            or (kind == "attached_law" and "article" in observed_kinds)
        )
        if expected_count and not has_kind:
            missing_key = f"missing_{kind}_block"
            numbering_gaps[missing_key] = list(range(1, expected_count + 1))

    report += ["", "## Numbering audit", "",
               f"- Blocks with missing article numbers: {len(numbering_gaps)}",
               f"- Blocks with duplicate article numbers: {len(duplicate_numbers)}",
               f"- Blocks with out-of-range article numbers: {len(out_of_range_numbers)}"]
    for block, missing in numbering_gaps.items():
        report.append(f"- Block {block} missing: {', '.join(map(str, missing))}")
    for block, duplicates in duplicate_numbers.items():
        report.append(f"- Block {block} duplicates: {', '.join(map(str, duplicates))}")
    for block, out_of_range in out_of_range_numbers.items():
        report.append(f"- Block {block} out of expected range: {', '.join(map(str, out_of_range))}")
    if preamble_characters:
        report += [
            "", "## Unparsed preamble excluded from candidate rows", "",
            f"{preamble_characters} characters before the first recognized heading were not imported. Review this text to ensure it contains only cover/title material and no missed legal provision.",
        ]
    if empty_articles:
        report += ["", "## Empty article bodies", "", ", ".join(empty_articles)]
    report += ["", "## Human review", "",
               "- Compare each candidate article against the supplied Gazette image/text.",
               "- Resolve missing pages, numbering resets, schedules, tables, and OCR/transcription ambiguities.",
               "- Obtain separate source-rights, currentness, amendment/corrigendum, and Egyptian-lawyer review.",
               "- Do not change verification flags in this importer."]
    _write_new_output_files(output_dir, {
        "law_rows.jsonl": jsonl.encode("utf-8"),
        "import_report.md": ("\n".join(report) + "\n").encode("utf-8"),
    })
    return {"document_id": metadata["document_id"], "article_headings": len(articles),
            "promulgation_provisions": promulgation_count,
            "attached_law_articles": attached_law_count,
            "unparsed_preamble_characters": preamble_characters,
            "candidate_chunks": len(rows), "empty_articles": empty_articles,
            "sha256": metadata["actual_sha256"],
            "missing_article_numbers": numbering_gaps,
            "duplicate_article_numbers": duplicate_numbers,
            "out_of_range_article_numbers": out_of_range_numbers,
            "output_dir": str(output_dir)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text_file", type=Path)
    parser.add_argument("metadata_json", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    try:
        result = import_text(args.text_file, args.metadata_json, args.output_dir)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
