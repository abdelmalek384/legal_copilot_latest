- Live SMTP acceptance for the first-run test reminder is blocked pending provider credentials and a controlled mailbox; route tests use a fake SMTP sender.
- 2026-11-04: The 155-question live retrieval/abstention baseline is not measurable in this session because no authenticated local Legal Copilot API endpoint or evaluation account is available; draft questions also have no lawyer-approved relevance labels, so answer correctness must remain unscored.
- 2026-11-04: PR #1404's optional claim-support polarity guard still fails the same three English/Arabic negated-obligation regressions after three attempts; stop speculative retries and resume only with a local minimal reproduction that identifies why the guard is bypassed.
- 2026-11-06: Pilot PRs #1459, #1463 and #1465 have failing required GitHub Actions workflows. The job-log endpoint returns 404 BlobNotFound, so the failures cannot be diagnosed or counted as executed tests from this environment. Keep these PRs unmerged/draft until a healthy runner produces exact-head results.
- 2026-11-06: Existing prompt-injection tests cover JSON-quoted untrusted retrieved passages, but require extension for firm-uploaded/OCR-derived matter text and metadata vectors. Matter-document PDF/DOCX extraction budgets and legal-import PDF size/page limits have unit coverage; full upload-route abuse, OCR worker timeout/concurrency and malformed/encrypted-file acceptance remain outstanding in docs/security/INDEPENDENT_REVIEW_HANDOFF.md.
- 2026-11-06: Physical-device acceptance remains unperformed. Browser automation is not a substitute for witnessed Android/iOS or desktop-device evidence in Arabic RTL and English LTR.
- 2026-11-06: Proposed `LLM_URL` SSRF hardening now includes non-global destination rejection and a custom HTTPS connection pinned to the validated public IP, retaining the original hostname for TLS. Independent controlled DNS-rebinding integration testing and production egress verification remain outstanding before SSRF can be signed off.
- 2026-11-06: GitHub code search surfaced no root-level `.patch` or `.csv` files (the visible CSV corpus/evidence files are under `docs/`). PR #1465 adds a repository-root glob regression to verify there are no misplaced root fixtures; it is unexecuted pending CI.
- 2026-11-06: Dependabot #1187 had five green checks on its exact head SHA. Its branch had been deleted after closure, so the same commit was restored as PR #1467 and squash-merged; `docker/setup-buildx-action@v4` is now on main.
- 2026-11-06: Independent security-review handoff and its README entry were merged in PR #1462. It remains a reviewer plan, not an independent sign-off.
- 2026-11-06: PRs #1459/#1471 (trusted-proxy wording) and #1463/#1473 (older mobile UX branches) were closed as superseded. Current-main replacements are #1484 (wildcard-proxy rejection regression and deployment wording) and #1483 (15px phone text/login layout, named navigation, 423-to-billing recovery, Arabic/English first-run/setup-health phone coverage, and expired-subscription phone flow). Both remain draft/unexecuted pending healthy CI.
- 2026-11-06: Payment audit-event detail assertions (partial and final payment IDs/amounts/method), cross-firm invoice read/payment-write denial, SSRF, prompt-injection, CSV, MFA, platform-payment authorization, and PDF/DOCX/OCR resource-limit regressions are consolidated in current-main PR #1485. Older PR #1465 and duplicate #1472 were closed. No new runtime security test has exact-head execution evidence because GitHub Actions jobs continue to fail before any steps or log URL are reported.
- 2026-11-06: The strict deployment preflight has not been run against a production-like environment with real SMTP, public origin, separate MFA/backup keys, accepted database manifest, S3/KMS and three database paths. Do not fabricate credentials or enable live reminders/payment gateways; stage these only with operator-owned credentials and mailbox.
- 2026-11-06: Browser first-run setup-health acceptance now has a 390×844 automated viewport assertion in PR #1473. Real-device acceptance (physical phone and desktop, Arabic and English) remains outstanding and must be recorded in the restricted evidence store without committing screenshots.
- 2026-11-06: Security handoff coverage pointers and production public-origin/manual-payment boundary guidance were merged in PRs #1481 and #1482. Security regression suite, mobile UX acceptance and trusted-proxy wildcard regression are consolidated on current-main draft PRs #1485, #1483 and #1484 respectively; their workflows still fail before test steps/logs, so none is merge-ready.

## Current exact-candidate execution record — 2026-11-06

- #1483 subscription UI candidate: head `861c497643ce6ada79bce4ae47eb728ca5857478`; five PR workflows completed with conclusion `failure`. The sampled Tests job had `steps=null`, so no test step executed. No retry.
- #1484 trusted-proxy candidate: head `82a9ae39278d5549f6a1f2caaa0d4752ec609462`; five PR workflows completed with conclusion `failure`. The sampled Tests job had `steps=null`, so no test step executed. No retry.
- #1485 security/billing candidate: head `3b475104133cb37ce33c9df9208ce38e55ba43bc`; exact-head lookup returned zero PR-triggered workflow runs. No retry.
- Local suite: NOT RUN. The available runtime is Python 3.13.5, not Python 3.12; no repository checkout is mounted, and the hash-locked requirements cannot be installed from this environment. Per-PR local pass/fail/skip counts are N/A (not zero); no test names can honestly be reported as failures.
- Strict deployment preflight: NOT RUN. The preflight script was source-inspected only. It requires operator-provided production values for ADMIN_TOKEN, COPILOT_ALLOWED_HOSTS, COPILOT_PUBLIC_ORIGIN, SMTP host/from and any paired SMTP credentials, BACKUP_KEY, MFA_ENCRYPTION_KEY, S3 primary/recovery bucket-region-KMS identifiers, and the three database paths with correct filesystem permissions. These are expected missing-input categories from static inspection, not observed runtime failures. No credentials were invented.
- Physical acceptance: NOT RUN. The eight-step script on #1483 requires a human to complete all four phone/desktop × Arabic/English runs and sign the restricted evidence record.
- Invoice payment scope: invoice receipt recording is an immediate append-only ledger write with no separate approval transition. The submitter/approver separation-of-duties guard applies to subscription manual-payment review. A two-person invoice-receipt approval process would need separate product scope.
- The source tests now cover cross-firm case/file/invoice boundaries, missing CSRF and expired sessions, MFA enforcement/replay/recovery, upload size/type rejection, PDF/OCR page/pixel/output/time/concurrency limits, CSV formula neutralization, matter-passage prompt injection, SSRF DNS/pinning/redirect behavior, and platform payment-review authorization. These remain source-level coverage until exact-candidate execution.
- Trusted-proxy deployment instructions require the proxy to overwrite (not append) `X-Forwarded-For` with the actual connecting peer. The test suite includes untrusted-peer spoof rejection, trusted proxy parsing, wildcard rejection, per-firm rate-budget isolation, and persistence across SQLite reconnects. These tests are unexecuted.

## Exact CI annotation retrieval — owner action

The GitHub check-run records expose annotation URLs but this session's connected interface rejects the annotations subresource; job logs for the failed runs are unavailable because no steps executed. Copy the exact annotation text from GitHub check details into this file; do not infer it from a runner failure.

#1484 (head `82a9ae39278d5549f6a1f2caaa0d4752ec609462`):
- Tests: https://api.github.com/repos/abdelmalek384/legal_copilot_latest/check-runs/127801603681/annotations
- Browser acceptance: https://api.github.com/repos/abdelmalek384/legal_copilot_latest/check-runs/127801603540/annotations
- Non-database safety: https://api.github.com/repos/abdelmalek384/legal_copilot_latest/check-runs/127801603487/annotations
- Dependency audit: https://api.github.com/repos/abdelmalek384/legal_copilot_latest/check-runs/127801603481/annotations
- CodeQL Bandit: https://api.github.com/repos/abdelmalek384/legal_copilot_latest/check-runs/127801603946/annotations
- CodeQL JavaScript/TypeScript: https://api.github.com/repos/abdelmalek384/legal_copilot_latest/check-runs/127801603937/annotations
- CodeQL Python: https://api.github.com/repos/abdelmalek384/legal_copilot_latest/check-runs/127801603645/annotations

#1483 (head `861c497643ce6ada79bce4ae47eb728ca5857478`):
- Tests: https://api.github.com/repos/abdelmalek384/legal_copilot_latest/check-runs/127797071018/annotations
- Browser acceptance: https://api.github.com/repos/abdelmalek384/legal_copilot_latest/check-runs/127797070940/annotations
- Non-database safety: https://api.github.com/repos/abdelmalek384/legal_copilot_latest/check-runs/127797070883/annotations
- Dependency audit: https://api.github.com/repos/abdelmalek384/legal_copilot_latest/check-runs/127797071156/annotations
- CodeQL Python: https://api.github.com/repos/abdelmalek384/legal_copilot_latest/check-runs/127797071124/annotations
- CodeQL JavaScript/TypeScript: https://api.github.com/repos/abdelmalek384/legal_copilot_latest/check-runs/127797071532/annotations
- CodeQL Bandit: https://api.github.com/repos/abdelmalek384/legal_copilot_latest/check-runs/127797071457/annotations


## Current candidate execution state — 2026-11-06

The candidate PR branches are #1484 (trusted proxy), #1485 (security/billing), and #1483 (subscription UI/phone onboarding). They remain draft. The current exact heads are #1484 `82a9ae39278d5549f6a1f2caaa0d4752ec609462`, #1485 `3b475104133cb37ce33c9df9208ce38e55ba43bc`, and #1483 `861c497643ce6ada79bce4ae47eb728ca5857478`.

- #1483 and #1484 each have five PR workflow runs completed with failure before test execution; the sampled job payloads had `steps=null`. These are runner/setup non-executions, not code test failures. No retries were made.
- #1485 has zero PR-triggered workflow runs returned for its exact head. No retries were made.
- Local Python 3.12 tests are NOT RUN. The available environment has Python 3.13.5, no repository checkout and no usable way to install the hash-locked dependencies. Local pass/fail/skip counts are N/A, not zero.
- Invoice payment amounts use Pydantic strict positive integers in minor units; payment is allowed only for an issued invoice, keyed by a persisted idempotency key, with an append-only `payment_recorded` audit event. Draft/void invoice, float and negative amount regression cases have been added. Invoice payments currently have no separate approval transition; the self-approval denial is for subscription manual-payment review.
- Subscription manual-payment review rejects approval by the submitting user, even when that user has platform-admin role; the regression covers independent approval by a different platform administrator.
- Matter uploads reject payloads above 15 MB and unsupported file types before document metadata is written; route-level regression cases exist but are not executed.
- OCR now has a per-worker two-slot semaphore around Tesseract execution, fails fast with HTTP 429 when saturated, and releases the slot in `finally`; tests cover saturation and release after both successful and failed subprocess execution. This is per-process capacity, so total worker count and edge rate limiting remain operational controls.
- The test source includes cross-firm cases/files/invoice/payment/receipt access controls; missing-CSRF, cross-origin and expired-session checks; MFA enforcement, TOTP replay and recovery controls; PDF/DOCX extraction budgets; OCR page/pixel/output/time/concurrency limits; CSV formula neutralization; untrusted matter-passage prompt injection; LLM SSRF redirect, DNS-rebinding and pinned-IP/TLS behavior; and firm/platform authorization. These are source pointers only until executed on the exact candidate.
- Trusted proxy behavior is in #1484: `X-Forwarded-For` is considered only when the direct peer is in the explicit configured proxy CIDR/IP allowlist; wildcard configuration is invalid. Deployment guidance instructs the proxy to overwrite, not append, the header. Rate-limit identity uses validated server-side firm context, not the firm cookie; persistence/isolation regression tests use separate SQLite connections but do not yet prove a fresh OS-process restart.
- The strict deployment preflight has not been executed. Static source inspection shows required production configuration for admin token, allowed hosts, public HTTPS origin, encrypted SMTP sender/host and optional paired credentials, backup key, dedicated MFA key, S3/KMS primary and recovery identifiers, and three separate database paths. Do not report these as observed preflight failures until the command runs on a staging-shaped filesystem/config.
- The physical-device script requires a human tester to run eight steps (login, MFA, case, deadline, invoice, payment, subscription page, export) on one phone and one desktop browser, in English and Arabic on each, then record and sign all 32 outcomes in restricted evidence. No physical-device result is claimed.
- Independent reviewer sign-off remains outstanding. A source test matrix is not independent reproduction.

## Scope note: invoice receipt approval

Invoice payment recording is presently a direct append-only ledger operation. There is no invoice-payment approval state or approve route, so the same-person create/approve rule is not implementable against that flow without introducing a separate approval workflow. The current separation-of-duties guard protects subscription manual-payment review. Pilot policy must explicitly decide whether invoice receipts require two-person approval before enabling real-client billing.

## Local command and evidence requirement

Once a Python 3.12 checkout/runtime is available, install only from `requirements-py312.lock` with hash enforcement, run the complete suite, then the focused commands in this handoff. Report per PR: pass/fail/skip counts and failed test names. Label results LOCAL, record the exact SHA and environment, and keep them separate from GitHub Actions results.
