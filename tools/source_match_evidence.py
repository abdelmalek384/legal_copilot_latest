"""Read exact-version source-match evidence from the shared legal corpus."""
from __future__ import annotations


def load_source_match_evidence(connection, version_id, source_id):
    """Return the latest packet only when it matches the exact registry row.

    This read-only adapter never synthesizes evidence, grants permissions, or
    changes verification state. Missing/mismatched records return None.
    """
    if (isinstance(version_id, bool) or not isinstance(version_id, int)
            or version_id <= 0 or not isinstance(source_id, str)
            or not source_id or source_id != source_id.strip()):
        return None

    cursor = connection.execute(
        """
        SELECT e.*, d.source_id AS registry_source_id,
               v.publication_date AS registry_publication_date,
               v.effective_date AS registry_effective_date,
               v.original_sha256 AS registry_original_sha256
        FROM legal_source_match_evidence e
        JOIN legal_document_versions v ON v.version_id=e.version_id
        JOIN legal_documents d ON d.document_id=v.document_id
        WHERE e.version_id=? AND e.source_id=? AND d.source_id=e.source_id
        ORDER BY e.evidence_revision DESC, e.evidence_id DESC
        LIMIT 1
        """,
        (version_id, source_id),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    record = dict(zip((column[0] for column in cursor.description), row))

    if (record.get("registry_source_id") != source_id
            or record.get("registry_publication_date") != record.get("publication_date")
            or record.get("registry_effective_date") != record.get("effective_date")
            or not isinstance(record.get("registry_original_sha256"), str)
            or record.get("registry_original_sha256", "").lower()
                != str(record.get("original_capture_sha256", "")).lower()):
        return None

    uses_cursor = connection.execute(
        """
        SELECT approved_use
        FROM legal_source_match_evidence_uses
        WHERE evidence_id=?
        ORDER BY approved_use
        """,
        (record["evidence_id"],),
    )
    approved_uses = [row[0] for row in uses_cursor.fetchall()]
    if (any(not isinstance(value, str) for value in approved_uses)
            or (approved_uses and not bool(record.get("reuse_rights_allowed")))):
        # Defend the read boundary as well as the insert trigger: legacy or
        # manually altered databases must never expose uses without affirmative rights.
        return None

    return {
        "validator_passed": bool(record["validator_passed"]),
        "original_capture_sha256": record["original_capture_sha256"],
        "independent_copy_source_id": record["independent_copy_source_id"],
        "independent_copy_sha256": record["independent_copy_sha256"],
        "publication_date": record["publication_date"],
        "effective_date": record["effective_date"],
        "reuse_rights_evidence": record["reuse_rights_evidence"],
        "reuse_rights_evidence_url": record["reuse_rights_evidence_url"],
        "approved_uses": approved_uses,
        "article_inventory_complete": bool(record["article_inventory_complete"]),
        "differences_resolved_against_primary": bool(record["differences_resolved_against_primary"]),
        "publication_and_effective_dates_verified": bool(record["publication_and_effective_dates_verified"]),
        "reuse_rights_allowed": bool(record["reuse_rights_allowed"]),
        "evidence_revision": record["evidence_revision"],
        "recorded_at": record["recorded_at"],
    }
