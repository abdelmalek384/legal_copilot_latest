"""Register Labour Law 14/2025 as a pending versioned-source candidate.

This writes registry metadata and pending review events only. It never imports article
chunks, trusts supplied verified/in_force flags, or marks the law as current/verified.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORD = ROOT / "data" / "candidates" / "labour_law_14_2025" / "registry_candidate.json"


def register(db, record):
    """Idempotently insert candidate source/document/version metadata."""
    sources = record["sources"]
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
                version["legal_status"], version["review_status"], 0, 0, 0,
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
    db.commit()
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

    record = json.loads(Path(args.record).read_text(encoding="utf-8"))
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
