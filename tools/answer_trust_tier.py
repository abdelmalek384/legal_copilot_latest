"""Conservative answer-level trust classification for legal research responses.

Pure policy helper. Call only with server-generated source records and claim
verification results; never pass model-authored evidence flags. This does not
replace research_inspector.source_status or the legal release gate.
"""
from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from datetime import date
from urllib.parse import urlsplit

TIER_VERIFIED = "verified"
TIER_SOURCE_MATCHED = "source_matched"
TIER_UNREVIEWED = "unreviewed"

_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _valid_sha256(value: object) -> bool:
    return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None


def _source_matched_evidence_ready(source: Mapping) -> bool:
    """Require the complete technical evidence package proposed for this tier."""
    evidence = source.get("source_match_evidence")
    if not isinstance(evidence, Mapping):
        return False
    if evidence.get("validator_passed") is not True:
        return False
    if not _valid_sha256(evidence.get("original_capture_sha256")):
        return False
    if not _valid_sha256(evidence.get("independent_copy_sha256")):
        return False
    source_id = source.get("source_id")
    independent_source_id = evidence.get("independent_copy_source_id")
    if (not isinstance(source_id, str) or not source_id.strip() or source_id != source_id.strip()
            or not isinstance(independent_source_id, str) or not independent_source_id.strip()
            or independent_source_id != independent_source_id.strip()
            or independent_source_id == source_id):
        return False
    for field in ("publication_date", "effective_date"):
        value = evidence.get(field)
        try:
            parsed = date.fromisoformat(value) if isinstance(value, str) else None
        except ValueError:
            return False
        if parsed is None or parsed.isoformat() != value:
            return False
    rights_url = evidence.get("reuse_rights_evidence_url")
    if (not isinstance(rights_url, str) or not rights_url or rights_url != rights_url.strip()
            or any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in rights_url)):
        return False
    try:
        parsed_url = urlsplit(rights_url) if isinstance(rights_url, str) else None
        port = parsed_url.port if parsed_url else None
    except ValueError:
        return False
    if (parsed_url is None or parsed_url.scheme.lower() != "https"
            or not parsed_url.hostname or parsed_url.username is not None
            or parsed_url.password is not None or parsed_url.query or parsed_url.fragment
            or parsed_url.netloc.endswith(":") or (port is not None and not 1 <= port <= 65535)):
        return False
    required = (
        "article_inventory_complete",
        "differences_resolved_against_primary",
        "publication_and_effective_dates_verified",
        "reuse_rights_allowed",
    )
    return all(evidence.get(key) is True for key in required)


def classify_answer_trust_tier(
    sources: object,
    *,
    claims_supported: object,
    citations_complete: object,
    contradictory_sources: object = False,
    source_matched_policy_approved: object = False,
    source_matched_feature_enabled: object = False,
) -> dict:
    """Return a fail-closed answer tier and machine-readable reasons.

    Claim support and citation completeness must be backend verification
    results, not values copied from an LLM response. Source status must come
    from the backend's existing source-status inspector.

    The source-matched tier is unavailable unless both policy approval and an
    explicit feature enablement are supplied by trusted server configuration.
    This does not authorize enabling it in production.
    """
    if not isinstance(sources, Sequence) or isinstance(sources, (str, bytes)):
        return {"trust_tier": TIER_UNREVIEWED, "reason_codes": ["sources_invalid"]}
    if not sources:
        return {"trust_tier": TIER_UNREVIEWED, "reason_codes": ["sources_missing"]}

    normalized = []
    seen_source_ids = set()
    for source in sources:
        if not isinstance(source, Mapping):
            return {"trust_tier": TIER_UNREVIEWED, "reason_codes": ["source_record_invalid"]}
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            return {"trust_tier": TIER_UNREVIEWED, "reason_codes": ["source_id_missing"]}
        if source_id in seen_source_ids:
            return {"trust_tier": TIER_UNREVIEWED, "reason_codes": ["duplicate_source_id"]}
        seen_source_ids.add(source_id)
        normalized.append(source)

    if claims_supported is not True:
        return {"trust_tier": TIER_UNREVIEWED, "reason_codes": ["claims_not_verified_supported"]}
    if citations_complete is not True:
        return {"trust_tier": TIER_UNREVIEWED, "reason_codes": ["citations_incomplete"]}
    if contradictory_sources is not False:
        return {"trust_tier": TIER_UNREVIEWED, "reason_codes": ["contradictory_sources_unresolved"]}

    statuses = [source.get("source_status") for source in normalized]
    if all(status == "verified_operative_text" for status in statuses):
        return {"trust_tier": TIER_VERIFIED, "reason_codes": []}

    if any(status == "verified_operative_text" for status in statuses):
        return {"trust_tier": TIER_UNREVIEWED, "reason_codes": ["mixed_source_statuses"]}

    if source_matched_policy_approved is not True:
        return {"trust_tier": TIER_UNREVIEWED, "reason_codes": ["source_matched_policy_not_approved"]}
    if source_matched_feature_enabled is not True:
        return {"trust_tier": TIER_UNREVIEWED, "reason_codes": ["source_matched_feature_disabled"]}

    if all(
        source.get("source_status") == "source_matched_unreviewed"
        and _source_matched_evidence_ready(source)
        for source in normalized
    ):
        return {"trust_tier": TIER_SOURCE_MATCHED, "reason_codes": ["not_lawyer_reviewed"]}

    return {"trust_tier": TIER_UNREVIEWED, "reason_codes": ["source_evidence_incomplete"]}
