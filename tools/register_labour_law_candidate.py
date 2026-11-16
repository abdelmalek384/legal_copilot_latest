"""Register Labour Law 14/2025 as a pending versioned-source candidate.

This writes registry metadata and pending review events only. It never imports article
chunks, trusts supplied verified/in_force flags, or marks the law as current/verified.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import json
import os
import stat
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORD = ROOT / "data" / "candidates" / "labour_law_14_2025" / "registry_candidate.json"


class DuplicateJSONKeyError(ValueError):
    pass


def _reject_duplicate_json_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_candidate_record(path: Path) -> dict:
    """Read candidate input as a bounded regular file; reject links and ambiguous JSON."""
    try:
        before = Path(path).lstat()
        if not stat.S_ISREG(before.st_mode) or before.st_size > 1024 * 1024:
            raise ValueError("candidate record must be a regular file no larger than 1 MiB")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if (not stat.S_ISREG(opened.st_mode)
                    or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)):
                raise ValueError("candidate record changed identity while opening")
            raw = stream.read(1024 * 1024 + 1)
            after = os.fstat(stream.fileno())
            if len(raw) > 1024 * 1024 or len(raw) != after.st_size:
                raise ValueError("candidate record changed or exceeds 1 MiB")
            if (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns) != (after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise ValueError("candidate record changed while being read")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_json_keys)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateJSONKeyError, ValueError) as exc:
        raise ValueError("candidate record is unreadable, ambiguous, or unsafe") from exc
    if not isinstance(value, dict):
        raise ValueError("candidate record root must be a JSON object")
    return value

SENSITIVE_QUERY_KEYS = {
    "token", "access_token", "auth", "authorization", "password", "secret",
    "signature", "sig", "api_key", "apikey", "session", "sessionid",
    "credential", "api-key", "auth_token", "session_token",
    "awsaccesskeyid", "googleaccessid", "key-pair-id",
    "x-amz-signature", "x-amz-credential", "x-amz-security-token",
    "x-amz-algorithm", "x-amz-date", "x-amz-expires", "x-amz-signedheaders",
    "x-goog-signature", "x-goog-credential", "x-goog-algorithm",
    "x-goog-date", "x-goog-expires", "x-goog-signedheaders",
}


def _valid_https_url(value: object) -> bool:
    if (not isinstance(value, str) or not value or value != value.strip()
            or "\\" in value or "#" in value
            or any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in value)):
        return False
    try:
        parsed = urlsplit(value)
        port = parsed.port
        query_keys = {
            key.casefold() for key, _ in parse_qsl(parsed.query, keep_blank_values=True)
        }
        return (
            parsed.scheme.lower() == "https" and bool(parsed.hostname)
            and parsed.username is None and parsed.password is None
            and not parsed.netloc.endswith(":")
            and (port is None or 1 <= port <= 65535)
            and not (query_keys & SENSITIVE_QUERY_KEYS)
        )
    except (TypeError, ValueError):
        return False


def register(db, record):
    """Idempotently insert candidate source/document/version metadata."""
    sources = record["sources"]
    if not isinstance(sources, list) or not sources:
        raise ValueError("candidate record must contain a non-empty source list")
    source_by_id = {}
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("candidate source entries must be objects")
        for field in (
            "source_id", "authority", "source_page", "access_status",
            "collection_permission", "commercial_reuse_permission",
        ):
            if not isinstance(source.get(field), str) or not source[field].strip():
                raise ValueError(f"candidate source {field} must be a non-empty string")
        source_id = source["source_id"]
        if (source_id != source_id.strip()
                or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", source_id)
                or source_id in source_by_id):
            raise ValueError("candidate source IDs must be unique valid non-empty identifiers")
        if not _valid_https_url(source.get("source_page")):
            raise ValueError("candidate source_page must be a clean HTTPS URL")
        terms_url = source.get("terms_url")
        if terms_url is not None and not _valid_https_url(terms_url):
            raise ValueError("candidate terms_url must be a clean HTTPS URL or null")
        source_by_id[source_id] = source
    document_input = record.get("document")
    if not isinstance(document_input, dict):
        raise ValueError("candidate document must be an object")
    for field in ("document_id", "official_title", "document_type", "source_id"):
        if not isinstance(document_input.get(field), str) or not document_input[field].strip():
            raise ValueError(f"candidate document {field} must be a non-empty string")
        if any(ord(char) < 32 or ord(char) == 127 for char in document_input[field]):
            raise ValueError(f"candidate document {field} must not contain control characters")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", document_input["document_id"]):
        raise ValueError("candidate document_id must be a valid identifier")
    document_source_id = document_input.get("source_id")
    if not isinstance(document_source_id, str) or document_source_id not in source_by_id:
        raise ValueError("candidate document source_id must reference a listed source")
    version_input = record.get("version")
    if not isinstance(version_input, dict):
        raise ValueError("candidate version must be an object")
    if (not isinstance(version_input.get("version_label"), str)
            or not version_input["version_label"].strip()
            or version_input["version_label"] != version_input["version_label"].strip()):
        raise ValueError("candidate version_label must be a trimmed non-empty string")
    if not _valid_https_url(version_input.get("source_url")):
        raise ValueError("candidate version source_url must be a clean HTTPS URL")
    for field in ("publication_date", "effective_date", "repeal_date", "consolidated_as_of"):
        value = version_input.get(field)
        if value is not None:
            try:
                if not isinstance(value, str) or dt.date.fromisoformat(value).isoformat() != value:
                    raise ValueError
            except ValueError as exc:
                raise ValueError(f"candidate version {field} must be an ISO YYYY-MM-DD date or null") from exc
    original_sha256 = version_input.get("original_sha256")
    if original_sha256 is not None and (
        not isinstance(original_sha256, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", original_sha256)
    ):
        raise ValueError("candidate original_sha256 must be a 64-character SHA-256 or null")
    version_host = urlsplit(version_input["source_url"]).hostname.casefold()
    document_source_host = urlsplit(source_by_id[document_source_id]["source_page"]).hostname.casefold()
    if version_host != document_source_host:
        raise ValueError("candidate version source_url host must match the document source")
    reviews = record.get("reviews", [])
    if not isinstance(reviews, list):
        raise ValueError("candidate reviews must be a list")
    allowed_review_types = {
        "source_authenticity", "extraction_quality", "legal_status",
        "amendment_history", "licensing", "lawyer_approval",
    }
    seen_review_types = set()
    for event in reviews:
        if not isinstance(event, dict):
            raise ValueError("candidate review events must be objects")
        review_type = event.get("review_type")
        if (not isinstance(review_type, str)
                or review_type not in allowed_review_types
                or review_type in seen_review_types):
            raise ValueError("candidate review_type values must be unique supported review types")
        seen_review_types.add(review_type)
        if not isinstance(event.get("notes"), str) or not event["notes"].strip():
            raise ValueError("candidate review notes must be a non-empty string")
        evidence_url = event.get("evidence_url")
        if evidence_url is not None and not _valid_https_url(evidence_url):
            raise ValueError("candidate review evidence_url must be a clean HTTPS URL or null")
    # Candidate JSON is not a permission authority. Permission grants must be
    # recorded through the canonical source-permission review workflow.
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("candidate source entries must be objects")
        collection_permission = source.get("collection_permission", "unknown")
        commercial_permission = source.get("commercial_reuse_permission", "unknown")
        if not isinstance(collection_permission, str) or not collection_permission.strip():
            raise ValueError("candidate collection_permission must be a non-empty string")
        if not isinstance(commercial_permission, str) or not commercial_permission.strip():
            raise ValueError("candidate commercial_reuse_permission must be a non-empty string")
        if collection_permission in ("allowed", "allowed_limited"):
            raise ValueError("candidate registration cannot grant collection permission; use the canonical source-permission register")
        if commercial_permission in ("allowed", "allowed_limited"):
            raise ValueError("candidate registration cannot grant commercial reuse permission; use the canonical source-permission register")
    db.execute("SAVEPOINT candidate_registration")
    try:
        for source in sources:
            existing = db.execute(
                "SELECT authority,source_page FROM legal_sources WHERE source_id=?",
                (source["source_id"],),
            ).fetchone()
            expected = (source["authority"], source["source_page"])
            if existing is None:
                db.execute(
                    """INSERT INTO legal_sources
                       (source_id,authority,source_page,access_status,collection_permission,
                        commercial_reuse_permission,terms_url,terms_checked_on,permission_evidence)
                       VALUES(?,?,?,?,?,?,?,?,?)""",
                    (
                        source["source_id"], source["authority"], source["source_page"],
                        source["access_status"], source["collection_permission"],
                        source["commercial_reuse_permission"], source.get("terms_url"),
                        source.get("terms_checked_on"), source.get("permission_evidence"),
                    ),
                )
            elif tuple(existing) != expected:
                raise ValueError("Existing source metadata conflicts with candidate: " + source["source_id"])
    
        doc = record["document"]
        existing_doc = db.execute(
            "SELECT source_id,official_title,document_type FROM legal_documents WHERE document_id=?",
            (doc["document_id"],),
        ).fetchone()
        expected_doc = (doc["source_id"], doc["official_title"], doc["document_type"])
        if existing_doc is None:
            db.execute(
                """INSERT INTO legal_documents
                   (document_id,source_id,official_title,document_type,law_number,law_year,language)
                   VALUES(?,?,?,?,?,?,?)""",
                (doc["document_id"], doc["source_id"], doc["official_title"], doc["document_type"],
                 doc.get("law_number"), doc.get("law_year"), doc.get("language", "ar")),
            )
        elif tuple(existing_doc) != expected_doc:
            raise ValueError("Existing document metadata conflicts with candidate: " + doc["document_id"])
    
        version = record["version"]
        existing_version = db.execute(
            """SELECT version_id,source_url,publication_date,effective_date,legal_status,review_status
               FROM legal_document_versions WHERE document_id=? AND version_label=?""",
            (doc["document_id"], version["version_label"]),
        ).fetchone()
        if existing_version is None:
            cur = db.execute(
                """INSERT INTO legal_document_versions
                   (document_id,version_label,source_url,original_path,original_sha256,retrieved_at,
                    publication_date,effective_date,repeal_date,consolidated_as_of,gazette_issue,gazette_pages,
                    legal_status,review_status,authenticity_verified,status_verified,amendment_history_verified,
                    permission_evidence,notes)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    doc["document_id"], version["version_label"], version["source_url"],
                    version.get("original_path"), version.get("original_sha256"), version.get("retrieved_at"),
                    version.get("publication_date"), version.get("effective_date"), version.get("repeal_date"),
                    version.get("consolidated_as_of"), version.get("gazette_issue"), version.get("gazette_pages"),
                    "under_review", "pending_source_review", 0, 0, 0,
                    version.get("permission_evidence"), version.get("notes"),
                ),
            )
            version_id = cur.lastrowid
        else:
            version_id = existing_version["version_id"]
            if (existing_version["source_url"], existing_version["publication_date"],
                existing_version["effective_date"]) != (
                version["source_url"], version.get("publication_date"), version.get("effective_date")
            ):
                raise ValueError("Existing version metadata conflicts with candidate.")
            # Never reset or overwrite existing review decisions.
        for event in record.get("reviews", []):
            found = db.execute(
                """SELECT 1 FROM legal_review_events
                   WHERE version_id=? AND review_type=? AND outcome='pending' LIMIT 1""",
                (version_id, event["review_type"]),
            ).fetchone()
            if not found:
                db.execute(
                    """INSERT INTO legal_review_events
                       (version_id,reviewer,review_type,outcome,notes,evidence_url)
                       VALUES(?,?,?,?,?,?)""",
                    (version_id, "candidate-registration-tool", event["review_type"], "pending",
                     event["notes"], event.get("evidence_url")),
                )
    
        db.execute("RELEASE SAVEPOINT candidate_registration")
    except Exception:
        db.execute("ROLLBACK TO SAVEPOINT candidate_registration")
        db.execute("RELEASE SAVEPOINT candidate_registration")
        raise
    chunk_count = db.execute(
        "SELECT COUNT(*) FROM chunks WHERE document_version_id=?", (version_id,)
    ).fetchone()[0]
    row = db.execute(
        """SELECT legal_status,review_status,authenticity_verified,status_verified,
                  amendment_history_verified
           FROM legal_document_versions WHERE version_id=?""",
        (version_id,),
    ).fetchone()
    return {"version_id": version_id, "version_state": dict(row), "linked_chunk_count": chunk_count}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", default=str(DEFAULT_RECORD), help="Candidate registry JSON")
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT))
    import app

    required = ("COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB")
    missing = [name for name in required if not os.environ.get(name, "").strip()]
    if missing or os.environ.get("COPILOT_DB", "").strip():
        parser.error(
            "profile-separated corpus paths are required and COPILOT_DB must be unset"
            + (": missing " + ", ".join(missing) if missing else "")
        )

    try:
        record = load_candidate_record(Path(args.record))
    except ValueError as exc:
        parser.error(str(exc))
    db = app.corpus_conn()
    try:
        result = register(db, record)
        print(json.dumps({
            "registered": True,
            "document_id": record["document"]["document_id"],
            **result,
            "search_eligible": False,
            "article_chunks_imported": 0,
        }, ensure_ascii=False, indent=2))
    finally:
        app.get_database_runtime().close_current_thread()


if __name__ == "__main__":
    main()
