"""Firm-scoped case listing and search routes."""

from fastapi import APIRouter, Depends, HTTPException, Query


def create_router(*, connection_provider, user_dependency):
    router = APIRouter()

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

    return router
