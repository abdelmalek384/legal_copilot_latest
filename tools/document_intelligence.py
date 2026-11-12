"""Conservative, source-located signals for uploaded legal documents.

This module analyses text already extracted by the bounded PDF/DOCX upload path.
It does not perform OCR, make legal conclusions, or mutate original files.
Every extracted signal is a review candidate, not an established fact.
"""
from __future__ import annotations
import difflib
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
        return {"category": "unclassified", "confidence": "low", "matched_terms": [], "requires_review": True}
    scored.sort(key=lambda item: (-item[0], item[1]))
    count, category, matched = scored[0]
    return {"category": category, "confidence": "medium" if count >= 2 else "low",
            "matched_terms": matched, "requires_review": True}

def _page_at(text: str, position: int) -> int | None:
    page = None
    for match in _PAGE_MARKER.finditer(text, 0, position):
        page = int(match.group(1))
    return page

def _candidate(kind: str, match: re.Match, text: str) -> dict[str, Any]:
    start, end = match.span()
    excerpt = re.sub(r"\s+", " ", text[max(0, start-90):min(len(text), end+90)]).strip()
    return {"kind": kind, "value": match.group(0).strip(), "excerpt": excerpt,
            "page": _page_at(text, start), "start": start, "end": end,
            "review_status": "candidate_unverified"}

def extract_review_candidates(text: str) -> dict[str, Any]:
    """Extract literal dates, case references, amounts and labelled party names."""
    if not isinstance(text, str):
        raise TypeError("text must be str")
    if len(text) > MAX_ANALYSIS_CHARS:
        raise ValueError("document text exceeds analysis limit")
    candidates = []
    for pattern in _DATE_PATTERNS:
        candidates.extend(_candidate("date", match, text) for match in pattern.finditer(text))
    candidates.extend(_candidate("case_reference", match, text) for match in _CASE_PATTERN.finditer(text))
    candidates.extend(_candidate("amount", match, text) for match in _MONEY_PATTERN.finditer(text))
    candidates.extend(_candidate("party_label", match, text) for match in _PARTY_LABEL_PATTERN.finditer(text))
    candidates.sort(key=lambda item: (item["start"], item["end"], item["kind"]))
    return {"candidate_count": len(candidates), "candidates": candidates,
            "limitations": [
                "Candidates are literal text matches, not verified facts.",
                "Dates, amounts, names and case references require human confirmation.",
                "A missing candidate does not prove that information is absent.",
                "Scanned image content is not analysed by this text-only function.",
            ]}

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
