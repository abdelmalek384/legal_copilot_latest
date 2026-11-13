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
import unicodedata
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
    r"(?:المدعي|المدعى عليه|المتهم|المجني عليه|الطالب|المطلوب ضده|المؤجر|المستأجر|البائع|المشتري|Plaintiff|Defendant|Claimant|Respondent)\s*[:：-]\s*([^\n،؛;.!?؟]{2,100})",
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

_LEGAL_REFERENCE_PATTERN = re.compile(
    rf"(?:المادة|مادة|Article)\s*(?:رقم|No\.?)?\s*[{_DIGITS}]+|"
    rf"(?:قانون|القانون)\s*(?:رقم|No\.?)?\s*[{_DIGITS}]+\s*(?:لسنة|of|/)\s*[{_DIGITS}]{{4}}",
    re.IGNORECASE,
)
_EVENT_MENTION_PATTERN = re.compile(
    r"(?:جلسة|حكم|إنذار|إخطار|استئناف|طعن|قرار|توقيع|إبرام|فسخ|سداد|استلام|hearing|judgment|notice|appeal|termination|payment)",
    re.IGNORECASE,
)


def extract_review_candidates(text: str, max_candidates: int = 250) -> dict[str, Any]:
    """Extract bounded literal candidates; every result remains unverified."""
    if not isinstance(text, str):
        raise TypeError("text must be str")
    if len(text) > MAX_ANALYSIS_CHARS:
        raise ValueError("document text exceeds analysis limit")
    if isinstance(max_candidates, bool) or not isinstance(max_candidates, int) or not 1 <= max_candidates <= 1000:
        raise ValueError("max_candidates must be an integer between 1 and 1000")
    candidates = []
    page_markers = [(match.start(), int(match.group(1))) for match in _PAGE_MARKER.finditer(text)]
    patterns = [
        ("date", pattern) for pattern in _DATE_PATTERNS
    ] + [
        ("case_reference", _CASE_PATTERN),
        ("amount", _MONEY_PATTERN),
        ("party_label", _PARTY_LABEL_PATTERN),
        ("legal_reference", _LEGAL_REFERENCE_PATTERN),
        ("event_mention", _EVENT_MENTION_PATTERN),
    ]
    truncated = False
    # Bound intermediate work per pattern, then retain the earliest candidates
    # across all types so a frequent date pattern cannot starve other signals.
    for kind, pattern in patterns:
        for index, match in enumerate(pattern.finditer(text)):
            if index >= max_candidates:
                truncated = True
                break
            candidates.append(_candidate(kind, match, text, page_markers))
    candidates.sort(key=lambda item: (item["start"], item["end"], item["kind"]))
    if len(candidates) > max_candidates:
        candidates = candidates[:max_candidates]
        truncated = True
    return {"candidate_count": len(candidates), "candidates": candidates, "truncated": truncated,
            "limitations": [
                "Candidates are literal text matches, not verified facts.",
                "Dates, amounts, names, case references, legal references and event mentions require human confirmation.",
                "A missing candidate does not prove that information is absent.",
                "Scanned image content is not analysed by this text-only function.",
            ]}



def group_same_matter_duplicates(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group duplicate candidates only inside identical firm/matter scopes.

    Each record requires firm_id, matter_id, document_id and may include
    original_sha256 and extracted_text_sha256. Hashes must be lowercase or
    uppercase 64-character SHA-256 hex strings. The caller must still enforce
    authorization before supplying records. Groups are review candidates;
    matching extracted text does not mean the original files are identical.
    """
    if not isinstance(documents, list):
        raise TypeError("documents must be a list")
    buckets: dict[tuple[str, str, str, str], list[dict[str, str]]] = {}
    for item in documents:
        if not isinstance(item, dict):
            raise TypeError("each document must be a mapping")
        firm_id, matter_id, document_id = (
            item.get("firm_id"), item.get("matter_id"), item.get("document_id")
        )
        if not all(isinstance(value, str) and value.strip()
                   for value in (firm_id, matter_id, document_id)):
            raise ValueError("each document requires firm_id, matter_id and document_id")
        for basis in ("original_sha256", "extracted_text_sha256"):
            digest = item.get(basis)
            if digest is None:
                continue
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
                raise ValueError(f"{basis} must be a 64-character SHA-256 hex digest")
            key = (firm_id, matter_id, basis, digest.lower())
            buckets.setdefault(key, []).append({
                "firm_id": firm_id, "matter_id": matter_id, "document_id": document_id
            })
    results = []
    for (firm_id, matter_id, basis, digest), members in buckets.items():
        unique = {member["document_id"]: member for member in members}
        if len(unique) > 1:
            results.append({
                "firm_id": firm_id, "matter_id": matter_id, "match_basis": basis,
                "document_ids": sorted(unique),
                "review_status": "possible_duplicate_requires_review",
            })
    results.sort(key=lambda group: (
        group["firm_id"], group["matter_id"], group["match_basis"], group["document_ids"]
    ))
    return results

def group_candidate_entity_mentions(
    documents: list[dict[str, Any]],
    max_candidates: int = 5000,
    max_groups: int = 500,
) -> dict[str, Any]:
    """Group exact normalized party/reference mentions within firm/matter scope.

    A group means only that the same literal mention appears in multiple
    documents. It is not an identity-resolution result or proof that two
    references denote the same person, entity, case or instrument.
    """
    if not isinstance(documents, list):
        raise TypeError("documents must be a list")
    for name, value, maximum in (
        ("max_candidates", max_candidates, 10000),
        ("max_groups", max_groups, 2000),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
            raise ValueError(f"{name} must be an integer between 1 and {maximum}")

    buckets: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    candidate_count = 0
    truncated = False
    allowed_types = {"labelled_party", "case_reference", "legal_reference"}
    for document in documents:
        if not isinstance(document, dict):
            raise TypeError("each document must be a mapping")
        firm_id, matter_id, document_id = (
            document.get("firm_id"), document.get("matter_id"), document.get("document_id")
        )
        if not all(isinstance(value, str) and value.strip()
                   for value in (firm_id, matter_id, document_id)):
            raise ValueError("each document requires firm_id, matter_id and document_id")
        filename = document.get("filename", "")
        if not isinstance(filename, str):
            raise ValueError("filename must be a string")
        entities = document.get("entities", [])
        if not isinstance(entities, list):
            raise ValueError("entities must be a list")
        for entity in entities:
            if not isinstance(entity, dict) or entity.get("entity_type") not in allowed_types:
                continue
            literal = entity.get("name_mention") if entity.get("entity_type") == "labelled_party" else entity.get("mention")
            if not isinstance(literal, str) or not literal.strip():
                continue
            if candidate_count >= max_candidates:
                truncated = True
                break
            normalized = " ".join(unicodedata.normalize("NFKC", literal).casefold().split())
            if not normalized:
                continue
            candidate_count += 1
            key = (firm_id, matter_id, str(entity["entity_type"]), normalized)
            buckets.setdefault(key, []).append({
                "document_id": document_id,
                "filename": filename,
                "mention": entity.get("mention", literal),
                "matched_value": literal,
                "role_label": entity.get("role_label"),
                "page": entity.get("page"),
                "chunk_id": entity.get("chunk_id"),
                "chunk_ref": entity.get("chunk_ref"),
                "start": entity.get("start"),
                "end": entity.get("end"),
            })
        if truncated:
            break

    groups = []
    for (firm_id, matter_id, entity_type, normalized), members in buckets.items():
        unique_documents = {member["document_id"] for member in members}
        if len(unique_documents) < 2:
            continue
        groups.append({
            "firm_id": firm_id,
            "matter_id": matter_id,
            "entity_type": entity_type,
            "normalized_match": normalized,
            "matched_values": sorted({member["matched_value"] for member in members}),
            "document_ids": sorted(unique_documents),
            "members": members,
            "match_basis": "exact_nfkc_casefold_whitespace",
            "review_status": "possible_repeat_mention_requires_human_review",
        })
    groups.sort(key=lambda item: (
        item["entity_type"], item["normalized_match"], item["document_ids"]
    ))
    if len(groups) > max_groups:
        groups = groups[:max_groups]
        truncated = True
    return {
        "groups": groups,
        "group_count": len(groups),
        "candidate_count": candidate_count,
        "truncated": truncated,
        "requires_review": True,
        "warning": (
            "Groups indicate exact normalized text recurrence only. They do not establish identity, "
            "common ownership, party equivalence, case linkage or legal relationship."
        ),
        "limitations": [
            "Only labelled-party, case-reference and legal-reference mentions are grouped.",
            "Normalization applies Unicode NFKC, case-folding and whitespace collapse only; no fuzzy or transliteration matching is performed.",
            "Common names and repeated reference strings may belong to different people, entities or matters.",
            "A missing group does not prove that documents concern different parties.",
            "Every group requires lawyer review against its source documents.",
        ],
    }


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
                "chunk_id": candidate.get("chunk_id"),
                "chunk_ref": candidate.get("chunk_ref"),
                "start": candidate.get("start"),
                "end": candidate.get("end"),
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

_ARABIC_RELATION_PATTERN = re.compile(
    r"(?P<subject>[\u0621-\u064A][\u0621-\u064A\s]{1,70}?)\s+"
    r"(?P<relation>وكيل عن|محام عن|محامي عن|مفوّض عن|مفوض عن|يمثل|تمثل|مالك|مستأجر|مؤجر|بائع|مشتري|شريك مع|زوج|زوجة|ابن|ابنة)\s+"
    r"(?P<object>[\u0621-\u064A][\u0621-\u064A\s]{1,70}?)(?=$|[،,؛;.!؟?\n])",
    re.IGNORECASE,
)
_ENGLISH_RELATION_PATTERN = re.compile(
    r"(?P<subject>[A-Z][A-Za-z'-]*(?:\s+[A-Z][A-Za-z'-]*){0,3})\s+"
    r"(?P<relation>represents|represented by|agent for|attorney for|lessor of|lessee of|employer of|employee of|partner of)\s+"
    r"(?P<object>[A-Z][A-Za-z'-]*(?:\s+[A-Z][A-Za-z'-]*){0,3})(?=$|[,.!?;\n])",
    re.IGNORECASE,
)


def _sentence_spans(text: str):
    """Yield conservative sentence-like spans without changing source offsets."""
    start = 0
    for match in re.finditer(r"[.!?؟؛;\n]+", text):
        end = match.start()
        if text[start:end].strip():
            yield start, end
        start = match.end()
    if text[start:].strip():
        yield start, len(text)


def _page_at(position: int, page_markers: list[tuple[int, int]]):
    marker_index = bisect.bisect_right(page_markers, (position, 10**18)) - 1
    return page_markers[marker_index][1] if marker_index >= 0 else None


def extract_structured_candidates(text: str, max_items: int = 250) -> dict[str, Any]:
    """Build provenance-linked entity, event and explicit-relationship candidates.

    This is a conservative rule-based structuring pass over extracted text. It
    only links dates/party labels to an event when they occur in the same
    sentence-like span, and only emits relationships when an explicit relation
    phrase is present. Every result is unverified and requires human review.
    """
    if not isinstance(text, str):
        raise TypeError("text must be str")
    if len(text) > MAX_ANALYSIS_CHARS:
        raise ValueError("document text exceeds analysis limit")
    if isinstance(max_items, bool) or not isinstance(max_items, int) or not 1 <= max_items <= 500:
        raise ValueError("max_items must be an integer between 1 and 500")

    page_markers = [(match.start(), int(match.group(1))) for match in _PAGE_MARKER.finditer(text)]
    # Collect each signal family independently, then interleave families before
    # applying the shared cap. A dense date list must not starve party/legal IDs.
    entity_patterns = (
        ("party_label", (_PARTY_LABEL_PATTERN,)),
        ("case_reference", (_CASE_PATTERN,)),
        ("legal_reference", (_LEGAL_REFERENCE_PATTERN,)),
        ("amount", (_MONEY_PATTERN,)),
        ("date", _DATE_PATTERNS),
    )
    queues = {kind: [] for kind, _ in entity_patterns}
    truncated = False
    for kind, patterns in entity_patterns:
        for pattern in patterns:
            for index, match in enumerate(pattern.finditer(text)):
                if index >= max_items:
                    truncated = True
                    break
                queues[kind].append(_candidate(kind, match, text, page_markers))
    selected = []
    while len(selected) < max_items:
        added = False
        for kind, _ in entity_patterns:
            if queues[kind]:
                selected.append(queues[kind].pop(0))
                added = True
                if len(selected) >= max_items:
                    break
        if not added:
            break
    if any(queues.values()):
        truncated = True
    selected.sort(key=lambda item: (item["start"], item["end"], item["kind"]))

    entities = []
    entity_types = {
        "party_label": "labelled_party",
        "case_reference": "case_reference",
        "legal_reference": "legal_reference",
        "amount": "monetary_amount",
        "date": "date_mention",
    }
    for candidate in selected:
        kind = candidate["kind"]
        entity = {
            "entity_type": entity_types[kind],
            "mention": candidate["value"],
            "excerpt": candidate["excerpt"],
            "page": candidate["page"],
            "start": candidate["start"],
            "end": candidate["end"],
            "review_status": "entity_candidate_unverified",
        }
        if kind == "party_label":
            parts = re.split(r"[:：-]", candidate["value"], maxsplit=1)
            entity["role_label"] = parts[0].strip()
            entity["name_mention"] = parts[1].strip() if len(parts) > 1 else ""
        entities.append(entity)

    events = []
    relationships = []
    for sentence_start, sentence_end in _sentence_spans(text):
        sentence = text[sentence_start:sentence_end].strip()
        if not sentence:
            continue
        leading_trim = len(text[sentence_start:sentence_end]) - len(text[sentence_start:sentence_end].lstrip())
        absolute_start = sentence_start + leading_trim
        date_evidence = []
        for pattern in _DATE_PATTERNS:
            for match in pattern.finditer(sentence):
                date_evidence.append({
                    "mention": match.group(0),
                    "start": absolute_start + match.start(),
                    "end": absolute_start + match.end(),
                })
                if len(date_evidence) >= 10:
                    break
        party_evidence = [
            {
                "mention": match.group(0).strip(),
                "start": absolute_start + match.start(),
                "end": absolute_start + match.end(),
            }
            for match in list(_PARTY_LABEL_PATTERN.finditer(sentence))[:10]
        ]
        local_dates = [item["mention"] for item in date_evidence]
        local_parties = [item["mention"] for item in party_evidence]
        for trigger in _EVENT_MENTION_PATTERN.finditer(sentence):
            if len(events) >= max_items:
                truncated = True
                break
            start = absolute_start + trigger.start()
            end = absolute_start + trigger.end()
            events.append({
                "trigger": trigger.group(0),
                "sentence": sentence[:1000],
                "date_mentions": local_dates,
                "date_evidence": date_evidence,
                "party_mentions": local_parties,
                "party_evidence": party_evidence,
                "page": _page_at(start, page_markers),
                "start": start,
                "end": end,
                "sentence_start": absolute_start,
                "sentence_end": absolute_start + len(sentence),
                "review_status": "event_candidate_requires_human_context",
            })
        for pattern in (_ARABIC_RELATION_PATTERN, _ENGLISH_RELATION_PATTERN):
            for match in pattern.finditer(sentence):
                if len(relationships) >= max_items:
                    truncated = True
                    break
                relationships.append({
                    "subject_mention": match.group("subject").strip(),
                    "relation_mention": match.group("relation").strip(),
                    "object_mention": match.group("object").strip(),
                    "sentence": sentence[:1000],
                    "page": _page_at(absolute_start + match.start(), page_markers),
                    "start": absolute_start + match.start(),
                    "end": absolute_start + match.end(),
                    "review_status": "explicit_relationship_candidate_unverified",
                })
        if len(events) >= max_items and len(relationships) >= max_items:
            truncated = True
            break

    return {
        "entities": entities,
        "events": events,
        "relationships": relationships,
        "entity_count": len(entities),
        "event_count": len(events),
        "relationship_count": len(relationships),
        "truncated": truncated,
        "requires_review": True,
        "limitations": [
            "Entity mentions are extracted from explicit labels and literal identifiers; this is not general named-entity recognition.",
            "Event triggers are mentions, not proof that an event occurred; dates and parties are linked only by sentence co-occurrence.",
            "Relationships are emitted only for explicit relation phrases; direction and legal effect require human confirmation.",
            "All values retain source offsets and available PDF page markers but may reflect extraction or OCR errors.",
            "A missing candidate does not prove that an entity, event or relationship is absent.",
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
