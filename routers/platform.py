"""Public platform-level PWA asset routes."""

import base64
from pathlib import Path

from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse


router = APIRouter()


def _read_pwa_asset(filename: str) -> str:
    """Read one fixed, public PWA asset; callers cannot choose a filesystem path."""
    asset_path = Path(__file__).resolve().parents[1] / "static" / filename
    return asset_path.read_text(encoding="utf-8")


@router.get("/manifest.webmanifest")
def pwa_manifest():
    return Response(_read_pwa_asset("manifest.webmanifest"), media_type="application/manifest+json")


@router.get("/service-worker.js")
def pwa_service_worker():
    return Response(
        _read_pwa_asset("service-worker.js"),
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"},
    )


@router.get("/offline.html")
def pwa_offline_page():
    return HTMLResponse(_read_pwa_asset("offline.html"))


@router.get("/app-icon.svg")
def pwa_app_icon():
    return Response(_read_pwa_asset("app-icon.svg"), media_type="image/svg+xml")


@router.get("/apple-touch-icon.png")
def pwa_apple_touch_icon():
    encoded = _read_pwa_asset("apple-touch-icon.png.b64").strip()
    return Response(base64.b64decode(encoded, validate=True), media_type="image/png")

def create_payment_review_router(
    *,
    user_dependency,
    require_platform_admin_dependency,
    control_connection_provider,
    subscription_audit,
    payment_decision_model,
):
    import sqlite3
    import time

    billing_router = APIRouter()

    @billing_router.get("/platform/billing/payment-submissions")
    def list_platform_payment_submissions(u: dict = Depends(user_dependency)):
        require_platform_admin_dependency(u)
        return [dict(row) for row in control_connection_provider().execute(
            "SELECT p.*,f.name AS firm_name FROM subscription_payment_submissions p "
            "JOIN firms f ON f.id=p.firm_id WHERE p.status='pending' ORDER BY p.created_at,p.id"
        ).fetchall()]
    
    
    @billing_router.post("/platform/billing/payment-submissions/{submission_id}/approve")
    def approve_subscription_payment(submission_id: int, u: dict = Depends(user_dependency)):
        require_platform_admin_dependency(u)
        control = control_connection_provider()
        now = int(time.time())
        try:
            control.execute("BEGIN IMMEDIATE")
            payment = control.execute(
                "SELECT * FROM subscription_payment_submissions WHERE id=?", (submission_id,)
            ).fetchone()
            if payment is None or payment["status"] != "pending":
                raise HTTPException(404, "pending payment submission not found")
            control.execute(
                "UPDATE subscription_payment_submissions SET status='approved',reviewed_by_user_id=?,reviewed_at=?,decision_note='' WHERE id=? AND status='pending'",
                (u["id"], now, submission_id),
            )
            current = control.execute(
                "SELECT current_period_end FROM firm_subscriptions WHERE firm_id=?", (payment["firm_id"],)
            ).fetchone()
            period_start = max(now, int(current["current_period_end"] or 0)) if current else now
            control.execute(
                "UPDATE firm_subscriptions SET status='active',current_period_start=?,current_period_end=?,updated_at=? WHERE firm_id=?",
                (period_start, period_start + 30 * 86400, now, payment["firm_id"]),
            )
            subscription_audit(control, payment["firm_id"], u["id"], "payment_approved", {
                "submission_id": submission_id, "amount_piasters": int(payment["amount_piasters"]),
            })
            control.commit()
        except HTTPException:
            if control.in_transaction:
                control.rollback()
            raise
        except sqlite3.Error as exc:
            if control.in_transaction:
                control.rollback()
            raise HTTPException(503, "payment approval could not be saved") from exc
        return {"ok": True, "status": "approved"}
    
    
    @billing_router.post("/platform/billing/payment-submissions/{submission_id}/reject")
    def reject_subscription_payment(submission_id: int, b: payment_decision_model, u: dict = Depends(user_dependency)):
        require_platform_admin_dependency(u)
        control = control_connection_provider()
        now = int(time.time())
        try:
            control.execute("BEGIN IMMEDIATE")
            payment = control.execute(
                "SELECT * FROM subscription_payment_submissions WHERE id=?", (submission_id,)
            ).fetchone()
            if payment is None or payment["status"] != "pending":
                raise HTTPException(404, "pending payment submission not found")
            control.execute(
                "UPDATE subscription_payment_submissions SET status='rejected',reviewed_by_user_id=?,reviewed_at=?,decision_note=? WHERE id=? AND status='pending'",
                (u["id"], now, b.reason.strip(), submission_id),
            )
            subscription = control.execute(
                "SELECT trial_ends_at,current_period_end FROM firm_subscriptions WHERE firm_id=?", (payment["firm_id"],)
            ).fetchone()
            if subscription and subscription["current_period_end"] and int(subscription["current_period_end"]) > now:
                status = "active"
            elif subscription and subscription["trial_ends_at"] and int(subscription["trial_ends_at"]) > now:
                status = "trial"
            else:
                status = "expired"
            control.execute(
                "UPDATE firm_subscriptions SET status=?,updated_at=? WHERE firm_id=?",
                (status, now, payment["firm_id"]),
            )
            subscription_audit(control, payment["firm_id"], u["id"], "payment_rejected", {
                "submission_id": submission_id, "reason": b.reason.strip(),
            })
            control.commit()
        except HTTPException:
            if control.in_transaction:
                control.rollback()
            raise
        except sqlite3.Error as exc:
            if control.in_transaction:
                control.rollback()
            raise HTTPException(503, "payment rejection could not be saved") from exc
        return {"ok": True, "status": "rejected"}

    return billing_router

