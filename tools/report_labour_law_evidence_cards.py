#!/usr/bin/env python3
"""Render provisional Labour Law evidence cards as a reviewer-friendly Markdown report.

This tool formats recorded metadata only. It does not authenticate legal text,
grant source permissions, determine current law, or enable authoritative retrieval.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "candidates" / "labour_law_14_2025" / "provision_evidence_cards.json"
DEFAULT_OUTPUT = ROOT / "data" / "candidates" / "labour_law_14_2025" / "provision_evidence_cards_review.md"


def _link(url: str, label: str | None = None) -> str:
    return f"[{label or url}]({url})"


def render_report(data: dict[str, Any]) -> str:
    instrument = data["instrument"]
    cards = data["cards"]
    lines = [
        "# Labour Law No. 14 of 2025 — provision evidence review",
        "",
        f"**Record:** `{data['record_id']}`  ",
        f"**Prepared on:** {data['created_on']}  ",
        f"**Cards in this report:** {len(cards)}",
        "",
        "## Status and limits",
        "",
        "- **Provisional source-linked research leads only. Not authoritative legal advice.**",
        f"- Authenticity verified: `{str(instrument['authenticity_verified']).lower()}`.",
        f"- Currentness verified: `{str(instrument['currentness_verified']).lower()}`.",
        f"- Amendment history verified: `{str(instrument['amendment_history_verified']).lower()}`.",
        f"- Egyptian-lawyer review: `{instrument['egyptian_lawyer_review']}`.",
        f"- Collection permission: `{instrument['collection_permission']}`; commercial reuse: `{instrument['commercial_reuse_permission']}`.",
        f"- Authoritative search eligibility: `{str(instrument['search_eligible']).lower()}`.",
        "",
        data["source_method_note"],
        "",
        "## Provision cards",
        "",
    ]
    for index, card in enumerate(cards, 1):
        pin = card["pinpoint"]
        printed_page = pin.get("official_gazette_printed_page")
        pdf_page_index = pin.get("pdf_page_index_zero_based")
        printed_page_label = printed_page if printed_page is not None else "not established"
        pdf_page_label = pdf_page_index if pdf_page_index is not None else "not established"
        lines.extend([
            f"### {index}. {card['card_id']}",
            "",
            f"**Question:** {card['question']}",
            "",
            f"**Pinpoint:** {pin['part']}, {pin['article']}, printed Gazette page {printed_page_label} (PDF page index {pdf_page_label}).",
            "",
            "**Provisional summary (Arabic):**",
            "",
            card["provisional_answer_ar"],
            "",
            "**Primary-source leads:**",
            "",
        ])
        for source in card["primary_evidence"]:
            lines.append(f"- {_link(source['url'], source['source_id'])} — {source['source_type']}; {source['supports']} (checked {source['retrieved_or_checked_on']}).")
        lines.extend(["", "**Cross-checks:**", ""])
        for source in card["cross_checks"]:
            lines.append(f"- {_link(source['url'], source['source_type'])} — {source['supports']}.")
        if card.get("related_instruments_to_review"):
            lines.extend(["", "**Related instruments requiring separate review:**", ""])
            for item in card["related_instruments_to_review"]:
                lines.append(f"- `{item['document_id']}` — {item['title_ar']}; {item['status']}. Source: {_link(item['source_url'])}.")
                gazette = item.get("official_gazette_metadata")
                if gazette:
                    lines.append(f"  - Gazette metadata lead: {gazette['gazette_publication']}, {gazette['publication_date']}; {gazette['full_text_status']}")
        lines.extend(["", "**Limitations:**", ""])
        lines.extend(f"- {item}" for item in card["limitations"])
        lines.extend([
            "",
            f"**Review state:** `{card['review_state']}`.",
            f"**Usable for:** {card['usable_for']}.",
            f"**Not usable for:** {card['not_usable_for']}.",
            "",
        ])
    lines.extend([
        "## Activation gates",
        "",
        *[f"{i}. {gate}" for i, gate in enumerate(data["activation_gates"], 1)],
        "",
        "## Important interpretation rule",
        "",
        "A source link, search snippet, or Gazette-index record is evidence of a source lead—not proof that the complete instrument is current, fully compared, licensed for reuse, or approved by Egyptian counsel. Do not activate these cards for authoritative retrieval until all recorded gates are satisfied.",
        "",
    ])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Evidence-card JSON file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Markdown report path")
    args = parser.parse_args(argv)
    data = json.loads(args.input.read_text(encoding="utf-8"))
    report = render_report(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"Wrote {len(data['cards'])} provisional evidence cards to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
