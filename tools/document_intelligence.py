"""Conservative, source-located signals for uploaded legal documents.

This module analyses text already extracted by the bounded PDF/DOCX upload path.
It does not perform OCR, make legal conclusions, or mutate original files.
Every extracted signal is a review candidate, not an established fact.
"""
from __future__ import annotations
import bisect
import difflib
from datetime import date
import hashlib
import re
from typing import Any

MAX_ANALYSIS_CHARS = 1_000_000
MAX_COMPARE_CHARS = 100_000
MAX_DIFF_SEGMENTS = 200
_PAGE_MARKER = re.compile(r"\[\[PDF_PAGE:(\d+)\]\]")
_DIGITS = r"0-9٠-٩"
_DATE_PATTERNS = (
    re.compile(rf"(?<![{_DIGITS}])([{_DIGITS}]{{1,2}})[/.-]([{_DIGITS}]{{1,2}})[/.-]([{_DIGITS}]{{2,4}})(?![{_DIGITS}])"),
    re.compile(rf"(?<![{_DIGITS}])([{_DIGITS}]{{4}})[/.-]([{_DIGITS}]{{1,2}})[/.-]([{_DIGITS}]{{1,2}})(?![{_DIGITS}])"),
)
_CASE_PATTERN = re.compile(
    rf"(?:دعوى|القضية|قضية|استئناف|طعن|جنحة|جناية|الدعوى)\s*(?:رقم|رقمها)?\s*[:：#]?\s*([{_DIGITS}]+(?:\s*[/\\-]\s*[{_DIGITS}]+){{0,2}})",
    re.IGNORECASE,
)
_MONEY_PATTERN = re.compile(
    rf"([{_DIGITS}]+(?:[,.٫٬][{_DIGITS}]+)?)\s*(جنيه(?:اً|ا)?|جنيهات|ج\.م|EGP|LE|دولار|ريال)",
    re.IGNORECASE,
)
_PARTY_LABEL_PATTERN = re.compile(
    r"(?:المدعي|المدعى عليه|المتهم|المجني عليه|الطالب|المطلوب ضده|المؤجر|المستأجر|البائع|المشتري|Plaintiff|Defendant|Claimant|Respondent)\s*[:：-]\s*([^\n،؛;]{2,100})",
    re.IGNORECASE,
)
_CLASSIFIERS = (
    ("court_judgment", ("حكم", "محكمة", "منطوق الحكم", "حيثيات", "judgment", "court ruling")),
    ("contract", ("عقد", "اتفق الطرفان", "بند", "الطرف الأول", "الطرف الثاني", "agreement", "contract")),
    ("pleading", ("صحيفة دعوى", "مذكرة دفاع", "طلبات المدعي", "مذكرة", "statement of claim", "pleading", "legal brief")),
    ("correspondence", ("إنذار", "خطاب", "مراسلة", "إخطار", "notice", "correspondence", "letter")),
    ("evidence_or_receipt", ("إيصال", "فاتورة", "محضر", "كشف حساب", "receipt", "invoice", "report")),
)

def sha256_bytes(data: bytes) -> str:
    """Digest exact original bytes; this does not prove authenticity."""
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    return hashlib.sha256(data).hexdigest()

def normalized_text_digest(text: str) -> str:
    """Whitespace-normalized extracted-text digest for candidate grouping."""
    if not isinstance(text, str):
        raise TypeError("text must be str")
    return hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()

def classify_document(filename: str, text: str) -> dict[str, Any]:
    """Return a cautious document-type candidate with transparent keyword evidence."""
    if not isinstance(filename, str) or not isinstance(text, str):
        raise TypeError("filename and text must be strings")
    haystack = f"{filename}\n{text[:MAX_ANALYSIS_CHARS]}".casefold()
    scored = []
    for category, keywords in _CLASSIFIERS:
        matched = [word for word in keywords if word.casefold() in haystack]
        if matched:
            scored.append((len(matched), category, matched))
    if not scored:
        return {"category": "unclassified", "signal_strength": "no_keyword_match", "matched_terms": [], "requires_review": True}
    scored.sort(key=lambda item: (-item[0], item[1]))
    count, category, matched = scored[0]
    return {"category": category, "signal_strength": "multiple_keyword_matches" if count >= 2 else "single_keyword_match",
            "matched_terms": matched, "requires_review": True}

def _candidate(kind: str, match: re.Match, text: str,
               page_markers: list[tuple[int, int]]) -> dict[str, Any]:
    start, end = match.span()
    excerpt = re.sub(r"\s+", " ", text[max(0, start-90):min(len(text), end+90)]).strip()
    marker_index = bisect.bisect_right(page_markers, (start, 10**18)) - 1
    page = page_markers[marker_index][1] if marker_index >= 0 else None
    return {"kind": kind, "value": match.group(0).strip(), "excerpt": excerpt,
            "page": page, "start": start, "end": end,
            "review_status": "candidate_unverified"}

def extract_review_candidates(text: str) -> dict[str, Any]:
    """Extract literal dates, case references, amounts and labelled party names."""
    if not isinstance(text, str):
        raise TypeError("text must be str")
    if len(text) > MAX_ANALYSIS_CHARS:
        raise ValueError("document text exceeds analysis limit")
    candidates = []
    page_markers = [(match.start(), int(match.group(1))) for match in _PAGE_MARKER.finditer(text)]
    for pattern in _DATE_PATTERNS:
        candidates.extend(_candidate("date", match, text, page_markers) for match in pattern.finditer(text))
    candidates.extend(_candidate("case_reference", match, text, page_markers) for match in _CASE_PATTERN.finditer(text))
    candidates.extend(_candidate("amount", match, text, page_markers) for match in _MONEY_PATTERN.finditer(text))
    candidates.extend(_candidate("party_label", match, text, page_markers) for match in _PARTY_LABEL_PATTERN.finditer(text))
    candidates.sort(key=lambda item: (item["start"], item["end"], item["kind"]))
    return {"candidate_count": len(candidates), "candidates": candidates,
            "limitations": [
                "Candidates are literal text matches, not verified facts.",
                "Dates, amounts, names and case references require human confirmation.",
                "A missing candidate does not prove that information is absent.",
                "Scanned image content is not analysed by this text-only function.",
            ]}


def build_date_mention_timeline(documents: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a review queue of parseable date mentions from caller-scoped documents.

    Each input item must contain document_id, filename and the candidates list
    returned by extract_review_candidates. Dates are mentions, not events or
    deadlines. Numeric day-first dates follow the Egyptian DD/MM/YYYY convention;
    ISO year-first dates are parsed separately. Two-digit years are not guessed.
    """
    if not isinstance(documents, list):
        raise TypeError("documents must be a list")
    dated = []
    unparsed = []
    arabic_digits = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
    for document in documents:
        if not isinstance(document, dict):
            raise TypeError("each document must be a mapping")
        document_id = document.get("document_id")
        filename = document.get("filename")
        candidates = document.get("candidates")
        if not isinstance(document_id, str) or not document_id.strip():
            raise ValueError("each document requires a non-empty document_id")
        if not isinstance(filename, str) or not isinstance(candidates, list):
            raise ValueError("each document requires filename and candidates")
        for candidate in candidates:
            if not isinstance(candidate, dict) or candidate.get("kind") != "date":
                continue
            raw = candidate.get("value")
            parsed = None
            interpretation = None
            if isinstance(raw, str):
                parts = re.split(r"[/.-]", raw.translate(arabic_digits))
                try:
                    if len(parts) == 3 and all(part.isdigit() for part in parts):
                        if len(parts[0]) == 4:
                            year, month, day = map(int, parts)
                            interpretation = "year_first"
                        elif len(parts[2]) == 4:
                            day, month, year = map(int, parts)
                            interpretation = "day_first"
                        else:
                            raise ValueError("two-digit year is ambiguous")
                        parsed = date(year, month, day).isoformat()
                except ValueError:
                    parsed = None
            item = {
                "date_mention": raw,
                "normalized_date": parsed,
                "interpretation": interpretation,
                "document_id": document_id,
                "filename": filename,
                "page": candidate.get("page"),
                "excerpt": candidate.get("excerpt", ""),
                "review_status": "date_mention_requires_human_context",
            }
            if parsed is None:
                unparsed.append(item)
            else:
                dated.append(item)
    dated.sort(key=lambda item: (item["normalized_date"], item["document_id"], item["date_mention"]))
    return {
        "dated_mentions": dated,
        "unparsed_mentions": unparsed,
        "limitations": [
            "A date mention is not necessarily an event date, filing date, or legal deadline.",
            "Context and legal effect must be confirmed by a lawyer.",
            "Only documents supplied by the caller are considered; callers must enforce firm and matter scope.",
            "Two-digit years and invalid calendar dates are not guessed.",
        ],
    }

def compare_extracted_text(before: str, after: str, context_chars: int = 100) -> list[dict[str, str]]:
    """Return reviewable text changes; never labels a change as legally significant."""
    if not isinstance(before, str) or not isinstance(after, str):
        raise TypeError("before and after must be strings")
    if len(before) > MAX_COMPARE_CHARS or len(after) > MAX_COMPARE_CHARS:
        raise ValueError("text comparison is limited to 100,000 characters per version")
    if isinstance(context_chars, bool) or not isinstance(context_chars, int) or not 0 <= context_chars <= 1000:
        raise ValueError("context_chars must be an integer between 0 and 1000")
    matcher = difflib.SequenceMatcher(a=before, b=after, autojunk=True)
    changes = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        changes.append({"change_type": tag,
                        "before": before[max(0, i1-context_chars):min(len(before), i2+context_chars)],
                        "after": after[max(0, j1-context_chars):min(len(after), j2+context_chars)],
                        "review_status": "requires_lawyer_review"})
        if len(changes) >= MAX_DIFF_SEGMENTS:
            break
    return changes
