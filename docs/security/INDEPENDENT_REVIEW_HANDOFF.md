# Independent security review handoff — pilot release

**Status: NOT READY FOR SIGN-OFF.** This package is a reviewer brief and evidence checklist, not a statement that the controls have passed. The reviewer must run the exact candidate commit in an isolated environment and attach the raw test results to the restricted evidence store.

## Scope and acceptance rule

Review the application as a multi-tenant legal case-management system. Test both read and write paths, direct object identifiers, alternate HTTP methods, exports/print/receipt endpoints, background tasks, and API/UI parity. For every denial, verify that the response does not disclose whether another firm's object exists. Use synthetic firms A and B with unique sentinel values; never use real client data.

A category passes only when: (1) positive control proves the test reaches the intended code path; (2) negative cross-tenant/unauthorized attempt is denied; (3) no sentinel, metadata, file bytes, or side effect leaks; (4) audit/session state is checked where relevant; and (5) the exact command, commit SHA, environment, and output are retained.

## Existing repository evidence found during preparation

These are pointers for reviewer orientation, **not proof of current passing tests**:

- `tests/test_invoice_payment_routes.py`: payment idempotency, partial/full payment, overpayment rejection, append-only ledger, receipt binding and cross-firm receipt denial. PR #1465 additionally asserts the `payment_recorded` event includes the immutable payment ID and amount, and explicitly denies cross-firm invoice reads/payment writes.
- `tests/invoice_test_support.py`: shared invoice test setup; inspect fixture isolation and role membership.
- `tests/browser/test_acceptance.py`: browser test `test_cross_firm_case_identifier_does_not_reveal_other_firm_sentinel`.
- `tests/test_security_transport_config.py`: unsafe remote HTTP `LLM_URL` must not trigger a network call, even with processing approval.
- `tests/test_deployment_preflight.py`: endpoint-scheme validation for `LLM_URL`.
- `docs/llm_data_processing_policy.md`: approval gates, response-size bounds, and sources-only fallback policy.
- `tests/test_trusted_proxy_client_ip.py`: forwarded-header spoofing from an untrusted peer and trusted-proxy parsing. The pilot proxy regression PR adds explicit wildcard rejection.
- `tests/test_mfa_account_security.py`: admin enrollment requirement, TOTP replay rejection, one-time recovery codes, throttling, recovery-code rotation and reenrollment safeguards. PR #1465 adds a non-admin `all_required` enrollment gate; exact-head execution remains outstanding. Continue review for session lifecycle and bypass permutations.
- `tests/test_client_csv_import.py` and `tests/test_case_csv_import.py`: firm-admin authorization, bounded rows/fields, malformed-input rollback, duplicate handling, and tenant separation. PR #1465 adds an import-to-invoice-export regression for a formula-like imported case title; it remains draft and unexecuted until CI recovers. Expand to leading tabs/CR/LF/whitespace and all formula prefixes (`=`, `+`, `-`, `@`) in each exported text field.
- `tests/test_subscription_billing_routes.py`: trial, manual payment submission, platform approval, and firm scoping. PR #1465 adds explicit platform-admin-only payment rejection coverage; it remains draft/unexecuted pending CI. Reviewer must still enumerate all platform-admin endpoints and role combinations.
- `tests/test_first_run_wizard_api.py`: first-run checklist/profile isolation and completion tracking; it is API coverage, not phone acceptance.
- `tests/test_security_transport_config.py`: request-body limits, content-length validation, remote LLM HTTPS restrictions and redirect refusal. PR #1465 adds rejection of private/link-local/loopback HTTPS literals, hostnames with any non-global DNS answer, DNS lookup suppression until model-processing approval, and a custom HTTPS connection that pins the validated public IP while preserving hostname-based TLS validation; it remains draft/unexecuted. Independent reviewer must still verify the full connection path under a controlled DNS-rebinding harness and confirm proxy/egress assumptions.
- `tests/test_research_prompt_injection_boundary.py`: JSON-quoted, explicitly untrusted retrieved passages; newline/instruction injection containment; citation metadata separation; and fail-closed firm-data approval for case-scoped/follow-up prompts. PR #1465 adds a case-scoped adversarial matter-passage regression; it remains draft/unexecuted. Extend to actual uploaded/OCR-derived chunks, metadata/filename payloads and retrieval authorization checks.
- `tests/test_document_extraction_budget.py`: incremental PDF/DOCX text-budget enforcement and unsupported-extension rejection for matter-document extraction. PR #1465 adds 501-page pre-extraction rejection and DOCX zip-expansion rejection regressions; it remains draft/unexecuted pending CI.
- `tests/test_pdf_ocr_fallback.py`: OCR only for missing-text pages, 30-page OCR cap, and 1 MiB OCR output budget. The runtime also supplies a 30-second per-page OCR timeout; PR #1465 asserts timeout argument propagation and fail-closed handling. Reviewer should still verify this through the upload route and worker/concurrency controls.
- `tests/test_import_laws_bundle.py`: legal-corpus PDF size/page limits, invalid limit rejection, exact-byte hashing and signature checks. This is a separate importer and does not substitute for matter-upload route abuse tests.
- `tests/test_frontend_ux_contract.py` and `tests/browser/test_acceptance.py`: navigation landmark, phone-width focus behavior, keyboard operation and responsive UI contracts. PR #1463 increases phone text to 15px, tightens the login/password-row layout, and adds phone-width first-run wizard/setup-health and expired-subscription/billing overflow assertions; it remains draft/unexecuted. Browser execution and physical-device acceptance remain separate gates.

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
