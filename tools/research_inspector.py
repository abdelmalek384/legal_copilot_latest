"""Evidence-preserving formatting helpers for the research source inspector.

These functions label recorded metadata; they never infer legal validity from model
confidence or URL presence. Malformed metadata fails closed to review status.
"""
from datetime import date, datetime, timedelta, timezone
from collections.abc import Mapping
import re
from urllib.parse import urlsplit


STATUS_VERIFIED = "verified_operative_text"
STATUS_SECONDARY = "secondary_copy"
STATUS_USER_SUPPLIED = "user_supplied_unverified"
STATUS_METADATA_ONLY = "metadata_only"
STATUS_REVIEW = "outdated_or_under_review"
STATUS_NO_SOURCE = "no_relevant_verified_source"


_REQUIRED_REVIEW_TYPES = {
    "source_authenticity", "extraction_quality", "legal_status",
    "amendment_history", "licensing", "lawyer_approval",
}


def _valid_review_evidence_url(value):
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = urlsplit(value.strip())
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            return False
        _ = parsed.port
        return True
    except (TypeError, ValueError):
        return False


def _parse_reviewed_at(value):
    """Parse a review timestamp conservatively; naive SQLite UTC timestamps remain supported."""
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        # Existing SQLite datetime('now') values are naive UTC timestamps.
        parsed = parsed.replace(tzinfo=timezone.utc)
    else:
        parsed = parsed.astimezone(timezone.utc)
    # Permit small clock skew but never accept obviously future-dated review evidence.
    if parsed > datetime.now(timezone.utc) + timedelta(minutes=5):
        return None
    return parsed


def _has_current_review_evidence(provenance):
    records = provenance.get("review_evidence")
    if not isinstance(records, list):
        return False
    latest = {}
    for record in records:
        if not isinstance(record, Mapping):
            return False
        kind = record.get("review_type")
        if not isinstance(kind, str):
            return False
        if kind not in _REQUIRED_REVIEW_TYPES:
            continue
        event_id = record.get("review_event_id")
        if isinstance(event_id, bool) or not isinstance(event_id, int) or event_id <= 0:
            return False
        reviewed_at = _parse_reviewed_at(record.get("reviewed_at"))
        if reviewed_at is None:
            return False
        previous = latest.get(kind)
        if previous is None or (reviewed_at, event_id) > (previous[0], previous[1]):
            latest[kind] = (reviewed_at, event_id, record)
    if set(latest) != _REQUIRED_REVIEW_TYPES:
        return False
    for _, _, record in latest.values():
        if record.get("outcome") != "pass":
            return False
        if not isinstance(record.get("reviewer"), str) or not record["reviewer"].strip():
            return False
        if not _valid_review_evidence_url(record.get("evidence_url")):
            return False
    return True


def _calendar_date(value):
    """Return a real ISO calendar date, or None for missing/malformed values."""
    if not isinstance(value, str) or len(value) != 10:
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == value else None


def source_status(source, as_of=None):
    """Return a conservative, UI-ready source state based only on recorded fields."""
    if not isinstance(source, Mapping):
        return STATUS_METADATA_ONLY
    passage = source.get("text")
    if not isinstance(passage, str) or not passage.strip():
        return STATUS_METADATA_ONLY

    # Matter-linked text is always user-supplied evidence, independent of corpus dates.
    if source.get("scope") == "firm_documents" or source.get("case_id") is not None:
        return STATUS_USER_SUPPLIED

    if as_of is None:
        as_of_date = date.today()
    else:
        as_of_date = _calendar_date(as_of)
        if as_of_date is None:
            return STATUS_REVIEW

    # Only an explicitly selected verified-corpus scope may pass the legal-status gates.
    # Missing, malformed, or future scope values must not inherit a verified label.
    if source.get("scope") != "verified_corpus":
        return STATUS_REVIEW

    provenance = source.get("provenance")
    if not isinstance(provenance, Mapping):
        return STATUS_REVIEW
    document_type = provenance.get("document_type")
    if not isinstance(document_type, str) or not document_type.strip():
        return STATUS_REVIEW
    if document_type in {"secondary", "commentary", "guide", "summary"} or source.get("source_type") == "secondary_copy":
        return STATUS_SECONDARY
    if provenance.get("status") != "registry_linked":
        return STATUS_REVIEW

    # "Verified" requires a traceable source and a hash of the original file,
    # not only reviewer flags. Missing or malformed evidence stays under review.
    if not isinstance(provenance.get("official_title"), str) or not provenance["official_title"].strip():
        return STATUS_REVIEW
    if not _valid_review_evidence_url(provenance.get("source_url")):
        return STATUS_REVIEW
    original_sha256 = provenance.get("original_sha256")
    if not isinstance(original_sha256, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", original_sha256):
        return STATUS_REVIEW

    required_true = ("authenticity_verified", "status_verified", "amendment_history_verified")
    if provenance.get("review_status") != "verified":
        return STATUS_REVIEW
    if provenance.get("legal_status") != "in_force":
        return STATUS_REVIEW
    if not all(provenance.get(key) is True or (type(provenance.get(key)) is int and provenance.get(key) == 1) for key in required_true):
        return STATUS_REVIEW
    if provenance.get("collection_permission") != "allowed":
        return STATUS_REVIEW
    if provenance.get("commercial_reuse_permission") != "allowed":
        return STATUS_REVIEW
    # Narrative database fields cannot replace inspectable collection/commercial
    # rights evidence in the central, versioned permission register.
    if provenance.get("source_permission_register_match") is not True:
        return STATUS_REVIEW
    if provenance.get("source_permission_register_collection_permission") != "allowed":
        return STATUS_REVIEW
    if provenance.get("source_permission_register_commercial_reuse_permission") != "allowed":
        return STATUS_REVIEW
    if not _valid_review_evidence_url(provenance.get("permission_evidence_url")):
        return STATUS_REVIEW
    if not _valid_review_evidence_url(provenance.get("commercial_reuse_evidence_url")):
        return STATUS_REVIEW
    for field in ("terms_checked_on", "commercial_terms_checked_on"):
        checked = _calendar_date(provenance.get(field))
        if checked is None or checked > as_of_date:
            return STATUS_REVIEW
    if not str(provenance.get("source_permission_evidence") or "").strip():
        return STATUS_REVIEW
    if not str(provenance.get("permission_evidence") or "").strip():
        return STATUS_REVIEW
    if not _has_current_review_evidence(provenance):
        return STATUS_REVIEW

    effective = _calendar_date(provenance.get("effective_date"))
    if effective is None or effective > as_of_date:
        return STATUS_REVIEW
    repeal_value = provenance.get("repeal_date")
    if repeal_value not in (None, ""):
        repeal = _calendar_date(repeal_value)
        if repeal is None or repeal <= as_of_date:
            return STATUS_REVIEW
    return STATUS_VERIFIED


def citation_text(source, as_of=None):
    """Build a citation from available metadata without inventing missing fields."""
    if not isinstance(source, Mapping):
        return "Unresolved citation — source metadata was not recorded"
    requested_as_of = as_of or source.get("requested_as_of") or "unknown"
    # Invalid dates are still shown as supplied, but must never be used to imply verified status.
    p = source.get("provenance")
    if not isinstance(p, Mapping):
        p = {}
    parts = []
    title = p.get("official_title")
    if title:
        parts.append(str(title))
    number, year = p.get("law_number"), p.get("law_year")
    if number is not None or year is not None:
        parts.append("No. %s/%s" % (number if number is not None else "?", year if year is not None else "?"))
    article = source.get("article")
    if article:
        parts.append("Article %s" % article)
    page = source.get("page")
    if page:
        parts.append("Page %s" % page)
    if p.get("version_label"):
        parts.append("Version: %s" % p["version_label"])
    if p.get("gazette_issue"):
        issue = "Official Gazette %s" % p["gazette_issue"]
        if p.get("gazette_pages"):
            issue += ", pp. %s" % p["gazette_pages"]
        parts.append(issue)
    parts.append("as of %s" % requested_as_of)
    url = p.get("source_url") or source.get("source_url")
    if url:
        parts.append("Source: %s" % url)
    return " · ".join(parts) if parts else "Unresolved citation — source metadata was not recorded"


def research_memo(question, result, scope=None):
    """Produce a plain-text research memo that preserves exact source passages and caveats."""
    if not isinstance(result, Mapping):
        result = {}
    raw_as_of = result.get("requested_as_of")
    try:
        parsed_as_of = date.fromisoformat(raw_as_of) if isinstance(raw_as_of, str) else None
        as_of = parsed_as_of.isoformat() if parsed_as_of and parsed_as_of.isoformat() == raw_as_of else "unknown"
    except ValueError:
        as_of = "unknown"
    scope = scope or result.get("scope")
    if not isinstance(scope, str) or not scope.strip():
        scope = "unknown"
    lines = [
        "LEGAL RESEARCH MEMO",
        "Question: %s" % (question or "(not recorded)"),
        "As of: %s" % as_of,
        "Search scope: %s" % scope,
        "",
        "Answer",
        str(result.get("answer") or result.get("message") or "No generated answer."),
        "",
        "Sources and exact passages",
    ]
    sources = result.get("sources")
    if not isinstance(sources, list):
        sources = []
        lines.append("Source data was malformed; no sources were included in this memo.")
    if not sources:
        empty_scope_messages = {
            "verified_corpus": "No relevant verified passage was returned by this verified-corpus search.",
            "firm_documents": "No relevant passage was returned from the selected matter documents.",
            "metadata_only": "No matching source-catalog metadata was returned; this search did not retrieve legal text.",
            "all_permitted": "No relevant passage was returned by the selected combined search.",
            "unknown": "No source records were returned; the search scope was not recorded.",
        }
        lines.append(empty_scope_messages.get(scope, "No source records were returned for the recorded search scope."))
    for index, source in enumerate(sources, 1):
        if not isinstance(source, Mapping):
            lines.extend([
                "",
                "[%d] Unresolved citation — malformed source record" % index,
                "Status: %s" % STATUS_REVIEW,
                "Exact passage (verbatim):",
                "(No passage text recorded; source record was malformed.)",
            ])
            continue
        passage = source.get("text")
        if not isinstance(passage, str) or not passage.strip():
            passage = "(No passage text recorded; metadata-only result.)"
        lines.extend([
            "",
            "[%d] %s" % (index, citation_text(source, as_of)),
            "Status: %s" % source_status(source, as_of),
            "Exact passage (verbatim):",
            passage,
        ])
    lines.extend([
        "",
        "Limitations",
        ("- The search as-of date was not recorded; do not infer current legal status." if as_of == "unknown" else "- This memo reflects only the selected search scope and records available as of the stated date."),
        "- A URL, registry entry, or model-generated answer is not independent proof of authenticity or current legal status.",
        "- Missing pin-cites, publication/effective dates, amendment history, or permission evidence remain missing; do not infer them.",
        "- An empty result in any selected scope is not evidence that no applicable law exists.",
    ])
    return "\n".join(lines)
