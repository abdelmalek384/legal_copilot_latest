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


def load_inventory(input_path: Path) -> dict[str, Any]:
    """Load the canonical inventory and enforce manifest counts; archived split snapshots stay excluded."""
    data = json.loads(input_path.read_text(encoding="utf-8"))
    manifest_path = input_path.with_name("provision_evidence_cards_manifest.json")
    if not manifest_path.exists() or input_path.resolve() != DEFAULT_INPUT.resolve():
        return data

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cards = list(data["cards"])
    seen = {card["card_id"] for card in cards}
    duplicates: set[str] = set()
    supplemental_count = 0
    for entry in manifest["inventory_files"]:
        candidate = (ROOT / entry["path"]).resolve()
        if candidate == input_path.resolve():
            continue
        payload = json.loads(candidate.read_text(encoding="utf-8"))
        if len(payload.get("cards", [])) != entry["expected_cards"]:
            raise ValueError(f"Card count mismatch for {entry['path']}")
        for raw in payload["cards"]:
            card = dict(raw)
            card_id = card["card_id"]
            if card_id in seen:
                duplicates.add(card_id)
                continue
            seen.add(card_id)
            supplemental_count += 1
            pin = dict(card["pinpoint"])
            article_number = int(str(pin["article"]).replace("المادة ", ""))
            pin.setdefault(
                "part",
                "الكتاب الثالث — علاقات العمل"
                if article_number <= 241
                else "الكتاب الرابع — السلامة والصحة المهنية وتأمين بيئة العمل"
                if article_number <= 274
                else "الكتاب الخامس — تفتيش العمل والعقوبات",
            )
            pin.setdefault("official_gazette_printed_page", None)
            pin.setdefault("pdf_page_index_zero_based", None)
            card["pinpoint"] = pin
            for source in card.get("primary_evidence", []):
                source.setdefault("supports", "مصدر استدلالي؛ يلزم التحقق من النص الرسمي")
                source.setdefault("retrieved_or_checked_on", manifest["updated_on"])
                source.setdefault("source_id", source.get("source_type", "public-source-lead"))
            for source in card.get("cross_checks", []):
                source.setdefault("supports", "مقارنة ثانوية؛ لا تحل محل النص الرسمي")
            card.setdefault("related_instruments_to_review", [])
            cards.append(card)

    if duplicates:
        duplicate_list = ", ".join(sorted(duplicates))
        raise ValueError(f"Duplicate Labour Law evidence card IDs: {duplicate_list}")

    if len(cards) != manifest["combined_expected_cards"]:
        raise ValueError(
            f"Combined card count mismatch: expected {manifest['combined_expected_cards']}, got {len(cards)}"
        )
    data["cards"] = cards
    data["source_method_note"] += (
        f" Canonical manifest inventory loaded: {len(cards)} cards; "
        "archived split snapshots are excluded to avoid duplicate IDs and divergent records."
    )
    return data


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
        page_label = (
            f"printed Gazette page {pin['official_gazette_printed_page']} (PDF page index {pin['pdf_page_index_zero_based']})"
            if pin.get("official_gazette_printed_page") is not None
            else "Official Gazette page pinpoint not verified"
        )
        lines.extend([
            f"### {index}. {card['card_id']}",
            "",
            f"**Question:** {card['question']}",
            "",
            f"**Pinpoint:** {pin['part']}, {pin['article']}, {page_label}.",
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
            f"**Usable for:** {card.get('usable_for', 'provisional research lead and manual source review only')}.",
            f"**Not usable for:** {card.get('not_usable_for', 'authoritative legal advice or definitive current-law conclusions pending source, currentness, rights and counsel review')}.",
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
    data = load_inventory(args.input)
    report = render_report(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"Wrote {len(data['cards'])} provisional evidence cards to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
