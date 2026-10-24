"""Evidence-preserving formatting helpers for the research source inspector.

These functions label recorded metadata; they never infer legal validity from model confidence or URL presence.
"""
from datetime import date


STATUS_VERIFIED = "verified_operative_text"
STATUS_SECONDARY = "secondary_copy"
STATUS_USER_SUPPLIED = "user_supplied_unverified"
STATUS_METADATA_ONLY = "metadata_only"
STATUS_REVIEW = "outdated_or_under_review"
STATUS_NO_SOURCE = "no_relevant_verified_source"


def source_status(source, as_of=None):
    """Return a conservative, UI-ready source state based only on recorded fields."""
    as_of = as_of or date.today().isoformat()
    if not isinstance(source, dict) or not str(source.get("text") or "").strip():
        return STATUS_METADATA_ONLY
    if source.get("scope") == "firm_documents" or source.get("case_id") is not None:
        return STATUS_USER_SUPPLIED
    provenance = source.get("provenance") or {}
    if provenance.get("status") != "registry_linked":
        return STATUS_REVIEW
    required_true = ("authenticity_verified", "status_verified", "amendment_history_verified")
    if provenance.get("review_status") != "verified":
        return STATUS_REVIEW
    if provenance.get("legal_status") != "in_force":
        return STATUS_REVIEW
    if not all(provenance.get(key) is True or provenance.get(key) == 1 for key in required_true):
        return STATUS_REVIEW
    if provenance.get("collection_permission") != "allowed":
        return STATUS_REVIEW
    if provenance.get("commercial_reuse_permission") != "allowed":
        return STATUS_REVIEW
    if not str(provenance.get("source_permission_evidence") or "").strip():
        return STATUS_REVIEW
    if not str(provenance.get("permission_evidence") or "").strip():
        return STATUS_REVIEW
    effective = provenance.get("effective_date")
    if not effective or effective > as_of:
        return STATUS_REVIEW
    repeal = provenance.get("repeal_date")
    if repeal and repeal <= as_of:
        return STATUS_REVIEW
    if provenance.get("document_type") in {"secondary", "commentary", "guide", "summary"}:
        return STATUS_SECONDARY
    return STATUS_VERIFIED


def citation_text(source, as_of=None):
    """Build a citation from available metadata without inventing missing fields."""
    as_of = as_of or source.get("requested_as_of") or date.today().isoformat()
    p = source.get("provenance") or {}
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
    if p.get("version_label"):
        parts.append("Version: %s" % p["version_label"])
    if p.get("gazette_issue"):
        issue = "Official Gazette %s" % p["gazette_issue"]
        if p.get("gazette_pages"):
            issue += ", pp. %s" % p["gazette_pages"]
        parts.append(issue)
    parts.append("as of %s" % as_of)
    url = p.get("source_url") or source.get("source_url")
    if url:
        parts.append("Source: %s" % url)
    return " · ".join(parts) if parts else "Unresolved citation — source metadata was not recorded"


def research_memo(question, result, scope=None):
    """Produce a plain-text research memo that preserves exact source passages and caveats."""
    as_of = result.get("requested_as_of") or date.today().isoformat()
    scope = scope or result.get("scope") or "verified_corpus"
    lines = [
        "LEGAL RESEARCH MEMO",
        "Question: %s" % (question or "(not recorded)"),
        "As of: %s" % as_of,
        "Search scope: %s" % scope,
        "",
        "Answer",
        result.get("answer") or result.get("message") or "No generated answer.",
        "",
        "Sources and exact passages",
    ]
    sources = result.get("sources") or []
    if not sources:
        lines.append("No relevant verified passage was found in this search scope.")
    for index, source in enumerate(sources, 1):
        lines.extend([
            "",
            "[%d] %s" % (index, citation_text(source, as_of)),
            "Status: %s" % source_status(source, as_of),
            "Exact passage (verbatim):",
            str(source.get("text") or "(No passage text recorded; metadata-only result.)"),
        ])
    lines.extend([
        "",
        "Limitations",
        "- This memo reflects only the selected search scope and records available as of the stated date.",
        "- A URL, registry entry, or model-generated answer is not independent proof of authenticity or current legal status.",
        "- Missing pin-cites, publication/effective dates, amendment history, or permission evidence remain missing; do not infer them.",
        "- If no relevant verified passage was found, this is not evidence that no applicable law exists.",
    ])
    return "\n".join(lines)
