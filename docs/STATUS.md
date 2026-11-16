# Legal Copilot — release-candidate status

**Updated:** 2026-11-16  
**Decision:** **NOT READY** for lawyer pilot or production. This is an engineering checkpoint, not legal, security or operational certification. Historical tracker detail is archived at [STATUS history](archive/STATUS_history_through_2026-11-13.md).

## AI-1 delivery

| Workstream | Current state |
|---|---|
| Answer rating contract | **Complete.** [Contract](answer_rating_contract.md) defines answer ID, rating, cited-article rating, notes, rater, timestamp, trust tier and UTF-8 CSV export for AI-2. The firm export now includes message-time `trust_tier` with a conservative fail-closed mapping; `tools/adapt_answer_rating_export.py` implements the canonical interchange and `docs/answer_rating_contract.md` documents its usage. A route regression passes actual export rows through the adapter; execution remains pending. Adapter tests are committed and registered in `.github/workflows/tests.yml`, but unexecuted. `tools/validate_answer_ratings.py` validates exported CSV structure, enums and timezone-aware timestamps; tests are committed but unexecuted. Evidence-URL validation parity was extended across `research_inspector`, `evaluate_legal_answers`, `app.validate_review_evidence_url`, the deadline-rule verifier, and the legal-document collector/manifest, manual-capture, deadline-rule attestation, source-match rights, legal-draft source and bulk-law-import URL checks (DEL, raw backslashes, query/fragment ambiguity where evidence URLs are used); regression tests remain unexecuted. The evaluation API runner now rejects DEL and raw-backslash base URLs; the reviewed-question/result JSONL parser and reviewer-registry JSON loader now reject duplicate object keys at every nesting depth; the legal-candidate seeder validates HTTPS source-page, terms, official-PDF and secondary-metadata URLs and rechecks source hosts against the permission register. The Gazette importer CLI now has a direct-execution import fallback; its CLI regression explicitly clears `PYTHONPATH`. |
| Negation guard | **Implemented; tests unexecuted.** Always-on guard is in `app.ask()`. Three focused English/Arabic reproductions and an integrated answer-path test are committed directly to main (`92e5177`, `f988e76`). No test pass is claimed. |
| Firm-test source-matched mode | **Fail-closed response gate implemented; real retrieval unavailable.** Exact firm-ID + non-production environment flag, source-only fallback and explicit `source-matched, not lawyer-verified` API label are on main (`ce2ebc8`, `7c5e09d`, `5ec22a1`, `b377af0`, `311287d`, `2009b9f`, `29e4a13`). The dedicated scope currently returns no candidates; tests use synthetic hits and are unexecuted. Never enable in production. |
| Reviewer spreadsheets | **Templates complete.** [Gazette review CSV](legal_evidence/law_14_2025_gazette_comparison_template.csv) has 311 rows, machine comparison labels, similarity, page locators and prior page-review notes. Text and lawyer decision fields remain blank pending authorized source text. [Deadline CSV](legal_evidence/deadline_rules_lawyer_review.csv) has five draft rules. [Review guide](legal_evidence/lawyer_review_quick_guide.md) gives steps and time estimates. |
| Evaluation | **116 unapproved drafts complete; a new structural validator checks Arabic question text, question IDs/text uniqueness, one formal/one colloquial variant per article pin, expected-article pin consistency and no premature lawyer approval/release flags. Static audit of the current inventory found 116 rows (58 formal/58 colloquial), 58 proposed article pins and zero invariant mismatches. [Lawyer review guide](legal_evidence/law14_2025_evaluation_review_guide.md) added. Metrics unavailable.** Structural-validator, negation reproducer, firm-test gate, rating-validator and adapter tests are now explicitly registered in `.github/workflows/tests.yml`; they remain unexecuted. Dataset contains 58 formal + 58 colloquial questions with machine-proposed article IDs. [Unreviewed inventory](legal_evidence/law14_2025_retrieval_baseline_unreviewed.json) records 116 unique questions, zero approved answer keys and zero run records. Top-3 hit rate, wrong-article rate and abstention rate are null—not zero. The scorer requires lawyer-approved labels and real retrieval runs. |
| Documentation | **Complete.** Detailed tracker archived; this is the concise release summary. The Phase 2 metadata inventory validator now rejects credentialed/empty-userinfo URLs, fragments, literal backslashes, invalid ports, whitespace/control characters and signed-query parameters; regression cases are committed but unexecuted. |
| Gazette importer owner handoff | **Prepared.** Added [operator handoff](legal_evidence/law14_2025_import_operator_handoff.md) and [metadata template](legal_evidence/law14_2025_import_metadata.template.json), including exact input requirements, SHA-256 procedure, CLI command and trust safeguards. The importer accepts explicit expected promulgation/attached-law counts and reports internal gaps, missing trailing numbers, out-of-range headings, and an entirely absent expected block; focused regression cases are committed but unexecuted. Metadata JSON now rejects duplicate keys at every nesting depth in the Gazette text importer, legacy PDF law importer, legal collection manifest, manual-capture catalog/existing provenance sidecars, the canonical source-permission register used by the collection gate, and both legal-candidate seeder inputs (candidate catalog and permission register); regression cases are committed but unexecuted. No real import run is claimed; authorized UTF-8 text and truthful supplier/source metadata are still required. |

## Dependency lock — implementation aligned; release validation open

The current `requirements-py312.lock` pins `boto3==1.43.123` and `botocore==1.43.123`, satisfying the direct Boto3 range in `requirements.txt`. FastAPI and python-multipart lock pins were also aligned with their direct requirements. A generic regression now checks every direct requirement against the lock, and the local/hosted audit commands enforce hashes. Static inspection of all eight direct requirements passed in this session. The lock has **not** been regenerated by the pinned Python 3.12 pip-tools resolver, installed in a clean Python 3.12 environment, or audited by pip-audit; do not treat static pin consistency as release validation.

## AI-2 delivery

| Workstream | Current state |
|---|---|
| Security mainline | Trusted-proxy hardening (#1495), LLM SSRF IP pinning and payment self-approval prevention (#1505), role-aware subscription recovery (#1504), and phone-login readability (#1506) are merged. Relevant security invariants still require exact-head local execution. |
| Lawyer answer rating | **Implemented on main; tests unexecuted.** Firm-scoped submit/update/read API, reviewer identity from the authenticated principal, admin-only firm list/export, append-only event ledger, CSV BOM/quoting/formula neutralization, bilingual per-answer controls, and universal assistant trust-tier fallback badge are committed. Its export now includes message-time `trust_tier` with conservative mapping: explicit `source_matched` is preserved, `verified` requires every source to be verified operative text, and all other cases become `unverified`. The AI-1 adapter maps `partially_correct` to `partial` and excludes `not_applicable` without coercion. The export also now emits a real UTF-8 BOM and RFC-style CRLF row endings and normalizes SQLite UTC timestamps to explicit `Z` timestamps. The route regression sends actual exported rows through the canonical AI-1 adapter. Export/adapter tests remain unexecuted. See [firm export contract](answer_rating_export_contract.md) and [canonical interchange contract](answer_rating_contract.md). |
| CSV import/export injection | Added an import-to-invoice-export regression using formula-like case title/client values; the export must neutralize spreadsheet formulas. Test is registered in the existing workflow and security matrix; execution remains pending. |
| Upload and prompt-injection tests | Encrypted-PDF rejection and the 500-page parser limit have focused tests; multipart route regressions now cover oversized, over-500-page, malformed, and encrypted PDF uploads and assert that rejected objects are not retained. Case-scoped retrieved-passage/provenance prompt-injection serialization has a regression. An end-to-end regression uploads a hostile DOCX and a scanned PDF through the multipart route (with only the OCR engine stubbed), retrieves both extracted/OCR text from the tenant-scoped index, checks cross-firm isolation and the matter-data LLM approval gate, and asserts hostile text plus filename metadata are serialized as untrusted JSON. Concurrent OCR/rasterization jobs are bounded to two, with a five-second capacity wait and fail-closed 503 before expensive page rendering; saturation and timeout-release regressions are committed. The per-page OCR subprocess timeout remains 30 seconds and has timeout-propagation/semaphore-release coverage. All remain unexecuted. |
| Test-firm package | Demo-firm procedure, test-mode banner and first-run wizard are documented; clean-clone-to-first-login procedure has been added. It has not been executed. |
| Staging and recovery | The local release checker now requires Python 3.12 before starting Python gates and explicitly runs the focused security matrix, isolated encrypted multi-tenant backup/restore drill with a real firm-owned original binary and tamper-rejection fixture, placeholder-only Compose configuration validation, lock regeneration/drift comparison, pip-audit, and optional workflow lint/Bandit scans when installed. The operator drill now rejects overlapping physical backup/restore directory trees; two-direction regression is committed and registered in the focused security matrix and Tests workflow. The read-only firm-offboarding preflight now converts any unexpected object-reconciliation exception into a blocking finding and reports only the exception class; an `OverflowError` regression is committed. These tests remain unexecuted. The destructive local original-file purge function now enforces the same explicit quiescence assertion as its CLI boundary, and the CLI passes that assertion through; direct-call regression is committed and registered in the focused security matrix and Tests workflow. All checks remain unexecuted. Credential-only preflight failures must be recorded separately from missing infrastructure/configuration. |
| Validation | GitHub Actions runner allocation/billing prevents hosted test execution. Latest exact-head check on `main` commit `bf5ddf5d8a04c889f03b010202f4e0db054ddfe4`: Tests run `43602358989`, Browser acceptance `43602359120`, Dependency audit `43602359046`, and CodeQL `43602359089` all concluded failure before any job step; inspected jobs report `runner_id=0` and `steps=[]`. The prior exact-head check on `8955b38d564932fc908073eb230e9940b893e230` showed the same pattern. This is runner/service allocation evidence, not a code-test failure or pass. A static GitHub directory/workflow audit finds all 186 top-level `test_*.py` modules registered in the workflow or known-unrun register; this is not execution. No newly added local tests have been executed in this work session. Direct-main commits are implementation evidence, not test passes or pilot acceptance. |

## Repository tasks closed at implementation level

The following bounded repository tasks now meet their source-change acceptance criteria. Their percentages describe implementation only; the linked runtime/release gates remain separate.

| Task | Implementation | Validation boundary |
|---|---:|---|
| Align all eight direct dependency pins with the checked-in Python 3.12 lock | **100%** | Static consistency check completed; clean resolver/install/audit still open |
| Protect applied migration-ledger rows from update/delete and reject same-name weakened guards | **100%** | SQLite immutability triggers and spoofed-trigger regression committed; test registered but unexecuted |
| Add generic direct-requirement versus lock regression | **100%** | Test committed; repository test execution pending |
| Enforce hash-required dependency audits in local and hosted workflow commands | **100%** | Workflow/script source reviewed; pip-audit execution pending |
| Remove duplicate local pip-audit execution and gate release checks on Python 3.12/toolchain | **100%** | Script implementation committed; full local release check pending |
| Reject symlinks/special files and open recovery inputs without FIFO blocking | **100%** | Focused source review/custom isolated harness; repository tests pending |
| Hash and upload the same already-open recovery source descriptor | **100%** | Focused source review/custom isolated harness; repository tests pending |
| Bind archive upload to the exact encrypted bytes returned by verification | **100%** | Focused source review/custom isolated harness; repository tests pending |
| Require and verify expected SHA-256 before any recovery object upload | **100%** | Focused source review/custom isolated harness; repository tests pending |
| Reject duplicate JSON keys, duplicate device/browser acceptance records, and reused evidence paths at release-gate integration boundary | **100%** | Strict parser, validator and unit/integration regressions committed and registered in Tests workflow; execution pending |
| Reject duplicate JSON keys in database/staging release-evidence manifests | **100%** | Strict object-pairs parser and regression committed; existing database acceptance test module is registered in Tests workflow; execution pending |
| Bound and harden release-evidence manifest parsing | **100%** | Binary bounded read (1 MB), UTF-8/JSON-depth/duplicate-key rejection, and pre-open inode binding against path replacement; valid/invalid encoding, nesting and replacement regressions committed, execution pending |
| Bound and harden device/browser evidence input parsing | **100%** | Stable regular-file descriptor, symlink/special-file rejection, 5 MB bounded read, UTF-8 validation and excessive JSON nesting rejection for JSON/JSONL; regressions committed, execution pending |
| Register backup-archive and production/device/database release-acceptance tests in focused security matrix | **100%** | Security script and workflow-contract regression committed; execution pending |
| Synchronize README, release status and blocker register with current lock/recovery implementation | **100%** | Current-main source inspection completed |
| Make fake billing-provider request creation idempotent by merchant reference and reject conflicting reuse | **100%** | Implementation and two regression cases committed; tests registered but unexecuted |
| Add client-profile required-name accessible error association and correction state | **100%** | Source and frontend contract committed; tests/browser review unexecuted |
| Add persistent bilingual labels and associated validation errors to product-feedback fields | **100%** | Source and frontend contract committed; tests/browser review unexecuted |
| Add persistent bilingual labels to account password and firm-invitation email controls | **100%** | Source and frontend contract committed; tests/browser review unexecuted |
| Return tenant-bound matter/document provenance and original-retention state on firm search hits | **100%** | Backend implementation and true/false retention regression cases committed; tests unexecuted |
| Display matter provenance in research source inspector and open the exact matching document/chunk | **100%** | Frontend implementation and navigation lifecycle contract committed; browser/tests unexecuted |
| Clear stale one-shot passage navigation on close, failed load, missing target, manual navigation and identity boundary changes | **100%** | Source and frontend contract committed; browser behavior unverified |
| State that extracted page references are provisional until checked against the original | **100%** | Bilingual warning and workflow-registered regression committed; tests unexecuted |
| Reject physically overlapping backup and restore directory trees | **100%** | Canonical-path guard and two-direction regression committed and registered; execution pending |
| Enforce explicit quiescence inside the destructive original-file purge function | **100%** | Function-level fail-closed guard, CLI pass-through and negative direct-call regression committed and registered in the security matrix and Tests workflow; execution pending |
| Fail closed when original-document download audit logging fails | **100%** | Route regression injects a SQLite audit-write failure and asserts HTTP 503 without releasing the binary; test is in the already registered separate-runtime module, execution pending |
| Preserve committed original uploads when post-commit usage metering fails | **100%** | Upload cleanup now distinguishes pre-commit rollback from post-commit failures; regression asserts ready metadata, retained bytes and successful subsequent download; execution pending |
| Block matter deletion when original-file audit records are still linked | **100%** | Deletion now returns HTTP 409 before destructive writes; regression confirms matter, document and original metadata remain intact; execution pending |
| Verify document metadata/text search and matter indexes do not disclose another firm's records | **100%** | Separate-runtime regression committed; route execution pending |
| Pin firm-data-export success-audit fail-closed behavior and exclude authentication/session/MFA secrets from exports | **100%** | Positive- and negative-path route regressions committed and registered in the existing workflow/security matrix; execution pending |
| Verify firm export includes original evidence byte-for-byte and records matching SHA-256/manifest metadata | **100%** | Route regression committed and registered through the existing workflow suite; AST syntax check passed; route execution pending |
| Verify suspending a user's membership revokes access to only that firm, including recovery from a stale firm cookie, while preserving access to another active firm | **100%** | Route regression committed; stale-context fallback and cross-firm denial are asserted; execution pending |
| Reject control-plane or legal-corpus database files nested inside the local original-file object root during offboarding preflight | **100%** | Focused filesystem containment regression committed and registered in Tests workflow; execution pending |
| Convert S3 inventory-listing outages into blocking offboarding findings without authorizing purge | **100%** | ObjectStorageError handling and synthetic provider-outage regression committed; execution pending |
| Block offboarding when the S3 provider returns an unknown bucket-versioning state | **100%** | Unknown-status finding and regression committed; execution pending |
| Prevent S3 reconciliation from looping indefinitely when the provider repeats a continuation token | **100%** | Repeated-token detection and fake-provider regression committed; test registered in Tests workflow and security matrix; execution pending |

## AI-2 implementation completion estimate

These are unweighted engineering estimates for the seven AI-2 delivery workstreams, not test-pass rates or production-readiness scores.

| Workstream | Estimated implementation completion | Remaining acceptance |
|---|---:|---|
| Local release baseline | 20% | Release-check implementation exists; exact local checker output and all Python 3.12 gates remain unavailable |
| Security integration | 83% | Production/staging login, configured API middleware, and recovery throttle identifiers are purpose-separated HMAC pseudonyms; route-authentication, case/document parent-scope, fail-closed original-file export and download-audit boundaries, post-commit original retention, and explicit matter-deletion retention conflicts are now guarded; exact-head security verification remains blocked |
| Security regression coverage | 98.0% | Backup source no-follow, same-descriptor upload, mandatory checksum and verification-to-upload byte-binding regressions, duplicate release-evidence validation, S3 cross-region KMS, recovery/login/API HMAC, route-auth, case-ID/document-ID/query-scope, corrupted original-file export, mandatory original-download audit failure, post-commit upload-metering failure, matter-deletion retention, firm-export audit-failure, authentication-secret-exclusion, byte-for-byte original-export integrity, cross-firm membership-suspension, offboarding database/object-root containment, S3 inventory-outage, and unknown S3 versioning-state regressions are committed; all repository tests remain unexecuted, real OCR-engine/image-quality acceptance still pending |
| Lawyer rating UI/export | 95% | Browser acceptance and adapter execution remain pending |
| Test-firm package | 90% | Clean-clone first-login rehearsal remains unexecuted |
| Repository cleanup/accessibility | 83% | Bilingual form labels/errors, source-inspector metadata and passage navigation are implemented; run hygiene scan and finish manual accessibility review |
| Staging/recovery | 40% | Two-bucket S3 preflight resolves original/recovery KMS keys in their own regions; backup/restore overlap guard and direct purge-quiescence guard have registered regressions; recovery drill, Compose gate, provider configuration and witnessed restore remain unexecuted |

## AI-2 S3 reconciliation CLI error handling — 2026-11-16

- The standalone read-only S3 reconciliation CLI now catches TypeError and OverflowError from malformed inventory/metadata values and exits through its controlled diagnostic path instead of emitting an unhandled traceback. Its diagnostic reports the exception type, not provider-supplied exception text, reducing the risk of leaking sensitive endpoint/request details. This complements the offboarding preflight's blocking-finding behavior; it does not convert malformed data into a clean reconciliation result.
- **Bounded source task: 100% implemented; CLI regression execution remains pending.**

## AI-2 S3 pagination and fail-closed offboarding hardening — 2026-11-16

- S3 inventory pagination now rejects empty, non-string, or repeated continuation tokens. A malformed provider response can no longer trap the reconciliation process in an unbounded loop.
- Added a fake-S3 regression that returns the same continuation token indefinitely and asserts an ObjectStorageError is raised.
- Offboarding reconciliation also converts TypeError from malformed inventory/metadata processing into a blocking object_reconciliation_failed finding; a focused synthetic TypeError regression asserts no purge authorization or mutation.
- **Bounded source tasks: 100% implemented; repository regressions remain unexecuted.** An isolated harness against the pagination guard reproduced the repeated-token failure after two provider calls, confirming the loop terminates rather than retrying indefinitely.

## AI-2 offboarding storage-boundary regression — 2026-11-16

- Added a regression proving that the read-only firm-offboarding preflight rejects both the control-plane database and the legal-corpus database when either is physically nested inside the local original-file object root. This prevents database files from being treated as object inventory and pins the existing symmetric containment boundary.
- The focused path predicate was exercised independently with temporary filesystem paths and passed. The repository test module remains unexecuted; no application test pass is claimed.
- **Bounded regression task: 100% implemented; runtime test execution: pending.**

## AI-2 S3 offboarding outage handling — 2026-11-16

- The read-only firm-offboarding preflight now converts S3 inventory-listing failures (ObjectStorageError) into a blocking object_reconciliation_failed finding instead of allowing the provider exception to escape the report path. The CLI therefore emits a controlled blocked result rather than an unhandled traceback.
- Added a regression with a synthetic S3 inventory outage; it asserts the preflight remains blocked, performs no mutation, and never authorizes production purge.
- **Bounded implementation task: 100% implemented; regression execution: pending.** No GitHub Actions run or full application test was possible.

## AI-1 Gazette provenance timestamp correction — 2026-11-16

- PR #1647 merged the explicit-timezone requirement for datetime provenance while retaining date-only metadata; duplicate PR #1646 was closed without merge.
- A manual Python check exposed a compatibility defect in the merged implementation: Python's datetime parser accepts a date-only string as a naive midnight datetime, so the new timezone check accidentally rejected the promised date-only format. Corrected the mainline validator to distinguish canonical YYYY-MM-DD dates before parsing datetimes.
- Manual isolated validation passed for date-only, UTC-offset datetime, non-UTC-offset datetime, and rejection of a naive datetime. The full Gazette importer test module remains unexecuted due unavailable GitHub runners.
- Mainline correction: 80009598e5c3601cd0b4fbc436d66fe1a171abc0.

## AI-2 S3 offboarding versioning-state validation — 2026-11-16

- Tightened the read-only offboarding gate so only an absent bucket-versioning Status is treated as the unversioned/Disabled case. Enabled and Suspended remain blocked pending retention policy; any unexpected non-empty status now produces a blocking s3_bucket_versioning_status_unavailable finding.
- Added a synthetic unknown-provider-state regression. It asserts blocked preflight, no mutation and no production-purge authorization. The offboarding test module is registered in both the Tests workflow and focused security regression matrix; execution remains pending.
- **Bounded implementation task: 100% implemented; runtime test execution: pending.**

**Unweighted AI-2 implementation estimate: 72.7%** (arithmetic mean of the seven workstream values above). The provisional whole-project engineering estimate is approximately **72%**; this is not a test-pass rate or production-readiness score. The application remains **NOT READY** for lawyer pilot or production. No test pass is inferred from committed test code.

## Legal evidence boundary

- Labour Law 14/2025 remains **source-matched, not lawyer-reviewed**; `verified=0` for all 311 candidate rows; `authoritative=false` and `retrieval_eligible=false`.
- The supplied ZIP candidate JSONL was structurally inventoried (13 promulgation provisions + 298 articles; no missing/duplicate numbers; malformed rows 0). The separately supplied 112-page Gazette PDF text layer was also inspected locally: all 13 promulgation headings and all 298 attached-law article headings appear in sequence, with no gaps/duplicates. See [inventory audit](legal_evidence/law14_2025_uploaded_candidate_inventory_audit.json) and [PDF heading audit](legal_evidence/law14_2025_uploaded_pdf_heading_audit.md). This is numbering coverage only—not article-body matching, an importer run, or legal verification.
- Collection/reuse permission remains unknown and the supplied scan reports copy/print restrictions. Do not commit or serve the candidate text, or bypass source restrictions.
- Decisions 248–252/2026 are metadata-only related-instrument candidates; full text is restricted/unavailable, permission unknown and legal review pending.
- No law becomes verified without qualified Egyptian counsel reviewing text, commencement, amendments/currentness and source rights.

## Remaining gates

1. GitHub billing/runtime access or a supported local Python 3.12 environment is needed to execute the focused tests; no CI or local test output is claimed.
2. AI-2 implementation is on main; execute rating-route/frontend tests and Arabic/English browser acceptance in a clean Python 3.12 checkout.
3. Owner must supply the UTF-8 Gazette transcription and completed truthful metadata described in [the importer handoff](legal_evidence/law14_2025_import_operator_handoff.md). The importer can create quarantined candidates while permission remains unknown, but no collection/reuse or production ingestion is permitted without evidence of permission.
4. Counsel must approve the evaluation questions/article key and answerability; then an authenticated corpus/API and before/after run exports are needed for scoring.
5. Billing/provider acceptance, tenant-isolation/recovery rehearsal, device/accessibility acceptance and pilot-firm workflow remain separate release gates.

**Last formally recalculated whole-project score:** 50.10% (2026-11-01). No newer weighted score is asserted.


## AI-2 auth-boundary navigation reset and PR #1610 review — 2026-11-14

- Cleared one-shot matter/document/chunk review navigation state when the API session expires (401) and on both ordinary and MFA firm-switch flows. This prevents a pending review target from being reused after the active identity/firm context changes.
- Added a frontend regression contract for the auth reset and both firm-switch paths. Static source assertions were reviewed after commit; the Python test was not executed.
- Direct-main commits: `d45e94ca4749dd3a39131cecad460e9c20221e19` (implementation), `a7e9ca8e21a4551692bd7070aeb67edbda3698ee` (regression contract). This does not establish runtime/browser acceptance.
- PR #1610 head `fc5e6e99716fb7fbcada8b2ac5b93a3d62ebca5f` is divergent from current main (218 ahead / 527 behind; four net changed files). Its frontend diff deletes the existing answer-rating panel and save/load controls, so do not merge or transplant it wholesale. Any desired navigation changes need a narrow current-main rebase preserving answer ratings and newer document/session safeguards.
- PR #1610's validation record shows runner-allocation failures before steps; no test or browser execution is established.


## Manual-capture provenance JSON ambiguity hardening — 2026-11-14

- The read-only manual-capture record validator now rejects duplicate JSON object keys at every nesting depth. Previously, the default decoder silently kept the last value, which could make conflicting permission or provenance fields ambiguous.
- Added a CLI regression covering duplicate top-level and nested keys. The test module is registered in `.github/workflows/tests.yml`.
- Static review only; test execution remains unavailable. No permission, authenticity, currentness, lawyer-review or retrieval-eligibility state changed.


## AI-2 fake billing-provider idempotency — 2026-11-14

- `FakeBillingProvider` now treats a trimmed merchant reference as an idempotency key. An identical retry returns the existing request; reuse with a different amount, normalized currency or metadata fails closed rather than creating a second pending request.
- Added regression contracts for identical retries and conflicting reuse. The tests are registered in the existing workflow through `tests/test_billing_provider.py`; they were not executed because GitHub runner allocation/billing is blocked.
- Direct-main commits: implementation `acdd4a1d89d423a89709ec428ff5563b69d31351`; tests `d8bd4a27638b314fb9e35619a10aa3345ea15590`.
- **Bounded task: 100% implementation.** **Live billing integration: 0%**—no selected/credentialed merchant provider, hosted checkout, signed webhook verification, provider-event idempotency, refunds/chargebacks or settlement reconciliation is implemented. Do not treat the fake provider as payment acceptance evidence. Overall AI-2 and release readiness estimates are unchanged; application remains NOT READY.

## Manual-capture evidence URL policy alignment — 2026-11-14

- The manual-capture provenance validator now rejects URL fragments (including a bare fragment delimiter), empty or non-empty user-info, malformed ports, raw backslashes, control/whitespace characters, and signed/credential query parameters across source, terms and permission-evidence URLs.
- Added focused regressions for fragments, empty user-info, cloud-signed URL parameters and access-token parameters. Static source review only; tests remain unexecuted.
- These checks validate URL shape only; they do not establish that a source grants collection or commercial-reuse rights.


## AI-2 client-profile required-field accessibility — 2026-11-14

- Added a bilingual inline required-name error to new/edit client-profile dialogs. The name input now exposes `aria-describedby` and `aria-invalid` on native/custom validation, focuses on invalid submission, and clears the error state as the user corrects the value. The alert is rendered outside the label so it does not pollute the control's accessible name.
- Added a frontend contract test; the existing Tests workflow already runs `tests/test_frontend_ux_contract.py`. Static inspection confirms the source, test assertion and workflow registration. The test/browser suite was not executed.
- Direct-main commits: UI `d816cfbd01f10f481e96f46a1c1fbb5edd934037`; regression `fceb630dece68e738e62eb5086de2d2bcfccb562`.
- **Bounded implementation task: 100%.** Broader form-error consistency and manual screen-reader/browser acceptance remain open; do not mark the entire accessibility workstream complete.


## AI-2 product-feedback form accessibility — 2026-11-14

- Added persistent bilingual labels for feedback title/details and field-associated inline validation errors for the existing minimum lengths. Invalid controls expose `aria-invalid` and `aria-describedby`; correction clears the state. The category selector retains its explicit accessible name.
- Added frontend contract coverage in the existing UX test module/workflow. Static source assertions confirm labels, error IDs, descriptions, invalid-state transitions and form wiring; no test/browser execution is claimed.
- Direct-main commits: UI `cf4d73c3222b23d2fa83e842c7107644d045ed9a`; regression `becf8009dcbaf10905fe643def90b60395e08433`.
- **Bounded implementation task: 100%.** Remaining dynamic forms, complete bilingual form review and manual accessibility acceptance remain open.


## AI-2 account and invitation form labels — 2026-11-14

- Added persistent bilingual visible labels to the current/new/confirm password controls and the firm-invitation email control. This removes placeholder-only accessible names from these settings forms; the invitation-role selector already had an explicit accessible name.
- Added frontend contract coverage in the existing UX workflow. Static source assertions confirm labels and form wiring; no Python/browser test execution is claimed.
- Direct-main commits: UI `f53e528bc422c296394142e80cad53a43e6787dd`; regression `5852ee0c471ae4f83d7920462d3a8c8518284df9`.
- **Bounded implementation task: 100%.** Broader form semantics and manual screen-reader acceptance remain open.


## AI-2 matter-search document provenance hand-off — 2026-11-14

- Separate-runtime firm-document retrieval now joins each hit to its document under the same document/case/firm keys and returns document/chunk IDs, original filename, stored SHA-256, extraction status, OCR-used state and an original-availability flag. The flag is true only for a ready, non-purged original object in the same firm scope. Corpus and legacy hits do not receive matter-document download metadata.
- Added separate-runtime regressions for the no-original case and the ready-original case, including filename and SHA-256 binding. The existing workflow runs `tests/test_app_separate_database_runtime.py`; no test execution is claimed.
- Updated the source-inspector contract to document the provenance fields and the distinction between UI traceability and server-side download authorization.
- Direct-main commits: backend `889857dffff78d1ec495a764c37178289854f52e`; false-path regression `04c301ed21418f4ca457a8ea90f8c2329e82c252`; ready-original regression `0c176283757306d0250f5826c0e50eea473f8f43`; contract doc `79f1e2eafa44f85228921ab12192855dd134764d`.
- **Bounded implementation task: 100%.** Static review confirms tenant-scoped join predicates, ready/non-purged filtering, output mapping and regression assertions. Runtime query execution, browser hand-off and exact-original download acceptance remain unexecuted. This is a safe backend-only extraction from PR #1610; no PR UI changes were merged or copied.


## AI-2 source-inspector matter hand-off — 2026-11-14

- The source inspector now displays firm-document matter/document/chunk IDs, SHA-256, extraction status, OCR-used state and the backend-reported retained-original state. With valid matter/document IDs and a chunk ID it opens the matter's Documents section, expands the matching review panel and focuses/scrolls to the exact chunk. Without a chunk ID it offers only a matter-level Documents hand-off. Missing documents/chunks, request failures, close actions and manual section/firm/session changes clear the one-shot target.
- Added a frontend contract test in the existing UX test module/workflow. Static assertions confirm metadata rendering, OCR/retention labels, matter-scope gating, action wiring and preservation of the answer-rating panel. No browser or Python test execution is claimed.
- Direct-main commits: UI `044a7f6f0da3f7592c5cbdfaee7f2cb06412bce7`; regression `ffdcd6ed8415baad345dea83f7f39df2411acf7b`; source-inspector contract `ac674467c0110c41114c411d94c4b8dc8e0b47af`.
- **Bounded implementation task: 100%.** Browser hand-off, screen-reader reading order and exact-chunk positioning remain unaccepted. No legal verification status is changed.


- Follow-up source correction: `1714b2a109400807f598cf51aaeeb46fd4cee46f` corrected the generated settings-label element object syntax after static review. This is a source correction only; the inline JavaScript syntax workflow check has not been executed.


- Exact-passage navigation commits: UI `fecfa00d0bf3c84eeb4317dcc82ed7dba3e115c3`, stale-target/failure cleanup `f29a6833d79316b182137ef45f3107a975399de6`, positive-safe-integer chunk-ID validation `d683ea9b57f9086f9dd1a4bd4bef9cd840fc5f4d`, and global-navigation target clearing `81202653f797f1511bc72caca0ba3ca7179f1423`; lifecycle regression contracts `b60f8d5ea6d32bc68bbd306018619815ad9d6369` and `49b6c05c58689c818334e56c91b732e8e2a7687d`; updated inspector contract `71fef4ca4fedbe6e3afc99396adb4f2e415f611d`. Implementation is complete at source level; browser behavior remains unverified.


## AI-2 extracted page-reference caveat — 2026-11-14

- The matter extraction review now displays the recorded extracted page number with an explicit bilingual warning that the page reference has not been independently checked against the original file. The check accepts only a present page value and does not imply page-level verification.
- Added a regression contract in `tests/test_document_classifications.py`, already registered in the existing workflow. Static inspection confirms the condition and both language strings; tests/browser review were not run.
- Direct-main commits: UI `f8aa9a4d406ca92ef19bfe7c1c084f1a74e55c31`; regression `b6afb6de0b337b7db686340c7a8ef43db6e6ba89`.
- **Bounded implementation task: 100%.** Independent page-by-page lawyer verification remains an operational/legal review requirement.


## AI-2 S3 recovery preflight cross-region KMS fix — 2026-11-15

- The separate recovery-archive preflight previously resolved the original-object KMS key using the recovery-archive region's KMS client. When the two configured buckets/keys were in different AWS regions, the original-key lookup could fail and the preflight would reject the configuration even when the keys were correctly distinct.
- The preflight now accepts a separate original-region KMS client; its CLI constructs that client from `COPILOT_S3_REGION`, while archive-key and archive-default-encryption lookups continue through `COPILOT_S3_RECOVERY_REGION`.
- The live synthetic round-trip command now passes its already-created original-region KMS client into the recovery-archive preflight.
- Added a regression with distinct original/recovery regions and canonical key ARNs. Static source inspection only; no repository tests or cloud calls were executed.
- Direct-main commits: preflight `05698a6`, regression `19db7ef`, round-trip caller `3547179`.
- **Bounded implementation task: 100%.** Runtime validation and live AWS acceptance remain open; this change does not establish production readiness.

## AI-2 S3 architecture status documentation alignment — 2026-11-15

- Updated the architecture decision, physical-purge review checklist, tenant-isolation inventory and retention proposal to state accurately that the former single-bucket versioning conflict is resolved in repository code by separate never-versioned original storage and versioned encrypted recovery-archive storage.
- Preserved the outstanding blockers: deployment-owner approval, live bucket/KMS/IAM evidence, enforced no-writer controls, counsel/security-approved retention semantics, witnessed restore/deletion drills and independent review.
- Documentation commits: `9499e03`, `d4de53c`, `c3f09a5`, `e8452a1`.
- **Bounded documentation correction: 100%.** No external acceptance is implied.

## AI-1 evaluation JSONL integrity — 2026-11-15

- Added duplicate-object-key rejection at every nesting depth to `tools/score_arabic_retrieval.py` and `tools/run_legal_eval.py`. Both JSONL loaders now fail closed instead of accepting Python JSON's last-key-wins behavior.
- Added regression coverage for top-level and nested duplicates in `tests/test_score_arabic_retrieval.py` and `tests/test_legal_eval_runner.py`. Both modules are already registered in the Tests workflow.
- Changes are on branch `ai1/reject-duplicate-jsonl-keys-mainline`; test execution remains unavailable. This is source/test implementation, not a test pass, legal review, or retrieval metric.


## AI-2 account-recovery rate-limit privacy hardening — 2026-11-15

- Replaced the unkeyed SHA-256 email/IP recovery identifiers and production login-attempt email/IP identifiers with purpose-separated HMAC-SHA-256 digests. All configured production/staging API middleware IP budgets are also HMAC-pseudonymized while preserving firm scoping; recovery request/consume middleware always HMACs client IPs. A database-only reader cannot test likely email addresses or directly read production login/recovery IP keys without the dedicated secret.
- Added `COPILOT_IDENTITY_RATE_LIMIT_KEY`; runtime login/recovery/API throttling fails closed in production and staging if it is missing, short, placeholder-like, untrimmed, or reused from ADMIN_TOKEN, BACKUP_KEY or MFA_ENCRYPTION_KEY. Production and separate-runtime preflight require an independent secret of at least 32 bytes.
- Updated the production environment template, deployment checklist and tenant-isolation inventory. Added regressions for keyed recovery and login digests, missing-key fail-closed behavior for production login/recovery, and deployment preflight requirements.
- Direct-main commits: app `79a9f3c`, `22fb5bd`, `799b9ed`, `c5d16f3`, `4434b76`, `1b9340a`, and `846a3f1`; login/API throttle tests `6f2fc1d`, `972479f`, `0b6f2e4`, `1dea873`, `a00b92b`, `675ee7b`, `7837453`, `9c4f3be`, and `477d14d`; preflight `d467b40`, `1a92a42`, `636dcff`, `69683c8`, and `ed21b80`, identity tests `d5a9f76`, `44f902b`, `ec525f2`, `a1e0460`, `a83f0e3`, preflight tests `4f08dfa`, `772fce5`, `2942416`, `01d207c`, and `108b06c`, runtime key validation `6cfb3d9`, environment/docs `fefea03`, `215df99`, `eaf70d4`, `ca1e183`, `3827c96`, `8d39c57`, `e9145b2`, `195d321`, `b8df49e`, `64cddba`, `14f1bf0`, `4bb039f`, `8c13644`.
- **Bounded implementation task: 100%.** Static source inspection only; no repository tests or live multi-host rate-limit exercise were run. Production/staging deployment must provision the new independent secret before enabling login, API throttling, or account recovery.
- The deployment preflight now requires the HMAC secret whenever any separate-runtime database profile is configured, not only for production or an explicit strict-release invocation. The default separate-runtime test fixture supplies an independent test-only secret; focused configuration regressions cover missing, weak, padded and reused keys. Commits: preflight `ed21b80`; test fixture `2942416`; regression `01d207c`.


## AI-1 legal JSONL parser coverage — 2026-11-15

- Follow-up hardening extends duplicate-key rejection to `tools/validate_law14_eval_draft.py` and `tools/evaluate_ocr_quality.py`, covering nested as well as top-level objects. The scorer and API runner guards were merged in PR #1621.
- Added corresponding tests in the already workflow-registered Law 14 draft-validator and OCR evaluation test modules. This branch is source/test implementation only; execution remains blocked and no test pass is claimed.

## AI-1 human-review input integrity — 2026-11-15

- `tools/evaluate_legal_answer_reviews.py` now rejects duplicate keys at every nesting depth in review JSONL records and in the private reviewer-registry JSON file. Added regressions for conflicting assessment fields, nested score fields and duplicate registry keys.
- The existing review-evaluation test module is already workflow-registered. Execution remains blocked; this is source implementation only and does not establish reviewer credentials or legal accuracy.

## AI-1 extended JSONL integrity coverage — 2026-11-15

- Extended strict duplicate-key handling to general retrieval-quality evaluation (including its reviewer registry), Arabic OCR evaluation, article-row auditing, and candidate/reference corpus comparison. Regression tests were added to the existing test modules.
- Duplicate-key rows are rejected by evaluation/validation paths or counted as malformed/skipped by evidence-only audit/comparison tools. Test execution remains unavailable; no test pass or legal verification is claimed.

## AI-1 release-gate and draft-input integrity — 2026-11-15

- Hardened `tools/production_release_gate.py` to reject duplicate keys in candidate source documents and reviewer registry JSON. Duplicate candidate records cannot enter the ready-source index; duplicate registry keys block evaluation.
- Hardened `tools/build_legal_draft.py` to reject duplicate keys in structured legal-draft input. Regression tests are committed but unexecuted.


## AI-2 route authentication dependency guard — 2026-11-15

- Added `tools/audit_route_auth.py`, an AST-based inventory of registered FastAPI routes. Every route in `app.py` and the two mounted platform/identity routers must declare `Depends(user)` unless it matches one of 12 exact public endpoints: the public shell, five fixed PWA assets, two token-fragment invitation/recovery pages, login, new-identity invitation acceptance, and the two account-recovery API endpoints.
- The audit fails closed for unprotected routes and for stale public allowlist entries. The focused security regression script now runs the route-auth audit test module and both strict route-to-SQL/route-auth static audits. Added focused synthetic-source tests, current-application inventory coverage, and strict CI workflow registration alongside the route-to-SQL audit.
- Direct-main commits: initial audit `c1b6268`; tests `9edc6c1`; CI `c1a0591`; tenant-isolation documentation `5851648`; mounted-router coverage `13e885c`; synthetic-test mode `c21571b`; current-app regression update `6bc0d99`; fail-closed router discovery `6ea82e6`; router-discovery regressions `c312b36`, and synthetic-import newline correction `675943d`. FastAPI `api_route` default-method correction `11d4fe1` and regression `d13a164`. Focused security matrix integration `de130d0`; deployment-contract regression `839875b`.
- **Bounded implementation task: 100%.** This is a static dependency-presence guard only. It does not establish role-level authorization, case membership, tenant SQL scoping, or route behavior. The test and strict audit commands have not been run due the GitHub billing/runner constraint.
- Follow-up case-membership guard: `tests/test_tenant_route_inventory_coverage.py` now statically requires every `{cid}` route to call `need()` or the reviewed `delete_case()` wrapper. Commit `8ffdb15`; tenant inventory note committed with this status update.
- Follow-up document binding guard: the same module now requires every `{document_id}` route to call `need()` and contain an explicit `firm_id` predicate/binding. Test commit `f34d661`; inventory note committed with this update. Query-based document search/compare predicate regression `e40088d`.
- Query-based document boundary guard: source regression now pins firm/membership predicates for extracted-text search, metadata search, and document-version comparison. Test commit `e40088d`; inventory note committed with this update.
- Firm export defense-in-depth: original-file metadata is filtered by object, document, and case firm IDs; any mis-tagged, orphaned, or cross-firm object row now fails the export with HTTP 503 before a success audit event. A corruption-fixture regression removes the normal DB trigger and verifies fail-closed behavior. Initial filter `1840ea6`; fail-closed validation `4d80fa6`; tests `06e550a`, `1a6c146`, and `276072c`; inventory note `e89ba26`. Added a parallel encrypted-backup regression proving corrupted cross-firm original-object metadata is rejected before a bundle is emitted (`5651a0e`); backup implementation already validates every original-object row against the trusted tenant ID.


## AI-1 acquisition permission input integrity — 2026-11-15

- Hardened `tools/validate_acquisition_readiness.py` to reject duplicate keys in collection manifests and source-permission register JSON. Added CLI regression tests for both input paths.
- This preserves the source-rights fail-closed boundary; it does not grant collection or commercial reuse permission. Tests remain unexecuted.

## AI-1 collection provenance integrity — 2026-11-15

- `tools/collect_legal_documents.py` now parses existing current metadata pointers with the strict duplicate-key hook and refuses to overwrite ambiguous provenance. Added a preservation regression; test unexecuted.

## AI-1 Labour Law evidence-card report integrity — 2026-11-15

- Hardened `tools/report_labour_law_evidence_cards.py` to reject duplicate keys in canonical/supplemental card JSON and manifest JSON. Added regressions for inventory and manifest ambiguity. Tests remain unexecuted.

## AI-1 legal corpus inventory input integrity — 2026-11-15

- `tools/report_legal_corpus_inventory.py` now rejects duplicate keys at every nesting depth in every JSON register it reads. Added regression tests; no corpus status or legal verification is inferred.

## AI-1 legal release-readiness input integrity — 2026-11-15

- Hardened `tools/validate_legal_release_readiness.py` to reject duplicate keys in the canonical permission register and each candidate JSON. Ambiguous candidates cannot be treated as ready; added regression coverage. Tests remain unexecuted.

## AI-1 Phase 2 inventory input integrity — 2026-11-15

- Hardened `tools/validate_phase2_document_inventory.py` with a strict JSON loader. Conflicting duplicate fields cannot override instrument permission, legal status or review-state checks. Added regression tests; unexecuted.

## AI-1 Arabic scorer registry integrity — 2026-11-15

- Completed strict duplicate-key parsing for the Arabic retrieval scorer's reviewer registry and existing metrics report. Added a CLI regression for duplicate reviewer-registry keys; test remains unexecuted.

## AI-1 existing collection sidecar integrity — 2026-11-16

- Hardened `--process-existing` metadata reads with a 1 MiB bounded regular-file read, no-follow open, file identity/change checks, UTF-8 parsing, and duplicate-key rejection. Added duplicate-key and symlink regressions. Tests remain unexecuted.

## AI-1 manual capture sidecar integrity — 2026-11-16

- Hardened `tools/record_manual_capture.py` when reusing existing metadata: bounded 1 MiB regular-file read, no-follow open, inode/change checks and duplicate-key rejection. Added duplicate-key and symlink regressions. Test execution remains blocked.

## AI-1 Labour Law candidate registration input — 2026-11-16

- Candidate registry CLI now uses a bounded 1 MiB regular-file reader with no-follow open, file identity/change checks, UTF-8 validation and duplicate-key rejection before opening the shared legal-corpus connection. Added regression coverage; tests not executed.

## AI-1 evaluation response parsing — 2026-11-16

- `tools/run_legal_eval.py` rejects ambiguous API response JSON at every object depth and returns a safe `RunnerError`; regression coverage added. Tests not executed.

## AI-1 candidate seeder input integrity — 2026-11-16

- `tools/seed_legal_candidates.py` now uses bounded stable-file reads for the candidate catalog and permission register, rejecting symlinks and oversized/changed inputs while retaining duplicate-key rejection. Added regressions; tests not executed.
## AI-2 migration-ledger integrity hardening — 2026-11-16

- Added numbered migration-history immutability migrations to all three profiles: control plane `0024`, firm `0024`, and legal corpus `0004`. Each installs SQLite `BEFORE UPDATE` and `BEFORE DELETE` abort triggers on `schema_migrations`, while allowing new migration rows to be inserted.
- This is delivered through the normal profile migration path, not unversioned startup DDL; existing deployments can roll it out through the control-plane/corpus upgrade and quiesced tenant-fleet migration process. A pre-existing same-name weakened trigger makes the migration fail atomically.
- Added regression coverage for update/delete rejection, idempotent re-entry, refusal of a pre-existing weakened guard, and application of the guards across all three repository profiles. `tests/test_db_migrations.py` and `tests/test_schema_profiles.py` are already registered in the Tests workflow.
- Tenant database preflight now independently reports missing/weakened ledger guards for both the control-plane catalog and each provisioned tenant. Corruption fixtures explicitly remove guards before simulating offline ledger tampering; the normal guarded path remains immutable. `tests/test_tenant_database_preflight.py` is workflow-registered.
- Direct-main commits: migration-runner rollback `e30b576`, regression `8f19050`, profile migrations `89db25f`, `927ac1f`, `d7db063`, documentation `0a181b8`, cross-profile regression `4f10056`, status `f5e8ae4`, blocker register `48a0831`, preflight audit `4e73805`, preflight regressions `7902df9`, preflight docs `87e0d99`. Tests remain unexecuted because GitHub runner allocation/billing is unavailable; this is source implementation, not a test pass.


## AI-2 firm data export audit fail-closed regression — 2026-11-16

- Added a route-level regression that injects a SQLite failure when the firm-data-export success audit event is written. The export must return HTTP 503, must not return an application/zip response, and must not leave a success audit row.
- The existing export implementation builds the archive before writing the success audit, then closes the temporary archive and returns an error if audit persistence fails. The new test pins that security contract.
- Test is in the already workflow-registered separate-database application suite. It is committed but unexecuted; no runtime pass is claimed.


- Added a positive-path firm-export regression as well: the ZIP must contain the firm invitation/membership business records while excluding auth-session, MFA credential and MFA recovery-code files; invitation and membership headers are checked for credential/hash fields. Both export regressions are committed but unexecuted.


- Added a positive-path firm-export integrity regression. It creates a ready original object, exports the firm ZIP, and asserts that the archive contains the exact original bytes at the expected document-scoped path and that the manifest includes the matching path, SHA-256 digest and included status. The test is committed but unexecuted; its method passed standalone AST syntax validation.


## AI-2 grouped primary navigation — 2026-11-16

- Ported the safe information-architecture improvement from draft PR #1610 onto current main without merging its divergent branch. Primary navigation is grouped into Workspace and Firm administration; mobile navigation keeps the groups horizontally scrollable and hides desktop-only group captions.
- All existing destinations remain present. Firm setup remains admin-gated, platform metrics remain platform-admin-gated, and legal corpus/source review remains behind `ME.can_review_legal`. Navigation still clears one-shot document/chunk review targets before switching pages.
- Preserved the current-main answer-rating panel and its save/list/export controls; no answer-rating code was replaced or removed.
- Added a frontend regression contract for route retention, role gates, mobile grouping and answer-rating preservation. Source and test contract are committed directly to main (`5cdf0cb`, `9c14448`).
- Static inspection confirms the expected route entries, role checks and rating panel are present. **The test was not executed** because GitHub Actions runner/billing remains unavailable; no browser, RTL/LTR, responsive or screen-reader acceptance is claimed.


## AI-2 dashboard and document-library hierarchy — 2026-11-16

- The dashboard now places an explicit overdue-work attention panel before its compact activity metrics. It counts overdue tasks and legal deadlines from the existing dashboard payload and links directly to Tasks and Calendar. Duplicate quick-access tiles and dashboard fee/outstanding-fee summary cards were removed; the Finance workspace and navigation entry remain available.
- The global document library keeps its common document-name search visible and moves file type, extraction status, classification and reset controls into a collapsed native `details` disclosure. Existing filter controls and their reset behavior are retained.
- Upload queue results now expose list/list-item semantics and polite live announcements for per-file state updates.
- Added frontend regression contracts for dashboard hierarchy, finance navigation preservation, progressive document filters and upload queue announcements. Direct-main commits: dashboard `2cb3a06`, tests `b0cf5f1`; document/upload UI `3114eff`, tests `e4a59f2`.
- Static inspection only. Tests, browser interaction, Arabic RTL/English LTR, mobile reflow, keyboard and screen-reader acceptance remain unexecuted because GitHub Actions runner/billing is unavailable.


- Added a multi-firm membership-suspension regression. It logs a member into Firm A, suspends only that membership from the Firm A administrator session, then verifies the member can recover from the stale Firm A cookie by switching to still-active Firm B, while Firm A remains inaccessible and the Firm B membership remains active. The test is committed but unexecuted.


## AI-2 matter workspace navigation and document review safeguards — 2026-11-16

- Matter detail navigation now groups all 12 existing tabs into Overview, Work, Documents & research, Finance, and Team & activity. Existing tab IDs and renderers remain intact; the selected group exposes its relevant sub-pages. Section controls use native buttons with `aria-pressed`/`aria-current`, visible focus and narrow-screen horizontal scrolling.
- The matter context strip keeps client, status, case number/year, court, circuit, stage and task progress visible while switching sections.
- Matter-document review now shows OCR and partial-page extraction cautions using the existing extraction metadata. Page display and reviewer prefill accept both `page` and `page_number`.
- The original-download control is displayed only when the case-detail API explicitly reports `original_available=true` (or serialized `1`); otherwise the UI states that the original is unavailable. The existing server endpoint remains the authorization/integrity boundary. Download filenames are sanitized in the UI.
- Added frontend regression contracts for all 12 tab destinations, grouped navigation/context, retention-aware downloads and OCR/page-reference warnings. Direct-main commits: matter UI `9c97603`, tests `020ec75`; review safeguards UI `720b2a8`, tests `1a655f8`.
- Static inspection only. Tests and browser/RTL/LTR/keyboard/screen-reader acceptance remain unexecuted under the GitHub runner/billing restriction.


## AI-2 matter Ask legal-source guidance — 2026-11-16

- Added the same verified-source scope and abstention explanation to matter-level Ask that is already shown in Legal Research. It explains that the default scope searches verified legal text only, abstains when provenance/review requirements are unmet, and distinguishes source-catalog metadata from matter-document search.
- The guidance is informational only; no retrieval scope, answer gate, legal-source trust tier or authorization behavior was changed.
- Added a frontend regression contract. Direct-main UI/test commits: `6bd9e91`, `9a1da54`. Static inspection only; tests and browser acceptance remain unexecuted.


## AI-2 purge authorization validation ordering — 2026-11-16

- Moved positive-integer validation for firm and operator IDs to the start of `purge_approved_requests`, before S3 target authorization and acceptance-manifest inspection. Malformed identifiers now fail before storage-target checks are performed.
- Direct-main implementation commit: `b10645f`. No repository test module or GitHub Actions job was executed; this is a bounded source hardening change, not independent acceptance.


## AI-2 expired-session browser cleanup — 2026-11-16

- Added a shared auth-cookie cleanup helper and invoke it when separate-runtime or legacy authentication rejects a missing, expired, or inactive session. The cleanup clears the session, CSRF, and selected-firm cookies; explicit logout uses the same helper.
- Extended the separate-database expired-session regression to assert all three browser cookies are cleared and the expired token hash is removed from the control-plane session table.
- Direct-main commits: application `c82cbb2`, regression `3ff45f5`. Regression is committed but unexecuted because GitHub Actions billing/runner availability remains blocked; no browser test is claimed.


## AI-2 execution checkpoint — 2026-11-16 15:37 +02:00

- Additional bounded implementation: purge firm/operator identifiers are validated before S3 target/acceptance inspection (`b10645f`); expired/inactive session rejection clears session, CSRF and firm-selection cookies in both runtime modes, with a committed separate-runtime regression (`c82cbb2`, `3ff45f5`).
- Current workstream estimates: tenant isolation/access control 84%; authentication/administration 85%; case management 90%; document processing/security 99%; backup/release readiness 40%. AI-2 overall remains approximately 72.7%; whole-project estimate remains approximately 72%. These are engineering estimates only and do not represent executed tests or security acceptance.
- Two bounded implementation tasks completed in this execution slice; zero repository test modules executed; zero PRs merged in this slice. Five PRs remain open at this checkpoint: four dependency updates and draft UI PR #1610. Dependency PR diffs/lock regeneration were not independently reviewed in this slice; #1610 remains unsuitable for wholesale merge. No safe merge was established.
- GitHub Actions billing/runner allocation remains an external blocker. Local repository checkout and full test execution remain unavailable. Pilot/production decision remains **NOT READY**.


## AI-2 tenant database open-race hardening and dependency maintenance — 2026-11-16

- The tenant SQLite router now revalidates the database inode, database permissions, and all SQLite sidecars after SQLite opens the file and before caching the connection. It rejects a database replacement, permission change, sidecar symlink/non-regular file, or permissive sidecar discovered in that window, and closes the just-opened connection on failure.
- Added a POSIX regression that changes the tenant database mode during the mocked SQLite open and asserts the router rejects the connection and closes the handle. Source commit: `0d9925f`; regression commit: `09a8506`.
- Updated FastAPI from 0.162.0 to 0.162.5 and boto3 lower bound from 1.43.123 to 1.44.2 in one direct-main dependency commit (`f8c8023`). Their one-line Dependabot PRs #1642 and #1643 were closed as superseded, not merged. No dependency installation or integration tests were run.
- PR #1644 (pypdf 7.0.1 major upgrade) and #1645 (Playwright 1.65.1) remain open and unmerged; their PR metadata reported non-mergeable. pypdf major compatibility and browser runtime validation remain outstanding. Draft PR #1610 remains unmerged.
- Validation: source and regression were reviewed statically only. No repository test module, dependency install, browser test, or GitHub Actions job was executed. The GitHub billing/runner issue remains a blocker for hosted checks; local checkout is still unavailable.
- Current engineering estimates: tenant isolation/access control 84.5%; authentication/administration 85%; case management 90%; document processing/security 99%; backup/release readiness 40%; AI-2 overall approximately 72.8%; whole project approximately 72%. These are estimates, not test pass rates or acceptance evidence.
- Execution-slice totals: 1 bounded tenant-router source hardening change, 1 regression added, 2 dependency pins updated, 2 superseded PRs closed, 0 PRs merged, 0 repository test modules executed. Remaining open PRs: #1610, #1644, #1645. Pilot/production remains **NOT READY**.


## Dependency lock consistency correction — 2026-11-16

- Reverted the direct FastAPI 0.162.5 and boto3 >=1.44.2 requirement edits in commit `ea88d36`: the checked-in `requirements-py312.lock` still pins FastAPI 0.162.0 and boto3/botocore 1.43.123, so the direct changes would make the lock-drift gate fail and boto3's lock pin would not satisfy the new lower bound.
- PRs #1642 and #1643 remain closed; GitHub rejected reopening them because their Dependabot branches had been deleted. They were not merged and no dependency upgrade is currently applied. A new dependency update must regenerate the hash lock with the pinned Python 3.12 pip-tools resolver before it is eligible for review.
- Corrected execution totals: tenant router source hardening 1; regression added 1; dependency upgrades retained 0; PRs merged 0; PRs closed as superseded 2; repository test modules executed 0. Open PRs remain #1610, #1644 and #1645.
- Estimates remain tenant isolation/access control 84.5%, authentication/administration 85%, case management 90%, document processing/security 99%, backup/release readiness 40%, AI-2 approximately 72.8%, whole project approximately 72%. No test pass, dependency lock validation, or pilot readiness is claimed.


## AI-2 tenant path substitution race closure — 2026-11-16

- Extended post-open tenant storage revalidation to reject the database path itself becoming a symlink during SQLite open, even when the symlink resolves to the same inode captured before open. Source commit: `510451f`.
- Added a POSIX regression that replaces the database path with a symlink during the mocked open and asserts the newly opened handle is closed and never cached. Test commit: `ccdb445`.
- Static review only; neither new tenant-router regression nor any repository test module has been executed. Tenant isolation estimate remains 84.5% pending runtime evidence; other workstream and overall estimates remain unchanged. Open PRs: #1610, #1644, #1645; 0 PRs merged.


- Additional isolated Python filesystem reproductions passed for both new race conditions: (1) replacing the open database pathname with a symlink to the same inode is detectable via `Path.is_symlink()` even though device/inode identity is unchanged; (2) changing database permissions to `0644` during the open window is visible to the post-open mode check. These were small harnesses of the filesystem conditions, **not executions of `tests/test_tenant_storage.py` or the repository test suite**.


## AI-2 backup/restore root-path safety — 2026-11-16

- The witnessed backup/restore drill now rejects filesystem root as either BACKUP_DIR or RESTORE_PARENT before creating a bundle or restore target. This closes a path-overlap edge case where the string-prefix check could miss `/` because the normalized root plus slash becomes `//`. Source commit: `a19ff62`.
- Added a regression covering both root positions in `tests/test_backup_restore_drill_paths.py`. Test commit: `5f4ddc8`.
- An isolated shell harness exercised both root cases and an ordinary non-root pair: both root cases were rejected and the ordinary pair remained eligible. This is not execution of the repository test module. Backup/release estimate remains 40% because full encrypted backup/restore, recovery and witness acceptance remain outstanding.


- Follow-up: after physical overlap validation, the drill now replaces the caller-supplied backup and restore directory variables with their canonical physical paths before invoking backup/restore commands. This prevents the write phase from switching back to a symlink-containing alias. Source commit: `97f398a`. No repository test module was executed.


## Repository PR state refresh — 2026-11-16

- PR #1651 (`Serve the missing logo asset and diagnose Legal Research 404s`) was merged on GitHub as `11c1d252720ac2b5bcb0e2ed68eaf14f33afd93b` after the earlier inspection. The change adds both icon URL routes and bounded method/status/path diagnostics for Legal Research API failures. The PR's regression contract is committed but has not been executed here; no browser or route-runtime acceptance is claimed.
- Current open PRs are #1610 (draft workspace simplification), #1644 (pypdf 7.1.0 major upgrade), and #1645 (Playwright 1.65.1). PRs #1642/#1643 remain closed and not merged; dependency pins remain aligned with the checked-in hash lock.
- Current execution slice: tenant database open/symlink race hardening (1 source change series, 2 regression contracts), backup/restore root and canonical-path hardening (1 source change series, 1 regression), isolated filesystem/shell harnesses passed, 0 repository test modules executed. PR #1651 was merged externally; no PR was merged by this execution. Pilot/production remains **NOT READY**.


## AI-2 purge CLI authority validation — 2026-11-16

- Both local and S3 purge command-line entry points now reject non-positive firm and operator IDs immediately after argument parsing, before environment/acceptance checks, database access, offboarding inspection or AWS client creation. This complements the existing function-boundary validation.
- Added one regression covering both CLI entry points and asserting argparse exits before environment validation. Source commits: local `6f13239`, S3 `3a602fd`; regression commit: `491168f`.
- Static inspection only; the purge test module has not been executed. No purge was performed.


## AI-2 database runtime authority input validation — 2026-11-16

- `DatabaseRuntime.create_firm_membership` now rejects boolean, non-integer, zero and negative user/firm IDs, validates optional creator IDs the same way, and rejects non-string roles before opening a control-plane transaction.
- `create_initial_firm_owner` now rejects invalid firm IDs and non-string/empty password hashes before querying or writing. This prevents Python booleans being accepted as integer firm identifiers and avoids storing a non-string bootstrap credential value.
- Added runtime regressions for invalid ID shapes, creator IDs, role types, and password-hash types. Source commits: `0fe6c49`, `c50a12e`; regression commits: `3c55fae`, `96a22e4`.
- Static review only; `tests/test_database_runtime.py` remains unexecuted. No identity or membership records were created in the repository.


- An isolated Python ID-shape harness confirmed the same validation predicate rejects `0`, `-1`, `True`, a numeric string and `None`, while accepting a positive integer. This validates the predicate only; the repository runtime regression was not executed.


## Consolidated AI-2 execution checkpoint — 2026-11-16

| Workstream | Current estimate |
|---|---:|
| Tenant isolation / access control | 84.5% |
| Authentication / firm administration | 85% |
| Case management | 90% |
| Document processing / security | 99% |
| Backup / release readiness | 40% |
| AI-2 overall | 72.8% |
| Whole project | 72% |

These are engineering estimates, not acceptance rates. This slice committed tenant database post-open inode/permission/sidecar checks and symlink-race rejection, CLI and runtime validation for purge/firm authority identifiers, stricter initial-owner credential typing, and backup/restore filesystem-root and canonical-path protections. Regression contracts were added for each area. Four isolated predicate/filesystem/shell harnesses passed; **zero repository test modules were executed** and no GitHub Actions jobs ran.

- Task accounting for this slice: 6 bounded source hardening edits across 4 workstreams; 5 regression-test additions/extensions; 4 isolated harnesses passed; 0 repository test modules run; 0 PRs merged by this execution.
- PR #1651 was merged externally as `11c1d25`. Current open PRs: #1610 (draft), #1644 (pypdf 7.1.0), #1645 (Playwright 1.65.1). All three currently report non-mergeable. PRs #1642/#1643 remain closed and unmerged; their direct requirement edits were reverted because the Python 3.12 hash lock was not regenerated.
- No hosted CI, dependency installation, browser acceptance, encrypted restore drill, live S3/KMS validation, or witnessed recovery rehearsal has been completed. GitHub billing/runner allocation and lack of local checkout remain blockers. The application is **NOT READY** for a law-firm pilot or production.


## AI-2 request-time catalog write isolation — 2026-11-16

- Tenant routing now receives a dedicated read-only control-plane catalog connection (`mode=ro`, `PRAGMA query_only=ON`, foreign keys verified) instead of the writable catalog connection used by firm provisioning. The router only resolves trusted firm-to-database mappings; it has no need to mutate the control plane.
- Added a runtime regression that verifies both pragmas and proves an INSERT is rejected without creating a row. Source commit: `36579f5`; regression commit: `97b7b24`.
- An isolated SQLite harness confirmed that read-only URI plus query-only rejects writes while foreign-key enforcement remains enabled. This is not execution of `tests/test_database_runtime.py`.


## Latest AI-2 checkpoint — 2026-11-16

| Workstream | Completion estimate |
|---|---:|
| Tenant isolation / access control | 84.7% |
| Authentication / firm administration | 85.2% |
| Case management | 90% |
| Document processing / security | 99% |
| Backup / release readiness | 40.2% |
| AI-2 overall | 72.9% |
| Whole project | 72.1% |

Updated estimates reflect source implementation only; regression execution and external acceptance remain open. In this execution, five implementation files were hardened across tenant routing, runtime authority inputs, purge CLI boundaries, and backup/restore paths; six regression methods were added or extended; five isolated Python/filesystem/shell harnesses passed. No repository test module or GitHub Actions job ran. No production purge, live AWS action, or restore drill was performed.

- Remaining open PRs: #1610 (draft; divergent UI work), #1644 (pypdf 7.1.0 major version; lock regeneration/compatibility not validated), #1645 (Playwright 1.65.1; browser runtime not validated). All report non-mergeable. #1651 merged externally; no PR merged by this execution. #1642/#1643 are closed, unmerged, and their requirement changes were reverted.
- Blockers: GitHub billing/runner allocation; no local checkout; Python 3.12 hash-lock regeneration and clean dependency install; complete test suite; browser/RTL/LTR/accessibility acceptance; witnessed encrypted backup/restore and operational sign-off; live S3/KMS and independent security review. Pilot/production remains **NOT READY**.


## AI-2 shared database profile open-race hardening — 2026-11-16

- Cached control-plane and legal-corpus connections now rerun the complete profile storage validation after SQLite opens the file, before retaining the handle. This catches symlink substitution and permission/sidecar changes in the open window, in addition to the existing device/inode comparison.
- Added a POSIX control-plane regression that replaces the database path with a symlink to the same inode during the mocked open and asserts the new connection is closed rather than cached. Source commit: `4953fa5`; regression commit: `2c25160`.
- Static review only; the database runtime regression module remains unexecuted.


- Registered both `test_database_runtime.py` and `test_tenant_storage.py` in the focused security regression matrix, so the new profile/catalog and tenant-router regressions are part of the operator-run security gate. Script commit: `dfb2661`. The matrix itself has not been executed.


- The fresh writable provisioning catalog connection and the read-only request-time router catalog connection now both revalidate the control-plane file/sidecars and compare device/inode after SQLite opens it. This closes the same open-window substitution gap at both catalog entry points. Source commit: `f78e299`; added read-only router-catalog symlink-race regression: `624e9b8`.


## Latest checkpoint refresh — 2026-11-16

- Additional shared-profile work: request-time router catalog reads are read-only; both writable provisioning and read-only routing catalog connections revalidate the control-plane storage boundary after SQLite open; cached control/corpus connections now repeat profile/sidecar checks after open. Regression coverage includes a same-inode symlink substitution on the shared control-plane path.
- Current slice totals, corrected: 6 implementation files changed across tenant storage, shared database runtime, purge CLI, backup/restore, and security-matrix registration; 8 regression methods added/extended; 5 isolated harnesses passed; 0 repository test modules executed; 0 PRs merged by this execution.
- Current estimates remain tenant isolation/access control 84.7%, authentication/firm administration 85.2%, case management 90%, document processing/security 99%, backup/release readiness 40.2%, AI-2 72.9%, whole project 72.1%. These are not test or acceptance percentages.
- Current open PRs remain #1610, #1644 and #1645, all non-mergeable. #1651 merged externally. Dependency lock remains aligned to original requirements; no new dependency version was retained. GitHub billing/runner, local checkout, dependency installation/lock regeneration, repository tests, browser acceptance, S3/KMS and witnessed recovery remain blockers. Pilot/production: **NOT READY**.


## AI-2 original-document object finalization race — 2026-11-16

- Local private object finalization now checks the staged file's device/inode and regular-file type before linking, then verifies both the published destination and remaining staged path still reference that exact regular inode. If a staged path is swapped for a symlink or another file during linking, the published destination is removed and finalization fails closed.
- Added a POSIX regression that replaces the staged path with a symlink immediately before the hard-link operation and asserts no final object is published and the outside target bytes remain unchanged.
- Isolated filesystem reproduction passed: substituted symlink was not published; final path remained absent; outside bytes were unchanged. This is not execution of `tests/test_original_file_storage.py`.
- Source commit: `a2b126c`; regression commit: `1a93620`. Repository test modules executed in this slice: 0.


## AI-2 restore destination boundary hardening — 2026-11-16

- Both the public restore entry point and the internal verified-byte restore path now share one destination validator. It rejects filesystem-root parents, resolves the parent directory before use, and rechecks that the canonical destination does not already exist. This prevents the restore API from accepting a root-level target merely because the shell drill wrapper rejects it.
- Added a regression proving root-parent rejection occurs before attempting to read the supplied backup file and creates no destination.
- Isolated path-validation harness passed for a normal temporary parent and a filesystem-root parent. This is not execution of `tests/test_database_backup_bundle.py`.
- Source commit: `664008b`; regression commit: `c28e4db`. Repository test modules executed: 0.


## AI-2 recovery locator input hardening — 2026-11-16

- S3 recovery archive download now reads its locator JSON using a bounded (16 KiB), non-blocking, no-follow file descriptor; it verifies the opened descriptor is a regular file and parses only the bytes read from that descriptor. This removes the previous symlink-check/stat/read_text path race and rejects FIFOs/devices before parsing.
- Added valid-object, oversized-file, non-object JSON, and symlink regression cases in `tests/test_manage_recovery_locator.py`; registered the module in the security regression matrix.
- Source commit: `85f51e1`; test commit: `8e135cff`; matrix commit: `778555d`. No repository test module executed.


- The focused security matrix now explicitly includes `test_original_file_storage.py` (including the staged-object symlink substitution regression) and `test_backup_restore_safety.py` in addition to the bundle and recovery-locator modules. Matrix registration commit: `c1d2ff6`. No matrix execution is claimed.


- An isolated reproduction of the exact recovery-locator read contract passed the valid-object case and rejected oversized and symlink inputs. This remains a harness, not execution of the new test module.


## Consolidated execution checkpoint — 2026-11-16 (continued)

| Workstream | Completion estimate |
|---|---:|
| Tenant isolation / access control | 84.7% |
| Authentication / firm administration | 85.2% |
| Case management | 90% |
| Document processing / security | 99.1% |
| Backup / release readiness | 40.5% |
| AI-2 overall | 73.0% |
| Whole project | 72.2% |

Additional completed source work in this continuation:
- Local original-file finalization verifies the exact staged inode before and after no-follow hard-link publication; staged-path substitution cannot leave a finalized symlink.
- Both public and internal encrypted-bundle restore paths reject filesystem-root parents and canonicalize/recheck the destination parent.
- S3 recovery locator JSON is read from a bounded 16 KiB no-follow descriptor and must be a regular file and JSON object.
- Registered local original-object storage, backup/restore safety, and recovery-locator regressions in the focused security matrix.

Execution evidence: 3 source files hardened in this continuation; 3 regression groups added; 3 isolated filesystem/path/locator harnesses passed; 0 repository test modules executed; 0 CI jobs executed; 0 PRs merged by this execution. Latest source commits include `a2b126c`, `664008b`, and `85f51e1`; test commits include `1a93620`, `c28e4db`, and `8e135cff`; matrix updates `778555d` and `c1d2ff6`.

PR review: #1644 changes only `requirements.txt` to pypdf 7.1.0, but the hash lock is not regenerated and the PR is non-mergeable; leave unmerged. #1645 changes only the browser Playwright pin and is non-mergeable; browser install/runtime acceptance is absent. #1610 remains draft and non-mergeable; its patch touches retrieval/application behaviour and frontend/tests and is not safe for wholesale merge. No PR was force-merged.

Remaining blockers: GitHub billing/runner allocation, no local checkout, no actual repository test execution, no lock regeneration/install, no browser acceptance, no witnessed encrypted restore, and no live S3/KMS validation. Source implementation is continuing; acceptance remains blocked. Pilot/production: **NOT READY**.


## AI-2 recovery-download and backup-object preflight hardening — 2026-11-16

- Encrypted S3 recovery downloads now validate locator structure and the local destination (new file, existing non-symlink directory, canonical parent) before contacting S3 or KMS. The locator's configured KMS ARN is checked after the KMS key is resolved and before the exact-version object request. This avoids cloud reads for malformed manifests or unsafe local targets.
- Added regressions proving malformed locator keys and pre-existing destinations are rejected before versioning, KMS, or object-head calls; existing destination bytes must remain unchanged. Source commits: `ef47ed7`, `843fd3d`; test commit: `df4ae60`.
- Local original-object backup now opens each source once with no-follow/non-blocking flags, verifies the opened descriptor is the same regular inode inspected before open, streams bytes into an exclusive mode-0600 target while hashing, and rejects size/digest drift before accepting the backup copy. This removes the previous separate path-based stat/hash/copy sequence and its replacement window.
- Added direct regressions for verified descriptor copying and symlink substitution at open time, including preservation of outside bytes. Source commit: `bd40c3a`; test commit: `083fb3c`.
- An isolated descriptor harness passed for a regular-file read and rejected a symlink without changing the outside target. This is not execution of either repository test module.
- The focused security matrix already includes `test_database_backup_bundle.py` and `test_database_backup_archive.py`; no matrix change was needed.
- Validation accounting for this slice: 2 implementation files hardened; 2 regression modules extended with 4 new tests; 1 isolated descriptor harness passed; 0 repository test modules executed; 0 Actions jobs executed; 0 PRs merged.
- Updated engineering estimates: tenant isolation/access control 84.7%; authentication/firm administration 85.2%; case management 90%; document processing/security 99.1%; backup/release readiness 41%; AI-2 overall 73.2%; whole project 72.3%. These are source-completion estimates, not test pass rates or operational acceptance.
- Remaining blockers are unchanged: no local checkout or runnable repository test environment, GitHub billing/runner issue, no lockfile regeneration/dependency install, no browser acceptance, no live S3/KMS verification, and no witnessed encrypted restore. Pilot/production remains **NOT READY**.


## AI-2 backup object stream and recovery preflight follow-up — 2026-11-16

- Extended local backup-object protection to S3-backed originals: metadata SHA-256 and byte size must be valid typed values before store access; the streamed copy stops immediately if it exceeds the recorded size or archive cap, hashes the bytes actually copied, and fsyncs the exclusive mode-0600 destination before acceptance. This supplements the store's presence/verification checks with an independent copy-time integrity check.
- Added a regression using a fake S3 object stream to prove overlong data is rejected and no backup copy remains, plus malformed byte-size metadata is rejected before object-store calls. Source commit: `9c8f6ef`; test commit: `980a496`.
- The local original-object descriptor-copy regressions and recovery-download preflight regressions remain committed in the focused security test modules. All are statically reviewed only; none of the repository test modules has run.
- Cumulative work in this continuation: 3 source hardening commits across 2 implementation files; 5 new regression tests across 2 test modules; 1 isolated descriptor/symlink harness passed; 0 repository test modules executed; 0 hosted Actions jobs executed; 0 PRs merged.
- Updated estimates: tenant isolation/access control 84.7%; authentication/firm administration 85.2%; case management 90%; document processing/security 99.1%; backup/release readiness 41.5%; AI-2 overall 73.4%; whole project 72.4%. Estimates measure implementation progress only; operational validation remains outstanding.
- No safe open PR became mergeable through this work. Dependency lock and browser validation remain unresolved; no force merge or bypass was attempted. GitHub billing/runner and missing local checkout still prevent repository test execution. Live S3/KMS verification and witnessed restore remain outstanding. Pilot/production: **NOT READY**.


- Follow-up static review of the S3 object-copy failure path found a descriptor-cleanup edge case if wrapping the newly created output descriptor failed. The copy now transfers descriptor ownership explicitly, closes any descriptor not transferred, removes partial output on failure, and normalizes filesystem/type/overflow errors to the backup-domain exception. Source commit: `9b9ecb7`. This is a defensive cleanup refinement; no additional test execution is claimed.


## AI-2 backup invocation authority validation — 2026-11-16

- `create_backup_bundle()` now requires `quiesced is True` rather than accepting any truthy value. A string such as `"false"` or integer `1` can no longer accidentally assert that application writes have been paused.
- The backup retention `keep` argument now rejects booleans, floats, strings and non-positive values; only a positive integer is accepted before filesystem or database work.
- Added regression coverage for false-like and truthy non-boolean quiescence values and malformed retention counts. Source commit: `f101d24`; test commit: `f4d4d7e`.
- The regression is in the already registered `test_database_backup_bundle.py` module. Static review only; repository test execution remains blocked.


## AI-2 original-object inventory and backup assertion hardening — 2026-11-16

- Local original-object inventory now rejects dangling symlink roots before treating them as absent. On POSIX, it inventories through no-follow directory descriptors, checks each firm namespace is the same real directory opened after inspection, and uses no-follow stat calls for object entries. This closes root/namespace substitution windows in the inventory pass; the non-POSIX fallback retains explicit per-entry symlink checks.
- Added regression coverage for dangling root symlinks and symlinked firm namespaces. Source commit: c23aa42; test commit: 63b1e79.
- An isolated directory-descriptor harness passed for regular root/namespace/object traversal and rejected a dangling symlink root. It is not execution of the repository test module.
- The same continuation also made backup quiescence an exact boolean assertion and validated retention count types before work begins (source f101d24, tests f4d4d7e).
- Updated engineering estimates: tenant isolation/access control 84.7%; authentication/firm administration 85.2%; case management 90%; document processing/security 99.1%; backup/release readiness 42.1%; AI-2 overall 73.7%; whole project 72.6%. These estimates reflect code implementation only.
- Cumulative continuation accounting: 4 source hardening commits across 2 implementation files; 7 regression cases added across 2 test modules; 2 isolated filesystem/descriptor harnesses passed; 0 repository test modules executed; 0 Actions jobs executed; 0 PRs merged. The relevant backup/recovery test modules are already registered in the security regression matrix.
- Blockers remain: hosted CI billing/runner allocation, no local checkout, no repository test execution, no dependency lock regeneration/install, no browser acceptance, no live S3/KMS verification, and no witnessed restore. Pilot/production remains NOT READY.
