#!/usr/bin/env python3
"""Read-only audit of Legal Copilot's SQLite legal corpus."""
from __future__ import annotations
import argparse, hashlib, json, os, re, sqlite3
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

REGISTRY_TABLES = {"legal_sources","legal_documents","legal_document_versions","legal_version_relations","legal_review_events"}

def table_names(db):
    return {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
def columns(db, table):
    return {r[1] for r in db.execute(f"PRAGMA table_info({table})")}
def count(db, table):
    return db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]

def valid_evidence_url(value):
    """Check URL shape only; an HTTPS URL is not proof that its content is authoritative."""
    if not isinstance(value, str) or not value or value != value.strip():
        return False
    if any(ch.isspace() or ord(ch) < 32 for ch in value):
        return False
    try:
        parsed = urlparse(value)
        port = parsed.port  # Forces urllib to reject malformed and out-of-range ports.
        return (
            parsed.scheme.lower() == "https"
            and bool(parsed.hostname)
            and parsed.username is None
            and parsed.password is None
            and not parsed.netloc.endswith(":")
            and (port is None or 1 <= port <= 65535)
        )
    except (ValueError, TypeError):
        return False

def valid_sha256(value):
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in value)

def valid_iso_date(value):
    if not isinstance(value, str) or len(value) != 10 or value[4:5] != "-" or value[7:8] != "-":
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False

def parse_reviewed_at(value):
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def existing_sqlite_sidecars(db_path: Path):
    sidecars = {}
    for suffix in ("-wal", "-journal"):
        path = Path(str(db_path) + suffix)
        if path.is_file():
            sidecars[path.name] = {"sha256": sha256_file(path), "size_bytes": path.stat().st_size}
    return sidecars

def audit(db_path: Path, *, check_fts_index: bool = False):
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    db = sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        db.execute("BEGIN")  # Pin all audit queries to one read-only SQLite snapshot.
        sidecars = existing_sqlite_sidecars(db_path)
        tables = table_names(db)
        if "database_profile" not in tables:
            raise ValueError("database is not bound to the legal_corpus profile")
        profile_rows = db.execute(
            "SELECT profile FROM database_profile WHERE singleton=1"
        ).fetchall()
        if len(profile_rows) != 1 or profile_rows[0]["profile"] != "legal_corpus":
            raise ValueError("database is not bound to the legal_corpus profile")
        integrity_messages = [str(row[0]) for row in db.execute("PRAGMA integrity_check(100)").fetchall()]
        foreign_key_violation_count = 0
        foreign_key_violations = []
        for row in db.execute("PRAGMA foreign_key_check"):
            foreign_key_violation_count += 1
            if len(foreign_key_violations) < 100:
                foreign_key_violations.append(
                    {"table": row[0], "rowid": row[1], "parent_table": row[2], "fk_index": row[3]}
                )
        result = {
            "report_type":"legal_corpus_audit",
            "generated_at":datetime.now(timezone.utc).isoformat(),
            "database_path":str(db_path),
            "database_sha256":sha256_file(db_path),
            "sqlite_sidecars":sidecars,
            "read_only":True, "counts":{}, "issues":[],
            "sqlite_integrity_check": integrity_messages,
            "foreign_key_violation_count": foreign_key_violation_count,
            "foreign_key_violations": foreign_key_violations,
            "notes":["Metadata audit only; does not establish legal correctness.",
                     "Missing dates are unknown, not evidence that a law is in force.",
                     "This audit never promotes records to verified.",
                     "database_sha256 hashes the main database file; WAL/journal sidecar hashes are listed separately when present.",
                     "Database queries run in one read-only SQLite transaction; file hashes are provenance metadata, not an atomic filesystem snapshot."]
        }
        if integrity_messages != ["ok"]:
            result["issues"].append({
                "severity": "high",
                "code": "sqlite_integrity_check_failed",
                "detail": integrity_messages[:20],
            })
        if foreign_key_violation_count:
            result["issues"].append({
                "severity": "high",
                "code": "sqlite_foreign_key_violations",
                "count": foreign_key_violation_count,
                "detail": "Only the first 100 structural violation descriptors are included.",
            })
        for table in ("chunks","legal_sources","legal_documents","legal_document_versions","legal_version_relations","legal_review_events"):
            if table in tables: result["counts"][table] = count(db,table)
        if "legal_review_events" in tables:
            event_cols = columns(db, "legal_review_events")
            event_required = {"review_event_id", "version_id", "reviewer", "review_type", "outcome", "evidence_url", "reviewed_at"}
            if event_required - event_cols:
                result["issues"].append({"severity": "high", "code": "review_event_columns_missing", "detail": str(sorted(event_required - event_cols))})
            else:
                notes_select = "notes" if "notes" in event_cols else "NULL AS notes"
                events = db.execute(f"SELECT review_event_id, version_id, reviewer, review_type, outcome, evidence_url, reviewed_at, {notes_select} FROM legal_review_events").fetchall()
                allowed_types = {"source_authenticity", "extraction_quality", "legal_status", "amendment_history", "licensing", "lawyer_approval"}
                allowed_outcomes = {"pending", "pass", "fail", "needs_correction"}
                quality = {"reviewer_missing": 0, "invalid_review_type": 0, "invalid_review_outcome": 0, "reviewed_at_invalid": 0, "reviewed_at_in_future": 0, "passing_event_without_valid_evidence": 0, "lawyer_approval_without_counsel_attestation": 0, "orphan_version": 0}
                now = datetime.now(timezone.utc)
                version_ids = None
                if "legal_document_versions" in tables and "version_id" in columns(db, "legal_document_versions"):
                    version_ids = {row[0] for row in db.execute("SELECT version_id FROM legal_document_versions")}
                for event in events:
                    quality["reviewer_missing"] += int(not isinstance(event["reviewer"], str) or not event["reviewer"].strip())
                    quality["invalid_review_type"] += int(event["review_type"] not in allowed_types)
                    quality["invalid_review_outcome"] += int(event["outcome"] not in allowed_outcomes)
                    reviewed_at = parse_reviewed_at(event["reviewed_at"])
                    quality["reviewed_at_invalid"] += int(reviewed_at is None)
                    quality["reviewed_at_in_future"] += int(reviewed_at is not None and reviewed_at > now)
                    if event["outcome"] == "pass" and not valid_evidence_url(event["evidence_url"]):
                        quality["passing_event_without_valid_evidence"] += 1
                    if event["review_type"] == "lawyer_approval" and event["outcome"] == "pass":
                        notes = event["notes"]
                        if not isinstance(notes, str) or not re.search(
                            r"\\[qualified_egyptian_counsel_attested:user_id=[1-9][0-9]*\\]", notes
                        ):
                            quality["lawyer_approval_without_counsel_attestation"] += 1
                    if version_ids is not None and event["version_id"] not in version_ids:
                        quality["orphan_version"] += 1
                result["review_event_quality"] = quality
                for key, value in quality.items():
                    if value:
                        result["issues"].append({"severity": "high", "code": "review_events_" + key, "count": value, "detail": "Review events are audit evidence; malformed, future-dated, unsupported, or orphaned events must be corrected before relying on them."})
        missing = sorted(REGISTRY_TABLES-tables)
        if missing:
            result["issues"].append({"severity":"high","code":"registry_tables_missing","detail":", ".join(missing)})
        if "chunks" in tables:
            cc=columns(db,"chunks")
            needed={"ref","article","text","source","verified","in_force"}
            if needed-cc:
                result["issues"].append({"severity":"high","code":"chunk_columns_missing","detail":str(sorted(needed-cc))})
            else:
                chunk_scope = "case_id IS NULL AND " if "case_id" in cc else ""
                q={
                  "missing_source":db.execute(f"SELECT COUNT(*) FROM chunks WHERE {chunk_scope}(source IS NULL OR trim(source)='')").fetchone()[0],
                  "empty_text":db.execute(f"SELECT COUNT(*) FROM chunks WHERE {chunk_scope}(text IS NULL OR trim(text)='')").fetchone()[0],
                  "unverified":db.execute(f"SELECT COUNT(*) FROM chunks WHERE {chunk_scope}COALESCE(verified,0)=0").fetchone()[0],
                  "marked_in_force_but_unverified":db.execute(f"SELECT COUNT(*) FROM chunks WHERE {chunk_scope}COALESCE(in_force,0)=1 AND COALESCE(verified,0)=0").fetchone()[0],
                  "no_article_number":db.execute(f"SELECT COUNT(*) FROM chunks WHERE {chunk_scope}(article IS NULL OR trim(article)='')").fetchone()[0],
                  "unlinked_to_version":db.execute(f"SELECT COUNT(*) FROM chunks WHERE {chunk_scope}document_version_id IS NULL").fetchone()[0] if "document_version_id" in cc else None
                }
                result["chunk_quality"]=q
                for key,sev in (("missing_source","high"),("empty_text","high"),("unverified","medium"),("marked_in_force_but_unverified","high"),("no_article_number","medium"),("unlinked_to_version","high")):
                    if q.get(key): result["issues"].append({"severity":sev,"code":"chunks_"+key,"count":q[key]})
        if "legal_sources" in tables:
            sc = columns(db, "legal_sources")
            if "collection_permission" in sc:
                result["source_permissions"] = dict(db.execute("SELECT COALESCE(collection_permission,'unknown'),COUNT(*) FROM legal_sources GROUP BY collection_permission").fetchall())
                unresolved = sum(n for status, n in result["source_permissions"].items() if status in ("unknown", ""))
                if unresolved:
                    result["issues"].append({"severity":"high","code":"source_permission_unknown","count":unresolved})
                if result["source_permissions"].get("prohibited", 0):
                    result["issues"].append({"severity":"high","code":"source_collection_prohibited","count":result["source_permissions"]["prohibited"],"detail":"Confirm prohibited sources are not used for ingestion or retrieval."})
            if "commercial_reuse_permission" in sc:
                result["commercial_reuse_permissions"] = dict(db.execute("SELECT COALESCE(commercial_reuse_permission,'unknown'),COUNT(*) FROM legal_sources GROUP BY commercial_reuse_permission").fetchall())
                unknown_commercial = sum(n for status, n in result["commercial_reuse_permissions"].items() if status.lower() in ("unknown", ""))
                if unknown_commercial:
                    result["issues"].append({"severity":"high","code":"source_commercial_reuse_permission_unknown","count":unknown_commercial,"detail":"Public accessibility alone does not establish commercial reuse permission."})
            if {"source_id", "collection_permission", "permission_evidence"}.issubset(sc):
                missing_permission_evidence = db.execute(
                    "SELECT COUNT(*) FROM legal_sources WHERE collection_permission IN ('allowed','allowed_limited') AND (permission_evidence IS NULL OR trim(permission_evidence)='')"
                ).fetchone()[0]
                if missing_permission_evidence:
                    result["issues"].append({"severity":"high","code":"source_allowed_without_permission_evidence","count":missing_permission_evidence})
            if {"commercial_reuse_permission", "permission_evidence"}.issubset(sc):
                missing_commercial_evidence = db.execute(
                    "SELECT COUNT(*) FROM legal_sources WHERE lower(trim(COALESCE(commercial_reuse_permission,'unknown'))) IN ('allowed','allowed_limited') AND (permission_evidence IS NULL OR trim(permission_evidence)='')"
                ).fetchone()[0]
                if missing_commercial_evidence:
                    result["issues"].append({"severity":"high","code":"source_commercial_reuse_allowed_without_evidence","count":missing_commercial_evidence,"detail":"A recorded permission label is not self-authenticating; retain the evidence that supports commercial reuse."})
            if {"terms_url"}.issubset(sc):
                invalid_terms = sum(not valid_evidence_url(row[0]) for row in db.execute("SELECT terms_url FROM legal_sources WHERE terms_url IS NOT NULL AND trim(terms_url)!=''").fetchall())
                if invalid_terms:
                    result["issues"].append({"severity":"medium","code":"source_terms_url_not_https","count":invalid_terms})
            if "source_page" in sc:
                missing_source_pages = db.execute("SELECT COUNT(*) FROM legal_sources WHERE source_page IS NULL OR trim(source_page)=''").fetchone()[0]
                invalid_source_pages = sum(not valid_evidence_url(row[0]) for row in db.execute("SELECT source_page FROM legal_sources WHERE source_page IS NOT NULL AND trim(source_page)!=''").fetchall())
                if missing_source_pages:
                    result["issues"].append({"severity":"high","code":"source_page_missing","count":missing_source_pages})
                if invalid_source_pages:
                    result["issues"].append({"severity":"high","code":"source_page_not_https","count":invalid_source_pages})
            if "terms_checked_on" in sc:
                checked_columns = [name for name in ("collection_permission", "commercial_reuse_permission") if name in sc]
                allowed_predicates = [f"lower(trim(COALESCE({name},'unknown'))) IN ('allowed','allowed_limited')" for name in checked_columns]
                if allowed_predicates:
                    allowed_where = " OR ".join(allowed_predicates)
                    missing_terms_dates = db.execute(
                        f"SELECT COUNT(*) FROM legal_sources WHERE ({allowed_where}) AND (terms_checked_on IS NULL OR trim(terms_checked_on)='')"
                    ).fetchone()[0]
                    invalid_terms_dates = sum(not valid_iso_date(row[0]) for row in db.execute(
                        f"SELECT terms_checked_on FROM legal_sources WHERE ({allowed_where}) AND terms_checked_on IS NOT NULL AND trim(terms_checked_on)!=''"
                    ).fetchall())
                    if missing_terms_dates:
                        result["issues"].append({"severity":"high","code":"source_permission_terms_check_date_missing","count":missing_terms_dates})
                    if invalid_terms_dates:
                        result["issues"].append({"severity":"high","code":"source_permission_terms_check_date_invalid","count":invalid_terms_dates})
                    future_terms_dates = sum(
                        valid_iso_date(row[0]) and date.fromisoformat(row[0]) > datetime.now(timezone.utc).date()
                        for row in db.execute(
                            f"SELECT terms_checked_on FROM legal_sources WHERE ({allowed_where}) AND terms_checked_on IS NOT NULL AND trim(terms_checked_on)!=''"
                        ).fetchall()
                    )
                    if future_terms_dates:
                        result["issues"].append({"severity":"high","code":"source_permission_terms_check_date_in_future","count":future_terms_dates,"detail":"A future date cannot evidence a completed permission-terms review."})
        if "legal_document_versions" in tables:
            vc=columns(db,"legal_document_versions")
            required={"source_url","original_path","original_sha256","publication_date","effective_date","repeal_date","legal_status","review_status","authenticity_verified","status_verified","amendment_history_verified"}
            if required-vc:
                result["issues"].append({"severity":"high","code":"version_columns_missing","detail":str(sorted(required-vc))})
            else:
                q={
                  "missing_hash":db.execute("SELECT COUNT(*) FROM legal_document_versions WHERE original_sha256 IS NULL OR trim(original_sha256)=''").fetchone()[0],
                  "missing_original_path":db.execute("SELECT COUNT(*) FROM legal_document_versions WHERE original_path IS NULL OR trim(original_path)=''").fetchone()[0],
                  "missing_publication_date":db.execute("SELECT COUNT(*) FROM legal_document_versions WHERE publication_date IS NULL OR trim(publication_date)=''").fetchone()[0],
                  "missing_effective_date":db.execute("SELECT COUNT(*) FROM legal_document_versions WHERE effective_date IS NULL OR trim(effective_date)=''").fetchone()[0],
                  "unknown_legal_status":db.execute("SELECT COUNT(*) FROM legal_document_versions WHERE legal_status='unknown'").fetchone()[0],
                  "not_verified":db.execute("SELECT COUNT(*) FROM legal_document_versions WHERE review_status!='verified' OR authenticity_verified!=1 OR status_verified!=1").fetchone()[0],
                  "amendment_history_unverified":db.execute("SELECT COUNT(*) FROM legal_document_versions WHERE amendment_history_verified!=1").fetchone()[0]
                }
                q["malformed_sha256"] = sum(not valid_sha256(row[0]) for row in db.execute(
                    "SELECT original_sha256 FROM legal_document_versions WHERE original_sha256 IS NOT NULL AND trim(original_sha256)!=''"
                ).fetchall())
                q["invalid_source_url"] = sum(not valid_evidence_url(row[0]) for row in db.execute(
                    "SELECT source_url FROM legal_document_versions WHERE source_url IS NOT NULL AND trim(source_url)!=''"
                ).fetchall())
                date_columns = [name for name in ("publication_date", "effective_date", "repeal_date", "consolidated_as_of") if name in vc]
                malformed_dates = 0
                repeal_before_effective = 0
                for version in db.execute("SELECT " + ",".join(date_columns) + " FROM legal_document_versions").fetchall():
                    values = dict(zip(date_columns, version))
                    malformed_dates += sum(value is not None and str(value).strip() != "" and not valid_iso_date(value) for value in values.values())
                    effective = values.get("effective_date")
                    repeal = values.get("repeal_date")
                    if valid_iso_date(effective) and valid_iso_date(repeal) and date.fromisoformat(repeal) < date.fromisoformat(effective):
                        repeal_before_effective += 1
                q["malformed_dates"] = malformed_dates
                q["repeal_before_effective_date"] = repeal_before_effective
                today = datetime.now(timezone.utc).date()
                q["in_force_before_effective_date"] = 0
                q["in_force_after_repeal_date"] = 0
                q["repealed_without_repeal_date"] = 0
                if {"legal_status", "effective_date", "repeal_date"}.issubset(vc):
                    for version in db.execute("SELECT legal_status, effective_date, repeal_date FROM legal_document_versions").fetchall():
                        status = str(version[0] or "").strip().lower()
                        effective = version[1]
                        repeal = version[2]
                        if status == "in_force" and valid_iso_date(effective) and date.fromisoformat(effective) > today:
                            q["in_force_before_effective_date"] += 1
                        if status == "in_force" and valid_iso_date(repeal) and date.fromisoformat(repeal) < today:
                            q["in_force_after_repeal_date"] += 1
                        if status == "repealed" and not valid_iso_date(repeal):
                            q["repealed_without_repeal_date"] += 1
                result["version_quality"]=q
                for key in q:
                    if q[key]: result["issues"].append({"severity":"high" if key in ("not_verified","unknown_legal_status","malformed_sha256","invalid_source_url","malformed_dates","repeal_before_effective_date","in_force_before_effective_date","in_force_after_repeal_date","repealed_without_repeal_date") else "medium","code":"versions_"+key,"count":q[key]})

                # Amendment-history assertions need evidence, not just a boolean flag.
                vc_required = {"version_id", "legal_status", "review_status", "amendment_history_verified"}
                if vc_required.issubset(vc):
                    q["verified_in_force_without_amendment_history_review"] = db.execute(
                        "SELECT COUNT(*) FROM legal_document_versions WHERE legal_status='in_force' "
                        "AND review_status='verified' AND amendment_history_verified!=1"
                    ).fetchone()[0]
                    if q["verified_in_force_without_amendment_history_review"]:
                        result["issues"].append({
                            "severity":"high",
                            "code":"versions_verified_in_force_without_amendment_history_review",
                            "count":q["verified_in_force_without_amendment_history_review"],
                            "detail":"Current-law candidates need an explicit amendment-history review; this audit does not change their status."
                        })
                if {"version_id", "amendment_history_verified"}.issubset(vc) and "legal_review_events" in tables:
                    rc = columns(db, "legal_review_events")
                    if {"version_id", "review_type", "outcome", "evidence_url"}.issubset(rc):
                        flagged_versions = db.execute(
                            "SELECT version_id FROM legal_document_versions WHERE amendment_history_verified=1"
                        ).fetchall()
                        missing_evidence_count = 0
                        for flagged in flagged_versions:
                            events = db.execute(
                                "SELECT evidence_url FROM legal_review_events "
                                "WHERE version_id=? AND review_type='amendment_history' AND outcome='pass'",
                                (flagged["version_id"],),
                            ).fetchall()
                            if not any(valid_evidence_url(event["evidence_url"]) for event in events):
                                missing_evidence_count += 1
                        q["amendment_history_flag_without_evidence"] = missing_evidence_count
                        if q["amendment_history_flag_without_evidence"]:
                            result["issues"].append({
                                "severity":"high",
                                "code":"versions_amendment_history_flag_without_evidence",
                                "count":q["amendment_history_flag_without_evidence"],
                                "detail":"The flag is set but no passing amendment-history review event with an evidence URL exists."
                            })
                # Verification flags are claims; require corresponding passing review events with direct HTTPS evidence.
                verification_flags = {"authenticity_verified", "status_verified", "review_status"}
                if verification_flags.issubset(vc):
                    needs_auth = db.execute(
                        "SELECT version_id FROM legal_document_versions WHERE authenticity_verified=1"
                    ).fetchall()
                    needs_status = db.execute(
                        "SELECT version_id FROM legal_document_versions WHERE status_verified=1"
                    ).fetchall()
                    needs_lawyer = db.execute(
                        "SELECT version_id FROM legal_document_versions WHERE review_status='verified'"
                    ).fetchall()
                    event_cols = columns(db, "legal_review_events") if "legal_review_events" in tables else set()
                    required_event_cols = {"version_id", "review_type", "outcome", "evidence_url"}
                    if required_event_cols.issubset(event_cols):
                        def has_passing_evidence(version_id, review_type):
                            events = db.execute(
                                "SELECT evidence_url FROM legal_review_events WHERE version_id=? AND review_type=? AND outcome='pass'",
                                (version_id, review_type),
                            ).fetchall()
                            return any(valid_evidence_url(event[0]) for event in events)
                        q["authenticity_flag_without_evidence"] = sum(
                            not has_passing_evidence(row["version_id"], "source_authenticity") for row in needs_auth
                        )
                        q["status_flag_without_evidence"] = sum(
                            not has_passing_evidence(row["version_id"], "legal_status") for row in needs_status
                        )
                        q["verified_status_without_lawyer_approval_event"] = sum(
                            not has_passing_evidence(row["version_id"], "lawyer_approval") for row in needs_lawyer
                        )
                        for key in ("authenticity_flag_without_evidence", "status_flag_without_evidence", "verified_status_without_lawyer_approval_event"):
                            if q[key]:
                                result["issues"].append({
                                    "severity": "high",
                                    "code": "versions_" + key,
                                    "count": q[key],
                                    "detail": "A stored verification flag needs a matching passing review event with a valid HTTPS evidence URL; the audit never promotes a version."
                                })
                    elif needs_auth or needs_status or needs_lawyer:
                        result["issues"].append({
                            "severity": "high",
                            "code": "verification_event_schema_incomplete",
                            "count": len(needs_auth) + len(needs_status) + len(needs_lawyer),
                            "detail": "Verification flags exist but review-event fields needed to audit their evidence are unavailable."
                        })
                result["version_quality"] = q
        if "chunks" in tables and "legal_document_versions" in tables:
            cc = columns(db, "chunks")
            vc = columns(db, "legal_document_versions")
            chunk_required = {"id", "document_version_id", "verified", "in_force"}
            version_required = {"version_id", "review_status", "authenticity_verified", "status_verified", "legal_status", "effective_date", "repeal_date"}
            if chunk_required.issubset(cc) and version_required.issubset(vc):
                today = datetime.now(timezone.utc).date()
                mismatch_verified = 0
                mismatch_in_force = 0
                chunk_scope = "c.case_id IS NULL AND " if "case_id" in cc else ""
                linked_rows = db.execute(
                    "SELECT c.verified, c.in_force, c.document_version_id, v.version_id, "
                    "v.review_status, v.authenticity_verified, v.status_verified, v.legal_status, "
                    "v.effective_date, v.repeal_date "
                    "FROM chunks c LEFT JOIN legal_document_versions v ON v.version_id=c.document_version_id "
                    f"WHERE {chunk_scope}(COALESCE(c.verified,0)=1 OR COALESCE(c.in_force,0)=1)"
                ).fetchall()
                for row in linked_rows:
                    version_missing = row["version_id"] is None
                    if row["verified"] == 1 and (
                        version_missing or row["review_status"] != "verified"
                        or row["authenticity_verified"] != 1 or row["status_verified"] != 1
                    ):
                        mismatch_verified += 1
                    effective = row["effective_date"]
                    repeal = row["repeal_date"]
                    invalid_timing = (
                        valid_iso_date(effective) and date.fromisoformat(effective) > today
                    ) or (
                        valid_iso_date(repeal) and date.fromisoformat(repeal) < today
                    )
                    if row["in_force"] == 1 and (
                        version_missing or row["legal_status"] != "in_force" or invalid_timing
                    ):
                        mismatch_in_force += 1
                result["chunk_version_consistency"] = {
                    "verified_chunks_without_verified_version": mismatch_verified,
                    "in_force_chunks_conflicting_with_version": mismatch_in_force,
                }
                if mismatch_verified:
                    result["issues"].append({
                        "severity": "high", "code": "chunks_verified_without_verified_version",
                        "count": mismatch_verified,
                        "detail": "A global corpus chunk marked verified must link to a version with verified review, authenticity, and legal-status flags."
                    })
                if mismatch_in_force:
                    result["issues"].append({
                        "severity": "high", "code": "chunks_in_force_conflicting_with_version",
                        "count": mismatch_in_force,
                        "detail": "A global corpus chunk marked in force must link to a version currently labelled in force and outside known effective/repeal dates."
                    })
        if "legal_version_relations" in tables:
            relc = columns(db, "legal_version_relations")
            if {"from_version_id", "to_version_id", "relation_type"}.issubset(relc) and "legal_document_versions" in tables:
                q = {
                    "relations_missing_endpoint": db.execute(
                        "SELECT COUNT(*) FROM legal_version_relations r "
                        "LEFT JOIN legal_document_versions f ON f.version_id=r.from_version_id "
                        "LEFT JOIN legal_document_versions t ON t.version_id=r.to_version_id "
                        "WHERE f.version_id IS NULL OR t.version_id IS NULL"
                    ).fetchone()[0],
                    "relations_touching_unreviewed_amendment_history": db.execute(
                        "SELECT COUNT(*) FROM legal_version_relations r "
                        "JOIN legal_document_versions f ON f.version_id=r.from_version_id "
                        "JOIN legal_document_versions t ON t.version_id=r.to_version_id "
                        "WHERE f.amendment_history_verified!=1 OR t.amendment_history_verified!=1"
                    ).fetchone()[0] if "amendment_history_verified" in columns(db, "legal_document_versions") else None
                }
                result["relation_quality"] = q
                if q["relations_missing_endpoint"]:
                    result["issues"].append({"severity":"high","code":"relations_missing_endpoint","count":q["relations_missing_endpoint"]})
                if q["relations_touching_unreviewed_amendment_history"]:
                    result["issues"].append({
                        "severity":"medium",
                        "code":"relations_touching_unreviewed_amendment_history",
                        "count":q["relations_touching_unreviewed_amendment_history"],
                        "detail":"Relation exists in metadata but one or both version histories have not been reviewed."
                    })
        if check_fts_index:
            # This stronger FTS5 index-vs-content check runs on a disposable in-memory
            # backup through the dedicated read-only preflight; it is opt-in because
            # memory use scales with the corpus database size.
            from scripts.chunks_fts_preflight import audit_path as audit_fts_path
            try:
                fts_report = audit_fts_path(db_path)
                result["fts_index_audit"] = {
                    "status": fts_report["status"],
                    "chunks_row_count": fts_report["chunks_row_count"],
                    "fts_row_count": fts_report["fts_row_count"],
                    "finding_count": fts_report["finding_count"],
                    "findings": fts_report["findings"],
                }
                for finding in fts_report["findings"]:
                    result["issues"].append({
                        "severity": finding.get("severity", "high"),
                        "code": "fts_" + str(finding.get("code", "audit_finding")),
                        "count": finding.get("count", 1),
                        "detail": str(finding.get("detail", "FTS index review required"))[:500],
                    })
            except (OSError, sqlite3.Error, ValueError) as exc:
                result["fts_index_audit"] = {"status": "error", "finding_count": 1}
                result["issues"].append({
                    "severity": "high",
                    "code": "fts_index_audit_failed",
                    "detail": str(exc)[:500],
                })
        result["issue_count"]=len(result["issues"])
        result["issue_counts_by_severity"]=dict(Counter(i["severity"] for i in result["issues"]))
        return result
    finally:
        db.close()

def render_markdown(report):
    lines=["# Legal corpus audit","",f"- Generated: {report['generated_at']}","- Database opened read-only: yes",f"- Database main-file SHA-256: {report['database_sha256']}","","## Record counts",""]
    if report["counts"]:
        lines += ["| Table | Rows |","|---|---:|"]+[f"| {k} | {v} |" for k,v in report["counts"].items()]
    else: lines.append("No recognized corpus tables found.")
    if report.get("sqlite_sidecars"):
        lines += ["", "## SQLite sidecars", "", "| File | Size (bytes) | SHA-256 |", "|---|---:|---|"]
        lines += [f"| {name} | {meta['size_bytes']} | {meta['sha256']} |" for name, meta in sorted(report["sqlite_sidecars"].items())]
    for section in ("chunk_quality","source_permissions","commercial_reuse_permissions","version_quality","review_event_quality","chunk_version_consistency","relation_quality"):
        if section in report:
            lines += ["",f"## {section.replace('_',' ').title()}",""]
            lines += [f"- **{k.replace('_',' ')}:** {v}" for k,v in report[section].items()]
    lines += ["","## Issues",""]
    if report["issues"]:
        lines += ["| Severity | Code | Count / details |","|---|---|---|"]
        lines += [f"| {i['severity']} | {i['code']} | {i.get('count',i.get('detail',''))} |" for i in report["issues"]]
    else: lines.append("No metadata-quality issues detected by this audit.")
    lines += ["","## Interpretation","","- Metadata audit only, not legal verification.","- Stored verification flags are reported as stored; evidence is not independently validated.","- Never guess missing dates or permissions.",""]
    return "\n".join(lines)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--db",
        type=Path,
        default=Path(os.environ["COPILOT_CORPUS_DB"]) if os.environ.get("COPILOT_CORPUS_DB", "").strip() else None,
        help="legal-corpus database (defaults to COPILOT_CORPUS_DB)",
    )
    p.add_argument("--out-dir",type=Path,required=True,help="Directory for JSON and Markdown reports")
    p.add_argument("--strict",action="store_true",help="exit non-zero when high-severity metadata issues are found")
    p.add_argument("--check-fts-index",action="store_true",help="run FTS5 index-vs-content integrity checks on a disposable in-memory database copy; memory use scales with database size")
    a=p.parse_args(argv)
    if os.environ.get("COPILOT_DB", "").strip():
        p.error("COPILOT_DB compatibility mode is not supported; configure COPILOT_CORPUS_DB or pass --db")
    if a.db is None:
        p.error("a legal-corpus database is required; configure COPILOT_CORPUS_DB or pass --db")
    try:
        report=audit(a.db, check_fts_index=a.check_fts_index)
    except (FileNotFoundError, sqlite3.Error, ValueError) as exc:
        p.error(str(exc))
    a.out_dir.mkdir(parents=True,exist_ok=True)
    (a.out_dir/"legal_corpus_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    (a.out_dir/"legal_corpus_audit.md").write_text(render_markdown(report),encoding="utf-8")
    print(f"Audited database read-only: {a.db}")
    print(f"Issues: {report['issue_count']} ({report['issue_counts_by_severity']})")
    print(f"Reports: {a.out_dir/'legal_corpus_audit.json'} and {a.out_dir/'legal_corpus_audit.md'}")
    high = report["issue_counts_by_severity"].get("high", 0)
    if a.strict and high:
        print(f"Strict audit failed: {high} high-severity issue(s) remain.")
        return 1
    return 0

if __name__=="__main__": raise SystemExit(main())
