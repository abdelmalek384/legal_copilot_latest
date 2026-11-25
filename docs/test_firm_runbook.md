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

Configure an isolated local database layout (do not copy production secrets or use production paths):

```bash
mkdir -p data/tenants
export COPILOT_ENV=development
export COPILOT_CONTROL_DB="$PWD/data/control_plane.sqlite3"
export COPILOT_TENANT_DB_ROOT="$PWD/data/tenants"
export COPILOT_CORPUS_DB="$PWD/data/legal_corpus.sqlite3"
unset ADMIN_TOKEN BACKUP_KEY MFA_ENCRYPTION_KEY
unset LLM_URL LLM_KEY LLM_DATA_PROCESSING_APPROVED LLM_FIRM_DATA_PROCESSING_APPROVED
```

Run `python tools/deployment_preflight.py` and review the sanitized development-mode output; do not use the production strict gate as a substitute for local configuration. Create the fictional demo firm using the command in section 1, then start the app with `python -m uvicorn app:app --host 127.0.0.1 --port 8000`. Sign in with the test-only owner and verify the demo banner, Arabic/English first-run wizard, setup-health state, and first dashboard load. Record the commit SHA and sanitized output. This is a documented acceptance procedure, not evidence that the rehearsal has already been executed.

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

## 3A. Two-firm authorization acceptance matrix (manual, synthetic-only)

Run this matrix only against an isolated local/staging deployment with two demo firms (Firm A and Firm B), distinct test accounts, and synthetic records. Record the commit SHA and sanitized evidence for each case. This is a procedure—not evidence of execution.

### Seed and sentinels

- Create two demo firms and at least one owner and one non-owner member per firm, where supported by the current role model.
- Create a unique case, document, note, deadline, invoice, and client/matter record in Firm A and Firm B. Use unmistakable synthetic sentinel strings (for example, `SYNTH-A-<random>` and `SYNTH-B-<random>`); do not use real names or data.
- Capture each firm's own record IDs using its authorized account. Do not alter cookies, tokens, or credentials between accounts except through the application's normal test login flow.

### Denial and isolation checks

| Surface | Firm A session attempting Firm B data | Expected |
|---|---|---|
| Case/matter detail | Direct navigation and API request using Firm B ID | Denied or indistinguishable not-found response; no Firm B content |
| Document preview/download | Firm B document ID and original-file endpoint | Denied; no bytes, metadata, or revealing filename |
| Search | Query Firm B sentinel and unique identifiers | No Firm B results or snippets |
| Notes/activity | Firm B note/activity identifiers | Denied; no content or metadata leakage |
| Deadline/session/fee | Firm B record IDs | Denied; no data or mutation |
| Invoice/payment evidence | Firm B invoice IDs and export surfaces | Denied; no content or metadata leakage |
| Bulk/export | Firm B scope or ID in export request | Denied; output contains only Firm A rows |
| Mutation endpoints | Update/delete/review/role actions targeting Firm B | Denied; Firm B state remains unchanged |
| Firm context switch | Missing/invalid CSRF or untrusted Origin | Denied; active firm/session context unchanged |
| Search pagination | Follow/modify cursor while querying Firm A | No cross-tenant rows at any page |

Repeat positive controls: Firm A must be able to read and mutate only its own authorized records, and Firm B must likewise access its own records. Test member-role restrictions separately from tenant boundary restrictions. For each denied action, confirm no state change by re-reading the target through Firm B's authorized account.

### Result recording

Use PASS only when the actual response and post-action state meet the expectation. Record endpoint/route or UI path, sanitized request parameters, status/result, response headers relevant to privacy, before/after state, tester, timestamp/timezone, browser/runtime and commit. Mark unexecuted cases BLOCKED—not PASS. Stop and log a release-blocking defect if any Firm B content, bytes, search result, or mutation is observable from Firm A.


## 6. Backup and restore rehearsal checklist (disposable environment)

This procedure is a rehearsal, not proof of backup safety. Use only a disposable demo deployment and synthetic firm data; never restore over production or a live test environment.

### Preparation

- Record the source commit, OS, runtime version, storage/database profile, operator and timestamp/timezone.
- Create or confirm a demo firm with synthetic cases, documents, notes, deadlines and audit events. Record non-sensitive row counts and sentinel IDs as a baseline.
- Identify the configured backup command and documented encryption/key-handling process for the environment. Do not put key material, credentials, or unencrypted backup contents in evidence.
- Confirm the destination is a separate, access-controlled disposable location with adequate space.

### Backup and integrity checks

- Execute the documented backup process and record its exit status and sanitized output.
- Verify the backup artifact exists, is non-empty, and passes the documented integrity/authentication verification. Record checksums where appropriate; checksums alone do not prove authenticity or confidentiality.
- Confirm that encryption is enabled and that secrets are not embedded in logs or filenames. Verify an invalid/wrong key or tampered artifact is rejected, using a disposable copy only.
- Confirm backup scope and retention policy, including databases, uploaded originals, tenant metadata, and required configuration. Explicitly note exclusions and dependencies.

### Restore and compare

- Restore into a fresh, isolated destination—not over the source environment.
- Verify the restored application can start using the restored data and the required configuration, without using production credentials or live external providers.
- Compare the pre-restore baseline with restored records: synthetic sentinel IDs, counts, document retrieval, notes, audit events and tenant boundaries. Investigate missing or inconsistent data.
- Confirm Firm A cannot access Firm B records in the restored environment if both synthetic firms are present.
- Record measured restore duration and any manual steps, warnings, or recovery gaps.

### Closure criteria

Mark PASS only if the actual backup verification, tamper/wrong-key rejection, isolated restore, baseline comparison and tenant-isolation checks all succeed and evidence is recorded. Otherwise mark FAIL or BLOCKED and log a defect. Do not claim a recovery-time or recovery-point objective unless the measured rehearsal supports it. Destroy disposable artifacts and databases according to the test environment's cleanup policy; retain only approved sanitized evidence.
