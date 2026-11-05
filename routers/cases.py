"""Firm-scoped case listing and search routes."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query


def create_router(*, connection_provider, user_dependency, need_dependency, arabic_skeleton_builder, meter_firm_usage, communication_model, rollback_tenant_transaction, log_event, case_model, ensure_client_profile, add_case_helper, meter_pilot_metric):
    router = APIRouter()


    @router.post("/cases")
    @rollback_tenant_transaction
    def new_case(b: case_model, u: dict = Depends(user_dependency)):
        c = connection_provider()
        client_id, client_name = ensure_client_profile(c, u, b.client, b.client_id)
        case_id = add_case_helper(
            c, u, b.title, client_name, b.stage, b.case_number, b.case_year,
            b.court, b.circuit, b.opposing_party, client_id,
        )
        meter_pilot_metric(u, "cases_created")
        return {"id": case_id, "client_id": client_id}

    @router.get("/cases")
    def cases(u: dict = Depends(user_dependency)):
        q = ("SELECT cs.*, (SELECT COUNT(*) FROM tasks t WHERE t.case_id=cs.id AND t.status='open') AS open_tasks, "
             "(SELECT COUNT(*) FROM tasks t WHERE t.case_id=cs.id AND t.status='done') AS done_tasks FROM cases cs "
             "WHERE cs.firm_id=? AND (?='admin' OR cs.id IN (SELECT case_id FROM members WHERE user_id=?)) ORDER BY cs.client, cs.id")
        return [dict(r) for r in connection_provider().execute(q, (u["firm_id"], u["role"], u["id"]))]
    
    
    @router.get("/cases/search")
    def search_cases(
        q: str = Query(default="", max_length=200),
        status: str = Query(default="", max_length=10),
        limit: int = Query(default=50, ge=1, le=100),
        offset: int = Query(default=0, ge=0, le=100000),
        u: dict = Depends(user_dependency),
    ):
        if status not in ("", "open", "closed"):
            raise HTTPException(422, "status must be open or closed")
        needle = q.strip()
        escaped = needle.replace("!", "!!").replace("%", "!%").replace("_", "!_")
        pattern = f"%{escaped}%" if needle else ""
        params = (
            int(u["firm_id"]), u["role"], int(u["id"]), status, status,
            needle, pattern, pattern, pattern, pattern, pattern, pattern, pattern,
        )
        c = connection_provider()
        total = int(c.execute(
            "SELECT COUNT(*) FROM cases cs "
            "WHERE cs.firm_id=? "
            "AND (?='admin' OR cs.id IN (SELECT case_id FROM members WHERE user_id=?)) "
            "AND (?='' OR cs.status=?) "
            "AND (?='' OR ("
            "COALESCE(cs.title,'') COLLATE NOCASE LIKE ? ESCAPE '!' OR "
            "COALESCE(cs.client,'') COLLATE NOCASE LIKE ? ESCAPE '!' OR "
            "COALESCE(cs.case_number,'') COLLATE NOCASE LIKE ? ESCAPE '!' OR "
            "COALESCE(cs.case_year,'') COLLATE NOCASE LIKE ? ESCAPE '!' OR "
            "COALESCE(cs.court,'') COLLATE NOCASE LIKE ? ESCAPE '!' OR "
            "COALESCE(cs.circuit,'') COLLATE NOCASE LIKE ? ESCAPE '!' OR "
            "COALESCE(cs.opposing_party,'') COLLATE NOCASE LIKE ? ESCAPE '!'"
            "))",
            params,
        ).fetchone()[0])
        rows = c.execute(
            "SELECT cs.*, "
            "(SELECT COUNT(*) FROM tasks t WHERE t.case_id=cs.id AND t.status='open') AS open_tasks, "
            "(SELECT COUNT(*) FROM tasks t WHERE t.case_id=cs.id AND t.status='done') AS done_tasks "
            "FROM cases cs "
            "WHERE cs.firm_id=? "
            "AND (?='admin' OR cs.id IN (SELECT case_id FROM members WHERE user_id=?)) "
            "AND (?='' OR cs.status=?) "
            "AND (?='' OR ("
            "COALESCE(cs.title,'') COLLATE NOCASE LIKE ? ESCAPE '!' OR "
            "COALESCE(cs.client,'') COLLATE NOCASE LIKE ? ESCAPE '!' OR "
            "COALESCE(cs.case_number,'') COLLATE NOCASE LIKE ? ESCAPE '!' OR "
            "COALESCE(cs.case_year,'') COLLATE NOCASE LIKE ? ESCAPE '!' OR "
            "COALESCE(cs.court,'') COLLATE NOCASE LIKE ? ESCAPE '!' OR "
            "COALESCE(cs.circuit,'') COLLATE NOCASE LIKE ? ESCAPE '!' OR "
            "COALESCE(cs.opposing_party,'') COLLATE NOCASE LIKE ? ESCAPE '!'"
            ")) "
            "ORDER BY cs.client,cs.id LIMIT ? OFFSET ?",
            params + (limit, offset),
        ).fetchall()
        return {"items": [dict(row) for row in rows], "total": total, "limit": limit, "offset": offset}

    @router.get("/cases/{cid}")
    def case(cid: int, u: dict = Depends(user_dependency)):
        c = connection_provider(); need_dependency(c, u, cid)
        # Record only successful, authorized detail reads; do not store client names or case contents.
        c.execute("INSERT INTO security_audit_events(firm_id,user_id,event) VALUES(?,?,?)",
                  (u["firm_id"], u["id"], "case_read:%s" % cid))
        c.commit()
        rows = lambda q: [dict(r) for r in c.execute(q, (cid,))]
        return {**dict(c.execute("SELECT * FROM cases WHERE id=?", (cid,)).fetchone()),
                "members": rows("SELECT m.user_id, m.role, u.name FROM members m JOIN users u ON u.id=m.user_id WHERE m.case_id=?"),
                "tasks": rows("SELECT t.*, u.name AS assignee_name FROM tasks t LEFT JOIN users u ON u.id=t.assignee WHERE t.case_id=? ORDER BY t.status DESC, t.due"),
                "sessions": rows("SELECT * FROM sessions WHERE case_id=? ORDER BY date"),
                "docs": rows("SELECT id AS document_id,name,added,sha256,content_type,byte_size,extraction_status,ocr_used,uploader_user_id FROM docs WHERE case_id=? ORDER BY id DESC"),
                "notes": rows("SELECT n.id,n.text,n.created_at,u.name AS author FROM notes n JOIN users u ON u.id=n.created_by WHERE n.case_id=? ORDER BY n.id DESC"),
                "deadlines": rows("SELECT * FROM deadlines WHERE case_id=? ORDER BY due"),
                "fees": rows("SELECT * FROM fees WHERE case_id=? ORDER BY due"),
                "events": rows("SELECT who, at, text FROM events WHERE case_id=? ORDER BY id DESC LIMIT 100")}
    
    
    @router.get("/cases/{cid}/draft-skeleton")
    def case_draft_skeleton(
        cid: int,
        document_type: str = Query(default="memorandum", pattern="^(memorandum|pleading)$"),
        u: dict = Depends(user_dependency),
    ):
        """Build a heading-only Arabic draft from metadata of an authorized case."""
        c = connection_provider()
        need_dependency(c, u, cid)
        record = c.execute(
            "SELECT title, client, case_number, case_year, court, circuit, opposing_party "
            "FROM cases WHERE id=? AND firm_id=?",
            (cid, u["firm_id"]),
        ).fetchone()
        if record is None:
            raise HTTPException(404, "case not found")
        content = arabic_skeleton_builder(dict(record), document_type)
        meter_firm_usage(u, "draft_generation")
        return {
            "document_type": document_type,
            "content": content,
            "draft_only": True,
            "lawyer_review_required": True,
            "message": "هيكل أولي فقط؛ يجب استكمال الوقائع والأسانيد والطلبات ومراجعته بواسطة محامٍ.",
        }
    @router.get("/cases/{cid}/communications")
    def list_case_communications(cid: int, u: dict = Depends(user_dependency)):
        c = connection_provider()
        need_dependency(c, u, cid)
        return [dict(row) for row in c.execute(
            "SELECT id,channel,subject,summary,occurred_at,created_at,created_by "
            "FROM case_communications WHERE case_id=? ORDER BY occurred_at DESC,id DESC LIMIT 200",
            (cid,),
        ).fetchall()]
    
    
    @router.post("/cases/{cid}/communications")
    @rollback_tenant_transaction
    def create_case_communication(cid: int, b: communication_model, u: dict = Depends(user_dependency)):
        c = connection_provider()
        need_dependency(c, u, cid)
        occurred_at = b.occurred_at or datetime.now(timezone.utc).isoformat()
        cursor = c.execute(
            "INSERT INTO case_communications(case_id,created_by,channel,subject,summary,occurred_at) "
            "VALUES(?,?,?,?,?,?)",
            (cid, int(u["id"]), b.channel, b.subject, b.summary, occurred_at),
        )
        log_event(c, cid, u["name"], "إضافة سجل تواصل")
        c.commit()
        return {"id": cursor.lastrowid, "ok": True}
    return router
