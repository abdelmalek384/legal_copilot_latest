#!/usr/bin/env python3
"""Read-only audit of Legal Copilot's SQLite legal corpus."""
from __future__ import annotations
import argparse, hashlib, json, sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REGISTRY_TABLES = {"legal_sources","legal_documents","legal_document_versions","legal_version_relations","legal_review_events"}

def table_names(db):
    return {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
def columns(db, table):
    return {r[1] for r in db.execute(f"PRAGMA table_info({table})")}
def count(db, table):
    return db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]

def audit(db_path: Path):
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    db = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        tables = table_names(db)
        result = {
            "report_type":"legal_corpus_audit",
            "generated_at":datetime.now(timezone.utc).isoformat(),
            "database_path":str(db_path),
            "database_sha256":hashlib.sha256(db_path.read_bytes()).hexdigest(),
            "read_only":True, "counts":{}, "issues":[],
            "notes":["Metadata audit only; does not establish legal correctness.",
                     "Missing dates are unknown, not evidence that a law is in force.",
                     "This audit never promotes records to verified."]
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
            result["source_permissions"]=dict(db.execute("SELECT collection_permission,COUNT(*) FROM legal_sources GROUP BY collection_permission").fetchall())
            if result["source_permissions"].get("unknown",0):
                result["issues"].append({"severity":"high","code":"source_permission_unknown","count":result["source_permissions"]["unknown"]})
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
                result["version_quality"]=q
                for key in q:
                    if q[key]: result["issues"].append({"severity":"high" if key in ("not_verified","unknown_legal_status") else "medium","code":"versions_"+key,"count":q[key]})
        result["issue_count"]=len(result["issues"])
        result["issue_counts_by_severity"]=dict(Counter(i["severity"] for i in result["issues"]))
        return result
    finally:
        db.close()

def render_markdown(report):
    lines=["# Legal corpus audit","",f"- Generated: {report['generated_at']}","- Database opened read-only: yes",f"- Database SHA-256: {report['database_sha256']}","","## Record counts",""]
    if report["counts"]:
        lines += ["| Table | Rows |","|---|---:|"]+[f"| {k} | {v} |" for k,v in report["counts"].items()]
    else: lines.append("No recognized corpus tables found.")
    for section in ("chunk_quality","source_permissions","version_quality"):
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

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db",type=Path,required=True,help="Path to SQLite database")
    p.add_argument("--out-dir",type=Path,required=True,help="Directory for JSON and Markdown reports")
    a=p.parse_args()
    report=audit(a.db)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    (a.out_dir/"legal_corpus_audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    (a.out_dir/"legal_corpus_audit.md").write_text(render_markdown(report),encoding="utf-8")
    print(f"Audited database read-only: {a.db}")
    print(f"Issues: {report['issue_count']} ({report['issue_counts_by_severity']})")
    print(f"Reports: {a.out_dir/'legal_corpus_audit.json'} and {a.out_dir/'legal_corpus_audit.md'}")

if __name__=="__main__": main()
