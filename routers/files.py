"""Firm-scoped document review and extracted-chunk read routes."""

import hashlib

from fastapi import APIRouter, Depends, HTTPException


def create_router(*, connection_provider, user_dependency, need_dependency):
    router = APIRouter()

    @router.get("/cases/{cid}/docs/{document_id}/reviews")
    def list_document_reviews(cid: int, document_id: int, u: dict = Depends(user_dependency)):
        c = connection_provider(); need_dependency(c, u, cid)
        doc = c.execute("SELECT id FROM docs WHERE id=? AND case_id=? AND firm_id=?", (document_id, cid, u["firm_id"])).fetchone()
        if not doc: raise HTTPException(404, "document not found")
        rows = c.execute(
            "SELECT r.id,r.chunk_id,r.reviewer_user_id,r.outcome,r.original_text,r.reviewed_text,r.page_reference,r.note,r.created_at "
            "FROM document_extraction_reviews r WHERE r.document_id=? AND r.case_id=? AND r.firm_id=? ORDER BY r.id DESC LIMIT 200",
            (document_id, cid, u["firm_id"])).fetchall()
        return {"document_id": document_id, "reviews": [dict(r) for r in rows]}
    
    
    @router.get("/cases/{cid}/docs/{document_id}/chunks")
    def list_document_chunks(cid: int, document_id: int, u: dict = Depends(user_dependency)):
        """Return extracted chunks for an authorized matter document so lawyers can review transcription."""
        c = connection_provider()
        need_dependency(c, u, cid)
        doc = c.execute(
            "SELECT id,name,extraction_status,ocr_used FROM docs WHERE id=? AND case_id=? AND firm_id=?",
            (document_id, cid, u["firm_id"]),
        ).fetchone()
        if not doc:
            raise HTTPException(404, "document not found")
        rows = c.execute(
            "SELECT id,ref,page,text FROM chunks WHERE document_id=? AND case_id=? ORDER BY id",
            (document_id, cid),
        ).fetchall()
        review_rows = c.execute(
            "SELECT chunk_id,outcome,reviewer_user_id,reviewed_text,page_reference,note,created_at "
            "FROM document_extraction_reviews WHERE document_id=? AND case_id=? AND firm_id=? ORDER BY id DESC",
            (document_id, cid, u["firm_id"]),
        ).fetchall()
        latest = {}
        for review in review_rows:
            latest.setdefault(review["chunk_id"], dict(review))
        chunks = []
        for row in rows:
            item = dict(row)
            item["text_sha256"] = hashlib.sha256(item["text"].encode("utf-8")).hexdigest()
            item["latest_review"] = latest.get(item["id"])
            chunks.append(item)
        return {
            "document_id": document_id,
            "name": doc["name"],
            "extraction_status": doc["extraction_status"],
            "ocr_used": bool(doc["ocr_used"]),
            "chunks": chunks,
            "warning": "Review compares extracted text only. It does not establish legal accuracy or source authenticity.",
        }

    return router
