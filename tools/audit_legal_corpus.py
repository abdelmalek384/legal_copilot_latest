#!/usr/bin/env python3
"""Read-only audit of Legal Copilot's SQLite legal corpus."""
from __future__ import annotations
import argparse, hashlib, json, sqlite3
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

def audit(db_path: Path):
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    db = sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        db.execute("BEGIN")  # Pin all audit queries to one read-only SQLite snapshot.
        sidecars = existing_sqlite_sidecars(db_path)
        tables = table_names(db)
        result = {
            "report_type":"legal_corpus_audit",
            "generated_at":datetime.now(timezone.utc).isoformat(),
            "database_path":str(db_path),
            "database_sha256":sha256_file(db_path),
            "sqlite_sidecars":sidecars,
            "read_only":True, "counts":{}, "issues":[],
            "notes":["Metadata audit only; does not establish legal correctness.",
                     "Missing dates are unknown, not evidence that a law is in force.",
                     "This audit never promotes records to verified.",
                     "database_sha256 hashes the main database file; WAL/journal sidecar hashes are listed separately when present.",
                     "Database queries run in one read-only SQLite transaction; file hashes are provenance metadata, not an atomic filesystem snapshot."]
        }
        for table in ("chunks","legal_sources","legal_documents","legal_document_versions","legal_version_relations","legal_review_events"):
            if table in tables: result["counts"][table] = count(db,table)
        missing = sorted(REGISTRY_TABLES-tables)
        if missing:
            result["issues"].append({"severity":"high","code":"registry_tables_missing","detail":", ".join(missing)})
        if "chunks" in tables:
            cc=columns(db,"chunks")
            needed={"ref","article","text","source","verified","in_force"}
            if needed-cc:
                result["issues"].append({"severity":"high","code":"chunk_columns_missing","detail":str(sorted(needed-cc))})
            else:
                q={
                  "missing_source":db.execute("SELECT COUNT(*) FROM chunks WHERE case_id IS NULL AND (source IS NULL OR trim(source)='')").fetchone()[0],
                  "empty_text":db.execute("SELECT COUNT(*) FROM chunks WHERE case_id IS NULL AND (text IS NULL OR trim(text)='')").fetchone()[0],
                  "unverified":db.execute("SELECT COUNT(*) FROM chunks WHERE case_id IS NULL AND COALESCE(verified,0)=0").fetchone()[0],
                  "marked_in_force_but_unverified":db.execute("SELECT COUNT(*) FROM chunks WHERE case_id IS NULL AND COALESCE(in_force,0)=1 AND COALESCE(verified,0)=0").fetchone()[0],
                  "no_article_number":db.execute("SELECT COUNT(*) FROM chunks WHERE case_id IS NULL AND (article IS NULL OR trim(article)='')").fetchone()[0],
                  "unlinked_to_version":db.execute("SELECT COUNT(*) FROM chunks WHERE case_id IS NULL AND document_version_id IS NULL").fetchone()[0] if "document_version_id" in cc else None
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
                result["version_quality"] = q
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
    p.add_argument("--db",type=Path,required=True,help="Path to SQLite database")
    p.add_argument("--out-dir",type=Path,required=True,help="Directory for JSON and Markdown reports")
    p.add_argument("--strict",action="store_true",help="exit non-zero when high-severity metadata issues are found")
    a=p.parse_args(argv)
    report=audit(a.db)
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
