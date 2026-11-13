# Test-firm runbook

**Purpose:** operate a disposable, clearly identified demo firm for product acceptance. This is not production onboarding or legal validation.

## 1. Setup

1. Use a clean local/staging environment with the three separate database paths configured (`COPILOT_CONTROL_DB`, `COPILOT_TENANT_DB_ROOT`, `COPILOT_CORPUS_DB`). Never point this exercise at production databases.
2. Keep both model-processing attestations unset/false by default: `LLM_DATA_PROCESSING_APPROVED` and `LLM_FIRM_DATA_PROCESSING_APPROVED`. Do not configure an external model until its provider, model, region, retention and matter-data terms have been reviewed and separately approved.
3. Create the fictional demo firm from the repository root:
   ```bash
   python manage.py demo-firm create --owner-name "Demo Owner" --owner-email demo-owner@example.invalid
   ```
   Enter a unique test-only email and a strong test password at the interactive prompt. The command marks the firm as demo and seeds fictional cases, deadlines, fees and one clearly labelled demonstration invoice.
4. Sign in as the demo owner, complete the first-run wizard in Arabic and English, and confirm the test-mode/demo identity is visible before entering any records.

## 1A. Clean-clone first-login rehearsal

Perform this rehearsal in a disposable directory, separate from any existing developer checkout:

```bash
git clone https://github.com/abdelmalek384/legal_copilot_latest.git
cd legal_copilot_latest
python3.12 --version
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install --require-hashes -r requirements-py312.lock
```

Configure the three separate database paths using the repository's deployment template and keep all production credentials absent. Review the strict preflight output before starting the application. Create the fictional demo firm using the command in section 1, sign in with the test-only owner, and verify the demo banner, Arabic/English first-run wizard, setup-health state, and first dashboard load. Record the commit SHA and sanitized output. This is a documented acceptance procedure, not evidence that the rehearsal has already been executed.

## 2. Permitted data

- Fictional records and synthetic files created solely for testing.
- Public, non-client material only where its storage and processing permissions are established.
- Never use client-confidential matters, real identity documents, real invoices/payment credentials, production secrets, or live payment gateways.
- Demo deadlines and invoice amounts are illustrative; they are not legal or accounting advice.

## 3. What to test

- Login, MFA policy, logout, session expiry and recovery flow.
- First-run wizard, firm profile, language switching and setup-health screen.
- Case creation/editing, team roles, notes, deadlines, sessions and document upload/OCR limits.
- Invoice issue, payment evidence/review, subscription read-only recovery, exports and audit records.
- Confirm every assistant answer shows a trust-tier badge, then save and update lawyer ratings, list firm ratings as an administrator, and export the CSV. Distinguish **source-matched** from **verified**; source matching is not lawyer verification.
- Cross-firm denial using a second synthetic firm and unique sentinel values. Do not rely on UI hiding; test direct IDs and API routes as well.
- Repeat critical flows in Arabic (ar-EG) and English (en-US).

## 4. Record results

For each test, record the exact commit SHA, environment, date/time and timezone, tester role, device/browser/OS, locale, steps, expected result, actual result, PASS/FAIL/BLOCKED, defect ID and sanitized evidence location. Do not include passwords, tokens, session cookies, client data or secret values. Automated tests are not physical-device sign-off.

## 5. Export ratings and clean up

Use the per-answer Lawyer assessment panel in Legal Research to save or update a rating. Firm administrators can use View firm ratings and Export CSV to list and export the active firm's ratings. The export includes answer/question pairing, verdicts, expected article IDs, reviewer and timestamps, and benchmark-ready status. Keep the export in the restricted pilot evidence location; ratings are quality feedback, not training consent or legal approval. Runtime verification remains pending until the focused route tests and clean-clone acceptance are executed.

Remove the demo firm only after exporting permitted synthetic evidence and confirming its firm ID:
```bash
python manage.py demo-firm remove --firm-id <DEMO_FIRM_ID> --confirm-remove
```
The CLI refuses to remove a firm that is not marked as demo. Retain only sanitized test evidence under the project's restricted evidence policy.