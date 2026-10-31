#!/usr/bin/env python3
"""Read-only reviewer queue for legal-source provenance and version checks."""
from __future__ import annotations
import argparse, json, os, re, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

def tables(db):
    return {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}

def cols(db, table):
    return {r[1] for r in db.execute(f'PRAGMA table_info("{table}")')}

def valid_evidence_url(value):
    """Check URL shape only; a valid link does not establish evidence authenticity."""
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

def commercial_reuse_issue(value):
    """Return a review reason unless commercial reuse is explicitly unrestricted."""
    if value == "allowed":
        return None
    if value == "allowed_limited":
        return "source_commercial_reuse_permission_scope_limited"
    if value in ("prohibited", "not_allowed_without_explicit_exception_or_license"):
        return "source_commercial_reuse_permission_not_allowed"
    return "commercial_reuse_permission_unknown"

def review_queue(db_path: Path) -> dict:
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    db = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        present = tables(db)
        report = {"report_type":"legal_source_review_queue","schema_version":"1.0",
            "generated_at":datetime.now(timezone.utc).isoformat(),"read_only":True,
            "records":[],"source_permissions":[],"issues":[],
            "limitations":["Prioritization aid only; not legal advice or certification of authenticity.",
                "Missing data or review events do not prove a law is invalid.",
                "The tool never modifies records or review statuses."]}
        required_tables = {"legal_sources","legal_documents","legal_document_versions","legal_review_events"}
        missing = sorted(required_tables-present)
        if missing:
            report["issues"].append({"severity":"high","code":"review_schema_tables_missing","detail":missing})
            return report
        if "database_profile" not in present:
            raise ValueError("database is not bound to the legal_corpus profile")
        profile_rows = db.execute(
            "SELECT profile FROM database_profile WHERE singleton=1"
        ).fetchall()
        if len(profile_rows) != 1 or profile_rows[0]["profile"] != "legal_corpus":
            raise ValueError("database is not bound to the legal_corpus profile")
        required = {
          "legal_sources":{"source_id","authority","source_page","collection_permission","commercial_reuse_permission","permission_evidence","terms_url"},
          "legal_documents":{"document_id","source_id","official_title","document_type"},
          "legal_document_versions":{"version_id","document_id","version_label","source_url","original_sha256","publication_date","effective_date","legal_status","review_status","authenticity_verified","status_verified","amendment_history_verified","permission_evidence"},
          "legal_review_events":{"version_id","review_type","outcome","evidence_url","reviewer","reviewed_at","review_event_id"}}
        actual = {t:cols(db,t) for t in required}
        bad = {t:sorted(fields-actual[t]) for t,fields in required.items() if fields-actual[t]}
        if bad:
            report["issues"].append({"severity":"high","code":"review_schema_columns_missing","detail":bad})
            return report
        sources = db.execute("SELECT source_id,authority,source_page,collection_permission,commercial_reuse_permission,terms_url,permission_evidence FROM legal_sources ORDER BY source_id").fetchall()
        for src in sources:
            row=dict(src); reasons=[]
            if row["collection_permission"] not in ("allowed","allowed_limited"): reasons.append("source_collection_permission_not_confirmed")
            reuse_issue = commercial_reuse_issue(row["commercial_reuse_permission"])
            if reuse_issue: reasons.append(reuse_issue)
            if not row["terms_url"]: reasons.append("terms_url_missing")
            if not row["permission_evidence"]: reasons.append("permission_evidence_missing")
            if reasons: report["source_permissions"].append({**row,"review_reasons":reasons,
                "next_action":"Review current terms and record scoped permission evidence; do not infer permission from public accessibility."})
        versions=db.execute("SELECT v.version_id,v.document_id,v.version_label,v.source_url,v.original_sha256,v.publication_date,v.effective_date,v.repeal_date,v.legal_status,v.review_status,v.authenticity_verified,v.status_verified,v.amendment_history_verified,v.permission_evidence,d.official_title,d.document_type,d.source_id,s.source_id AS matched_source_id,s.authority,s.collection_permission,s.commercial_reuse_permission FROM legal_document_versions v LEFT JOIN legal_documents d ON d.document_id=v.document_id LEFT JOIN legal_sources s ON s.source_id=d.source_id ORDER BY v.version_id").fetchall()
        review_types=("source_authenticity","extraction_quality","legal_status","amendment_history","licensing","lawyer_approval")
        for version in versions:
            row=dict(version)
            events=[dict(e) for e in db.execute("SELECT review_event_id,review_type,outcome,evidence_url,reviewer,notes,reviewed_at FROM legal_review_events WHERE version_id=? ORDER BY reviewed_at DESC,review_event_id DESC",(row["version_id"],)).fetchall()]
            reasons=[]
            if row["official_title"] is None:
                reasons.append("document_missing_from_registry")
            if row["matched_source_id"] is None:
                reasons.append("source_missing_from_registry")
            checks=[
              (not row["original_sha256"],"original_content_hash_missing"),
              (not row["publication_date"],"publication_date_unknown"),
              (not row["effective_date"],"effective_date_unknown"),
              (row["legal_status"] in (None,"","unknown","under_review"),"legal_status_unresolved"),
              (row["review_status"]!="verified","version_not_marked_verified"),
              (not row["authenticity_verified"],"source_authenticity_not_verified"),
              (not row["status_verified"],"legal_status_not_verified"),
              (not row["amendment_history_verified"],"amendment_history_not_verified"),
              (not row["permission_evidence"],"version_permission_evidence_missing"),
              (row["collection_permission"] not in ("allowed","allowed_limited"),"source_collection_permission_not_confirmed"),
              (commercial_reuse_issue(row["commercial_reuse_permission"]) is not None,commercial_reuse_issue(row["commercial_reuse_permission"]))]
            reasons.extend(label for missing,label in checks if missing)
            for rt in review_types:
                matching = [e for e in events if e["review_type"] == rt and e["outcome"] == "pass" and valid_evidence_url(e["evidence_url"])]
                if not matching:
                    reasons.append("review_evidence_missing:"+rt)
                elif rt == "lawyer_approval" and not any(
                    isinstance(e.get("notes"), str) and re.search(
                        r"\\[qualified_egyptian_counsel_attested:user_id=[1-9][0-9]*\\]", e["notes"]
                    ) for e in matching
                ):
                    reasons.append("lawyer_approval_counsel_attestation_missing")
            if reasons:
                report["records"].append({**row,"review_reasons":reasons,"review_events":events,
                  "next_action":"Inspect the official instrument and evidence; record scoped review events and leave unresolved items unresolved."})
        report["summary"]={"versions_in_queue":len(report["records"]),"sources_with_permission_follow_up":len(report["source_permissions"]),"versions_scanned":len(versions),"sources_scanned":len(sources)}
        return report
    finally:
        db.close()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--db",
        type=Path,
        default=Path(os.environ["COPILOT_CORPUS_DB"]) if os.environ.get("COPILOT_CORPUS_DB", "").strip() else None,
        help="legal-corpus database (defaults to COPILOT_CORPUS_DB)",
    )
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    if os.environ.get("COPILOT_DB", "").strip():
        p.error("COPILOT_DB compatibility mode is not supported; configure COPILOT_CORPUS_DB or pass --db")
    if args.db is None:
        p.error("a legal-corpus database is required; configure COPILOT_CORPUS_DB or pass --db")
    try: report=review_queue(args.db)
    except (FileNotFoundError,sqlite3.Error,ValueError) as exc: p.error(str(exc))
    text=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(text,encoding="utf-8")
    else: print(text,end="")
    if any(i["severity"]=="high" for i in report["issues"]): raise SystemExit(2)

if __name__=="__main__": main()
