- 2026-11-16: Matter-upload OCR raster limits now clamp operator settings to non-overridable hard maxima (40 million pixels and 20,000 pixels per dimension). Added regressions attempting to raise both values; exact repository tests remain unexecuted due hosted-runner billing and unavailable local clone/network.
- 2026-11-16: Encrypted S3 recovery downloads no longer use a path-based fallback when no-follow directory-descriptor operations are unavailable. The operation fails before contacting AWS; output creation and cleanup remain anchored to the opened parent descriptor. Added an unsupported-capability regression; repository test remains unexecuted.
- 2026-11-16: Added a second restore publication regression for a parent directory replaced by a symlink between identity check and open. An isolated OS check confirms `O_NOFOLLOW` rejects that substitution and leaves the outside target unchanged. The repository test remains unexecuted.
- 2026-11-16: Follow-up hardening anchors the restore rename to the validated parent directory file descriptor and verifies its device/inode after opening; source and destination names are resolved relative to that descriptor. The local OS-level dirfd/`RENAME_NOREPLACE` check passed for both new publication and raced-in destination preservation. Repository test execution remains blocked/unperformed.
- 2026-11-16: Restore publication now uses Linux `renameat2(RENAME_NOREPLACE)` so a target created after preflight is never replaced; platforms without the atomic no-replace primitive fail closed. Added a race regression. The OS primitive was independently exercised successfully in this environment, but the repository test module and full restore drill remain unexecuted.
- 2026-11-16: Legal-PDF importer hardening was committed to current `main`: OCR page dimensions/pixel ceilings are now non-escalatable by environment overrides, Tesseract execution is capped at 30 seconds per page, and README OCR configuration names/defaults were corrected. Regression contracts were added for both limits and timeout handling, but they remain unexecuted. GitHub Actions remains unavailable due billing; a local shallow clone was also unavailable because this execution environment could not resolve `github.com`. Do not report these tests as passing until exact-head Python 3.12 execution succeeds.
- 2026-11-14: GitHub Actions billing remains unavailable, so hosted tests and PR checks cannot execute. AI 2 has now committed the firm-scoped lawyer answer-rating submit/update/read API, admin rating list and CSV export, bilingual per-answer UI, universal assistant trust-tier fallback badge, focused rating-route/frontend tests, encrypted-PDF rejection, and uploaded-matter prompt-injection coverage directly to current `main`. These are implementation changes only: none of the newly added tests has been executed locally or in CI in this environment. Do not mark the rating feature, upload hardening, or prompt-injection gate runtime-verified until Python 3.12 exact-head tests run. Clean-clone first-login, Compose validation, and witnessed backup/restore also remain unexecuted.
- 2026-11-12: Current-main PRs #1499, #1495, #1502, #1503, #1505, #1506, #1507, #1508 and #1509 are merged by manual review; none has hosted test-pass evidence because GitHub Actions billing/runner execution remains blocked. #1508 adds a matter-scoped Legal Research document workspace using existing authorized endpoints, but persistent classification/audit history and server-side canonical helper integration remain outstanding. Physical-device acceptance, witnessed backup/restore, and lawyer review of Law 14/2025 remain outstanding. Retrieval scoring now requires the private approved reviewer registry (PR #1513).
- Dependabot PR #1490 (boto3 minimum bump) is held: `requirements-py312.lock` still pins boto3/botocore 1.43.122 with hashes. Regenerate the full hash lock with the pinned Python 3.12 resolver before updating the requirement; do not hand-edit hashes.
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

- 2026-11-16: Added unexecuted retained-original download regressions for same-length byte corruption, truncation, and an object exceeding the 15,000,000-byte response ceiling; all must fail before a download audit event is written (commits `9f64be8`, `470c652`). The repository test suite remains unexecuted; these are not passing test results.

- 2026-11-16: S3 original-object streaming integrity verification is now bounded by the adapter's configured `max_bytes`: impossible oversized metadata is rejected before S3 access and actual oversized bodies are read only through a one-byte-over-limit sentinel, then closed. Fake-S3 regressions are committed (`2668e8e`, `a77a6f1`); repository test execution remains unperformed and no pass is claimed.

- 2026-11-16: Local original-file reconciliation hashing now stops at 15,000,000 bytes plus one sentinel and reports `object_size_limit_exceeded`; a regression verifies the oversized file is retained. Commits: `1aa0a40`, `23aa5af`. Runtime tests remain unexecuted; no pass is claimed.

- 2026-11-16: Restore-to-S3 importer no longer trusts a prior path digest before later calling unbounded `read_bytes()`; it now opens a regular no-follow descriptor, performs a bounded read and revalidates digest/size immediately before upload. Regressions simulate replacement between initial digest and upload and a symlinked restore object; neither may stage an S3 object. Commits: `8b021f2`, `f89370f`, `4199fc8`, `d456768`, `b75cbdf`. Runtime tests remain unexecuted; no pass is claimed.


- 2026-11-16: Restore-to-S3 original reads now pin the firm namespace directory with no-follow directory-descriptor operations and open the blob relative to that descriptor, preventing a namespace-directory symlink swap from redirecting reads after the earlier path check. A regression verifies rejection and preservation of outside/parked content (commits 0b7f440, fef3d13). Runtime tests remain unexecuted; no pass is claimed.


- 2026-11-16: Encrypted backup ZIP preflight now rejects non-canonical member paths and special filesystem entry types before extraction. Added regressions for repeated separators, dot components, Windows drive-prefixed paths and FIFO metadata (commits d3d5841, 0775ba4). The module is already registered in the workflow and security matrix. Repository runtime tests remain unexecuted; no pass is claimed.


- 2026-11-16: Restore importer now pins the restore root, objects directory and firm namespace in sequence, opening the blob relative to the pinned namespace descriptor with no-follow flags. Added a regression for an objects-directory symlink swap (commits 0a41996, 56ce2d7). Together with existing namespace and file symlink tests, object path redirection is covered below the canonical root. Runtime tests remain unexecuted; no pass is claimed.


- 2026-11-16: Focused isolated harnesses passed for restore descriptor traversal (regular file accepted; objects/ and firm namespace symlink swaps rejected) and ZIP preflight (non-canonical paths, traversal, absolute paths and FIFO metadata rejected; normal archive accepted). These are not repository test-suite results. Restore dirfd capability is explicitly checked and unsupported platforms fail closed (commit a092388). Repository tests and Actions jobs remain unexecuted.


- 2026-11-16: Restore importer now walks the complete absolute directory chain from filesystem root with no-follow directory descriptors before opening objects/, firm namespace and blob. Added restore-root symlink regression; isolated harness rejected root, objects and namespace symlink substitutions while accepting a regular object (commits 2e7a7e3, 4c33f88). Repository tests remain unexecuted; no suite pass is claimed.


- 2026-11-16: S3 original-object open now enforces a bounded stream even when ContentLength is absent and rejects oversized ContentLength before reading. Added two adversarial regressions (commits 5e9f871, d4f5d26); module registration in workflow/security regression script verified. Runtime test suite remains unexecuted; no pass is claimed.


- Follow-up: bounded S3 open stream now closes the provider body on underlying read exceptions; regression added (commits 204d5a8, 28c5d90). Runtime tests remain unexecuted.


- 2026-11-16: S3 original-object inventory now caps unique keys at one million, alongside its existing page and continuation-token bounds; regression added (commits 0af3ef1, 0122ec1). Repository tests remain unexecuted.


- 2026-11-16: Backup creation now preflights total expanded snapshot size and manifest overhead against the restore ceiling before ZIP creation; a regression asserts no hashing or ZIP writer is invoked when the file payload alone exceeds the ceiling (commits 155e284, b41fb19). Runtime tests remain unexecuted.


- 2026-11-16: ZIP member path validation additionally rejects Windows ADS syntax, reserved device names and trailing-dot/space aliases, with regressions (commits 45d5391, 1119a10). Runtime tests remain unexecuted.


- 2026-11-16: Recovery archive hash and multipart upload loops now use exact remaining-size-plus-one sentinel reads; added a tracking-file regression asserting only max+1 bytes are read during hash rejection (commits 774670a, 70b13a2). Repository runtime tests remain unexecuted.


- 2026-11-16: Recovery archive persisted-byte verification and downloads now use exact declared-size-plus-one sentinel reads; oversized download regression verifies the read bound and partial-file cleanup (commits fb89aaf, 4b80528). Runtime tests remain unexecuted.


- PR #1644: do not merge yet. It updates requirements.txt to pypdf 7.1.0 but leaves requirements-py312.lock at 6.21.4; its head also reports a failed CodeQL check and no commit statuses. PR #1610 remains draft and non-mergeable. Resolve lock parity and review checks before merging; no unsafe merge attempted.
- Current validation blocker: GitHub Actions billing/runner availability prevents repository test execution. Static source review and isolated harnesses do not substitute for the registered repository suites.


- 2026-11-16: Bounded S3 original-object reader now detects and rejects provider bodies that over-return beyond the requested read size, closes the body and has a regression (commits 155eaa6, f0e9283). Runtime tests remain unexecuted.


- 2026-11-16: Recovery archive persisted verification/download reject provider streams that over-return beyond the requested read size; regression confirms rejection and partial destination cleanup (commits b82e174, 2dd5590). Runtime tests remain unexecuted.


- 2026-11-16: Corrected the Windows reserved-device filename regex after an isolated pattern probe exposed an escaping error; CON/PRN/AUX/NUL and COM1–9/LPT1–9 names with extensions now match correctly (commit 6da44db). Repository tests remain unexecuted.


- 2026-11-16: S3 metadata lookup now rejects non-object provider responses and safely classifies malformed provider error payloads; two regressions added (commits e1e8032, 8f1752c). Repository runtime tests remain unexecuted.


- 2026-11-16: S3 original-object open now fails closed unless the provider body supports both read and close; malformed bodies are closed when possible and a regression covers missing close (commits c26d213, 3d1f4fa). Runtime tests remain unexecuted.


- 2026-11-16: Bounded S3 response wrapper now makes close idempotent, with an assertion that overflow followed by caller close invokes provider close exactly once (commits 26bec92, d11ad41). Runtime tests remain unexecuted.


- 2026-11-16: Backup creation now preflights ZIP entry count against the restore-side limit, counting the manifest, and refuses before hashing/writing when exceeded; regression asserts no hash/ZIP work (commits f3aac85, 80f1a14). Runtime tests remain unexecuted.


- Latest observed main check runs (commit e896db2) report six failures: test, chromium, Python/JavaScript CodeQL, Bandit and dependency audit. The sampled workflow-job log endpoint returned `404 BlobNotFound`, preventing diagnosis. Treat as failed/unverified, not as a test pass; no rerun or merge should rely on them until healthy runner logs are available.


- 2026-11-16: Local original storage now pins every path component from filesystem root and performs all object operations relative to no-follow directory descriptors; symlink namespace swaps are rejected. Hardlinked staged/final objects are rejected via link-count checks. Added namespace-race and hardlink regressions (commits 04b463b, 1bd681d, 86a2e07, 434ad96). A focused syscall harness passed, but repository tests remain unexecuted.


- 2026-11-16: Local original-file reconciliation now walks the object-root directory chain with no-follow descriptors, scans firm namespaces via dirfd, opens object bytes relative to the pinned namespace, and rejects hardlinked entries. Added namespace-swap and hardlink regressions (commits 26288c8, 4e5eb61, 41f30f6, 13c27a6, ab94c94). Runtime repository tests remain unexecuted.


- 2026-11-16: Local storage and reconciliation capability gates now verify no-follow `stat` support; local writes additionally require no-follow hard-link support. Directory descriptor cleanup was hardened on both success and failed-open paths (commits 36b972a, cf179ca, d4e0342, 0e06fd0). Unsupported platforms fail closed. Repository runtime tests remain unexecuted.


- 2026-11-16: Local object storage and reconciliation now pin the root directory's device/inode and reject replacement by another real directory between validation and use; root-swap regressions added (commits a943983, 0beace0, d9baf0f, ffe1e4b). Runtime tests remain unexecuted.


- 2026-11-16: Root-identity validation failure paths now close their root directory descriptors before raising (commits c1fb85f, d2a2eca). Runtime tests remain unexecuted.


- 2026-11-16: Recovery archive upload/download now anchors caller paths to absolute paths before filesystem validation, preventing cwd changes from redirecting relative paths between checks and use (commit 7604edd). Runtime tests remain unexecuted.


- 2026-11-16: Local backup inventory/copy now fail closed without no-follow dirfd primitives, pin root/namespace descriptors, reject hardlinks, enforce the 15 MB original-file ceiling and read at most expected-size+1 bytes. Added hardlink and oversize regressions (commits 6f52127, 9cda365, 50ea8a9, f6a96f4, f04b707, 021a337). Runtime tests remain unexecuted.


- 2026-11-16: Added local backup regression for replacement of the object-root directory with a different real directory between stat and open; backup must fail before copying bytes (test 66f78c7). Removed the now-unreachable path-based fallback branch (commit 5d9a132). Runtime tests remain unexecuted.


## Pre-pilot / pre-production stop-gate bundle (2026-11-24)

Treat the risks below as **one combined release gate**, not separate optional tasks. A firm pilot with confidential client matters is blocked if any high-risk gate lacks evidence. This checklist consolidates the already-listed blockers; it does not claim new test execution or security sign-off.

### P0 — must be closed before confidential firm/client data
- **Tenant isolation & authorization:** route-by-route active membership, role checks, direct object IDs, alternate HTTP methods, exports, files, child writes, background jobs; synthetic firm A/B sentinel proving no data/metadata/side-effect leaks.
- **Authentication/session & admin compromise:** session fixation/rotation, MFA enrollment and enforcement, replay/recovery, rate limits, inactive-user/firm behavior, privilege escalation, platform-admin boundaries; independently check that operator credentials cannot casually access all firm data.
- **SQL injection & query scope:** parameterization review of user-controlled query values, safe dynamic identifiers, correct firm/case filters, search/ask routes; injection probes with non-destructive synthetic fixtures.
- **Uploads/document parsing & prompt injection:** limits before expensive parsing; malformed/encrypted/polyglot PDFs and DOCX/ZIP, page/dimension/expanded-size/timeout/concurrency bounds, cleanup and safe temp files; adversarial matter text, filenames and metadata must remain untrusted prompt data and never cross firm scope.
- **Private file storage, backup/restore & recovery:** live S3/KMS/IAM acceptance, firm namespace isolation, upload/finalize/readback/cleanup; encrypted backup, integrity and bounded restore, witnessed restore/rollback, protected secrets and storage permissions. No production originals enabled until provider acceptance is documented.
- **Transport/deployment boundary:** HTTPS public origin, secure cookies/CSRF, trusted-proxy allowlist (never wildcard), DNS-rebinding/SSRF and egress controls for external LLM calls, secrets, firewall/host hardening, monitoring/log redaction.
- **Data lifecycle/legal exposure:** firm-approved retention, deletion, export, legal hold, backup retention and incident-response plan; minimize real data in logs/metrics and restrict downloads/export.
- **Operational readiness:** independent reviewer sign-off; exact-head Python 3.12 tests and security suite; manual device/browser acceptance in Arabic RTL and English; credentials/provider/mailbox/config preflight; operator runbooks and recovery rehearsal.

### P1 — must be resolved before launch decision (not merely before a confidential-data pilot)
- **Legal-content reliability:** sources/currentness/corrigenda/amendments, lawyer validation, citation accuracy, answer abstention and retrieval evaluation. Keep source-matched material clearly not lawyer-reviewed; do not advertise verified legal advice.
- **Pilot usability/support:** 3-firm onboarding rehearsal, unaided phone use, backup/support ownership, metrics and incident escalation, no unresolved critical/major UX defects.
- **Dependencies/build integrity:** Python 3.12 hash lock parity, clean install, dependency vulnerability review, reproducible release artifact. Do not hand-edit lock hashes or bypass failing/blocked checks.

### Evidence rule / release decision
Each gate requires an owner, exact candidate commit, reproducible command/config, positive control, adversarial negative control, observed result, and retained evidence. **“Implemented”, static inspection, test files present, isolated primitive harnesses, or Actions blocked/failing are not PASS.** Record only PASS, FAIL, BLOCKED, or NOT RUN. Do not start a confidential client-data pilot, and do not release to production, until all P0 gates are PASS and the remaining launch gates are approved. For a first pilot, use synthetic or explicitly authorized/redacted data only while any P0 gate is unresolved.

## Manual security review checkpoint — SQL and tenant routing (2026-11-24)

- Source inspection confirms the trusted firm-context primitive queries active membership using bound values for user and firm IDs, and rejects missing/inactive membership, identity, or firm. Tenant catalog documentation says client-provided database paths/catalog filenames are not accepted and routing is through the trusted catalog. This is source inspection only; it does **not** prove all HTTP routes use these helpers correctly.
- The route-to-SQL inventory tool is an AST-based review aid. It explicitly describes itself as incomplete for indirect framework dependencies and dynamic SQL. It tracks SQL templates, connection-boundary helper names, unresolved/dynamic SQL, and direct SQLite opens, but is not a runtime SQL-injection test and cannot prove parameter binding for every query.
- Therefore, SQL injection and authorization remain P0 **BLOCKED/NOT RUN**, not PASS. No safe claim of a fully audited query surface is made from keyword searching or the existing static tool.
- Next manual-review slices should use exact source files and synthetic payloads: (1) route handler -> helper -> connection boundary and firm/case predicate, (2) user-controlled query values bound as parameters, (3) dynamic identifiers constrained to literals/allowlists, (4) no side effects or sentinel leakage in negative cross-firm controls. Do not use production data.

### Filesystem routing residual risk — manual source review
- `tenant_catalog.py` rejects symlink storage-root components and symlink tenant files and enforces a firm-ID-bound filename format before resolving paths. This is useful path validation, but it uses pathname checks followed by later file operations; the source review did not establish race-resistant open semantics (e.g. directory-descriptor-relative opens with no-follow flags). Treat this as **NOT TESTED / deployment-dependent** against a local attacker able to modify the tenant storage directory. Restrict that directory to the application service account and administrators; do not grant firm users or unrelated processes write access. This is not a confirmed exploitable vulnerability, but it is not proof of TOCTOU safety either.
### Legacy login throttling privacy — source fix committed
- The legacy `/login` handler previously persisted normalized email and raw client IP in `login_attempts`. It now derives purpose-separated HMAC pseudonyms using the dedicated identity rate-limit key; production/staging returns 503 if that key is unavailable, while the raw-identifier fallback is development-only. Commit `a2ec1f9`. This addresses the source-level PII persistence issue but still requires runtime regression and production configuration verification.
- 2026-11-24: Review endpoint fix on `stabilize/review-page-provenance-20261124` keeps reviewer-entered page references in the extraction-review audit event instead of overwriting `chunks.page`. Added a source-contract regression. Changes are statically reviewed only; the Python 3.12 repository test suite has not been executed in this environment.
- 2026-11-24: Client-wide extracted-text search now adds `chunks.id ASC` as a deterministic tie-breaker after BM25 rank so equal-scoring results have stable pagination order. Added a source-contract regression. Static source read-back only; runtime tests remain unexecuted.
- 2026-11-24 follow-up: the review UI now reloads the latest reviewer-entered page reference from the audit event while displaying the extraction-time page separately. Added UI contract assertions; runtime browser acceptance remains unexecuted.
- 2026-11-24 follow-up: both review UI entry points now leave reviewer page reference blank unless a reviewer supplied one, preserve a prior reviewer-entered value on subsequent review, and display extraction-time page separately. This avoids relabelling extracted metadata as human-entered review evidence. Static read-back only; browser/runtime acceptance remains pending.
- 2026-11-24: Fixed the compact extraction-review queue so it exposes a reviewer page-reference input and submits the current value for accepted, needs-recheck, and corrected outcomes. Previously the queue reused only the previous review's value and offered no way to enter a new one. Added a regression contract; static read-back confirms all three save paths pass the current input. Runtime/browser tests remain unexecuted.
- 2026-11-24: The compact review queue now explicitly warns when its 100-passage render cap hides additional passages and directs the reviewer to the document-level review panel. Added a regression contract; static read-back only, browser acceptance remains unexecuted.

- 2026-11-24: Firm switching now returns the destination firm's current MFA policy and session assurance fields, rather than leaving the client with stale/absent security state from the prior firm. Added a multi-firm route regression. Static source read-back only; Python 3.12 runtime execution remains unavailable and no test pass is claimed.

- 2026-11-24: Added `docs/fictional_client_end_to_end_acceptance.md`, a synthetic end-to-end Firm A/Firm B client-matter acceptance scenario covering onboarding, MFA, tenant isolation, uploads/original integrity, document review/annotations, retrieval, legal-research handoff, deadlines, export, revocation, and RTL/LTR device/accessibility checks. Linked it from the manual acceptance runbook. This is a test specification only; no scenario step has been executed or accepted.
- 2026-11-24 follow-up: strengthened the firm-switch MFA regression to create a real policy contrast: Firm A uses optional MFA, Firm B requires MFA for everyone, and the same user is an admin only in A and a lawyer in B. The test asserts the switch response and subsequent session report B's enrollment requirement and that protected matter access is blocked. Test authored only; not executed.
- 2026-11-24 follow-up: destination-firm MFA resolution now also clears the reported verified flag/timestamp when a session was admitted without a factor under the prior firm's optional policy but the destination firm requires enrollment. The regression asserts that the stale assurance marker is not exposed and protected matter access remains blocked. Authored only; not executed.
- 2026-11-24: Added original-file download route regressions for authorized byte-for-byte delivery with no-store headers and audit attribution, cross-firm direct-ID denial without an audit event, and digest-mismatch failure without releasing original bytes or recording a successful download. The route already performs matter authorization, firm-bound metadata lookup, object digest/size verification, and audit-before-release; these tests lock that contract. Authored only; not executed.
- 2026-11-24 MFA semantics follow-up: deeper inspection confirmed `_mfa_required_for_user` already treats a voluntarily enabled authenticator as required even when the firm policy is optional; the suspected enabled-factor switch bypass is therefore not supported by the actual policy helper. Tightened the session contract instead: a session is reported as `mfa_verified` only when an MFA credential is enabled and a factor was verified; password-only optional-policy login is no longer mislabeled as factor-verified. Added regression coverage for optional-policy password-only login and for a voluntarily enabled factor still requiring verification. Source read-back only; not executed.
- 2026-11-24: Extended the multi-firm MFA regression to simulate a legacy session row incorrectly marked `mfa_verified=1` by the former optional-policy login behavior. Session resolution must mask that marker when no authenticator is enabled, including after switching into a firm requiring enrollment. This is a compatibility regression authored but not executed.
- 2026-11-24: Added an additional original-download fail-closed regression: when the security-audit insert fails, the endpoint must return 503 and withhold the original bytes. Authored only; not executed.
- 2026-11-24: Extended the destination-firm MFA scenario to verify a user blocked by Firm B's enrollment requirement can still switch back to optional-policy Firm A, where matter access resumes without falsely reporting an MFA factor as verified. Authored only; not executed.
- 2026-11-24: Original-file downloads now return the document's basename after strict ASCII filename sanitization, plus `X-Content-Type-Options: nosniff`; the response remains attachment/no-store. Added a header-injection/path-separator regression. This is a download usability and response-hardening change; test authored, not executed.
