"""Firm billing and subscription routes."""

import json
import logging
import sqlite3
import time

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from html import escape as html_escape


logger = logging.getLogger(__name__)


def create_router(
    *,
    control_connection_provider,
    user_dependency,
    require_admin_dependency,
    subscription_plans,
    subscription_trial_days,
    read_only_grace_days,
    firm_seat_usage,
    firm_usage_summary,
    subscription_audit,
    subscribe_plan_model,
    payment_submission_model,
):
    router = APIRouter()

    @router.get("/billing")
    def get_firm_billing(u: dict = Depends(user_dependency)):
        require_admin_dependency(u)
        control = control_connection_provider()
        now = int(time.time())
        subscription = control.execute(
            "SELECT * FROM firm_subscriptions WHERE firm_id=?", (u["firm_id"],)
        ).fetchone()
        if subscription:
            status = str(subscription["status"])
            expiry = (
                subscription["trial_ends_at"] if status == "trial"
                else subscription["current_period_end"] if status == "active"
                else None
            )
            if expiry and int(expiry) <= now and status in {"trial", "active"}:
                control.execute(
                    "UPDATE firm_subscriptions SET status='expired',updated_at=? WHERE firm_id=?",
                    (now, u["firm_id"]),
                )
                control.commit()
                subscription = control.execute(
                    "SELECT * FROM firm_subscriptions WHERE firm_id=?", (u["firm_id"],)
                ).fetchone()
        payments = [dict(row) for row in control.execute(
            "SELECT id,amount_piasters,method,transfer_reference,status,created_at,reviewed_at,decision_note "
            "FROM subscription_payment_submissions WHERE firm_id=? ORDER BY id DESC LIMIT 20",
            (u["firm_id"],),
        ).fetchall()]
        subscription_events = []
        for event in control.execute(
            "SELECT e.id,e.event_type,e.detail_json,e.created_at,u.name AS actor_name "
            "FROM subscription_audit_events e LEFT JOIN users u ON u.id=e.actor_user_id "
            "WHERE e.firm_id=? ORDER BY e.id DESC LIMIT 50",
            (u["firm_id"],),
        ).fetchall():
            try:
                details = json.loads(event["detail_json"] or "{}")
            except (TypeError, ValueError):
                details = {}
            subscription_events.append({
                "id": int(event["id"]),
                "event_type": event["event_type"],
                "details": details if isinstance(details, dict) else {},
                "created_at": int(event["created_at"]),
                "actor_name": event["actor_name"] or "",
            })
        active, pending, limit = firm_seat_usage(control, u["firm_id"]) if subscription and subscription["status"] not in {"expired","cancelled","past_due"} else (
            int(control.execute("SELECT COUNT(*) FROM firm_memberships WHERE firm_id=? AND status='active'", (u["firm_id"],)).fetchone()[0]),
            int(control.execute("SELECT COUNT(*) FROM identity_invitations WHERE firm_id=? AND status IN ('pending','sent')", (u["firm_id"],)).fetchone()[0]),
            int(subscription["seat_limit"]) if subscription else 1,
        )
        subscription_data = dict(subscription) if subscription else None
        expiry_at = None
        if subscription_data:
            if subscription_data["status"] in {"trial", "pending_payment"}:
                expiry_at = subscription_data.get("trial_ends_at") or subscription_data.get("current_period_end")
            else:
                expiry_at = subscription_data.get("current_period_end") or subscription_data.get("trial_ends_at")
        grace_end = int(expiry_at) + read_only_grace_days * 86400 if expiry_at else None
        read_only = bool(subscription_data and (
            subscription_data["status"] in {"expired", "cancelled", "past_due"}
            or (
                subscription_data["status"] == "pending_payment"
                and expiry_at is not None and int(expiry_at) <= now
            )
        ))
        days_remaining = max(0, (int(expiry_at) - now + 86399) // 86400) if expiry_at else None
        grace_days_remaining = max(0, (int(grace_end) - now + 86399) // 86400) if read_only and grace_end else None
        return {
            "plans": [{"code": code, **value} for code, value in subscription_plans.items()],
            "trial_days": subscription_trial_days,
            "subscription": subscription_data,
            "read_only": read_only,
            "days_remaining": days_remaining,
            "grace_period_ends_at": grace_end,
            "grace_days_remaining": grace_days_remaining,
            "seat_usage": {"active": active, "pending_invitations": pending, "limit": limit},
            "usage": firm_usage_summary(control, u["firm_id"], now),
            "payments": payments,
            "subscription_events": subscription_events,
        }
    
    
    @router.post("/billing/subscribe")
    def start_firm_subscription_trial(b: subscribe_plan_model, u: dict = Depends(user_dependency)):
        require_admin_dependency(u)
        control = control_connection_provider()
        now = int(time.time())
        plan = subscription_plans[b.plan_code]
        firm = control.execute("SELECT status FROM firms WHERE id=?", (u["firm_id"],)).fetchone()
        if firm is None or firm["status"] != "active":
            raise HTTPException(409, "firm is not active")
        try:
            control.execute("BEGIN IMMEDIATE")
            existing = control.execute(
                "SELECT status,trial_started_at FROM firm_subscriptions WHERE firm_id=?", (u["firm_id"],)
            ).fetchone()
            if existing and existing["status"] == "active":
                raise HTTPException(409, "an active subscription already exists")
            if existing and existing["status"] in {"expired","cancelled","past_due"}:
                raise HTTPException(409, "trial cannot be restarted; submit a payment request")
            if existing:
                control.execute(
                    "UPDATE firm_subscriptions SET plan_code=?,seat_limit=?,updated_at=? WHERE firm_id=?",
                    (b.plan_code, plan["seat_limit"], now, u["firm_id"]),
                )
                subscription_audit(control, u["firm_id"], u["id"], "plan_changed", {"plan_code": b.plan_code})
            else:
                control.execute(
                    "INSERT INTO firm_subscriptions(firm_id,plan_code,status,seat_limit,trial_started_at,trial_ends_at,created_at,updated_at) "
                    "VALUES(?,?,'trial',?,?,?,?,?)",
                    (u["firm_id"], b.plan_code, plan["seat_limit"], now, now + subscription_trial_days * 86400, now, now),
                )
                subscription_audit(control, u["firm_id"], u["id"], "trial_started", {
                    "plan_code": b.plan_code, "trial_days": subscription_trial_days,
                    "seat_limit": plan["seat_limit"],
                })
            control.commit()
        except HTTPException:
            if control.in_transaction:
                control.rollback()
            raise
        except sqlite3.Error as exc:
            if control.in_transaction:
                control.rollback()
            logger.exception("subscription trial could not be started")
            raise HTTPException(503, "subscription could not be started") from exc
        return get_firm_billing(u)
    
    
    @router.post("/billing/payment-submissions")
    def submit_subscription_payment(b: payment_submission_model, u: dict = Depends(user_dependency)):
        require_admin_dependency(u)
        control = control_connection_provider()
        subscription = control.execute(
            "SELECT status FROM firm_subscriptions WHERE firm_id=?", (u["firm_id"],)
        ).fetchone()
        transfer_reference = b.transfer_reference.strip()
        if len(transfer_reference) < 3:
            raise HTTPException(422, "transfer reference is required")
        if subscription is None:
            raise HTTPException(409, "select a subscription plan before submitting payment")
        try:
            control.execute("BEGIN IMMEDIATE")
            cursor = control.execute(
                "INSERT INTO subscription_payment_submissions(firm_id,amount_piasters,method,transfer_reference,submitted_by_user_id,created_at) "
                "VALUES(?,?,?,?,?,?)",
                (u["firm_id"], b.amount_piasters, b.method, transfer_reference, u["id"], int(time.time())),
            )
            if subscription["status"] != "active":
                control.execute(
                    "UPDATE firm_subscriptions SET status='pending_payment',updated_at=? WHERE firm_id=?",
                    (int(time.time()), u["firm_id"]),
                )
            subscription_audit(control, u["firm_id"], u["id"], "payment_submitted", {
                "submission_id": int(cursor.lastrowid), "method": b.method, "amount_piasters": b.amount_piasters,
            })
            control.commit()
        except sqlite3.IntegrityError as exc:
            if control.in_transaction:
                control.rollback()
            raise HTTPException(409, "this transfer reference has already been submitted") from exc
        except sqlite3.Error as exc:
            if control.in_transaction:
                control.rollback()
            raise HTTPException(503, "payment submission could not be saved") from exc
        return {"ok": True, "submission_id": int(cursor.lastrowid), "status": "pending"}

    return router

def create_invoice_read_router(
    *,
    connection_provider,
    user_dependency,
    invoice_for_user,
    invoice_record,
):
    invoice_router = APIRouter()

    @invoice_router.get("/invoices/{invoice_id}")
    def get_invoice(invoice_id: int, u: dict = Depends(user_dependency)):
        c = connection_provider()
        return invoice_record(c, invoice_for_user(c, u, invoice_id))

    @invoice_router.get("/invoices/{invoice_id}/payments/{payment_id}/receipt")
    def print_invoice_payment_receipt(invoice_id: int, payment_id: int, u: dict = Depends(user_dependency)):
        c = connection_provider()
        row = invoice_for_user(c, u, invoice_id)
        payment = c.execute(
            "SELECT * FROM invoice_payments WHERE id=? AND invoice_id=?",
            (payment_id, invoice_id),
        ).fetchone()
        if payment is None:
            raise HTTPException(404, "payment receipt not found")
        esc = html_escape
        amount = int(payment["amount_piasters"])
        number = row["invoice_number"] or "مسودة"
        body = f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<title>إيصال سداد {esc(str(number))}</title><style>
body{{font-family:Tahoma,Arial,sans-serif;margin:32px;line-height:1.8;color:#111}}
main{{max-width:760px;margin:auto;border:1px solid #aaa;padding:24px}}
@media print{{body{{margin:10mm}}.no-print{{display:none}}}}
</style></head><body><main><button class="no-print" onclick="window.print()">طباعة / حفظ PDF</button>
<h1>إيصال استلام دفعة أتعاب</h1><p>إيصال داخلي — ليس إيصالاً ضريبياً إلكترونياً.</p>
<p>رقم الإيصال: {int(payment["id"])}</p><p>رقم الفاتورة: {esc(str(number))}</p>
<p>العميل: {esc(str(row["client_name_snapshot"]))}</p>
<p>المبلغ المستلم: {amount // 100}.{amount % 100:02d} جنيه مصري</p>
<p>تاريخ السداد: {esc(str(payment["paid_on"]))}</p>
<p>طريقة السداد: {esc(str(payment["method"]))}</p>
<p>المرجع: {esc(str(payment["reference"]))}</p>
<p>ملاحظة: {esc(str(payment["note"]))}</p></main></body></html>"""
        return HTMLResponse(body)

    @invoice_router.get("/invoices/{invoice_id}/print")
    def print_invoice(invoice_id: int, u: dict = Depends(user_dependency)):
        c = connection_provider()
        row = invoice_for_user(c, u, invoice_id)
        data = invoice_record(c, row)
        esc = html_escape
        line_rows = "".join(
            "<tr><td>" + esc(str(item["description"])) + "</td><td>" +
            esc(f'{int(item["quantity_milli"]) / 1000:.3f}'.rstrip("0").rstrip(".")) +
            "</td><td>" + esc(f'{int(item["unit_price_piasters"]) // 100}.{int(item["unit_price_piasters"]) % 100:02d}') +
            "</td><td>" + esc(f'{int(item["line_total_piasters"]) // 100}.{int(item["line_total_piasters"]) % 100:02d}') +
            "</td></tr>" for item in data["lines"]
        )
        payment_rows = "".join(
            "<tr><td>" + esc(str(item["paid_on"])) + "</td><td>" +
            esc(str(item["method"])) + "</td><td>" +
            esc(f'{int(item["amount_piasters"]) // 100}.{int(item["amount_piasters"]) % 100:02d}') +
            "</td><td>" + esc(str(item["reference"])) + "</td></tr>" for item in data["payments"]
        )
        invoice_number = data["invoice_number"] or "مسودة"
        body = f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<title>{esc(str(invoice_number))}</title><style>
body{{font-family:Tahoma,Arial,sans-serif;color:#111;margin:32px;line-height:1.7}}
h1,h2{{margin:0 0 12px}}.meta{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:18px 0}}
table{{width:100%;border-collapse:collapse;margin:18px 0}}th,td{{border:1px solid #aaa;padding:8px;text-align:right}}
.total{{font-size:1.15rem;font-weight:bold;margin-top:16px}}.muted{{color:#555}}
@media print{{body{{margin:12mm}}.no-print{{display:none}}}}
</style></head><body><button class="no-print" onclick="window.print()">طباعة / حفظ PDF</button>
<h1>فاتورة أتعاب قانونية</h1><p class="muted">مستند أتعاب عادي — ليس فاتورة ضريبية إلكترونية أو إيصالاً ضريبياً.</p>
<div class="meta"><div>رقم الفاتورة: {esc(str(invoice_number))}</div><div>الحالة: {esc(str(data["payment_state"]))}</div>
<div>العميل: {esc(str(data["client_name_snapshot"]))}</div><div>القضية: {esc(str(data["case_title_snapshot"]))}</div>
<div>تاريخ الإصدار: {esc(str(data["issue_date"] or "—"))}</div><div>تاريخ الاستحقاق: {esc(str(data["due_date"] or "—"))}</div></div>
<p>{esc(str(data["description"]))}</p><table><thead><tr><th>البيان</th><th>الكمية</th><th>سعر الوحدة (جنيه)</th><th>الإجمالي (جنيه)</th></tr></thead>
<tbody>{line_rows}</tbody></table><div class="total">الإجمالي: {data["total_piasters"] // 100}.{data["total_piasters"] % 100:02d} ج.م</div>
<div>المدفوع: {data["paid_piasters"] // 100}.{data["paid_piasters"] % 100:02d} ج.م</div>
<div>المتبقي: {data["balance_piasters"] // 100}.{data["balance_piasters"] % 100:02d} ج.م</div>
<h2>سجل المدفوعات</h2><table><thead><tr><th>التاريخ</th><th>الطريقة</th><th>المبلغ (جنيه)</th><th>المرجع</th></tr></thead><tbody>{payment_rows}</tbody></table>
</body></html>"""
        return HTMLResponse(body)

    return invoice_router


def create_invoice_write_router(
    *,
    connection_provider,
    user_dependency,
    invoice_for_user,
    invoice_record,
    invoice_event,
    rollback_transaction,
    payment_model,
    void_model,
    draft_model,
    invoice_write_lines,
    invoice_today,
    meter_pilot_metric,
):
    invoice_router = APIRouter()

    @invoice_router.put("/invoices/{invoice_id}")
    @rollback_transaction
    def update_invoice(invoice_id: int, b: draft_model, u: dict = Depends(user_dependency)):
        c = connection_provider()
        row = invoice_for_user(c, u, invoice_id)
        if row["status"] != "draft":
            raise HTTPException(409, "only draft invoices can be edited")
        c.execute("DELETE FROM invoice_lines WHERE invoice_id=?", (invoice_id,))
        total = invoice_write_lines(c, invoice_id, b.lines)
        c.execute(
            "UPDATE invoices SET description=?,due_date=?,subtotal_piasters=?,total_piasters=? "
            "WHERE id=? AND status='draft'",
            (b.description.strip(), b.due_date, total, total, invoice_id),
        )
        invoice_event(c, invoice_id, int(u["id"]), "draft_updated", {"line_count": len(b.lines)})
        c.commit()
        return invoice_record(c, c.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,)).fetchone())

    @invoice_router.post("/invoices/{invoice_id}/issue")
    @rollback_transaction
    def issue_invoice(invoice_id: int, u: dict = Depends(user_dependency)):
        c = connection_provider()
        row = invoice_for_user(c, u, invoice_id)
        c.execute("SAVEPOINT invoice_write")
        row = invoice_for_user(c, u, invoice_id)
        if row["status"] != "draft":
            raise HTTPException(409, "only draft invoices can be issued")
        if int(row["total_piasters"]) <= 0:
            raise HTTPException(422, "invoice total must be greater than zero")
        today_date = invoice_today()
        year = today_date.year
        sequence = c.execute(
            "INSERT INTO invoice_sequences(issue_year,next_sequence) VALUES(?,2) "
            "ON CONFLICT(issue_year) DO UPDATE SET next_sequence=next_sequence+1 "
            "RETURNING next_sequence-1",
            (year,),
        ).fetchone()[0]
        number = f"INV-{year}-{int(sequence):06d}"
        c.execute(
            "UPDATE invoices SET status='issued',invoice_number=?,issue_date=?,issued_at=datetime('now') "
            "WHERE id=? AND status='draft'",
            (number, today_date.isoformat(), invoice_id),
        )
        invoice_event(c, invoice_id, int(u["id"]), "issued", {"invoice_number": number})
        c.execute("RELEASE SAVEPOINT invoice_write")
        c.commit()
        meter_pilot_metric(u, "invoices_issued")
        return invoice_record(c, c.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,)).fetchone())

    @invoice_router.post("/invoices/{invoice_id}/payments")
    @rollback_transaction
    def record_invoice_payment(invoice_id: int, b: payment_model, u: dict = Depends(user_dependency)):
        c = connection_provider()
        row = invoice_for_user(c, u, invoice_id)
        c.execute("SAVEPOINT invoice_write")
        row = invoice_for_user(c, u, invoice_id)
        if row["status"] != "issued":
            raise HTTPException(409, "payments can only be recorded against issued invoices")
        reference = b.reference.strip()
        note = b.note.strip()
        existing = c.execute(
            "SELECT * FROM invoice_payments WHERE invoice_id=? AND idempotency_key=?",
            (invoice_id, b.idempotency_key),
        ).fetchone()
        if existing is not None:
            same = (
                int(existing["amount_piasters"]) == b.amount_piasters
                and existing["paid_on"] == b.paid_on
                and existing["method"] == b.method
                and existing["reference"] == reference
                and existing["note"] == note
            )
            if not same:
                raise HTTPException(409, "idempotency key was already used for a different payment")
            c.execute("RELEASE SAVEPOINT invoice_write")
            return invoice_record(c, row)
        paid = int(c.execute(
            "SELECT COALESCE(SUM(amount_piasters),0) FROM invoice_payments WHERE invoice_id=?",
            (invoice_id,),
        ).fetchone()[0])
        balance = int(row["total_piasters"]) - paid
        if b.amount_piasters > balance:
            raise HTTPException(422, "payment exceeds the outstanding invoice balance")
        payment_id = c.execute(
            "INSERT INTO invoice_payments(invoice_id,amount_piasters,paid_on,method,reference,note,"
            "idempotency_key,recorded_by) VALUES(?,?,?,?,?,?,?,?)",
            (invoice_id, b.amount_piasters, b.paid_on, b.method, reference,
             note, b.idempotency_key, u["id"]),
        ).lastrowid
        invoice_event(c, invoice_id, int(u["id"]), "payment_recorded", {
            "payment_id": payment_id, "amount_piasters": b.amount_piasters,
            "method": b.method, "paid_on": b.paid_on,
        })
        c.execute("RELEASE SAVEPOINT invoice_write")
        c.commit()
        return invoice_record(c, c.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,)).fetchone())

    @invoice_router.post("/invoices/{invoice_id}/void")
    @rollback_transaction
    def void_invoice(invoice_id: int, b: void_model, u: dict = Depends(user_dependency)):
        c = connection_provider()
        row = invoice_for_user(c, u, invoice_id)
        c.execute("SAVEPOINT invoice_write")
        row = invoice_for_user(c, u, invoice_id)
        if row["status"] != "issued":
            raise HTTPException(409, "only issued invoices can be voided")
        paid = int(c.execute(
            "SELECT COALESCE(SUM(amount_piasters),0) FROM invoice_payments WHERE invoice_id=?",
            (invoice_id,),
        ).fetchone()[0])
        if paid:
            raise HTTPException(409, "an invoice with recorded payments cannot be voided; refund policy is not configured")
        c.execute(
            "UPDATE invoices SET status='void',void_reason=?,voided_by=?,voided_at=datetime('now') "
            "WHERE id=? AND status='issued'",
            (b.reason.strip(), u["id"], invoice_id),
        )
        invoice_event(c, invoice_id, int(u["id"]), "voided", {"reason": b.reason.strip()})
        c.execute("RELEASE SAVEPOINT invoice_write")
        c.commit()
        return invoice_record(c, c.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,)).fetchone())

    return invoice_router
