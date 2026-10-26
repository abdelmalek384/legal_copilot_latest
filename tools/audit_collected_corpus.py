#!/usr/bin/env python3
"""Read-only integrity audit for collected source files and their metadata history."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def valid_sha256(value):
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in value)


def valid_https_url(value):
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = urlsplit(value)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            return False
        _ = parsed.port
        return True
    except ValueError:
        return False


def safe_relative_file(root: Path, value):
    if not isinstance(value, str) or not value.strip() or "\\" in value or "\x00" in value:
        return None
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        return None
    root_resolved = root.resolve()
    candidate = root
    for part in relative.parts:
        if part in ("", "."):
            continue
        candidate = candidate / part
        if candidate.is_symlink():
            return None
    try:
        candidate.resolve(strict=False).relative_to(root_resolved)
    except (OSError, ValueError):
        return None
    return candidate


def _issue(report, severity, code, detail, document_id=None, metadata_file=None):
    item = {"severity": severity, "code": code, "detail": detail}
    if document_id:
        item["document_id"] = document_id
    if metadata_file:
        item["metadata_file"] = metadata_file
    report["issues"].append(item)


def _read_metadata(path, expected_id, kind, root, report):
    if path.is_symlink():
        _issue(report, "high", "metadata_symlink", "Metadata files must not be symbolic links.", expected_id, str(path.relative_to(root)))
        return None
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _issue(report, "high", "metadata_unreadable", f"Could not read valid JSON metadata ({type(exc).__name__}).", expected_id, str(path.relative_to(root)))
        return None
    if not isinstance(record, dict):
        _issue(report, "high", "metadata_not_object", "Metadata JSON must be an object.", expected_id, str(path.relative_to(root)))
        return None
    document_id = record.get("document_id")
    if document_id != expected_id:
        _issue(report, "high", "metadata_document_id_mismatch", "Metadata document_id does not match its storage location.", expected_id, str(path.relative_to(root)))
    if not isinstance(document_id, str) or not document_id:
        _issue(report, "high", "metadata_document_id_missing", "Metadata needs a non-empty document_id.", expected_id, str(path.relative_to(root)))
    if not valid_sha256(record.get("sha256")):
        _issue(report, "high", "metadata_sha256_invalid", "Metadata sha256 must be a 64-character hexadecimal digest.", expected_id, str(path.relative_to(root)))
    if not valid_https_url(record.get("source_url")):
        _issue(report, "high", "metadata_source_url_invalid", "source_url must be an HTTPS URL without embedded credentials.", expected_id, str(path.relative_to(root)))
    if not isinstance(record.get("source_id"), str) or not record["source_id"].strip():
        _issue(report, "high", "metadata_source_id_missing", "Metadata needs a source_id.", expected_id, str(path.relative_to(root)))
    if record.get("collection_permission") != "allowed":
        _issue(report, "high", "metadata_collection_permission_not_allowed", "A collected artifact must retain explicit collection_permission='allowed'.", expected_id, str(path.relative_to(root)))
    try:
        timestamp = record.get("retrieved_at")
        parsed_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00")) if isinstance(timestamp, str) else None
        if parsed_time is None or parsed_time.tzinfo is None:
            raise ValueError
    except (TypeError, ValueError):
        _issue(report, "medium", "metadata_retrieved_at_invalid", "retrieved_at must be an ISO timestamp with timezone.", expected_id, str(path.relative_to(root)))
    for flag in ("legal_authenticity_verified", "current_legal_status_verified", "commercial_reuse_permission_verified"):
        if record.get(flag) is True:
            _issue(report, "high", "collector_claims_legal_verification", f"Collector metadata must not set {flag}=true.", expected_id, str(path.relative_to(root)))

    original = safe_relative_file(root, record.get("original_path"))
    if original is None:
        _issue(report, "high", "original_path_unsafe", "original_path must remain inside the corpus root and must not traverse symlinks.", expected_id, str(path.relative_to(root)))
        return record
    if not original.is_file():
        _issue(report, "high", "original_file_missing", "The recorded original file does not exist as a regular file.", expected_id, str(path.relative_to(root)))
        return record
    if not valid_sha256(record.get("sha256")):
        return record
    try:
        actual_hash = sha256_file(original)
        if actual_hash.lower() != record["sha256"].lower():
            _issue(report, "high", "original_hash_mismatch", "Original bytes do not match the recorded SHA-256.", expected_id, str(path.relative_to(root)))
        expected_size = record.get("original_size_bytes")
        if isinstance(expected_size, bool) or not isinstance(expected_size, int) or expected_size < 0:
            _issue(report, "medium", "original_size_invalid", "original_size_bytes must be a non-negative integer.", expected_id, str(path.relative_to(root)))
        elif original.stat().st_size != expected_size:
            _issue(report, "high", "original_size_mismatch", "Original file size does not match metadata.", expected_id, str(path.relative_to(root)))
        report["_referenced_originals"].add(str(original.resolve()))
    except OSError as exc:
        _issue(report, "high", "original_unreadable", f"Could not read original file ({type(exc).__name__}).", expected_id, str(path.relative_to(root)))
    return record


def audit(root: Path):
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Corpus root is not a directory: {root}")
    if root.is_symlink():
        raise ValueError("Corpus root must not be a symbolic link")
    root = root.resolve()
    metadata_root = root / "metadata"
    report = {
        "report_type": "collected_corpus_integrity_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "read_only": True,
        "counts": {"current_metadata": 0, "history_metadata": 0, "unique_original_files_referenced": 0},
        "issues": [],
        "notes": [
            "This is a read-only artifact-integrity audit, not legal verification.",
            "A matching hash proves byte consistency with recorded metadata, not source authenticity or reuse rights.",
            "Collector metadata must not be treated as lawyer verification of current law.",
        ],
        "_referenced_originals": set(),
    }
    if metadata_root.is_symlink():
        _issue(report, "high", "metadata_root_symlink", "metadata directory must not be a symbolic link.")
        metadata_root = None
    if metadata_root is None or not metadata_root.is_dir():
        _issue(report, "high", "metadata_root_missing", "No readable metadata directory exists.")
        current_files, history_files = [], []
    else:
        current_files = sorted(metadata_root.glob("*.json"))
        history_root = metadata_root / "history"
        if history_root.is_symlink():
            _issue(report, "high", "metadata_history_root_symlink", "metadata/history must not be a symbolic link.")
            history_files = []
        elif history_root.is_dir():
            history_files = []
            for document_dir in sorted(history_root.iterdir()):
                if document_dir.is_symlink():
                    _issue(report, "high", "metadata_history_directory_symlink", "History document directories must not be symbolic links.", document_dir.name)
                    continue
                if not document_dir.is_dir():
                    continue
                history_files.extend(sorted(document_dir.glob("*.json")))
        else:
            history_files = []

    history_by_id = {}
    for path in history_files:
        expected_id = path.parent.name
        record = _read_metadata(path, expected_id, "history", root, report)
        if record is not None:
            history_by_id.setdefault(expected_id, []).append(record)
            report["counts"]["history_metadata"] += 1
    current_by_id = {}
    for path in current_files:
        expected_id = path.stem
        record = _read_metadata(path, expected_id, "current", root, report)
        if record is not None:
            current_by_id[expected_id] = record
            report["counts"]["current_metadata"] += 1
            canonical = json.dumps(record, ensure_ascii=False, sort_keys=True)
            if not any(json.dumps(item, ensure_ascii=False, sort_keys=True) == canonical for item in history_by_id.get(expected_id, [])):
                _issue(report, "high", "current_metadata_not_archived", "Current metadata must also exist as an immutable history record.", expected_id, str(path.relative_to(root)))

    report["counts"]["unique_original_files_referenced"] = len(report["_referenced_originals"])
    report.pop("_referenced_originals", None)
    report["issue_count"] = len(report["issues"])
    report["issue_counts_by_severity"] = dict(Counter(item["severity"] for item in report["issues"]))
    return report


def render_markdown(report):
    lines = [
        "# Collected corpus integrity audit",
        "",
        f"- Generated: {report['generated_at']}",
        f"- Root: {report['root']}",
        "- Read-only: yes",
        "",
        "## Counts",
        "",
        "| Measure | Count |",
        "|---|---:|",
    ]
    lines.extend(f"| {key.replace('_', ' ')} | {value} |" for key, value in report["counts"].items())
    lines.extend(["", "## Issues", ""])
    if report["issues"]:
        lines.extend(["| Severity | Code | Document | Details |", "|---|---|---|---|"])
        lines.extend(
            f"| {item['severity']} | {item['code']} | {item.get('document_id', '')} | {item['detail'].replace('|', '\\|')} |"
            for item in report["issues"]
        )
    else:
        lines.append("No integrity issues detected.")
    lines.extend(["", "## Interpretation", ""])
    lines.extend(f"- {note}" for note in report["notes"])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Root directory of the collected corpus")
    parser.add_argument("--out-dir", type=Path, required=True, help="Directory for JSON and Markdown reports")
    parser.add_argument("--strict", action="store_true", help="exit non-zero if high-severity integrity issues remain")
    args = parser.parse_args(argv)
    try:
        report = audit(args.root)
    except (OSError, ValueError) as exc:
        print(f"Audit refused: {exc}", file=sys.stderr)
        return 2
    args.out_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.out_dir / "collected_corpus_audit.json"
    md_path = args.out_dir / "collected_corpus_audit.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    print(f"Audited collected corpus read-only: {args.root}")
    print(f"Issues: {report['issue_count']} ({report['issue_counts_by_severity']})")
    print(f"Reports: {json_path} and {md_path}")
    if args.strict and report["issue_counts_by_severity"].get("high", 0):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
