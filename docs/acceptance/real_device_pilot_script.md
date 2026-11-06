# Real-device pilot acceptance script

**Purpose:** witnessed end-to-end acceptance before any pilot firm uses real client data. This is a human-run checklist, not a browser-automation substitute.

## Test setup

1. Record the candidate release commit, date/time/timezone, tester, synthetic firm ID, phone make/model/OS/browser, and desktop OS/browser/version in the restricted acceptance record.
2. Use one physical phone and one desktop browser. On **each device**, execute the full script once in English (LTR) and once in Arabic (RTL), starting from a clean authenticated session. Use synthetic names and documents only.
3. Record each step as **PASS** or **FAIL** with a short observation. Record defects and sanitized request/correlation IDs in the restricted evidence store. Do not commit screenshots, client data, credentials, MFA seeds, or session tokens.

## Script — repeat all eight steps for each device/language pair

1. **Login:** open the production-shaped HTTPS origin, sign in as the designated synthetic firm user, and verify the correct firm context and readable layout. Expected: no clipped controls, horizontal page overflow, or cross-firm data.
2. **MFA:** complete the configured MFA challenge. Expected: enrolled user proceeds; an unenrolled user subject to policy is denied; recovery behavior follows the approved runbook.
3. **Create case:** create a synthetic case with a synthetic client and unique sentinel. Expected: save succeeds once, the case appears in the correct firm, and switching language does not lose the current view or data.
4. **Deadline:** create a test deadline using an explicitly reviewed fixture date/rule. Expected: displayed date, timezone, status and audit trail match the approved fixture; do not treat this as legal validation of an unreviewed deadline rule.
5. **Invoice:** create and issue a synthetic invoice for the case. Expected: currency and integer minor-unit amount are correct, invoice is bound to the intended firm/case, and print/export text is legible in the selected language.
6. **Payment:** record a synthetic manual payment using the approved non-live test procedure and a unique idempotency key. Expected: balance/state and receipt are correct, duplicate submission does not create a second payment, and the audit event is visible. Do not connect a live payment gateway.
7. **Subscription page:** open subscription/billing and payment-evidence views as the firm owner. Expected: status, recovery instructions and access restrictions are clear; platform-only review controls are not exposed to firm users.
8. **Export:** export the synthetic firm's permitted data. Expected: file opens, Arabic/English text is readable, formula-like cells are neutralized, and no other firm's sentinel or metadata appears.

## Result record

For each of the four runs (phone-English, phone-Arabic, desktop-English, desktop-Arabic), record eight individual PASS/FAIL outcomes, tester initials, timestamp, candidate SHA, and sanitized defect references. A run is complete only when all 8 steps have explicit outcomes. Any FAIL blocks physical acceptance until corrected and rerun. The human tester—not the implementer—signs the result. Store evidence in the restricted evidence location; keep screenshots and exported test files out of Git.
