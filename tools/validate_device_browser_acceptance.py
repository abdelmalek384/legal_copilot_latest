#!/usr/bin/env python3
"""Validate device/browser acceptance evidence without claiming tests were run.

A structurally valid record may still contain NOT_TESTED/BLOCKED results.
Use --require-pass for a release gate; it also requires desktop and phone
coverage in both supported locales.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REQUIRED_RESULTS = (
    "installation", "authentication_and_isolation", "case_management",
    "legal_research_and_abstention", "arabic_and_english",
    "keyboard_and_screen_reader", "pwa_offline_privacy", "deployment_smoke",
)
VALID_STATES = {"PASS", "FAIL", "BLOCKED", "NOT_TESTED"}
VALID_ENVIRONMENTS = {"local", "staging"}
VALID_LOCALES = {"ar-EG", "en-US"}
VALID_DEVICE_CLASSES = {"desktop", "phone", "tablet"}
REQUIRED_RELEASE_MATRIX = {
    (device_class, locale)
    for device_class in ("desktop", "phone")
    for locale in VALID_LOCALES
}


class EvidenceError(ValueError):
    pass


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _timestamp(value):
    if not _nonempty(value):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _validate_evidence_files(evidence_paths, evidence_root):
    if evidence_root is None:
        raise EvidenceError("evidence_root is required when --require-pass is used")
    root = Path(evidence_root)
    if root.is_symlink():
        raise EvidenceError("evidence root must not be a symlink")
    try:
        resolved_root = root.resolve(strict=True)
    except OSError as exc:
        raise EvidenceError("evidence root does not exist") from exc
    if not resolved_root.is_dir():
        raise EvidenceError("evidence root must be a directory")
    for raw_path in evidence_paths:
        if "\\" in raw_path or ":" in raw_path:
            raise EvidenceError("evidence paths must be relative POSIX paths")
        parts = raw_path.split("/")
        if raw_path.startswith("/") or any(part in {"", ".", ".."} for part in parts):
            raise EvidenceError("evidence paths must stay inside the evidence root")
        candidate = resolved_root
        for part in parts:
            candidate = candidate / part
            if candidate.is_symlink():
                raise EvidenceError("evidence paths must not contain symlinks")
        try:
            resolved = candidate.resolve(strict=True)
        except OSError as exc:
            raise EvidenceError("evidence file is missing: " + raw_path) from exc
        if not resolved.is_relative_to(resolved_root):
            raise EvidenceError("evidence path escapes the evidence root")
        if not resolved.is_file() or resolved.stat().st_size <= 0:
            raise EvidenceError("evidence file must be a non-empty regular file: " + raw_path)


def validate_record(record, expected_commit=None, require_pass=False, evidence_root=None):
    if not isinstance(record, dict):
        raise EvidenceError("record must be a JSON object")
    errors = []
    if type(record.get("record_version")) is not int or record.get("record_version") != 1:
        errors.append("record_version must equal 1")
    if not _timestamp(record.get("tested_at")):
        errors.append("tested_at must be an ISO-8601 timestamp with timezone")
    commit = record.get("application_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        errors.append("application_commit must be a full 40-character Git commit SHA")
    elif expected_commit and commit.lower() != expected_commit.lower():
        errors.append("application_commit does not match expected commit")
    if record.get("environment") not in VALID_ENVIRONMENTS:
        errors.append("environment must be local or staging")
    for field in ("os_and_build", "device", "browser_and_version", "viewport", "network", "tester_role"):
        if not _nonempty(record.get(field)):
            errors.append(field + " must be a non-empty string")
    if record.get("device_class") not in VALID_DEVICE_CLASSES:
        errors.append("device_class must be desktop, phone, or tablet")
    if record.get("locale") not in VALID_LOCALES:
        errors.append("locale must be ar-EG or en-US")
    results = record.get("results")
    if not isinstance(results, dict):
        errors.append("results must be an object")
        results = {}
    for key in REQUIRED_RESULTS:
        state = results.get(key)
        if state not in VALID_STATES:
            errors.append("results." + key + " must be PASS, FAIL, BLOCKED, or NOT_TESTED")
        elif require_pass and state != "PASS":
            errors.append("release gate requires PASS for results." + key)
    unknown = sorted(set(results) - set(REQUIRED_RESULTS))
    if unknown:
        errors.append("unknown result keys: " + ", ".join(unknown))
    defects = record.get("defect_ids")
    if not isinstance(defects, list) or any(not _nonempty(item) for item in defects):
        errors.append("defect_ids must be a list of non-empty strings")
        defects = []
    evidence = record.get("evidence_paths")
    if not isinstance(evidence, list) or any(not _nonempty(item) for item in evidence):
        errors.append("evidence_paths must be a list of non-empty strings")
        evidence = []
    if any(state == "PASS" for state in results.values()) and not evidence:
        errors.append("at least one evidence path is required when any check is PASS")
    if any(state in {"FAIL", "BLOCKED"} for state in results.values()) and not defects:
        errors.append("defect_ids must identify the issue for FAIL/BLOCKED results")
    if not _nonempty(record.get("notes")):
        errors.append("notes must be a non-empty string")
    if require_pass and evidence:
        try:
            _validate_evidence_files(evidence, evidence_root)
        except EvidenceError as exc:
            errors.append(str(exc))
    if errors:
        raise EvidenceError("; ".join(errors))
    return {
        "application_commit": commit.lower(),
        "environment": record["environment"],
        "device_class": record["device_class"],
        "locale": record["locale"],
        "passed_checks": sum(results[key] == "PASS" for key in REQUIRED_RESULTS),
        "total_checks": len(REQUIRED_RESULTS),
        "complete": all(results[key] == "PASS" for key in REQUIRED_RESULTS),
    }


def validate_release_matrix(records, summaries):
    """Require desktop and phone evidence in Arabic and English for one build."""
    if not records or not summaries:
        raise EvidenceError("release device matrix is empty")
    commits = {item["application_commit"] for item in summaries}
    environments = {item["environment"] for item in summaries}
    if len(commits) != 1:
        raise EvidenceError("release device matrix must cover exactly one application commit")
    if len(environments) != 1:
        raise EvidenceError("release device matrix must use exactly one environment")
    observed = {(item["device_class"], item["locale"]) for item in summaries}
    missing = sorted(REQUIRED_RELEASE_MATRIX - observed)
    if missing:
        labels = ", ".join(f"{device_class}/{locale}" for device_class, locale in missing)
        raise EvidenceError("release device matrix is incomplete; missing: " + labels)


def load_records(path):
    raw = Path(path).read_text(encoding="utf-8-sig")
    if not raw.strip():
        raise EvidenceError("input file is empty")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        records = []
        for line_number, line in enumerate(raw.splitlines(), 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise EvidenceError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
        return records
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict):
        return [parsed]
    raise EvidenceError("input must be one JSON object, a JSON array, or JSONL")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="JSON, JSON array, or JSONL evidence file")
    parser.add_argument("--expected-commit", help="Require every record to match this full commit SHA")
    parser.add_argument("--require-pass", action="store_true",
                        help="Require every check to pass and the desktop/phone × Arabic/English matrix")
    args = parser.parse_args(argv)
    if args.expected_commit and not re.fullmatch(r"[0-9a-fA-F]{40}", args.expected_commit):
        parser.error("--expected-commit must be a full 40-character commit SHA")
    try:
        records = load_records(args.input)
        if not records:
            raise EvidenceError("no evidence records found")
        evidence_root = Path(args.input).resolve().parent if args.require_pass else None
        summaries = [validate_record(item, args.expected_commit, args.require_pass, evidence_root) for item in records]
        identities = [
            (item["application_commit"], item["environment"], item["locale"],
             records[index].get("device_class"), records[index].get("device"),
             records[index].get("browser_and_version"), records[index].get("viewport"))
            for index, item in enumerate(summaries)
        ]
        if len(identities) != len(set(identities)):
            raise EvidenceError("duplicate evidence records for the same commit/environment/locale/device/browser/viewport")
        if args.require_pass:
            validate_release_matrix(records, summaries)
        print(json.dumps({
            "records_validated": len(summaries),
            "release_gate": "PASS" if args.require_pass and all(item["complete"] for item in summaries) else "NOT_PASSED",
            "records": summaries,
        }, ensure_ascii=False, indent=2))
        return 0
    except (OSError, EvidenceError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
