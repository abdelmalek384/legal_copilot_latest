"""Public identity invitation and account-recovery pages."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get("/invite/accept", response_class=HTMLResponse)
def invitation_accept_page(request: Request):
    return HTMLResponse("""<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Accept firm invitation</title><body><main><h1>Accept firm invitation</h1>
<p>This one-time invitation is tied to the invited email address and firm.</p>
<form id="new-account"><label>Name <input id="name" autocomplete="name" required maxlength="120"></label>
<label>Choose password <input id="password" type="password" autocomplete="new-password" minlength="12" required maxlength="200"></label>
<button type="submit">Create account and accept</button></form>
<button id="existing-account" type="button">Accept with my existing signed-in account</button>
<p id="result" role="status" aria-live="polite"></p></main><script nonce="__CSP_NONCE__">
const token=new URLSearchParams(location.hash.slice(1)).get("token")||"";
const result=document.getElementById("result");
function csrf(){const m=document.cookie.match(/(?:^|; )lc_csrf=([^;]+)/);return m?decodeURIComponent(m[1]):"";}
async function send(path,data,needsCsrf){const headers={"Content-Type":"application/json"};if(needsCsrf)headers["X-CSRF-Token"]=csrf();
const r=await fetch(path,{method:"POST",headers,body:JSON.stringify(data),credentials:"same-origin"});
const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.detail||"The invitation could not be accepted.");return d;}
document.getElementById("new-account").addEventListener("submit",async e=>{e.preventDefault();try{
await send("/invitations/accept/new",{token,name:document.getElementById("name").value,password:document.getElementById("password").value},false);
result.textContent="Invitation accepted. You can now sign in.";document.getElementById("new-account").reset();
}catch(err){result.textContent=err.message;}});
document.getElementById("existing-account").addEventListener("click",async()=>{try{
await send("/invitations/accept-existing",{token},true);result.textContent="Invitation accepted for your existing account.";
}catch(err){result.textContent=err.message;}});
if(!token)result.textContent="This invitation link is missing its token. Request a new invitation.";
</script></body></html>""".replace("__CSP_NONCE__", request.state.csp_nonce))


@router.get("/account/recovery", response_class=HTMLResponse)
def password_recovery_page(request: Request):
    return HTMLResponse("""<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Recover account</title><body><main><h1>Set a new password</h1>
<form id="recovery"><label>New password <input id="password" type="password" autocomplete="new-password" minlength="12" maxlength="200" required></label>
<button type="submit">Reset password</button></form><p id="result" role="status" aria-live="polite"></p></main><script nonce="__CSP_NONCE__">
const token=new URLSearchParams(location.hash.slice(1)).get("token")||"";
const form=document.getElementById("recovery"),result=document.getElementById("result");
form.addEventListener("submit",async e=>{e.preventDefault();try{const r=await fetch("/account/recovery/consume",{
method:"POST",headers:{"Content-Type":"application/json"},
body:JSON.stringify({token,new_password:document.getElementById("password").value}),credentials:"same-origin"});
const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.detail||"The recovery link is invalid or expired.");
result.textContent="Password reset successful. Sign in with your new password.";form.reset();
}catch(err){result.textContent=err.message;}});
if(!token)result.textContent="This recovery link is missing its token. Request a new recovery email.";
</script></body></html>""".replace("__CSP_NONCE__", request.state.csp_nonce))

def create_session_router(
    *,
    user_dependency,
    firm_switch_model,
    user_can_review_legal,
    separate_runtime_enabled,
    active_firms_for_user,
    platform_roles_for_user,
    firm_is_demo,
    database_runtime_provider,
    firm_context_error,
    secure_cookie_transport,
):
    session_router = APIRouter()

    @session_router.get("/session")
    def current_session(u: dict = Depends(user_dependency)):
        result = {
            "id": u["id"],
            "name": u["name"],
            "role": u["role"],
            "firm_id": u["firm_id"],
            "can_review_legal": user_can_review_legal(u),
        }
        if separate_runtime_enabled():
            result["firms"] = active_firms_for_user(u["id"])
            result["platform_roles"] = platform_roles_for_user(u["id"])
            result["is_demo"] = firm_is_demo(u["firm_id"])
            for field in (
                "mfa_enabled", "mfa_required", "mfa_policy_required", "mfa_verified",
                "mfa_verified_at", "mfa_enrollment_required", "mfa_verification_required",
            ):
                result[field] = u.get(field, False if field != "mfa_verified_at" else 0)
        return result

    @session_router.post("/session/firm")
    def switch_firm(b: firm_switch_model, request: Request, response: Response, u: dict = Depends(user_dependency)):
        if not separate_runtime_enabled():
            raise HTTPException(404, "firm switching is available only in separate-database mode")
        try:
            context = database_runtime_provider().resolve_context(u["id"], b.firm_id)
        except firm_context_error as exc:
            raise HTTPException(403, "active firm membership required") from exc
        response.set_cookie(
            "lc_firm",
            str(context.firm_id),
            max_age=43200,
            httponly=True,
            secure=secure_cookie_transport(request),
            samesite="lax",
            path="/",
        )
        switched_user = {
            "id": u["id"],
            "name": u["name"],
            "role": context.role,
            "firm_id": context.firm_id,
            "firms": active_firms_for_user(u["id"]),
            "platform_roles": platform_roles_for_user(u["id"]),
            "is_demo": firm_is_demo(context.firm_id),
        }
        switched_user["can_review_legal"] = user_can_review_legal(
            {"id": u["id"], "role": context.role, "email": u.get("email")}
        )
        return switched_user

    return session_router


def create_logout_router(
    *,
    control_connection_provider,
    user_dependency,
    token_hash,
    secure_cookie_transport,
):
    logout_router = APIRouter()

    @logout_router.post("/logout")
    def logout(request: Request, response: Response, u: dict = Depends(user_dependency)):
        tok = request.cookies.get("lc_session", "")
        c = control_connection_provider()
        c.execute(
            "DELETE FROM auth_sessions WHERE token_hash=? AND user_id=?",
            (token_hash(tok), u["id"]),
        )
        c.commit()
        for cookie in ("lc_session", "lc_csrf", "lc_firm"):
            response.delete_cookie(
                cookie,
                path="/",
                httponly=(cookie != "lc_csrf"),
                samesite="lax",
                secure=secure_cookie_transport(request),
            )
        return {"ok": True}

    return logout_router

