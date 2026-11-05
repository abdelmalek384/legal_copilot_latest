"""Public identity invitation and account-recovery pages."""

from fastapi import APIRouter, Request
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


