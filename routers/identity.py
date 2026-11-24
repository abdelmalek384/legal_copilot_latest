"""Public identity invitation and account-recovery pages."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse


router = APIRouter()


@router.get("/invite/accept", response_class=HTMLResponse)
def invitation_accept_page(request: Request):
    return HTMLResponse("""<!doctype html><html lang="en" dir="ltr"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Accept firm invitation</title>
<style>
body{font-family:system-ui,sans-serif;line-height:1.6;margin:0;padding:1.25rem;background:#f7f8fa;color:#172033}
main{max-width:34rem;margin:5vh auto;padding:1.5rem;background:white;border:1px solid #dce1e8;border-radius:12px}
label{display:block;margin:1rem 0}input{display:block;box-sizing:border-box;width:100%;padding:.7rem;margin-top:.35rem}
button{padding:.7rem 1rem;margin:.35rem 0;cursor:pointer}#language{float:inline-end}#result{min-height:1.5rem}
</style><body><main>
<button id="language" type="button" aria-label="Switch language">العربية</button>
<h1 data-en="Accept firm invitation" data-ar="قبول دعوة المكتب">Accept firm invitation</h1>
<p data-en="This one-time invitation is tied to the invited email address and firm." data-ar="هذه الدعوة صالحة لمرة واحدة ومرتبطة بالبريد الإلكتروني والمكتب المدعو إليه.">This one-time invitation is tied to the invited email address and firm.</p>
<form id="new-account">
<label><span data-en="Name" data-ar="الاسم">Name</span><input id="name" autocomplete="name" required maxlength="120"></label>
<label><span data-en="Choose password" data-ar="اختر كلمة المرور">Choose password</span><input id="password" type="password" autocomplete="new-password" minlength="12" required maxlength="200"></label>
<button type="submit" data-en="Create account and accept" data-ar="إنشاء الحساب وقبول الدعوة">Create account and accept</button></form>
<button id="existing-account" type="button" data-en="Accept with my existing signed-in account" data-ar="قبول الدعوة بحسابي الحالي">Accept with my existing signed-in account</button>
<p id="result" role="status" aria-live="polite"></p></main><script nonce="__CSP_NONCE__">
const token=new URLSearchParams(location.hash.slice(1)).get("token")||"";
const result=document.getElementById("result");
let language=(navigator.language||"en").toLowerCase().startsWith("ar")?"ar":"en";
function setLanguage(next){language=next;document.documentElement.lang=next;document.documentElement.dir=next==="ar"?"rtl":"ltr";
document.querySelectorAll("[data-en][data-ar]").forEach(el=>{el.textContent=el.dataset[next];});
document.getElementById("language").textContent=next==="ar"?"English":"العربية";
document.getElementById("language").setAttribute("aria-label",next==="ar"?"التبديل إلى الإنجليزية":"Switch to Arabic");}
document.getElementById("language").addEventListener("click",()=>setLanguage(language==="ar"?"en":"ar"));
function status(en,ar){result.textContent=language==="ar"?ar:en;}
function csrf(){const m=document.cookie.match(/(?:^|; )lc_csrf=([^;]+)/);return m?decodeURIComponent(m[1]):"";}
async function send(path,data,needsCsrf){const headers={"Content-Type":"application/json"};if(needsCsrf)headers["X-CSRF-Token"]=csrf();
const r=await fetch(path,{method:"POST",headers,body:JSON.stringify(data),credentials:"same-origin"});
const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.detail||"The invitation could not be accepted.");return d;}
document.getElementById("new-account").addEventListener("submit",async e=>{e.preventDefault();try{
await send("/invitations/accept/new",{token,name:document.getElementById("name").value,password:document.getElementById("password").value},false);
status("Invitation accepted. You can now sign in.","تم قبول الدعوة. يمكنك الآن تسجيل الدخول.");document.getElementById("new-account").reset();
}catch(err){result.textContent=err.message;}});
document.getElementById("existing-account").addEventListener("click",async()=>{try{
await send("/invitations/accept-existing",{token},true);status("Invitation accepted for your existing account.","تم قبول الدعوة لحسابك الحالي.");
}catch(err){result.textContent=err.message;}});
setLanguage(language);
if(!token)status("This invitation link is missing its token. Request a new invitation.","رابط الدعوة لا يحتوي على رمز. يرجى طلب رابط دعوة جديد.");
</script></body></html>""".replace("__CSP_NONCE__", request.state.csp_nonce))


@router.get("/account/recovery", response_class=HTMLResponse)
def password_recovery_page(request: Request):
    return HTMLResponse("""<!doctype html><html lang="en" dir="ltr"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Recover account</title>
<style>
body{font-family:system-ui,sans-serif;line-height:1.6;margin:0;padding:1.25rem;background:#f7f8fa;color:#172033}
main{max-width:34rem;margin:5vh auto;padding:1.5rem;background:white;border:1px solid #dce1e8;border-radius:12px}
label{display:block;margin:1rem 0}input{display:block;box-sizing:border-box;width:100%;padding:.7rem;margin-top:.35rem}
button{padding:.7rem 1rem;cursor:pointer}#language{float:inline-end}#result{min-height:1.5rem}
</style><body><main>
<button id="language" type="button" aria-label="Switch language">العربية</button>
<h1 data-en="Set a new password" data-ar="تعيين كلمة مرور جديدة">Set a new password</h1>
<form id="recovery"><label><span data-en="New password" data-ar="كلمة المرور الجديدة">New password</span>
<input id="password" type="password" autocomplete="new-password" minlength="12" maxlength="200" required></label>
<button type="submit" data-en="Reset password" data-ar="إعادة تعيين كلمة المرور">Reset password</button></form>
<p id="result" role="status" aria-live="polite"></p></main><script nonce="__CSP_NONCE__">
const token=new URLSearchParams(location.hash.slice(1)).get("token")||"";
const form=document.getElementById("recovery"),result=document.getElementById("result");
let language=(navigator.language||"en").toLowerCase().startsWith("ar")?"ar":"en";
function setLanguage(next){language=next;document.documentElement.lang=next;document.documentElement.dir=next==="ar"?"rtl":"ltr";
document.querySelectorAll("[data-en][data-ar]").forEach(el=>{el.textContent=el.dataset[next];});
document.getElementById("language").textContent=next==="ar"?"English":"العربية";
document.getElementById("language").setAttribute("aria-label",next==="ar"?"التبديل إلى الإنجليزية":"Switch to Arabic");}
document.getElementById("language").addEventListener("click",()=>setLanguage(language==="ar"?"en":"ar"));
function status(en,ar){result.textContent=language==="ar"?ar:en;}
form.addEventListener("submit",async e=>{e.preventDefault();try{const r=await fetch("/account/recovery/consume",{
method:"POST",headers:{"Content-Type":"application/json"},
body:JSON.stringify({token,new_password:document.getElementById("password").value}),credentials:"same-origin"});
const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.detail||"The recovery link is invalid or expired.");
status("Password reset successful. Sign in with your new password.","تم تغيير كلمة المرور بنجاح. يمكنك تسجيل الدخول باستخدام كلمة المرور الجديدة.");form.reset();
}catch(err){result.textContent=err.message;}});
setLanguage(language);
if(!token)status("This recovery link is missing its token. Request a new recovery email.","رابط استعادة الحساب لا يحتوي على رمز. يرجى طلب رسالة استعادة جديدة.");
</script></body></html>""".replace("__CSP_NONCE__", request.state.csp_nonce))
