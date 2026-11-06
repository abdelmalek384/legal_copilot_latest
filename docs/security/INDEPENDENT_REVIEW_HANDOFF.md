# Independent security review handoff — pilot release

**Status: NOT READY FOR SIGN-OFF.** This package is a reviewer brief and evidence checklist, not a statement that the controls have passed. The reviewer must run the exact candidate commit in an isolated environment and attach the raw test results to the restricted evidence store.

## Scope and acceptance rule

Review the application as a multi-tenant legal case-management system. Test both read and write paths, direct object identifiers, alternate HTTP methods, exports/print/receipt endpoints, background tasks, and API/UI parity. For every denial, verify that the response does not disclose whether another firm's object exists. Use synthetic firms A and B with unique sentinel values; never use real client data.

A category passes only when: (1) positive control proves the test reaches the intended code path; (2) negative cross-tenant/unauthorized attempt is denied; (3) no sentinel, metadata, file bytes, or side effect leaks; (4) audit/session state is checked where relevant; and (5) the exact command, commit SHA, environment, and output are retained.

## Existing repository evidence found during preparation

These are pointers for reviewer orientation, **not proof of current passing tests**:

- `tests/test_invoice_payment_routes.py`: payment idempotency, partial/full payment, overpayment rejection, append-only ledger, receipt binding and cross-firm receipt denial. PR #1465 asserts `payment_recorded` event payment IDs and amounts for partial/final payments, and denies cross-firm invoice reads/payment writes; exact-head execution is outstanding.
- `tests/invoice_test_support.py`: shared invoice test setup; inspect fixture isolation and role membership.
- `tests/test_app_separate_database_runtime.py`: existing missing-CSRF, malformed authorization and expired-session fail-closed coverage. PR #1465 adds valid-token cross-origin write rejection with no persisted mutation and login session-cookie rotation against an attacker-supplied fixation value; exact-head execution remains outstanding.
- `tests/browser/test_acceptance.py`: browser test `test_cross_firm_case_identifier_does_not_reveal_other_firm_sentinel`.
- `tests/test_security_transport_config.py`: unsafe remote HTTP `LLM_URL` must not trigger a network call, even with processing approval.
- `tests/test_deployment_preflight.py`: endpoint-scheme validation for `LLM_URL`.
- `docs/llm_data_processing_policy.md`: approval gates, response-size bounds, and sources-only fallback policy.
- `tests/test_trusted_proxy_client_ip.py`: forwarded-header spoofing from an untrusted peer and trusted-proxy parsing. PR #1471 adds an explicit `COPILOT_TRUSTED_PROXIES=*` rejection regression; deployment instructions specify the exact proxy IP or smallest controlled CIDR.
- `tests/test_mfa_account_security.py`: admin enrollment requirement, TOTP replay rejection, one-time recovery codes, throttling, recovery-code rotation and reenrollment safeguards. PR #1465 adds a non-admin `all_required` enrollment gate; exact-head execution remains outstanding. Continue review for session lifecycle and bypass permutations.
- `tests/test_client_csv_import.py` and `tests/test_case_csv_import.py`: firm-admin authorization, bounded rows/fields, malformed-input rollback, duplicate handling, and tenant separation. PR #1465 now adds import-to-invoice-export regressions for `=`, `+`, `-`, `@`, and leading tab/CR/LF/whitespace titles; invoice export sanitizer tests also cover formula-like values. Exact-head execution remains outstanding. Reviewer should extend the matrix to every exported text column and verify behavior in supported spreadsheet applications.
- `tests/test_subscription_billing_routes.py`: trial, manual payment submission, platform approval, and firm scoping. PR #1465 adds explicit platform-admin-only payment rejection coverage; it remains draft/unexecuted pending CI. Reviewer must still enumerate all platform-admin endpoints and role combinations.
- `tests/test_first_run_wizard_api.py`: first-run checklist/profile isolation and completion tracking; it is API coverage, not phone acceptance.
- `tests/test_security_transport_config.py`: request-body limits, content-length validation, remote LLM HTTPS restrictions and redirect refusal. PR #1465 adds rejection of private/link-local/loopback HTTPS literals, hostnames with any non-global DNS answer, DNS lookup suppression until model-processing approval, a public-to-private DNS-rebinding regression between validation and connection, and a custom HTTPS connection that pins the validated public IP while preserving hostname-based TLS validation; it remains draft/unexecuted. Independent reviewer must still verify the full connection path under a controlled DNS-rebinding harness and confirm proxy/egress assumptions.
- `tests/test_research_prompt_injection_boundary.py`: JSON-quoted, explicitly untrusted retrieved passages; newline/instruction injection containment; citation metadata separation; and fail-closed firm-data approval for case-scoped/follow-up prompts. PR #1465 adds a case-scoped adversarial matter-passage regression; it remains draft/unexecuted. Extend to actual uploaded/OCR-derived chunks, metadata/filename payloads and retrieval authorization checks.
- `tests/test_document_extraction_budget.py`: incremental PDF/DOCX text-budget enforcement and unsupported-extension rejection for matter-document extraction. PR #1465 adds 501-page pre-extraction rejection and DOCX zip-expansion rejection regressions; it remains draft/unexecuted pending CI.
- `tests/test_pdf_ocr_fallback.py`: OCR only for missing-text pages, 30-page OCR cap, 1 MiB OCR output budget, 30-second per-page timeout, and 20-megapixel per-page raster cap before image allocation. PR #1465 adds timeout and oversized-page regressions; exact-head execution remains outstanding. Reviewer should verify upload-route behavior and worker/concurrency controls.
- `tests/test_import_laws_bundle.py`: legal-corpus PDF size/page limits, invalid limit rejection, exact-byte hashing and signature checks. This is a separate importer and does not substitute for matter-upload route abuse tests.
- `tests/test_frontend_ux_contract.py` and `tests/browser/test_acceptance.py`: navigation landmark, phone-width focus behavior, keyboard operation and responsive UI contracts. PR #1473 reapplies the 15px phone text and responsive login/password-row layout on current main with a focused CSS contract test; it remains draft/unexecuted. PR #1463 also contains phone-width first-run wizard/setup-health and expired-subscription/billing overflow assertions, but its branch is stale relative to current main and must not be merged wholesale. Browser execution and physical-device acceptance remain separate gates.

**Coverage gaps identified during preparation:** prompt-injection serialization tests exist for retrieved passages, but their explicit coverage of firm-uploaded/OCR-derived matter content and metadata attack vectors needs extension. Matter-document extraction has incremental PDF/DOCX text-budget tests, and the separate legal-corpus importer has PDF size/page tests; end-to-end upload-route abuse, OCR worker timeouts/concurrency, malformed/encrypted PDFs and resource exhaustion still require reviewer verification. Do not treat unit-level extraction limits as complete upload-pipeline acceptance.

Inspect the current candidate tree before relying on any pointer; paths or test names may change.

## Required test matrix

### A. Cross-firm object authorization (cases, files, billing)

Create two firms with owner, ordinary member, non-member, and platform-admin identities. Create unique sentinels in case title/body, file name/content/metadata, invoice, payment, receipt and finance totals.

For each object class, attempt list, detail, search, update, delete, upload/replace, download, print/PDF, receipt, export, and any ID-based API operation using the other firm's identifiers. Include guessed UUIDs and integer IDs. Verify uniform non-disclosing denial, no body/header/filename/size leakage, no mutation, no audit event attributed to the victim, and no cross-tenant aggregation. Exercise non-member access separately from a member of the wrong firm. Platform administrators must not inherit matter access unless the documented policy explicitly grants it.

### B. MFA bypass and recovery

Cover password-only login for accounts subject to MFA; missing, malformed, incorrect, expired, replayed, and rate-limited TOTP; concurrent/replayed challenge submissions; recovery-code single use, invalidation after password reset, enrollment confirmation, unenrollment, and key rotation/loss behavior. Verify session issuance happens only after the second factor and that recovery does not silently disable MFA. Test admin-required and all-required enforcement modes.

### C. CSRF, cookies, and sessions

Test missing/invalid CSRF tokens on every state-changing browser route, cross-origin form and fetch requests, Origin/Referer mismatch, SameSite/Secure/HttpOnly attributes, session fixation across login/MFA, logout revocation, password change/reset revocation, expiry, concurrent sessions, and tenant switching. Include JSON and form-encoded requests and alternate methods. Confirm no state change on rejected requests.

### D. PDF/OCR upload abuse and resource limits

Exercise empty, oversized, truncated, malformed, encrypted, image-only, decompression-bomb-like, excessive-page, huge-dimension, and unsupported files. Test MIME/extension mismatch, polyglot files, path traversal names, duplicate uploads, archive/container formats if accepted, OCR timeouts, worker exhaustion, and cleanup after failure. Verify limits are enforced before expensive decode/OCR, bounded CPU/memory/time/concurrency, safe temporary-file permissions, no arbitrary path writes, and no cross-firm file access. Test reverse-proxy limits as well as application limits.

### E. CSV import injection

Use cells beginning with `=`, `+`, `-`, `@`, tabs, carriage returns, leading whitespace, quoted formulas, Unicode lookalikes, embedded delimiters/newlines, and malicious hyperlinks. Verify spreadsheet exports neutralize formula execution without corrupting ordinary data. Test malformed/oversized imports, row-level validation, transactional rollback, duplicate handling, and tenant scoping. Opening the exported CSV in a supported spreadsheet application must not execute formulas.

### F. Prompt injection through matter files

Create synthetic matter documents containing instructions to ignore system policy, disclose other matters, reveal prompts/secrets, invoke tools, alter legal conclusions, and exfiltrate retrieved text. Test direct extraction, OCR-derived text, chunk boundaries, quoted text, metadata, filenames, and retrieved multi-file context. Verify matter content is treated as untrusted evidence, cannot alter system/developer instructions or authorization, cannot call tools, and cannot cause cross-firm retrieval. Record model/provider/version and exact prompt configuration; do not use real client data.

### G. SSRF through LLM_URL

Test loopback, RFC1918, link-local, IPv6 loopback/link-local, cloud metadata addresses, DNS rebinding, redirects to private targets, credentials, non-HTTPS remote URLs, query/fragment, unusual ports, IPv4-mapped IPv6, and hostname resolution changes. Verify endpoint validation and actual connection behavior both fail closed. A scheme/hostname preflight check alone is not sufficient evidence against DNS rebinding or redirects. Mock network calls in unit tests and use a controlled isolated network harness for integration tests; never probe third-party infrastructure.

### H. Payment-review and platform-admin authorization

Enumerate every payment-review and platform-admin route from the current route registry. Test anonymous, ordinary firm member, firm owner, firm admin, reviewer, and platform admin as applicable. Verify object-level firm scoping, least privilege, method parity, CSRF on browser mutations, audit actor/target integrity, and denial without side effects. Test guessed IDs, replay, duplicate approval, state transitions, and privilege changes. Ensure a firm admin cannot access platform administration and that a platform role does not implicitly grant access to firm matter content.

## Focused test commands

Run from the repository root in the same Python 3.12 environment and isolated configuration used by the candidate build. These are starting points; add the reviewer-specific adversarial cases from the matrix above.

```sh
PYTHONPATH=. python tests/test_trusted_proxy_client_ip.py
PYTHONPATH=. python tests/test_app_separate_database_runtime.py
PYTHONPATH=. python tests/test_invoice_payment_routes.py
PYTHONPATH=. python tests/test_invoice_csv_export.py
PYTHONPATH=. python tests/test_case_csv_import.py
PYTHONPATH=. python tests/test_subscription_billing_routes.py
PYTHONPATH=. python tests/test_mfa_account_security.py
PYTHONPATH=. python tests/test_security_transport_config.py
PYTHONPATH=. python tests/test_deployment_preflight.py
PYTHONPATH=. python tests/test_document_extraction_budget.py
PYTHONPATH=. python tests/test_pdf_ocr_fallback.py
PYTHONPATH=. python tests/test_import_laws_bundle.py
PYTHONPATH=. python tests/test_research_prompt_injection_boundary.py
PYTHONPATH=. python tests/test_first_run_wizard_api.py
PYTHONPATH=. python tests/test_frontend_ux_contract.py
```

Run the complete repository Tests workflow and Browser acceptance workflow against the exact candidate SHA after focused tests. Preserve exit codes and full logs; a workflow that never starts its test step is NOT RUN, not FAIL evidence for the code and not a pass.

## Execution and evidence

1. Pin the candidate commit SHA and record Python/runtime, OS/container image digest, dependency lock hash, and test configuration.
2. Run focused tests for each matrix category, then the full unit/integration suite and browser suite. Use a clean isolated database for every run.
3. Add explicit positive controls and negative tests for every matrix row. A skipped test, mocked-only assertion where integration behavior is required, failed setup, or runner-start failure is **not a pass**.
4. Run dependency and static security analysis. Triage every finding; document accepted risks with owner and expiry.
5. Store logs, reports, browser traces, sanitized request/response samples, and device evidence in the restricted evidence store. Do not commit screenshots, secrets, tokens, client data, or raw sensitive traces.
6. Reviewer independently reproduces critical tests and signs the final findings report. Record severity, exploit preconditions, impact, remediation, retest SHA and residual risk.

## Release decision template

| Category | Status | Evidence reference | Reviewer |
|---|---|---|---|
| Cross-firm cases/files/billing | NOT RUN | | |
| MFA bypass/recovery | NOT RUN | | |
| CSRF/sessions | NOT RUN | | |
| PDF/OCR/resource limits | NOT RUN | | |
| CSV injection | NOT RUN | | |
| Matter-file prompt injection | NOT RUN | | |
| SSRF / LLM_URL | NOT RUN | | |
| Payment-review/platform-admin authorization | NOT RUN | | |
| Full test suite / browser suite | NOT RUN | | |
| Independent reproduction | NOT RUN | | |

**Decision:** NO-GO until every category is evidenced, all critical/high findings are remediated or formally risk-accepted, and the independent reviewer signs the exact release SHA.

## Current pilot-candidate delta — 2026-11-06

The following additional regression cases are included in the current security candidate PR #1485. They are implementation/test additions, **not passing test evidence**:

- **Invoice payments and audit:** `tests/test_invoice_payment_routes.py` asserts payment-event payment IDs, amounts and methods; duplicate idempotent submissions create one payment event; and a second firm cannot read or record payments against another firm's invoice. The existing route is `POST /invoices/{invoice_id}/payments`; it was already present on main, so the original missing-route report is not accurate for this checkout.
- **CSRF and sessions:** `tests/test_app_separate_database_runtime.py` rejects a cross-origin write even with a matching CSRF token and verifies no case mutation; login rotates an attacker-supplied session cookie.
- **MFA enforcement:** `tests/test_mfa_account_security.py` verifies `MFA_ENFORCEMENT=all_required` blocks an ordinary lawyer from accessing cases until enrollment.
- **CSV injection:** `tests/test_case_csv_import.py` imports formula-like matter titles/client names and verifies invoice CSV export prefixes dangerous values so spreadsheet formulas are inert.
- **Matter-file prompt injection:** `tests/test_research_prompt_injection_boundary.py` verifies case-scoped malicious passage text is serialized as JSON-encoded untrusted evidence and is not promoted into prompt instructions.
- **PDF/DOCX/OCR limits:** `tests/test_document_extraction_budget.py` checks PDF page-count and DOCX archive-expansion limits before extraction/parsing; `tests/test_pdf_ocr_fallback.py` checks oversized page dimensions before rasterization and a bounded 30-second OCR call.
- **LLM SSRF:** `tests/test_security_transport_config.py` covers non-global literal/DNS destinations, mixed public/private DNS answers, DNS deferral until processing approval, redirect refusal, proxy bypass and a pinned-IP TLS connection. Controlled DNS-rebinding integration and production egress verification remain independent-review requirements.
- **Payment-review authorization:** `tests/test_subscription_billing_routes.py` verifies a firm owner cannot list or reject platform payment submissions, while a platform administrator can reject and the event is visible in the firm's subscription audit.
- **Preflight and repository hygiene:** `tests/test_deployment_preflight.py` verifies DNS deferral, no root-level patch/diff/CSV fixture files, and the three-database README quick start. The README quick start on main already documents the control, tenant-root and corpus database paths.

Related current-main draft PRs are #1483 (phone onboarding/subscription recovery and responsive bilingual browser coverage) and #1484 (explicit wildcard trusted-proxy rejection plus deployment wording). Keep all three draft until a healthy runner executes the exact heads successfully. The observed GitHub Actions attempts for these candidate branches terminated with empty job step lists and runner ID 0; classify those attempts as **NOT RUN / runner unavailable**, not as test failures and not as passes. Do not merge on the strength of descriptions or source inspection alone.

### Outstanding operational acceptance

- Run the focused commands and full Tests/Browser workflows from the matrix above on the exact candidate SHA using a healthy runner; retain exit codes and logs.
- Perform physical-device acceptance on actual phone and desktop hardware in Arabic RTL and English LTR. Browser viewport automation is not physical-device evidence.
- Stage identity SMTP with an operator-controlled mailbox, set the actual public HTTPS origin, provision a dedicated MFA key separately from the backup key, validate all three production database paths and accepted database-operations evidence, and complete the required S3/KMS and recovery checks. Run `python tools/deployment_preflight.py --strict` against that real staging configuration; do not invent credentials or acceptance manifests.
- Keep live reminders and payment gateways disabled until their real provider credentials and controlled acceptance are available.
- Independent reviewer must reproduce the required matrix against the exact release SHA, store evidence in the restricted evidence store, and complete the release decision table. Current status remains **NO-GO / NOT SIGNED OFF**.

### Verification update — second CI attempt

A second GitHub Actions attempt was requested for all five workflows on security candidate SHA `7fb5a372bcc8cfed84599ad3e8122267aa0e7ef3` (Tests, dependency audit, CodeQL, non-database safety regression, Browser acceptance). Each attempt again completed in approximately 2–3 seconds with `runner_id=0`, an empty step list, and failure conclusion. No test command ran. This is a confirmed runner-allocation outage for both observed attempts; do not classify the code as test-failing or test-passing. Stop repeated retries until a healthy runner is available.

### Repository cleanup inspection

On the candidate branch, the README quick start already specifies the control-plane database, tenant database root, and shared corpus database separately. The repository root currently contains no `.patch`, `.diff`, or `.csv` fixture files; the existing CSV materials are under `docs/` and `tests/`. The corresponding deployment-preflight regression asserts the same hygiene invariant. No unnecessary file moves were made.

### PR triage disposition

- Router refactors #1438, #1439, #1441, #1443, #1444, #1446 and #1458 are already closed without merge. Their recorded close rationale is that exact-head checks had no executable test-step/log evidence. They remain closed; no replacement refactor PRs are being opened.
- #1455 (client CSV constraint handling), #1456 (duplicate scale smoke test), #1437 (scale/performance), and #1457 (deployment-guide clarification) are also already closed without merge after the same validation gate. #1437's history records #1456 as a superseded duplicate.
- Dependabot #1187 was closed, but its exact Buildx v4 head was preserved on #1467, whose successful checks were recorded and which was squash-merged to main at merge commit `97d09bcb52c92c8c83f87ae8fbaae246381c2c36`. Treat the dependency update as settled; do not reopen #1187.
- Do not reopen any closed PR merely to clear the queue. Reopen only after the relevant work is rebased and exact-head required checks execute successfully.

### CI retry outcome across all pilot candidates

The one permitted retry of each previously failed workflow on #1483 and #1484 has now also completed without runner allocation. Across all three pilot candidate PRs (#1483, #1484, #1485), the second attempts for Tests, Browser acceptance, dependency audit, CodeQL and applicable non-database safety workflows all report `runner_id=0` and zero steps. No workflow reached checkout, dependency installation, test execution, browser launch, or analysis. The retry budget is exhausted for this incident; do not loop retries. Required action is restoration of GitHub Actions runner capacity, followed by a single exact-head verification pass.

### Staging operator configuration checklist

Use the deployment secret manager; never place credential values in Git, PR comments, evidence filenames, or this handoff. Before strict preflight, the operator must provision:

- `COPILOT_ENV=production`, explicit `COPILOT_ALLOWED_HOSTS`, `COPILOT_SECURE_COOKIES=1`, the public bare HTTPS `COPILOT_PUBLIC_ORIGIN`, and `COPILOT_TRUSTED_PROXIES` containing only the exact edge-proxy IP or smallest controlled CIDR (never `*`).
- Identity SMTP: `COPILOT_EMAIL_SMTP_HOST`, `COPILOT_EMAIL_SMTP_PORT`, `COPILOT_EMAIL_SMTP_SECURITY=starttls` (or `ssl`), `COPILOT_EMAIL_FROM`, and a paired SMTP username/password if authentication is used. Then perform a controlled staging mailbox send/receive test; preflight configuration success is not delivery proof.
- MFA: set `MFA_ENFORCEMENT=admins_required` at minimum (or `all_required` if pilot policy requires it); generate a dedicated `MFA_ENCRYPTION_KEY` using `python manage.py gen-mfa-key`, store it in the secret manager, and ensure it differs from `BACKUP_KEY`. Do not paste the key into this repository or this handoff.
- All three absolute database paths: `COPILOT_CONTROL_DB`, `COPILOT_TENANT_DB_ROOT`, and `COPILOT_CORPUS_DB`, with distinct control/corpus files outside the tenant root and correct restrictive filesystem permissions.
- Production original-file storage and recovery: `COPILOT_OBJECT_STORAGE_BACKEND=s3`, `COPILOT_S3_BUCKET`, `COPILOT_S3_REGION`, `COPILOT_S3_KMS_KEY_ID`, `COPILOT_S3_RECOVERY_BUCKET`, `COPILOT_S3_RECOVERY_REGION`, and `COPILOT_S3_RECOVERY_KMS_KEY_ID`. Original and recovery buckets/keys must be distinct. Configuration is not a substitute for live encrypted upload, exact-version restore, reconciliation, retention and recovery acceptance.
- Review `LLM_URL` and processing approvals separately; keep matter-data processing disabled until the actual provider, data-processing terms, retention, and firm authorization have been reviewed. Keep live reminders and payment gateways disabled until their respective credentials and controlled tests exist.

Then run `python tools/deployment_preflight.py --strict` on the actual staging host under the same environment and service identity used by the application. Preserve the complete stdout, stderr, exit code, timestamp, candidate commit SHA, and redacted configuration inventory in the restricted evidence store. Do not call the preflight passed based on mocked unit tests or a local workstation configuration.

### Latest candidate-head check

After the handoff updates, the latest security candidate SHA is `b5dc3044237656386e5a498bdfa345c1b2a69675`. Its newly triggered Tests, Browser acceptance, dependency audit, CodeQL, and non-database safety workflows also terminated with `runner_id=0` and zero steps. This confirms the runner outage persists on a fresh commit, not only on a rerun. No more retries are justified until runner service is restored. The source-level review of the SSRF transport change confirmed that the configured HTTPS hostname is retained for TLS hostname verification while the TCP connection uses the validated pinned IP; this is code inspection only, not an executed network test.

## 2026-11-06 execution evidence

- Current candidate mapping and merge order: #1484 trusted proxy, #1485 invoice/security, then #1483 subscription/mobile UI. Keep all draft; merge only after exact-head green CI or explicit owner approval based on independent local results.
- On #1485 SHA `6406896dacef2de6f206f2471a23f3a2d9131610`, the fresh Browser, non-database safety, dependency audit, Tests and CodeQL runs completed with `steps=null`; job IDs and run IDs are listed in `BLOCKERS.md`. No retry was made.
- Local Python 3.12 tests were not run because this runtime has Python 3.13.5 only, no repository checkout and no outbound DNS/network. Counts are unavailable, not zero and not passing.
- The exact check annotation could not be retrieved via the available connector. The accessible job record is `conclusion=failure; steps=null`; the owner must capture the exact annotation from GitHub.
