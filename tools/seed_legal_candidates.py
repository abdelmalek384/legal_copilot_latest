#!/usr/bin/env python3
"""Seed candidate legislation metadata into Legal Copilot; never imports legal text.

Dry-run by default. Use --apply to add source/document discovery records to the
SQLite registry. Existing records are never overwritten. No legal version is created
until a direct document URL and collection permission evidence are established.
"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs" / "legal_document_candidates.json"

def load_catalog(path=CATALOG):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("catalog root must be an object")
    sources = data.get("sources")
    docs = data.get("documents")
    if not isinstance(sources, list) or not isinstance(docs, list):
        raise ValueError("catalog must contain sources and documents arrays")

    errors = []
    valid_sources = []
    valid_docs = []
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"sources[{index}] must be an object")
        else:
            valid_sources.append(source)
            for field in ("source_id", "authority", "source_page"):
                if not isinstance(source.get(field), str) or not source[field].strip():
                    errors.append(f"sources[{index}]: {field} must be a non-empty string")
    for index, document in enumerate(docs):
        if not isinstance(document, dict):
            errors.append(f"documents[{index}] must be an object")
        else:
            valid_docs.append(document)
            for field in ("document_id", "source_id", "official_title", "document_type"):
                if not isinstance(document.get(field), str) or not document[field].strip():
                    errors.append(f"documents[{index}]: {field} must be a non-empty string")

    source_ids = [s["source_id"] for s in valid_sources if isinstance(s.get("source_id"), str) and s["source_id"].strip()]
    if len(source_ids) != len(set(source_ids)):
        errors.append("duplicate source_id")
    document_ids = [d["document_id"] for d in valid_docs if isinstance(d.get("document_id"), str) and d["document_id"].strip()]
    if len(document_ids) != len(set(document_ids)):
        errors.append("duplicate document_id")
    known = set(source_ids)

    for document in valid_docs:
        document_id = document.get("document_id", "<missing document_id>")
        source_id = document.get("source_id")
        if not isinstance(source_id, str) or source_id not in known:
            errors.append(f"{document_id}: unknown source_id {source_id!r}")
        if document.get("candidate_status") != "discovery_only":
            errors.append(f"{document_id}: candidate_status must remain discovery_only")
    allowed_collection_permissions = {
        "unknown", "allowed", "allowed_limited", "prohibited",
        "not_allowed_without_explicit_exception_or_license",
    }
    for source in valid_sources:
        source_id = source.get("source_id", "<missing source_id>")
        permission = source.get("collection_permission", "unknown")
        if not isinstance(permission, str) or permission not in allowed_collection_permissions:
            errors.append(f"{source_id}: invalid collection_permission")
        if permission == "allowed" and not (source.get("permission_evidence") and source.get("terms_checked_on")):
            errors.append(f"{source_id}: allowed permission requires evidence and terms_checked_on")
    if errors:
        raise ValueError("; ".join(errors))
    return data

def validate_permission_parity(data, register_path=ROOT / "docs" / "source_permission_register.json"):
    """Fail closed if candidate seed metadata diverges from the canonical rights register."""
    register = json.loads(Path(register_path).read_text(encoding="utf-8"))
    if not isinstance(register, dict) or not isinstance(register.get("sources"), list):
        raise ValueError("permission register must contain a sources array")
    by_id = {}
    for item in register["sources"]:
        if not isinstance(item, dict) or not isinstance(item.get("source_id"), str):
            raise ValueError("permission register contains an invalid source record")
        source_id = item["source_id"]
        if source_id in by_id:
            raise ValueError(f"permission register has duplicate source_id {source_id}")
        by_id[source_id] = item

    errors = []
    for candidate in data["sources"]:
        source_id = candidate["source_id"]
        registered = by_id.get(source_id)
        if registered is None:
            errors.append(f"{source_id}: missing canonical permission-register record")
            continue
        for field in ("collection_permission", "commercial_reuse_permission"):
            candidate_state = candidate.get(field, "unknown")
            registered_state = registered.get(field, "unknown")
            if candidate_state != registered_state:
                errors.append(
                    f"{source_id}: {field} differs from canonical permission register "
                    f"({candidate_state!r} != {registered_state!r})"
                )
        candidate_host = urlparse(candidate["source_page"]).hostname
        register_host = urlparse(registered.get("source_page", "")).hostname
        if not candidate_host or not register_host or candidate_host.lower() != register_host.lower():
            errors.append(f"{source_id}: source_page host differs from canonical permission register")
    if errors:
        raise ValueError("; ".join(errors))
    return True

def seed(data, db):
    source_count=document_count=0
    for s in data["sources"]:
        cur=db.execute(
          """INSERT OR IGNORE INTO legal_sources
          (source_id,authority,source_page,access_status,collection_permission,
           commercial_reuse_permission,terms_url,terms_checked_on,permission_evidence)
          VALUES(?,?,?,?,?,?,?,?,?)""",
          (s["source_id"],s["authority"],s["source_page"],s.get("access_status","unknown"),
           s.get("collection_permission","unknown"),s.get("commercial_reuse_permission","unknown"),
           s.get("terms_url"),s.get("terms_checked_on"),s.get("permission_evidence")))
        source_count += cur.rowcount
    for d in data["documents"]:
        cur=db.execute(
          """INSERT OR IGNORE INTO legal_documents
          (document_id,source_id,official_title,document_type,law_number,law_year,language)
          VALUES(?,?,?,?,?,?,?)""",
          (d["document_id"],d["source_id"],d["official_title"],d["document_type"],
           d.get("law_number"),d.get("law_year"),d.get("language","ar")))
        document_count += cur.rowcount
    db.commit()
    return source_count,document_count

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apply",action="store_true",help="write candidates to the configured SQLite registry")
    p.add_argument("--catalog",type=Path,default=CATALOG)
    p.add_argument("--permission-register",type=Path,default=ROOT / "docs" / "source_permission_register.json")
    args=p.parse_args()
    data=load_catalog(args.catalog)
    validate_permission_parity(data, args.permission_register)
    print(f"Validated {len(data['sources'])} sources and {len(data['documents'])} document candidates against the canonical permission register.")
    if not args.apply:
        print("Dry run only; no database was opened or changed. Add --apply to seed metadata.")
        return
    sys.path.insert(0,str(ROOT))
    import app
    required = ("COPILOT_CONTROL_DB", "COPILOT_TENANT_DB_ROOT", "COPILOT_CORPUS_DB")
    missing = [name for name in required if not os.environ.get(name, "").strip()]
    if missing or os.environ.get("COPILOT_DB", "").strip():
        raise SystemExit(
            "Corpus seeding requires the profile-separated runtime with COPILOT_DB unset; "
            + ("missing " + ", ".join(missing) if missing else "remove COPILOT_DB")
        )
    db = app.corpus_conn()
    try:
        sources,documents=seed(data,db)
        print(f"Inserted {sources} new source records and {documents} new document candidates.")
        print("No legal text was downloaded, no legal version was created, and no source was marked permitted or verified.")
    finally:
        app.get_database_runtime().close_current_thread()

if __name__=="__main__":
    main()
