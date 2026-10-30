#!/usr/bin/env python3
"""Build a human review queue from Decision 250 Table 24 candidate batches.

The output is a triage aid, not a legal verification result. It intentionally
never repairs CAS numbers, formulas, units, or limits.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from validate_decision250_table24_candidates import BATCHES, DATA_DIR, flatten_rows, validate
except ImportError:  # package-style import in test runners
    from tools.validate_decision250_table24_candidates import BATCHES, DATA_DIR, flatten_rows, validate


def load_rows(root: Path = DATA_DIR) -> list[dict[str, Any]]:
    errors = validate(root)
    if errors:
        raise ValueError("candidate batches failed validation; refusing to build a partial review queue: " + "; ".join(errors[:10]))
    records: list[dict[str, Any]] = []
    for filename in BATCHES:
        path = root / filename
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for row in flatten_rows(data.get("rows", [])):
            records.append({**row, "_batch_file": filename})
    return sorted(records, key=lambda item: item.get("row", 0))


def categories(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    if row.get("anomaly"):
        tags.append("TEXT/IDENTIFIER ANOMALY")
    scan_status = row.get("secondary_scan_match_status")
    if scan_status == "secondary_image_discrepancy_found":
        tags.append("SECONDARY IMAGE DISCREPANCY — ORIGINAL GAZETTE REQUIRED")
    elif scan_status == "secondary_image_spot_check_partial_fields":
        tags.append("PARTIAL SECONDARY IMAGE CHECK — NOT COMPLETE")
    elif scan_status == "page_locator_assigned_pending_field_comparison":
        tags.append("SECONDARY IMAGE LOCATOR — FIELD COMPARISON PENDING")
    if row.get("risk_note"):
        tags.append("HIGH-RISK REVIEW")
    if row.get("currentness_candidate"):
        tags.append("CURRENTNESS CHECK")
    if not row.get("cas"):
        tags.append("NO CAS / GROUP ENTRY")
    raw = str(row.get("raw_limit_and_note_text") or "")
    if any(token in raw.lower() for token in ("sl)", "surface", "سطح", "سم2", "سم3")):
        tags.append("POSSIBLE SURFACE/AIR UNIT REVIEW")
    if row.get("status") != "pending_official_match":
        tags.append("STATUS GATE VIOLATION")
    return tags


def render(rows: list[dict[str, Any]]) -> str:
    flagged = [(row, categories(row)) for row in rows]
    flagged = [(row, tags) for row, tags in flagged if tags]
    lines = [
        "# Decision 250/2026 Table 24 — human review queue",
        "",
        "**Status:** Triage generated from secondary-transcription candidates; no legal row is approved.",
        "",
        "Do not use this queue as a source of exposure limits. It prioritizes manual review and preserves the original candidate fields.",
        "",
        f"- Candidate rows scanned: {len(rows)}",
        f"- Rows flagged for at least one review reason: {len(flagged)}",
        f"- Source class: secondary transcription only",
        f"- Official Gazette match: not performed",
        "",
        "## Flagged entries",
        "",
        "| Row | English label | Source line | Review flags | CAS candidate/raw token | Secondary image | Candidate vs image discrepancy | Candidate text note |",
        "|---:|---|---:|---|---|---|---|---|",
    ]
    for row, tags in flagged:
        label = str(row.get("name_en") or "MISSING LABEL").replace("|", "\\|").replace("\n", " ")
        cas = row.get("raw_cas_token") or row.get("cas") or "not supplied"
        cas = str(cas).replace("|", "\\|").replace("\n", " ")
        discrepancy = row.get("secondary_scan_discrepancy") or {}
        note = discrepancy.get("note") or row.get("anomaly") or row.get("currentness_candidate") or row.get("risk_note") or "manual source comparison required"
        note = str(note).replace("|", "\\|").replace("\n", " ")
        image = row.get("secondary_scan_image_url") or "not located"
        page = row.get("secondary_scan_printed_page")
        if page:
            image = f"p. {page}: {image}"
        image = str(image).replace("|", "\\|")
        discrepancy_summary = "—"
        if discrepancy:
            discrepancy_summary = (
                f"{discrepancy.get('field', 'field?')}: "
                f"{discrepancy.get('candidate_transcription', 'candidate?')} vs "
                f"{discrepancy.get('secondary_image_observed_tentative', 'image?')} "
                f"({discrepancy.get('status', 'status?')})"
            )
        discrepancy_summary = str(discrepancy_summary).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {row.get('row', '')} | {label} | {row.get('source_line', '')} | "
            f"{'; '.join(tags)} | {cas} | {image} | {discrepancy_summary} | {note} |"
        )
    lines.extend([
        "",
        "## Review rule",
        "",
        "For every flagged entry, compare the exact Official Gazette page image, record the Gazette page and a source-file SHA-256, preserve the transcription as a candidate if anything is unclear, and obtain qualified Egyptian OSH counsel approval before authoritative retrieval.",
        "",
        "This generated queue does not resolve a single anomaly automatically.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DATA_DIR,
                        help="Directory containing the candidate JSON batch files")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output Markdown path (default: stdout)")
    args = parser.parse_args()
    try:
        rows = load_rows(args.root)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    result = render(rows)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
        print(f"Wrote review queue for {len(rows)} candidate rows to {args.output}")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
