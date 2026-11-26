# AI-2 manual stabilization checkpoint — 25 November 2026

**Status:** initial inspection and source review only. No runtime, browser, or repository tests executed by this checkpoint. This is not pilot approval.

## Access and baseline
- Repository: `abdelmalek384/legal_copilot_latest`; mainline inspected through authenticated GitHub file operations.
- Latest commit search result: `d20da92b38960b80516f86cd2daf5dd73904f718` (search result snapshot, not a locally checked-out HEAD).
- Open PR search returned no open PRs.
- Local checkout is unavailable: clone attempt failed resolving `github.com`. The local environment has Python 3.13.5, not the documented Python 3.12 test runtime.
- GitHub Actions intentionally not used because runner billing is unavailable.

## Static source review
- Reviewed portions of `tenant_catalog.py`, `tenant_storage.py`, `tests/test_tenant_catalog.py`, `tests/test_tenant_storage.py`, and `tests/test_tenant_database_preflight.py`.
- Existing safeguards include catalog/firm binding checks, strict database filename mapping, symlink and hard-link checks, SQLite sidecar checks, restrictive file mode checks, post-open revalidation, and revocation of cached connections on validation failure.
- Existing tests cover several synthetic path replacement, symlink, hard-link, permission, and firm-binding scenarios; they are not executed here.
- The pathname-to-SQLite-open race remains a documented residual risk. This review does not establish exploitability or closure. Restrict tenant storage write access to the application service account and administrators.
- No source changes or test results are claimed from this checkpoint.

## AI-2 progress (conservative implementation/evidence estimates)
| Workstream | Current | Evidence and outstanding |
|---|---:|---|
| Backend and existing workflows | 25% | Status and code source review only; CRUD journeys and persistence not run |
| Frontend and usability | 20% | Existing accessibility source contracts; browser acceptance not run |
| Mobile and Arabic/English UI | 15% | No RTL/LTR viewport acceptance |
| Security and tenant isolation | 30% | Existing hardening inspected; adversarial execution and two-firm acceptance outstanding |
| Documents and file handling | 30% | Existing safeguards documented; full upload/review/download journey not run |
| Deployment, backup and recovery | 15% | Operational documents exist; restore rehearsal outstanding |
| Local testing and regression | 5% | No tests run in this checkpoint |
| **Overall AI-2 assignment** | **20%** | Initial inspection; no runtime acceptance |

No completion percentage is increased merely because code or documentation exists.

## Evidence produced
- Repository status and blockers files inspected.
- Static code/test inspection of tenant catalog and tenant storage routing.
- No files changed; no commits or PRs created by AI-2 in this checkpoint.

## Next practical execution requirement
A repository checkout and supported runtime are required to execute the existing test modules, modify application code safely, verify focused regressions, and perform browser/two-firm/restore acceptance. Do not repeatedly retry the blocked clone or CI. Continue source inspection only where it can identify a concrete, reviewable issue; do not make untested security-sensitive edits or claim runtime validation.


## Follow-up static review (same date)
- Reviewed README local-validation instructions, `scripts/security_regression_check.sh`, `scripts/local_release_check.sh`, `tools/run_local_test_suite.py`, `tests/test_ci_runs_all_tests.py`, `docs/STATUS.md`, and `docs/BLOCKERS.md` through repository file access.
- The local runner is explicitly gated to Python 3.12 and mirrors one-line test invocations with job-level environment assignments. The security matrix is a curated list and includes missing-file reporting; the release check distinguishes BLOCKED from PASS and includes restore-drill, dependency, static-analysis, and compose checks.
- This confirms the intended manual test pathway, but cannot validate its execution, coverage completeness, or whether current modules all pass. No attempt was made to run it without a checkout or compatible environment.
- Reconfirmed the release remains NOT READY, with actual two-firm authorization acceptance, browser/RTL checks, and witnessed restore evidence still open. These require an execution environment/operational witness and are not closed by source review.
- This follow-up produced review evidence only; no implementation/test percentages are raised.


## Follow-up continuation — identity and firm-boundary review (25 November 2026)

- Continued with a source-only review rather than retrying the unavailable checkout or GitHub Actions. Inspected the separate-runtime authentication path, CSRF/Origin checks, firm-context resolution and switching, MFA policy gating, case authorization helper, and the existing focused regression suites.
- Confirmed that `tests/test_app_separate_database_runtime.py` currently defines 123 separate-runtime regression test methods, including synthetic cross-firm denial, stale-membership revocation, case-child/task isolation, document/original-file isolation, export boundaries, audit rollback, and firm lifecycle coverage. This is an inventory count only; none of those tests were executed in this continuation.
- Inspected `tests/test_firm_security_policy.py` coverage for per-firm MFA, multi-firm policy switching, and CSRF/Origin rejection. Existing test source is not runtime evidence.
- Found a documentation drift in `docs/identity_firm_membership_contract.md`: its closing text still described a shared-database runtime and unimplemented tenant routing, contradicting the current separate control-plane / per-firm tenant / shared-corpus architecture. Updated the document to preserve its historical design rationale, point to current implementation entry points, and distinguish ongoing operational acceptance from pre-implementation design decisions.
- Documentation correction committed directly to `main`: `1e7e4f0fffbdf721804aaa1a3dc6e5de3e7a45f8`. GitHub read-back verified the updated blob `595ec23ea276dc1a7bc8c9141be748dd90064dc3`.
- No application code, schema, migration, tenant data, or AI-1 retrieval/evidence logic changed. No test, runtime, browser, mobile, deployment, backup/restore, or security acceptance pass is claimed.

### Progress accounting

| Workstream | Previous | Current | Change | Basis |
|---|---:|---:|---:|---|
| Backend and existing workflows | 25% | 25% | 0 pp | Source review only; no workflow execution |
| Frontend and usability | 20% | 20% | 0 pp | No browser execution |
| Mobile and Arabic/English UI | 15% | 15% | 0 pp | No device/viewport execution |
| Security and tenant isolation | 30% | 30% | 0 pp | Source/test inventory only; adversarial execution outstanding |
| Documents and file handling | 30% | 30% | 0 pp | No upload/review/download runtime journey |
| Deployment, backup and recovery | 15% | 15% | 0 pp | No deployment or restore rehearsal |
| Local testing and regression | 5% | 5% | 0 pp | No repository tests executed |
| **Overall AI-2 assignment** | **20%** | **20%** | **0 pp** | One stale architecture document corrected; no runtime acceptance evidence added |

The narrow documentation correction is complete, but it does not justify raising the overall assignment estimate. The checkout/network and Python 3.12 runtime constraints remain; no further attempt was made to repeat those blocked operations.


## Follow-up continuation — Cairo-local frontend date consistency (25 November 2026)

- Identified and corrected a concrete application-layer defect rather than repeating the blocked test/clone work: the frontend's shared `today` key, local reminder summary, and calendar current-day marker used the browser's local timezone, while backend workflow dates are Cairo-local. Users operating the browser in a different timezone could see overdue/today/tomorrow labels that disagree with the server's dashboard/deadline date interpretation.
- Added a single IANA `Africa/Cairo` date-key helper with calendar-day offset arithmetic. Rewired shared overdue date comparisons, reminder today/tomorrow keys, the calendar's current-day calculation, and both research-memo fallback `requested_as_of` values. No persisted dates, legal calculations, backend API contracts, or database state changed.
- Added source-contract regression `test_frontend_deadline_and_reminder_dates_use_cairo_calendar_day`.
- Manually ran the helper logic in the available JavaScript runtime for three representative instants, including one second before Cairo midnight and exactly at Cairo midnight. All five expected Cairo date and next-day values matched, including midnight, the spring DST transition, year rollover, and leap day. This is helper-level evidence only.
- Commits: `8e49f5e` frontend date change; `4440fbf` initial regression; `2a41f9d` research-memo fallback correction; `86a3df7` fallback regression assertion; `2560310` initial status evidence; `2344935` initial progress evidence; `525a166` expanded status evidence. Read-back verified the frontend/test blobs and absence of the former UTC fallback expression. No repository Python test or browser session was run.

### Updated progress accounting

| Workstream | Previous | Current | Change | Evidence |
|---|---:|---:|---:|---|
| Backend and existing workflows | 25% | 25% | 0 pp | No backend workflow changes |
| Frontend and usability | 20% | 22% | +2 pp | Fixed Cairo/browser timezone mismatch for task/deadline, reminder, and calendar date display |
| Mobile and Arabic/English UI | 15% | 15% | 0 pp | Date helper is locale-independent, but no device/viewport acceptance added |
| Security and tenant isolation | 30% | 30% | 0 pp | No new security verification |
| Documents and file handling | 30% | 30% | 0 pp | No document workflow changes |
| Deployment and recovery | 15% | 15% | 0 pp | No deployment/recovery evidence added |
| Local testing and regression | 5% | 6% | +1 pp | Added a focused frontend source-contract regression and manually checked helper outputs; suite remains unexecuted |
| **Overall AI-2 assignment** | **20%** | **21%** | **+1 pp** | One user-visible date consistency defect corrected, regression authored, and commits read back |

These remain conservative implementation estimates, not test pass rates or pilot-readiness claims. Browser/device execution, Python 3.12 regression, two-firm acceptance, production deployment, and witnessed recovery remain NOT RUN/BLOCKED or outstanding.


## Follow-up checkpoint — document upload reliability — 2026-11-25

Implemented directly on `main` without GitHub Actions:

- Hardened the compact matter-document upload button in the `view(id)` workflow against duplicate submission and unhandled fetch/network failures; added explicit handling for authentication expiry and common server rejection statuses.
- The correct refresh callback is `again()`, supplied by the enclosing `view(id)` scope. An intermediate diagnosis that it was undefined in `documentIntelligencePanel` was incorrect; the final source preserves the existing callback and awaits it after success. The final IIFE-scoped busy flag avoids declaring a `const` inside the parent element argument list.
- Added `test_document_intelligence_upload_prevents_duplicate_submissions_and_refreshes` against the correct view-scope source region.
- Final corrective commits: `0c974267344683c1165e55438a9720a9dc3485f6` and `0417d22dda57221a02f5e44ae8f9f208ba34d602`. Earlier `51ad502`, `2ef7591`, and `b147786` commits are intermediate, superseded edits. Latest frontend/test blobs were read back.

| Workstream | Previous | Current | Change | Evidence |
|---|---:|---:|---:|---|
| Backend and existing workflows | 25% | 25% | 0 pp | No backend or retrieval changes |
| Frontend and usability | 22% | 23% | +1 pp | Upload action now guards duplicate clicks, reports failures, and handles expired sessions |
| Mobile and Arabic/English UI | 15% | 15% | 0 pp | No device/viewport validation added |
| Security and tenant isolation | 30% | 30% | 0 pp | No new security verification; existing authenticated API/CSRF conventions retained |
| Documents and file handling | 30% | 32% | +2 pp | Duplicate upload protection, clear error reporting, and successful refresh through the existing case-view callback |
| Deployment and recovery | 15% | 15% | 0 pp | No deployment/recovery evidence added |
| Local testing and regression | 6% | 7% | +1 pp | Added focused source-contract regression; not executed |
| **Overall AI-2 assignment** | **21%** | **22%** | **+1 pp** | One user-visible upload workflow corrected and regression contract added; direct commits read back |

These are conservative implementation/evidence estimates, not test pass rates. Python suite, browser upload, mobile, two-firm acceptance, production deployment, and backup/restore rehearsal remain unrun/outstanding. No claim is made that storage integration or production upload behavior has been runtime-validated.


## Follow-up checkpoint — idempotent task completion — 2026-11-25

- Fixed duplicate case-history writes in `POST /tasks/{tid}/done`: the database update now changes only a task not already marked done, and the completion event is emitted only when the conditional update changes a row. This also closes the concurrent double-submit window for duplicate event creation.
- Preserved the route response and existing authorization path; no migration, schema, deadline-calculation, or retrieval changes.
- Extended the existing separate-database firm workflow test to call the endpoint twice and assert one completion event and a final `done` status.
- Commits: `c95b01ae8814bd5e673418ff27bb2496ff63aa0a`, `99ddcb8b88b48e54463f50a699d38ac78eed2657`. Read-back verified both updated files. Test execution remains unavailable; this is authored regression coverage, not a passing test result.

| Workstream | Previous | Current | Change | Evidence |
|---|---:|---:|---:|---|
| Backend and existing workflows | 25% | 26% | +1 pp | Task completion now records one event despite repeated/concurrent completion requests |
| Frontend and usability | 22% | 23% | +1 pp | Compact document upload blocks duplicate submission and reports failures |
| Mobile and Arabic/English UI | 15% | 15% | 0 pp | No device/viewport acceptance added |
| Security and tenant isolation | 30% | 30% | 0 pp | No new isolation claims; existing authorization path retained |
| Documents and file handling | 30% | 32% | +2 pp | Upload guard/error handling and correct post-success case refresh |
| Deployment and recovery | 15% | 15% | 0 pp | No deployment/recovery evidence added |
| Local testing and regression | 7% | 8% | +1 pp | Added repeat-completion regression assertion; not executed |
| **Overall AI-2 assignment** | **22%** | **23%** | **+1 pp** | One additional backend workflow defect fixed with focused regression coverage |

Estimates reflect implemented changes and authored evidence, not test pass rates or pilot readiness. Python 3.12 suite, browser/device acceptance, two-firm runtime acceptance, deployment, and backup/restore rehearsal remain outstanding.


## Follow-up checkpoint — idempotent legal-deadline completion — 2026-11-25

- Hardened `POST /deadlines/{did}/done` against repeated/concurrent requests: the conditional update writes the completion event only when the status transition changes a row.
- Extended the existing separate-database workflow test to call the deadline completion endpoint twice, verify final status `done`, and assert exactly one completion event. The test uses the persisted deadline ID; the create endpoint does not return an ID.
- Commits: `0162284af7f1dbc077dce26dd7037736ec65a034`, `8ea6a6ef22bc408f06e2e15ecb372a7e3c09bf5e`, `ece506ee8c8792ca7ecd694f57bfb565319effb6`, and `e1af882025a67222ffcc0855e48affc01a5df956`. The latter corrects the regression's ID lookup. Test not executed.

| Workstream | Previous | Current | Change | Evidence |
|---|---:|---:|---:|---|
| Backend and existing workflows | 26% | 27% | +1 pp | Both task and legal-deadline completion routes now avoid duplicate history events on repeated requests |
| Frontend and usability | 23% | 23% | 0 pp | No new frontend change in this checkpoint |
| Mobile and Arabic/English UI | 15% | 15% | 0 pp | No device/viewport acceptance added |
| Security and tenant isolation | 30% | 30% | 0 pp | Existing authorization checks preserved; no new isolation claims |
| Documents and file handling | 32% | 32% | 0 pp | No new document change in this checkpoint |
| Deployment and recovery | 15% | 15% | 0 pp | No deployment/recovery evidence added |
| Local testing and regression | 8% | 9% | +1 pp | Added repeated-deadline completion assertions; not executed |
| **Overall AI-2 assignment** | **23%** | **24%** | **+1 pp** | A second state-transition endpoint hardened with regression coverage |

Percentages remain implementation/evidence estimates, not test pass rates. Python tests, browser/mobile acceptance, two-firm runtime validation, production deployment, and backup/restore rehearsal remain outstanding.


## Follow-up checkpoint — guarded task/calendar actions — 2026-11-25

- Added one frontend completion-action helper that disables the button during the request/refresh, ignores repeated clicks, uses the existing API helper, and catches the resulting rejection after the helper surfaces its message.
- Applied it to the task list and calendar agenda for both task and legal-deadline completion. This complements the backend idempotency fixes; it is not a substitute for them.
- Added a source-contract test asserting the lock/unlock behavior and all three call sites.
- Commits: `cf2eb516c4c09a3ffe113e3c01a43f5e7b3bebd6`, `ca93d5c55a2c3afa5c6daf830f58351cefe165dc`. Source/test read-back only; no browser or Python execution.

| Workstream | Previous | Current | Change | Evidence |
|---|---:|---:|---:|---|
| Backend and existing workflows | 27% | 27% | 0 pp | Task and deadline completion endpoints already made idempotent in preceding checkpoint |
| Frontend and usability | 23% | 24% | +1 pp | Task and calendar completion controls now block repeat clicks while updating |
| Mobile and Arabic/English UI | 15% | 15% | 0 pp | No device/viewport acceptance added |
| Security and tenant isolation | 30% | 30% | 0 pp | No new isolation claims |
| Documents and file handling | 32% | 32% | 0 pp | No document changes in this checkpoint |
| Deployment and recovery | 15% | 15% | 0 pp | No deployment/recovery evidence added |
| Local testing and regression | 9% | 10% | +1 pp | Added frontend source-contract assertions; not executed |
| **Overall AI-2 assignment** | **24%** | **25%** | **+1 pp** | Task/deadline completion now guarded in UI and idempotent in backend, with authored regression coverage |

These are implementation/evidence estimates only. Python tests, browser/mobile acceptance, two-firm runtime validation, production deployment, and backup/restore rehearsal remain outstanding.


## Follow-up checkpoint — invoice transition race guard — 2026-11-25

- Added row-count checks to invoice issuance and voiding conditional updates. Audit events are now appended only if the requested state transition actually changed one row; stale state transitions return HTTP 409 and the tenant rollback decorator rolls back uncommitted writes.
- Added a focused invoice route regression covering issue/void success, repeat-request conflicts, and exactly one event per transition.
- Commits: `06b632a3a26a0d3a63bf167b4832e676411ff2a9`, `03e6e892761109b02bcd821172a7647ad6068c72`. GitHub read-back confirmed code/test. Test not executed.

| Workstream | Previous | Current | Change | Evidence |
|---|---:|---:|---:|---|
| Backend and existing workflows | 27% | 28% | +1 pp | Invoice issue/void now guard against stale state transitions before audit append |
| Frontend and usability | 24% | 24% | 0 pp | No UI change in this checkpoint |
| Mobile and Arabic/English UI | 15% | 15% | 0 pp | No device/viewport acceptance added |
| Security and tenant isolation | 30% | 30% | 0 pp | No new isolation claim |
| Documents and file handling | 32% | 32% | 0 pp | No document change |
| Deployment and recovery | 15% | 15% | 0 pp | No deployment/recovery evidence added |
| Local testing and regression | 10% | 11% | +1 pp | Added issue/void transition regression; not executed |
| **Overall AI-2 assignment** | **25%** | **26%** | **+1 pp** | One financial state-transition race guard with focused test coverage |

These remain implementation/evidence estimates, not test pass rates. The Python suite, browser/device acceptance, two-firm runtime acceptance, production deployment and backup/restore rehearsal remain outstanding.


## Follow-up checkpoint — guarded invoice controls — 2026-11-25

- Updated the shared UI action helper to support preflight confirmation/payload generation and button variants while retaining the repeat-click lock.
- Applied it to invoice issue and void controls. Issue confirmation and required void reason remain in place; both controls disable during request plus invoice-list refresh.
- Added frontend source-contract regression assertions for helper lock/unlock, prepare callback, and issue/void call sites.
- Commits: `43ea40b8f3ca672e26b7e88924e1f61243dcccfa`, `f3f6029ef230b11aa63078710076989f351c3c23`. Read-back only; tests not executed.

| Workstream | Previous | Current | Change | Evidence |
|---|---:|---:|---:|---|
| Backend and existing workflows | 28% | 28% | 0 pp | Backend invoice transition row-count guard completed in prior checkpoint |
| Frontend and usability | 24% | 25% | +1 pp | Invoice issue/void controls now prevent repeat clicks while request and refresh run |
| Mobile and Arabic/English UI | 15% | 15% | 0 pp | No device/viewport acceptance added |
| Security and tenant isolation | 30% | 30% | 0 pp | No new isolation claims |
| Documents and file handling | 32% | 32% | 0 pp | No document change |
| Deployment and recovery | 15% | 15% | 0 pp | No deployment/recovery evidence added |
| Local testing and regression | 11% | 12% | +1 pp | Added invoice issue/void frontend contract assertions; not executed |
| **Overall AI-2 assignment** | **26%** | **27%** | **+1 pp** | Invoice transitions now guarded in backend and UI with authored regression checks |

These percentages measure implementation/evidence progress, not runtime verification or pilot readiness. Python suite, browser/mobile, two-firm acceptance, deployment, and backup/restore remain outstanding.


## Follow-up checkpoint — invoice payment retry safety — 2026-11-25

- Added a payment-button busy lock and stable idempotency-key lifecycle. The same payment payload retains its key after ambiguous failure, preventing a network retry from becoming a second distinct ledger payment; changing the payload rotates the key; success clears it.
- Added source-contract regression assertions for duplicate-click lock, payload fingerprint, key reuse, success reset, and unlock.
- Commits: `560c70a951044c35fe4a1b7702eca95813d7e2eb`, `3cc3a7d04cb9939fb6dae6b81118144c19b0b5b5`. Source/test read-back only; test not executed.

| Workstream | Previous | Current | Change | Evidence |
|---|---:|---:|---:|---|
| Backend and existing workflows | 28% | 28% | 0 pp | No backend change in this checkpoint |
| Frontend and usability | 25% | 26% | +1 pp | Payment submission now guards repeat clicks and reuses idempotency key for same-payload retries |
| Mobile and Arabic/English UI | 15% | 15% | 0 pp | No device/viewport acceptance added |
| Security and tenant isolation | 30% | 30% | 0 pp | No new isolation claim |
| Documents and file handling | 32% | 32% | 0 pp | No document change |
| Deployment and recovery | 15% | 15% | 0 pp | No deployment/recovery evidence added |
| Local testing and regression | 12% | 13% | +1 pp | Added invoice payment retry contract test; not executed |
| **Overall AI-2 assignment** | **27%** | **28%** | **+1 pp** | Financial UI now pairs backend idempotency with retry-stable client keys |

These are implementation/evidence estimates, not test pass rates. Runtime payment behavior, browser acceptance, Python tests, two-firm validation, production deployment and backup/restore remain outstanding.

- Follow-up test-source correction: `db6da070cf6e62cffbda0a45f3ce06d182851638` aligns the invoice frontend regression tests with the actual `const renderInvoices=` declaration. Final source-marker read-back passed; test execution remains outstanding.


## Follow-up checkpoint — resilient global search partial results — 2026-11-25

- Found a user-facing failure mode in the shared workspace search: it queried matters, clients, and documents with one `Promise.all`, so a single unavailable endpoint rejected the entire operation and hid successful results from the other two sections.
- Changed the three independent searches to `Promise.allSettled`. Each successful section now renders its results even if another section fails. The UI reports when results are partial, distinguishes total search unavailability from a genuine empty result, and keeps the status message accessible with `role=status` and `aria-live=polite`.
- Added `test_global_search_keeps_successful_sections_when_another_section_fails` to the frontend UX contract suite. It checks independent result handling and the partial/total failure messages. Test is authored but **not executed**; no browser or runtime pass is claimed.
- Added a monotonically increasing search-request token. Typing a new query invalidates older in-flight requests, stale responses cannot overwrite newer results, and stale requests cannot re-enable the search button while a newer request is active. The same regression now checks this race guard.
- An isolated JavaScript control-flow simulation exercised a mixed success/failure result set and a query invalidated while requests were pending: partial results remained distinguishable, the stale response was suppressed, and invalidation left the button enabled. This does not execute the application bundle or browser lifecycle.
- Commits on `ai2/global-search-partial-results`: `b7872ce`, `88b3c96`, `9569e49`, and `f2ab7eb`. GitHub read-back verification completed for the frontend, regression contract, and this progress record.

| Workstream | Previous | Current | Change | Evidence |
|---|---:|---:|---|
| Backend and existing workflows | 28% | 28% | 0 pp | No backend change |
| Frontend and usability | 26% | 27% | +1 pp | One failed search endpoint no longer suppresses successful matter/client/document results |
| Mobile and Arabic/English UI | 15% | 15% | 0 pp | No viewport/device acceptance added |
| Security and tenant isolation | 30% | 30% | 0 pp | Existing endpoint authorization is unchanged |
| Documents and file handling | 32% | 32% | 0 pp | No document storage change |
| Deployment and recovery | 15% | 15% | 0 pp | No deployment/recovery evidence added |
| Local testing and regression | 13% | 14% | +1 pp | Added focused frontend contract regression; not executed |
| **Overall AI-2 assignment** | **28%** | **29%** | **+1 pp** | Improved an existing lawyer-facing workflow and added focused regression coverage |

These are implementation/evidence estimates, not test pass rates or pilot-readiness claims. Python tests, browser acceptance, two-firm validation, production deployment, and backup/restore rehearsal remain outstanding.


## Follow-up correction — effective global-search input handler — 2026-11-26

- A second assignment to `globalSearchInput.oninput` later in the same initialization block overwrote the earlier handler. The earlier handler invalidated stale requests and refreshed the command palette, but the final effective handler only cleared results. This made the source-level race assertion insufficient to prove the actual last assignment retained the behavior.
- Corrected the final/effective handler so every input change increments the request token, re-enables the button after invalidating an in-flight search, and refreshes command-palette suggestions for `>` queries. Normal search input still clears old results.
- Strengthened the frontend contract test to inspect the **last** `oninput` assignment, not merely search the file for the presence of the token string. It now asserts both invalidation and command-palette refresh in the effective handler.
- Commits: `d2c5a449c3bd2f165e035cde8a88d2bd2a585470` (frontend) and `1083af7a1d79a7c986a350c2010cdecac08bda4f` (regression). GitHub file read-back and runtime checks remain pending; Python/browser tests were not executed.

| Workstream | Previous | Current | Change | Evidence |
|---|---:|---:|---:|---|
| Backend and existing workflows | 28% | 28% | 0 pp | No backend change |
| Frontend and usability | 27% | 28% | +1 pp | Final input handler now actually preserves stale-request invalidation and command suggestions |
| Mobile and Arabic/English UI | 15% | 15% | 0 pp | No device/viewport acceptance |
| Security and tenant isolation | 30% | 30% | 0 pp | No new isolation evidence |
| Documents and file handling | 32% | 32% | 0 pp | No document change |
| Deployment and recovery | 15% | 15% | 0 pp | No deployment/recovery evidence |
| Local testing and regression | 14% | 15% | +1 pp | Regression now checks the last/effective handler; test not executed |
| **Overall AI-2 assignment** | **29%** | **30%** | **+1 pp** | Fixed an overwrite defect and made the regression detect this class of false-positive source check |

These are implementation/evidence estimates, not test pass rates or pilot-readiness claims. Python 3.12 tests, browser acceptance, two-firm validation, production deployment, and backup/restore rehearsal remain outstanding.


## Follow-up checkpoint — global search integrated; baseline failures isolated — 2026-11-26

- Manually reviewed the PR #2035 head and its three-file diff against `main`. The branch was 10 commits ahead and 0 behind; the changes were limited to global-search behavior, its frontend contract test, and this progress record.
- Merged PR #2035 by squash after inspecting the failed workflow logs and checking the base-branch JavaScript independently. Merge commit: `e01034b459606938ed218bb400821f56144d88c1`.
- The workflow failures were not introduced by this PR:
  - The two document-classification failures assert source fragments that do not match the current `app.py` implementation; neither `app.py` nor those tests were changed in this PR.
  - The two legal release-readiness failures concern duplicate/ragged coverage-matrix handling and a stale expected message; neither the validator nor its tests were changed in this PR.
  - The browser acceptance suite reports `missing ) after argument list`. Compiled the inline script using the available JavaScript runtime for both the base `main` file and the PR branch: both fail with the same parse error. The defect therefore predates PR #2035 and remains a release blocker; no claim of browser acceptance is made.
  - Dependency security audit and CodeQL passed. The focused AI-1 source-trust workflow passed.
- The merged global-search implementation preserves successful matter/client/document sections when one endpoint fails, distinguishes partial from total failure, and suppresses stale responses. The final/effective input handler now invalidates requests and refreshes command-palette results. The regression contract checks the final handler assignment.
- The focused frontend regression was authored but not executed in a local Python 3.12 environment. The merge is a reviewed integration decision, not a claim that the full test suite or browser acceptance passed.

| Workstream | Previous | Current | Change | Evidence |
|---|---:|---:|---:|---|
| Backend and existing workflows | 28% | 28% | 0 pp | No backend changes |
| Frontend and usability | 28% | 29% | +1 pp | Resilient partial search and stale-response suppression integrated into main |
| Mobile and Arabic/English UI | 15% | 15% | 0 pp | No device/viewport acceptance |
| Security and tenant isolation | 30% | 30% | 0 pp | CodeQL and dependency audit passed; no new tenant-boundary evidence |
| Documents and file handling | 32% | 32% | 0 pp | No document workflow change |
| Deployment and recovery | 15% | 15% | 0 pp | No deployment/restore rehearsal |
| Local testing and regression | 15% | 16% | +1 pp | Failure causes isolated; baseline parse defect independently reproduced; focused contract still needs local execution |
| **Overall AI-2 assignment** | **30%** | **31%** | **+1 pp** | A focused existing workflow fix was integrated and the unrelated baseline release blockers were separated |

These are conservative implementation/evidence estimates, not test pass rates or pilot-readiness claims. Browser acceptance remains blocked by the pre-existing inline JavaScript syntax error. The document and legal coverage-matrix contract failures remain open. Two-firm acceptance, production deployment, and witnessed backup/restore rehearsal remain outstanding.


## Follow-up checkpoint — repair stale regression contracts — 2026-11-26

- Reviewed the exact failing test logs and source on `main`; repaired the test contracts without changing application behavior or relaxing legal/security assertions.
- `tests/test_document_classifications.py` now checks the actual qualified review-column sequence (`r.original_text,r.reviewed_text`) and the actual firm-scoped SQL parameter tuples, including the optional client filter. The old assertions expected outdated source fragments and omitted the new client-filter parameters.
- `tests/test_legal_release_readiness.py` had duplicate-header and ragged-row CSV fixtures containing literal backslash-n text rather than line breaks. Corrected both fixtures to contain actual CSV records. Updated the diagnostic assertion to match the validator's existing explicit message that requires unique headers and the three mandatory columns.
- Changes were committed directly to `main` in `22c5cad`, `53ff27f`, and `8541ab2`. Read-back of `app.py`, both tests, and the validator was used to check the changed assertion fragments against the actual implementation. A small independent source-contract check confirmed all five revised expectations match the retrieved source.
- Important limitation: the Python test modules were not executed in the supported Python 3.12 environment, so these are corrected test contracts, not claimed passing test runs. No application runtime, database, legal evidence, permission state, or production data changed.

| Workstream | Previous | Current | Change | Evidence |
|---|---:|---:|---:|---|
| Backend and existing workflows | 28% | 28% | 0 pp | No backend behavior changed |
| Frontend and usability | 29% | 29% | 0 pp | No frontend behavior changed |
| Mobile and Arabic/English UI | 15% | 15% | 0 pp | No device acceptance |
| Security and tenant isolation | 30% | 30% | 0 pp | No security control changed |
| Documents and file handling | 32% | 32% | 0 pp | Only stale source-contract assertions corrected |
| Deployment and recovery | 15% | 15% | 0 pp | No deployment/recovery evidence |
| Local testing and regression | 16% | 18% | +2 pp | Corrected two failing document contract assertions, two malformed CSV fixture assertions, and one stale diagnostic expectation; source fragments independently checked, runtime tests still unexecuted |
| **Overall AI-2 assignment** | **31%** | **32%** | **+1 pp** | Five failing regression expectations corrected against current source; no runtime pass claimed |

The browser acceptance syntax error remains a separate pre-existing blocker. It was reproduced on both the PR branch and base main. It is not counted as fixed by these test-only changes. AI-2 remains not pilot-ready pending execution of the corrected suites, browser acceptance, two-firm workflow checks, and restore rehearsal.


## Browser failure diagnostics — 2026-11-26

- Updated `tests/browser/test_acceptance.py` to retain the JavaScript `pageerror` stack trace instead of only `str(error)`. The previous failure output discarded the source URL and line/column information needed to locate the inline-script parse defect.
- Commit: `c1d51ca7cd272910d47c876f7d4c092b029a0743`.
- Rechecked the current inline script with the available V8 parser and confirmed it still fails with `SyntaxError: missing ) after argument list`. Historical mainline snapshots back through the inspected commit range also fail; this is not a regression introduced by the recent search work.
- The diagnostic change is not a fix and no browser suite was run. No completion percentage is increased for this change. Next actionable step is to run browser acceptance in a supported runtime and use the preserved stack to repair the precise source location; do not guess at a 400 KB inline script.


## AI-1 source-locator permission hygiene — 2026-11-26

- Extended `tools/validate_source_permission_register.py` so optional `file_url`, `item_page_url`, `repository_homepage_url`, and `official_pdf_url` fields use the same HTTPS/no-credentials/no-fragment/no-signed-query validation as the primary source and permission-evidence locators. The nested `secondary_metadata_lead` now requires a clean HTTPS URL and a non-empty summary.
- Added two focused tests in `tests/test_source_permission_register.py` covering credentials, fragments, signed query parameters, and malformed nested metadata. The module now contains 43 tests (41 before this change).
- Applying the stricter contract exposed eight persisted Manshurat `file_url` values containing expiring `token=` query parameters. Cleared those transient URLs, retained the stable source-page locators, and annotated the access status to record that the tokenized locator was omitted. No source permission was upgraded and no legal text was added.
- Commits: `8bb5285` (validator), `8ed259a` (tests), `906019a` (register cleanup).
- Static read-back checked all 199 records and the eight optional URL fields: no credentials, fragments, non-HTTPS schemes, or recognized signed/token query parameters remain. This is a static consistency check; Python test execution is still outstanding.
- AI-1 implementation estimate: 86% → 87% (+1 percentage point). This reflects a bounded source-registry validator/integrity improvement, not runtime validation or lawyer approval. AI-2 remains 32% (no change).



## AI-1 claim-polarity guard continuation — 26 November 2026

- Static review identified a specific omission in the optional lexical claim-support screen: English `shalln't` was not treated as a negated obligation, and the positive-obligation matcher could classify the token `shall` inside that contraction as positive.
- Updated the positive obligation matcher to exclude `shall not` and `shalln't`; added the contraction to negated-obligation and prohibition matching.
- Added a fictional regression covering positive claim versus `shalln't` evidence and faithful negative wording. The test is committed but not executed.
- Commits: `c296694` (guard) and `cd8b291` (regression).
- AI-1 estimate: 87% → 88% (+1 pp) for a concrete claim-polarity defect and focused regression added. AI-2 remains 32%.
- Validation limit: GitHub file read-back only; Python test suite, runtime and browser are not available. This optional lexical guard is not semantic legal validation.


## AI-2 action-feedback reliability — 26 November 2026

- Updated the shared `actionButton` wrapper in `static/index.html`: task/workflow POST failures no longer silently disappear; users receive a bilingual generic retry message, while the control is still re-enabled in `finally` and duplicate-click protection remains in place.
- Commit: `87a576a`.
- Static read-back confirmed the shared wrapper now reports errors and preserves busy-state cleanup. No runtime/browser tests were run.
- AI-2 front-end/usability estimate: 29% → 30% (+1 pp). AI-2 overall estimate: 32% → 33% (+1 pp) for a small cross-workflow usability reliability fix. Testing/regression remains unchanged at 18%.

- Follow-on logout reliability fix: the three logout controls now warn if the server-side logout POST cannot be confirmed, while still clearing the local UI/session cache. Commit: `86c1b7b`. This avoids presenting local screen closure as confirmed server invalidation. Static read-back only; no browser execution.
- AI-2 front-end/usability estimate: 30% → 31% (+1 pp). AI-2 overall: 33% → 34% (+1 pp). Regression testing remains 18% because no test execution occurred.


## AI-2 invitation acceptance atomicity guard — 26 November 2026

- Hardened new-identity and existing-identity invitation acceptance: the invitation consumption UPDATE now checks that exactly one pending invitation transitioned to consumed before any membership/security/lifecycle success events can commit. Unexpected zero-row transitions return HTTP 409 and roll back the surrounding transaction.
- Added a regression assertion that invitation replay leaves exactly one `invitation_accepted` lifecycle event (alongside the existing single-use-token/user-count checks).
- Commits: `dbe84be` (app guard), `0a97923` (regression assertion). GitHub read-back only; tests were not executed in this environment.
- AI-2 overall estimate: 34% → 35% (+1 pp); backend/workflow reliability: 28% → 29% (+1 pp). Security/tenant isolation estimate: 30% → 31% (+1 pp) for invitation-state integrity. Testing/regression remains 18% because execution is unavailable.
