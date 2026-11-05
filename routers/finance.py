"""Finance read routes with injected application dependencies."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException


def create_router(*, connection_provider, user_dependency, invoice_today, invoice_record, fee_model, need_dependency, rollback_tenant_transaction, log_event):
    router = APIRouter()

    @router.get("/finance/overview")
    def finance_overview(u: dict = Depends(user_dependency)):
        """Aggregate recorded fees only for cases the signed-in user is allowed to access."""
        c = connection_provider()
        row = c.execute(
            """
            SELECT
                COUNT(f.id) AS fee_count,
                COALESCE(SUM(f.amount), 0) AS total_amount,
                COALESCE(SUM(f.paid), 0) AS total_paid,
                COALESCE(SUM(CASE WHEN f.amount > f.paid THEN f.amount - f.paid ELSE 0 END), 0) AS outstanding_amount,
                COALESCE(SUM(CASE WHEN f.amount > f.paid AND f.due IS NOT NULL AND date(f.due) < date('now') THEN 1 ELSE 0 END), 0) AS overdue_count,
                COALESCE(SUM(CASE WHEN f.amount > f.paid AND f.due IS NOT NULL AND date(f.due) < date('now') THEN f.amount - f.paid ELSE 0 END), 0) AS overdue_amount
            FROM fees f
            JOIN cases cs ON cs.id = f.case_id
            WHERE cs.firm_id = ?
              AND (? = 'admin' OR cs.id IN (SELECT case_id FROM members WHERE user_id = ?))
            """,
            (u["firm_id"], u["role"], u["id"]),
        ).fetchone()
        return {
            "fee_count": int(row["fee_count"] or 0),
            "total_amount": round(float(row["total_amount"] or 0), 2),
            "total_paid": round(float(row["total_paid"] or 0), 2),
            "outstanding_amount": round(float(row["outstanding_amount"] or 0), 2),
            "overdue_count": int(row["overdue_count"] or 0),
            "overdue_amount": round(float(row["overdue_amount"] or 0), 2),
        }

    @router.get("/finance/invoices/overview")
    def invoice_finance_overview(u: dict = Depends(user_dependency)):
        c = connection_provider()
        if u["role"] == "admin":
            rows = c.execute(
                "SELECT i.* FROM invoices i JOIN cases cs ON cs.id=i.case_id WHERE cs.firm_id=? "
                "ORDER BY i.id", (u["firm_id"],)
            ).fetchall()
        else:
            rows = c.execute(
                "SELECT i.* FROM invoices i JOIN cases cs ON cs.id=i.case_id "
                "WHERE cs.firm_id=? AND EXISTS (SELECT 1 FROM members m "
                "WHERE m.case_id=i.case_id AND m.user_id=?) ORDER BY i.id",
                (u["firm_id"], u["id"]),
            ).fetchall()
        today_date = invoice_today()
        case_totals = {}
        client_totals = {}
        total_issued = total_paid = total_outstanding = 0
        for row in rows:
            item = invoice_record(c, row)
            if item["status"] != "issued":
                continue
            balance = int(item["balance_piasters"])
            paid = int(item["paid_piasters"])
            total_issued += int(item["total_piasters"])
            total_paid += paid
            total_outstanding += balance
            if balance <= 0:
                bucket = "settled"
            elif not item["due_date"] or item["due_date"] >= today_date.isoformat():
                bucket = "current"
            else:
                overdue_days = (today_date - date.fromisoformat(item["due_date"])).days
                bucket = "1_30" if overdue_days <= 30 else "31_60" if overdue_days <= 60 else "61_90" if overdue_days <= 90 else "over_90"
            cid = int(item["case_id"])
            case_entry = case_totals.setdefault(cid, {
                "case_id": cid, "case_title": item["case_title_snapshot"],
                "client_name": item["client_name_snapshot"], "invoice_count": 0,
                "issued_piasters": 0, "paid_piasters": 0, "outstanding_piasters": 0,
                "aging": {"current": 0, "1_30": 0, "31_60": 0, "61_90": 0, "over_90": 0},
            })
            case_entry["invoice_count"] += 1
            case_entry["issued_piasters"] += int(item["total_piasters"])
            case_entry["paid_piasters"] += paid
            case_entry["outstanding_piasters"] += balance
            if bucket != "settled":
                case_entry["aging"][bucket] += balance
            client_key = (item["client_name_snapshot"] or "").strip() or "غير محدد"
            client_entry = client_totals.setdefault(client_key, {
                "client_name": client_key, "invoice_count": 0,
                "issued_piasters": 0, "paid_piasters": 0, "outstanding_piasters": 0,
                "aging": {"current": 0, "1_30": 0, "31_60": 0, "61_90": 0, "over_90": 0},
            })
            client_entry["invoice_count"] += 1
            client_entry["issued_piasters"] += int(item["total_piasters"])
            client_entry["paid_piasters"] += paid
            client_entry["outstanding_piasters"] += balance
            if bucket != "settled":
                client_entry["aging"][bucket] += balance
        return {
            "currency": "EGP", "as_of_date": today_date.isoformat(),
            "issued_piasters": total_issued, "paid_piasters": total_paid,
            "outstanding_piasters": total_outstanding,
            "cases": sorted(case_totals.values(), key=lambda x: x["outstanding_piasters"], reverse=True),
            "clients": sorted(client_totals.values(), key=lambda x: x["outstanding_piasters"], reverse=True),
        }
    @router.post("/cases/{cid}/fees")
    @rollback_tenant_transaction
    def new_fee(cid: int, b: fee_model, u: dict = Depends(user_dependency)):
        c = connection_provider(); need_dependency(c, u, cid)
        if b.paid > b.amount: raise HTTPException(422, "paid amount cannot exceed total")
        c.execute("INSERT INTO fees(case_id,title,amount,paid,due,note,created_by) VALUES(?,?,?,?,?,?,?)",
                  (cid, b.title, b.amount, b.paid, b.due, b.note, u["id"]))
        log_event(c, cid, u["name"], "تسجيل أتعاب: " + b.title); c.commit()
        return {"ok": True}
    return router
