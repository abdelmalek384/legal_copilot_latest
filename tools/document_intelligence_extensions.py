"""Additional literal legal-reference and event-mention candidates.

Kept separate from the canonical document-intelligence module so integration
can extend its output without changing the helper's established contract.
Every result is an unverified text mention, never a verified legal fact/event.
"""
from __future__ import annotations

import bisect
import re
from typing import Any

from tools.document_intelligence import MAX_ANALYSIS_CHARS

_PAGE_MARKER = re.compile(r"\[\[PDF_PAGE:(\d+)\]\]")
_LEGAL_REFERENCE_PATTERNS = (
    re.compile(
        r"(?:المادة|مادة|Article)\s*(?:رقم|No\.?)?\s*[0-9٠-٩]+",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:قانون|القانون)\s*(?:رقم|No\.?)?\s*[0-9٠-٩]+\s*(?:لسنة|of|/)\s*[0-9٠-٩]{4}",
        re.IGNORECASE,
    ),
)
_EVENT_MENTION_PATTERN = re.compile(
    r"جلسة|حكم|إنذار|إخطار|استئناف|طعن|قرار|توقيع|إبرام|فسخ|سداد|استلام|"
    r"محضر|إيداع|تنفيذ|hearing|judgment|notice|appeal|signing|execution|payment|receipt",
    re.IGNORECASE,
)
MAX_ADDITIONAL_CANDIDATES = 250


def extract_legal_reference_and_event_mentions(text: str) -> dict[str, Any]:
    """Return page-located legal-reference and event-term mentions."""
    if not isinstance(text, str):
        raise TypeError("text must be str")
    if len(text) > MAX_ANALYSIS_CHARS:
        raise ValueError("document text exceeds analysis limit")

    page_markers = [
        (match.start(), int(match.group(1)))
        for match in _PAGE_MARKER.finditer(text)
    ]
    patterns = (
        ("legal_reference", _LEGAL_REFERENCE_PATTERNS[0]),
        ("legal_reference", _LEGAL_REFERENCE_PATTERNS[1]),
        ("event_mention", _EVENT_MENTION_PATTERN),
    )
    candidates: list[dict[str, Any]] = []
    for kind, pattern in patterns:
        for match in pattern.finditer(text):
            start, end = match.span()
            marker_index = bisect.bisect_right(page_markers, (start, 10**18)) - 1
            page = page_markers[marker_index][1] if marker_index >= 0 else None
            excerpt = re.sub(
                r"\s+", " ", text[max(0, start - 90):min(len(text), end + 90)]
            ).strip()
            candidates.append({
                "kind": kind,
                "value": match.group(0).strip(),
                "excerpt": excerpt,
                "page": page,
                "start": start,
                "end": end,
                "review_status": "candidate_unverified",
            })
            if len(candidates) >= MAX_ADDITIONAL_CANDIDATES:
                break
        if len(candidates) >= MAX_ADDITIONAL_CANDIDATES:
            break
    candidates.sort(key=lambda item: (item["start"], item["end"], item["kind"]))
    return {
        "candidate_count": len(candidates),
        "candidates": candidates,
        "limitations": [
            "Legal references and event terms are literal mentions, not verified citations or events.",
            "Context, applicability, currentness and legal effect require lawyer review.",
        ],
    }
