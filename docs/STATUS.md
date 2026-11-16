# Legal Copilot — release-candidate status

**Updated:** 2026-11-16  
**Decision:** **NOT READY** for lawyer pilot or production. This is an engineering checkpoint, not legal, security or operational certification. Historical tracker detail is archived at [STATUS history](archive/STATUS_history_through_2026-11-13.md).

## AI-1 delivery

| Workstream | Current state |
|---|---|
| Answer rating contract | **Complete.** [Contract](answer_rating_contract.md) defines answer ID, rating, cited-article rating, notes, rater, timestamp, trust tier and UTF-8 CSV export for AI-2. The firm export now includes message-time `trust_tier` with a conservative fail-closed mapping; `tools/adapt_answer_rating_export.py` implements the canonical interchange and `docs/answer_rating_contract.md` documents its usage. A route regression passes actual export rows through the adapter; execution remains pending. Adapter tests are committed and registered in `.github/workflows/tests.yml`, but unexecuted. `tools/validate_answer_ratings.py` validates exported CSV structure, enums and timezone-aware timestamps; tests are committed but unexecuted. Evidence-URL validation parity was extended across `research_inspector`, `evaluate_legal_answers`, `app.validate_review_evidence_url`, the deadline-rule verifier, and the legal-document collector/manifest, manual-capture, deadline-rule attestation, source-match rights, legal-draft source and bulk-law-import URL checks (DEL, raw backslashes, query/fragment ambiguity where evidence URLs are used); regression tests remain unexecuted. The evaluation API runner now rejects DEL and raw-backslash base URLs; the reviewed-question/result JSONL parser and reviewer-registry JSON loader now reject duplicate object keys at every nesting depth; the legal-candidate seeder validates HTTPS source-page, terms, official-PDF and secondary-metadata URLs and rechecks source hosts against the permission register. New candidate-version registration also forces under_review/pending_source_review and zero authenticity/status/amendment verification flags, ignoring candidate-supplied trust claims; the metadata-only candidate registrar rejects self-granted collection or commercial-reuse permissions, validates stable HTTPS source/version/review-evidence URLs, binds version URLs to their declared source host, and directs grants to the canonical source-permission workflow. The read-only legal-source review queue now applies the same signed-query/fragment rejection to review-event evidence URLs; this is locator hygiene, not evidence-authenticity validation. The Gazette importer CLI now has a direct-execution import fallback; its CLI regression explicitly clears `PYTHONPATH`. |
| Negation guard | **Implemented; tests unexecuted.** The always-on guard remains in `app.ask()`. AI-1 claim-support coverage now handles English contracted/negated obligations (including curly apostrophes and do-not-have-to non-obligation forms), Arabic diacritics and tatweel, Egyptian ma-verb-sh negation, masculine/feminine obligation forms, denial of entitlement, and permission/prohibition reversals, including Egyptian `ما...ش` forms such as `ماينفعش`, `مايحقش` and `مايسمحش`. Arabic query expansion distinguishes interrogative `ما` from negation and resets scope at punctuation/contrast clauses. Focused regressions are registered; no test pass is claimed. |
| Firm-test source-matched mode | **Fail-closed response gate implemented; real retrieval unavailable.** Exact firm-ID + non-production environment flag, source-only fallback and explicit `source-matched, not lawyer-verified` API label are on main (`ce2ebc8`, `7c5e09d`, `5ec22a1`, `b377af0`, `311287d`, `2009b9f`, `29e4a13`). The dedicated scope currently returns no candidates; tests use synthetic hits and are unexecuted. Never enable in production. |
| Reviewer spreadsheets | **Templates complete.** [Gazette review CSV](legal_evidence/law_14_2025_gazette_comparison_template.csv) has 311 rows, machine comparison labels, similarity, page locators and prior page-review notes. Text and lawyer decision fields remain blank pending authorized source text. [Deadline CSV](legal_evidence/deadline_rules_lawyer_review.csv) has five draft rules. [Review guide](legal_evidence/lawyer_review_quick_guide.md) gives steps and time estimates. |
| Evaluation | **116 unapproved curated candidate questions complete; these are not observed user questions or lawyer-approved ground truth.** The structural validator checks Arabic question text, question ID/text uniqueness, one formal/one Egyptian-colloquial variant per article pin, expected-article pin consistency and no premature lawyer approval/release flags. Static audit found 116 rows (58 formal/58 colloquial), 58 proposed article pins, zero duplicate IDs/texts, zero approved answers and zero release-eligible rows. Stable bounded JSONL readers and scorer identifier checks are implemented. Metrics remain unavailable. Structural-validator, negation reproducer, firm-test gate, rating-validator and adapter tests are now explicitly registered in `.github/workflows/tests.yml`; they remain unexecuted. Dataset contains 58 formal + 58 colloquial questions with machine-proposed article IDs. [Unreviewed inventory](legal_evidence/law14_2025_retrieval_baseline_unreviewed.json) records 116 unique questions, zero approved answer keys and zero run records. Top-3 hit rate, wrong-article rate and abstention rate are null—not zero. The scorer requires lawyer-approved labels and real retrieval runs. |
| Documentation | **Complete.** Detailed tracker archived; this is the concise release summary. The Phase 2 metadata inventory validator now rejects credentialed/empty-userinfo URLs, fragments, literal backslashes, invalid ports, whitespace/control characters and signed-query parameters; regression cases are committed but unexecuted. |
| Gazette importer owner handoff | **Prepared.** Added [operator handoff](legal_evidence/law14_2025_import_operator_handoff.md) and [metadata template](legal_evidence/law14_2025_import_metadata.template.json), including exact input requirements, SHA-256 procedure, CLI command and trust safeguards. The importer accepts explicit expected promulgation/attached-law counts and reports internal gaps, missing trailing numbers, out-of-range headings, and an entirely absent expected block; retrieval timestamps must be timezone-aware when datetimes and cannot be in the future. OCR cache pages are created exclusively, read through stable no-follow descriptors, and capped at 8 MB per page. Collection metadata/original/extraction collision reads and both Law 14/OCR evaluation JSONL inputs now use stable bounded readers. Focused regression cases are committed but unexecuted. Metadata JSON now rejects duplicate keys at every nesting depth in the Gazette text importer, legacy PDF law importer, legal collection manifest, manual-capture catalog/existing provenance sidecars, the canonical source-permission register used by the collection gate, and both legal-candidate seeder inputs (candidate catalog and permission register); regression cases are committed but unexecuted. No real import run is claimed; authorized UTF-8 text and truthful supplier/source metadata are still required. |

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
| Validation | GitHub Actions runner allocation/billing prevents hosted test execution. Latest exact-head check on `main` commit `a202cc6bee4bb6de192feaa57d0206c1c27409f4` (2026-11-16): Tests run `43948912741` and Browser acceptance `43948912737` failed before any job step; inspected jobs report `runner_id=0` and `steps=[]`. CodeQL run `43948912966` likewise has zero-step jobs (`runner_id=0`, one job not yet allocated); dependency audit run `43948912813` had no jobs returned at inspection time and remains unresolved. This confirms runner allocation/service failure, not an application test failure or pass. The preceding exact-head check on `8b8f7589277f0eca11a5fc8be5d60eb294c37549` showed the same pattern. This is runner/service allocation evidence, not a code-test failure or pass. A static GitHub directory/workflow audit finds all 186 top-level `test_*.py` modules registered in the workflow or known-unrun register; this is not execution. No newly added local tests have been executed in this work session. Direct-main commits are implementation evidence, not test passes or pilot acceptance. |

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
- Current open PRs are #1610 (draft workspace simplification) and #1644 (pypdf 7.1.0 major upgrade). PR #1645 (Playwright 1.65.1) was subsequently merged on GitHub as `5f568522b4766ae226fc0e465d625a0934ebc3b8`; this execution did not merge it. PRs #1642/#1643 remain closed and not merged; dependency pins remain aligned with the checked-in hash lock.
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


## AI-2 S3 backup inventory response validation — 2026-11-16

- S3 object inventory now fails closed on malformed provider responses: response and Contents must have the expected mapping/list shapes, every entry must be a mapping with a string key under the originals prefix, and IsTruncated must be an explicit boolean. Missing, malformed, or repeated continuation tokens are rejected rather than silently treating an incomplete inventory as complete.
- Added regressions for non-string keys, non-object entries, and omitted truncation state. Source commit: e89ac58; test commit: cd2142a.
- Existing repeated-token and inventory namespace tests remain in the same registered S3 storage module. Static review only; no repository test module or hosted job ran.
- Updated estimates: tenant isolation/access control 84.7%; authentication/firm administration 85.2%; case management 90%; document processing/security 99.1%; backup/release readiness 42.4%; AI-2 overall 73.9%; whole project 72.7%. Source progress only; pilot/production acceptance remains incomplete.
- Additional work in this slice: 1 S3 inventory implementation change; 2 regression methods; 0 repository tests executed; 0 Actions jobs executed; 0 PRs merged. No safe PR is currently mergeable; #1610 remains draft and #1644/#1645 remain dependency/runtime changes without lock/browser acceptance.


## AI-2 backup destination side-effect prevention — 2026-11-16

- Backup output paths are now physically resolved and checked against tenant/object storage roots before any output directory is created. Previously, a new output directory reached through a symlinked parent could be created inside protected tenant storage and only then rejected. The overlap check now runs first; directory creation follows only after the canonical destination is accepted.
- Added a regression using a symlinked parent alias into tenant storage and asserting the rejected destination directory is never created. Source commit: 000998d; test commit: 2890bd2.
- Static review only; the registered backup bundle test module remains unexecuted. Updated estimates: tenant isolation/access control 84.7%; authentication/firm administration 85.2%; case management 90%; document processing/security 99.1%; backup/release readiness 42.8%; AI-2 overall 74.1%; whole project 72.9%. These are implementation estimates, not test/acceptance rates.


## AI-2 local backup namespace descriptor anchoring — 2026-11-16

- Local original-object backup now opens the configured object root and firm namespace as no-follow directory descriptors, verifies the opened namespace device/inode against its no-follow directory entry, and opens each object relative to that pinned namespace descriptor. Replacing the namespace path with a symlink after it is opened cannot redirect the backup read to an outside directory.
- Retained a guarded path-based fallback for platforms without directory-relative open support; the focused POSIX regression skips only when that primitive is unavailable.
- Added a regression that renames the opened namespace and replaces its old pathname with a symlink to an outside directory, then verifies the copied bytes still come from the already-opened namespace. Source commits: 5d1ab80, c8f0541; test commits: f9d4e15, 05c7a77.
- An isolated namespace-dirfd harness passed: the path swap did not redirect the open and outside bytes remained unchanged. This is not execution of the repository test module.
- Updated estimates: tenant isolation/access control 84.7%; authentication/firm administration 85.2%; case management 90%; document processing/security 99.1%; backup/release readiness 43.3%; AI-2 overall 74.4%; whole project 73.1%. Implementation estimates only.


## AI-2 recovery locator JSON ambiguity rejection — 2026-11-16

- Recovery locator parsing now rejects duplicate JSON object keys at every nesting depth using an object-pairs hook. Previously, the JSON parser silently retained the last duplicate value, allowing a locator file to contain conflicting bucket/version/KMS fields without an explicit parse failure.
- Added a regression for duplicate nested keys. Source commit: 8c150c8; test commit: 11e7f86. The recovery-locator module is already registered in the focused security matrix.
- Static review only; no repository test module or Actions job ran. Updated estimates: tenant isolation/access control 84.7%; authentication/firm administration 85.2%; case management 90%; document processing/security 99.1%; backup/release readiness 43.6%; AI-2 overall 74.6%; whole project 73.3%. Implementation estimates only; recovery acceptance remains outstanding.

- A separate isolated Python parser harness accepted a valid object and rejected a nested duplicate key under the same object-pairs-hook contract. This does not count as execution of tests/test_manage_recovery_locator.py.


## AI-2 bounded S3 inventory pagination — 2026-11-16

- Added a hard page ceiling to S3 originals inventory pagination. Repeated-token detection already rejected a stuck cursor; the new bound also stops a provider that returns a fresh token forever, preventing unbounded inventory loops and memory growth. The limit is 10,000 pages and fails closed when exceeded.
- Added a regression with unique continuation tokens proving the inventory stops exactly at the configured page ceiling. Source commit: 0f5fe1f; test commit: 6ae6445.
- The S3 storage module is already registered in the focused security regression matrix. Static review only; no repository test or CI job ran. Updated estimates: tenant isolation/access control 84.7%; authentication/firm administration 85.2%; case management 90%; document processing/security 99.1%; backup/release readiness 43.8%; AI-2 overall 74.8%; whole project 73.5%.


## AI-2 backup inventory and exact-version recovery download hardening — 2026-11-16

- Local original-object inventory now rejects dangling root symlinks before treating a missing path as an empty store. On POSIX it pins the object-root and firm namespace directories with no-follow descriptors, verifies namespace inode identity, and inventories children using descriptor-relative no-follow metadata. Added regressions for dangling root and namespace symlinks. Source commit: `c23aa42`; test commit: `63b1e79`.
- Exact-version S3 recovery downloads now pin the already-validated destination directory with a no-follow directory descriptor, verify its device/inode, create the target exclusively relative to that descriptor, and remove partial output relative to the same pinned directory on failure. A final path identity check prevents reporting success if the destination directory was renamed/replaced during streaming.
- Added a regression that swaps the destination directory for a symlink while the S3 body is being read; the operation must fail, must not write into the symlink target, and must remove the partial file from the originally opened directory. Source commits: `0247668`, `aa00c3d`; test commit: `c7930c5`.
- Both test modules are already included in the focused security matrix. Static source/test review only: 0 repository test modules executed, 0 Actions jobs executed. No CI result is implied.
- Current estimates (implementation, not acceptance): tenant isolation/access control 84.7%; authentication/firm administration 85.2%; case management 90%; document processing/security 99.1%; backup/release readiness 44.5%; AI-2 overall 75%; whole project 73.7%.
- Remaining blockers: GitHub billing/runner issue; no local checkout or dependency environment; no repository test execution; no live S3/KMS verification; no witnessed restore or browser acceptance. I am not blocked from further source-level work, but pilot/production remains **NOT READY**.


- Portability refinement: the descriptor-relative recovery-download path is selected only when the runtime advertises `dir_fd` support for `os.open`. Other platforms retain exclusive/no-follow file creation where available and verify parent identity before reporting success. This avoids making the recovery download API unconditionally depend on POSIX directory-relative open support. Source commit: `2741b48`.


- Final static checkpoint for this continuation: verified the recovery-download source contains the stat dependency, the runtime dir_fd capability guard, final parent identity verification and descriptor-relative cleanup; verified both backup test modules remain registered in scripts/security_regression_check.sh. This is source inspection only, not a test run.
- Continuation totals since the previous status checkpoint: 4 implementation commits touching database_backup.py and database_backup_archive.py, 3 regression modules updated across the slice (backup bundle, archive transport, plus existing inventory tests), 6 regression cases added/extended, and 0 repository test modules / 0 Actions jobs executed. No PR was merged.
- Backup/release readiness estimate revised to 44.8%; AI-2 overall 75.1%; whole project 73.8%. Other workstream estimates remain tenant isolation/access control 84.7%, authentication/firm administration 85.2%, case management 90%, and document processing/security 99.1%.


## AI-2 encrypted recovery multipart upload source-size binding — 2026-11-16

- Multipart recovery uploads now count bytes read from the already-open, previously hashed source descriptor. A source that grows beyond the verified size or shrinks before multipart completion is rejected before completion; the incomplete multipart upload is aborted by the existing failure path.
- Added a regression that appends bytes to the source immediately after the initial digest/size pass, forces the multipart path, and asserts rejection plus multipart abort with no incomplete upload retained. Source commit: 1124d7e; test commit: 9f2875e.
- This closes a size-binding gap for multipart transfer. The single-put path still performs exact-version persisted-byte verification after upload, so a concurrent source mutation cannot be accepted as a valid locator.
- Static review only: 0 repository test modules executed and 0 Actions jobs executed. Recovery archive test module remains registered in the security matrix.
- Updated estimates: backup/release readiness 45%; AI-2 overall 75.2%; whole project 73.9%. Remaining external acceptance blockers are unchanged; pilot/production remains NOT READY.


## AI-2 encrypted backup manifest ambiguity rejection — 2026-11-16

- Restore manifest parsing now rejects duplicate JSON object keys at every nesting level instead of silently accepting the last value. This makes encrypted backup metadata unambiguous before profile, file inventory, tenant catalog and checksum acceptance.
- Added a regression that starts from a valid encrypted bundle, injects a duplicate format_version key into the manifest, re-encrypts it, and asserts restore fails closed. Source commit: 173ddb1; test commit: f78a441.
- The backup bundle test module is already registered in the focused security matrix. Static review only; no repository test execution or Actions run.
- Updated estimates: backup/release readiness 45.2%; AI-2 overall 75.3%; whole project 74%. Pilot/production remains NOT READY pending live and operational acceptance.


## AI-2 restore tenant manifest schema validation — 2026-11-16

- Restore now validates every tenant manifest record before comparing it with the control-plane catalog or opening tenant databases. Records must be objects with a unique positive integer firm ID, non-empty tenant/firm status strings, and a filename/archive path pair that matches the strict firm-specific tenant filename. Malformed records, duplicate firm IDs, mismatched filenames and orphan archive paths fail closed as DatabaseBundleError rather than leaking type/key exceptions deeper into restore.
- Added an encrypted-bundle regression that replaces a tenant record with a non-object value and verifies restore rejection. Source commit: 429d59c; test commit: fed98e9.
- Static review only; repository tests and Actions remain unavailable. Backup/release readiness estimate 45.5%; AI-2 overall 75.4%; whole project 74.1%. Pilot/production remains NOT READY.


## AI-2 S3/KMS recovery response schema validation — 2026-11-16

- Recovery archive KMS inspection now requires a dictionary response with a dictionary KeyMetadata before reading ARN/state fields. S3 upload/download paths now validate response and Metadata object shapes before consuming version IDs, checksums or encryption metadata; malformed body interfaces are rejected, and response bodies are closed when possible.
- Added regressions for malformed KMS metadata and malformed exact-version S3 HEAD metadata. Source commits: 698751b, 93e4fb9; test commits: 12b976d, 993d91a.
- Existing upload/download response verification and exact-version pinning remain intact. Static review only; no repository test module or Actions job ran.
- Updated estimates: backup/release readiness 45.6%; AI-2 overall 75.5%; whole project 74.2%. No safe open PR is mergeable; dependency lock/browser validation blockers remain. Pilot/production remains NOT READY.

- An isolated Python harness accepted unique JSON objects, rejected a nested duplicate key, and demonstrated that a destination-directory rename/symlink swap could not redirect a descriptor-relative write; the pinned file was removed without touching the symlink target. This is a focused primitive reproduction, not execution of the repository test modules.


- Recovery download now treats a response-body close failure as a failed operation: the destination is removed through the pinned directory handle, and best-effort cleanup does not mask the primary failure. Added a regression with a body stream whose close raises and asserted no output remains. Source commit: a2926dc; test commit: fe11f19. Static review only; test module not executed.


## AI-2 encrypted backup publication no-overwrite semantics — 2026-11-16

- Encrypted local backup publication now uses exclusive hard-link creation instead of os.replace, so a timestamp/name collision cannot silently overwrite an existing backup. The temporary file is removed after successful publication; directory metadata is fsynced where directory descriptors are supported. A sync failure is reported without deleting a possibly published backup.
- Added a regression that fixes the generated timestamp, pre-creates the exact destination name, and verifies backup creation fails while preserving the pre-existing bytes and cleaning the temporary file. Source commits: 56ef2ae, 63e3881; test commit: 929cd59.
- Static review only; no repository test module or Actions job executed. Backup/release readiness estimate 45.9%; AI-2 overall 75.6%; whole project 74.3%. Pilot/production remains NOT READY.


## AI-2 backup object-root inode binding — 2026-11-16

- Local original-object inventory now captures the root directory's lstat identity before opening it and compares the pinned descriptor's device/inode against that identity. A replacement directory at the same configured path is rejected, even if it is itself a valid directory. The portable path fallback also checks root identity again after enumeration.
- Added a race regression that swaps the configured object-root directory for a different valid directory immediately before open and asserts inventory fails closed. Source commits: f05c297, fa65ac7; test commits: 6e18137, bb0b06b.
- Static review only; repository test module and CI remain unexecuted. Backup/release readiness estimate 46.1%; AI-2 overall 75.7%; whole project 74.4%. Pilot/production remains NOT READY.

- Follow-up race review moved the local object-root existence check fully onto lstat: only FileNotFoundError is treated as an absent store, while dangling symlinks and other non-directory entries fail closed. This closes the narrow is_symlink()/exists() gap before root identity capture. Source commit: 7819ea7.


## AI-2 restore manifest/control-plane firm-state binding — 2026-11-16

- Restore now compares every manifest firm_status value with the status recorded in the restored control-plane firms table. This prevents an internally well-formed but contradictory manifest from presenting stale/altered firm lifecycle state alongside the database snapshot.
- Added an encrypted-bundle regression that alters a tenant record's firm_status while preserving the database and verifies restore rejects the mismatch. Source commit: b91e243; test commit: 903a400.
- Static review only; no repository test module or Actions job ran. Backup/release readiness estimate 46.3%; AI-2 overall 75.8%; whole project 74.5%. Pilot/production remains NOT READY.

- Refinement: firm-state equality is scoped to firms represented in the tenant catalog, matching the backup manifest's documented catalog inventory. This preserves legitimate non-active control-plane firm records that have no tenant catalog entry while still rejecting missing, extra or contradictory cataloged firm states. Source commit: 3147eba.


- Added a recovery-download preflight regression for a destination whose parent path traverses a symlinked ancestor (not merely a symlink at the final parent component). It asserts the canonical-path mismatch is rejected before bucket-versioning, KMS, HEAD or GET calls. Test commit: b3dc94a. Static review only; repository tests remain unexecuted.


## AI-2 recovery locator pre-open inode binding — 2026-11-16

- Recovery locator reads now lstat the path before opening and compare the opened descriptor's device/inode to the inspected file. On platforms without O_NOFOLLOW, a post-open lstat comparison also detects a path that became a symlink or changed identity. This closes the regular-file replacement window in addition to the existing symlink and bounded-read checks.
- Added a regression that swaps one regular JSON file for another between lstat and os.open; the replacement must not be accepted. Source commit: 22b0c36; test commit: adde810.
- The recovery-locator test module is already registered in the focused security matrix. Static review only; repository tests and Actions remain unexecuted.

- An isolated filesystem harness confirmed that replacing a regular locator file between lstat and open changes the opened descriptor inode and is detected by the new identity comparison. This is not execution of tests/test_manage_recovery_locator.py.

- Recovery download and restore destination canonicalization now normalize both filesystem OSErrors and symlink-resolution RuntimeErrors into controlled domain failures. This avoids leaking raw path-resolution exceptions for malformed or cyclic parent paths. Source commits: 2a03e96, a64b3bc.

- An isolated directory-inode harness confirmed that swapping a configured object-root for a different real directory produces a different opened device/inode and is detectable by the new backup inventory check. This is not execution of tests/test_database_backup_bundle.py.


## AI-2 continuation checkpoint — 2026-11-16

- Additional completed items since the prior checkpoint: backup object-root lstat/inode binding and replacement regression; recovery locator pre-open inode binding and replacement regression; manifest/control-plane firm-state consistency checks; symlink-ancestor destination preflight coverage; controlled path-resolution errors; and isolated primitive harnesses for locator and object-root inode substitution.
- Current engineering estimates: tenant isolation/access control 84.7%; authentication/firm administration 85.2%; case management 90%; document processing/security 99.1%; backup/release readiness 46.7%; AI-2 overall 76%; whole project 74.7%. These remain implementation estimates, not acceptance or test pass rates.
- Validation: isolated Python harnesses passed for duplicate JSON keys, pinned-directory replacement, locator inode replacement and object-root inode replacement. Repository test modules executed: 0. GitHub Actions jobs executed: 0. Live S3/KMS and restore drill: not performed.
- Open PR review unchanged: #1644 and #1645 remain unmergeable without lockfile/browser validation; #1610 remains draft and unsafe to merge wholesale. No force merge or bypass. Pilot/production remains NOT READY.


## PR #1655 merged — Legal Research copy-helper initialization fix — 2026-11-16

- PR #1655 was merged into main as merge commit 0181cca589c8257b1e64bd9c61923883b5f9ebe4. It converts the Legal Research copy translation helper from a const arrow binding to a hoisted function declaration, fixing the temporal-dead-zone failure where earlier-created controls invoked copy() before initialization.
- Verified the merged main static/index.html contains the hoisted function and tests/test_research_copy_initialization.py exists on main. The regression contract is present but was not executed because Actions remain blocked.
- This was a small, scoped frontend bug fix; no dependency, retrieval, verification-state or permission behavior was changed. PR #1655 is merged; #1644/#1645 remain blocked by dependency lock/browser validation; #1610 remains draft and unsafe for wholesale merge.

- Follow-up on merged PR #1655: its new test_research_copy_initialization.py regression was not yet registered in either the explicit Tests workflow or focused security matrix. Added the workflow step and matrix entry. Source commits: 07676a1, 4caf0d6. Registration is complete; neither workflow nor test has executed.

- Test-registration audit also found test_manage_recovery_locator.py was present in the focused security matrix but absent from the explicit Tests workflow. Added a dedicated workflow step adjacent to recovery archive transport. Source commit: 1fcacea. Registration is complete; execution remains blocked.

- Static registration audit after the additions: all 40 modules listed in scripts/security_regression_check.sh are also explicitly referenced in .github/workflows/tests.yml; no security-matrix module is missing from the workflow. This is a source-text consistency check only, not execution of those modules.


## AI-2 test registration completeness — 2026-11-16

- Merged PR #1655's copy-helper regression and the previously added recovery-locator regression are now both registered in the explicit Tests workflow; the copy-helper test is also in the focused security matrix. A static comparison of the workflow's 190 distinct referenced test modules against the 40 focused security-matrix entries found zero matrix modules missing from the workflow.
- This closes the test-registration implementation task for the current focused security matrix: **100% registered**. It does not mean the tests passed; GitHub Actions remains unavailable due the billing/runner issue.
- Current estimates: tenant isolation/access control 84.7%; authentication/firm administration 85.2%; case management 90%; document processing/security 99.1%; backup/release readiness 46.7%; AI-2 overall 76.2%; whole project 74.8%.
- PR #1655 is merged. No other open PR is safe to merge without the missing lockfile/browser or draft-PR validation. Pilot/production remains **NOT READY**.


## AI-2 security test registration regression — 2026-11-16

- Added tests/test_security_matrix_registration.py with three checks: every focused security-matrix module has an explicit Tests workflow reference, the matrix has no duplicate module entries, and every listed module exists on disk. Registered this self-check in both the Tests workflow and focused security matrix.
- The preceding static comparison found all 40 original matrix entries already present in the workflow. The new self-check makes that invariant durable and will prevent future matrix/workflow drift. Source commits: 54ab031, b6f06a5, feed9b9, 2e8bfb4.
- Implementation and registration: **100%**. Execution: blocked by GitHub billing/runner issue; no test pass claimed.


## AI-2 route-authentication audit method parsing — 2026-11-16

- Hardened `tools/audit_route_auth.py`: `api_route(methods=...)` is now accepted only when its methods are a non-empty literal list/tuple/set of literal, supported HTTP method strings. Dynamic expressions, empty collections, non-string entries and unsupported methods produce explicit audit findings rather than silently removing the route from the audit.
- Added focused regressions for dynamic method expressions, empty method collections and non-literal entries in `tests/test_route_auth_audit.py`. The module was already registered in both the Tests workflow and focused security matrix; no registration change was required.
- Source commit: 728f1e9; regression commit: 69d72b9. An isolated AST parser harness rejected the three malformed forms and accepted a literal GET/POST declaration. This was not execution of the repository test module.
- Static implementation: **100%**. Runtime validation: pending; GitHub Actions remains unavailable due billing/runner issue. No test pass is claimed. Pilot/production remains **NOT READY**.


- Follow-up route-audit hardening: computed/non-literal route paths now produce an explicit finding instead of being omitted. Literal keyword `path="/..."` declarations remain auditable. Added regressions for both forms. Source commits: 0082827, 4101a8e; test commit: e71fc2e. An isolated AST harness rejected dynamic paths and malformed methods and accepted literal positional/keyword paths and GET/POST methods; repository tests remain unexecuted.


## AI-2 route-to-SQL inventory declaration hardening — 2026-11-16

- Hardened `tools/audit_route_sql_access.py` so route declarations with computed/non-literal paths or dynamic, empty, non-string, or unsupported `api_route(methods=...)` values are explicitly reported as uninventoried. The strict audit now fails on these declaration gaps instead of silently omitting the route or applying an inaccurate default method set. Literal keyword `path="/..."` routes remain inventoried.
- Added regressions for dynamic route paths, dynamic API methods, keyword path support, and strict CLI rejection. Existing route-SQL tests remain registered in the Tests workflow and focused security matrix.
- Source commits: d0ad7e3, 7a62bbf; regression commits: 2ed7593, 6d5c66d. An isolated AST harness rejected dynamic declarations and accepted literal path/method declarations; repository test modules and GitHub Actions remain unexecuted.
- Static implementation: **100%**. Runtime validation remains pending; pilot/production remains **NOT READY**.


- Registration follow-up: the new route-to-SQL inventory regressions were already in the Tests workflow but were absent from the focused security matrix. Added `test_route_sql_access_audit.py` to the matrix adjacent to the route-authentication audit. Matrix static check: 42 entries, 0 duplicates, 0 entries missing from the explicit Tests workflow. This is registration-only verification, not test execution. Matrix update commit: d4b27b6.


## AI-2 static route-boundary audit checkpoint — 2026-11-16

- Completed implementation hardening for both authentication-route discovery and route-to-SQL inventory: dynamic method/path declarations can no longer silently disappear from either static review. Added regression coverage for invalid and valid declarations, and registered both test modules in the explicit Tests workflow and focused security matrix.
- Source-level implementation for these two bounded audit tasks: **100%**. Static checks confirm both regression modules are workflow/matrix registered; the matrix contains 42 unique entries and all are referenced by the workflow.
- Isolated AST harnesses exercised the accepted/rejected declaration forms. Repository test modules executed in this continuation: **0**; GitHub Actions jobs executed: **0**. CI/runner billing remains the validation blocker. No repository test pass is claimed.
- AI-2 overall estimate remains **76.2%** and whole-project estimate **74.8%** pending runtime validation and broader workstream completion; these are engineering estimates, not certification. No safe open PR was identified for merge. Pilot/production remains **NOT READY**.


## AI-2 attached database identity binding — 2026-11-16

- Hardened `DatabaseRuntime._configure_firm_connection`: each read-only SQLite control-plane/legal-corpus attachment is now bound to its observed device/inode in a private TEMP identity table. Every reuse checks the current paths against those captured identities; same-path replacement is rejected, and path permissions/symlink state are revalidated after attachment.
- Any failed control-plane context revalidation or tenant connection configuration now revokes the thread's cached tenant handle, preventing a failed authorization/storage check from leaving a previously attached tenant connection reusable.
- Added `test_firm_connection_revokes_tenant_handle_when_control_file_is_replaced` and `test_firm_connection_revokes_tenant_handle_when_attached_corpus_is_replaced` to `tests/test_database_runtime.py`. The module is already registered in the explicit Tests workflow and focused security matrix.
- Source commits: `6032ecf`, `6937bd6`, `330e0b3`; regression commit: `0ae13c4`. Static source/registration review confirms both regressions are present and wired. An isolated SQLite harness confirmed a same-path corpus replacement changes the recorded identity and is detectable. This harness is not execution of the repository test module.
- Implementation: **100%**. Repository test execution: **0**; GitHub Actions: **0**. Runtime acceptance remains blocked by the CI billing/runner issue. Pilot/production remains **NOT READY**.


- Tenant-isolation estimate updated after the attached-profile identity fix: **84.9%** (previously 84.7%). AI-2 estimate: **76.3%**; whole-project estimate: **74.9%**. The increase is deliberately small because only one bounded storage-identity gap was closed; CI, multi-process/runtime, staging and independent acceptance remain outstanding.


## AI-2 voluntary MFA re-enrollment enforcement — 2026-11-16

- Fixed a policy gap where a user who voluntarily enabled MFA under `MFA_ENFORCEMENT=optional` could start authenticator replacement, move the credential to `pending`, and then have the MFA gate disappear because only `status='enabled'` counted as MFA-required.
- Added `_mfa_is_pending` and included pending enrollment in `_mfa_required_for_user`. During replacement, the session is now restricted to enrollment/verification/recovery paths until the new authenticator is confirmed; new logins are also required to complete enrollment.
- Added `test_optional_mfa_policy_does_not_bypass_voluntary_mfa_during_reenrollment` to `tests/test_mfa_account_security.py`. The test module is already registered in the explicit Tests workflow and focused security matrix.
- Source commit: `9a3c420`; regression commit: `43bbb0e`; import correction: `1f06e22`. Static source/registration inspection confirms the helper and regression are present. Repository test module and GitHub Actions execution remain unavailable due the billing/runner issue; no pass is claimed.
- Bounded implementation: **100%**. Authentication/firm-administration estimate: **85.4%** (from 85.2%); AI-2: **76.4%**; whole project: **75.0%**. Runtime staging and independent security review remain outstanding.


- MFA regression strengthened in commit `a2b3d6d`: besides proving the existing session is blocked from matter routes while voluntary authenticator replacement is pending, it now creates a second session and asserts a fresh login is marked `mfa_required` and `mfa_enrollment_required`, with `mfa_verified=false`.


## AI-2 MFA authenticator replacement session invalidation — 2026-11-16

- Hardened `/account/mfa/re-enroll`: in the same transaction that moves the credential to pending, all existing sessions for that identity now have `mfa_verified=0` and `mfa_verified_at=0`. The session completing the new enrollment is re-verified by confirmation; other devices must verify with the replacement authenticator. The append-only event records that existing sessions require re-verification without including secrets or tokens.
- Expanded `test_lost_authenticator_reenrollment_requires_recent_mfa_and_current_password` to create a second verified session, replace the authenticator, prove all prior MFA proofs were reset, confirm the replacement on the initiating session, and require the second session to verify using a fresh TOTP step before regaining matter access.
- Source commit: `bd7d364`; regression commits: `1f568c4`, `fcd2112`. Static review confirms the test module remains registered in both the Tests workflow and security matrix. An isolated SQLite transaction harness confirmed session reset/confirmation semantics; repository tests and CI remain unexecuted.
- Bounded implementation: **100%**. Authentication/firm-administration estimate: **85.7%**; AI-2: **76.5%**; whole project: **75.1%**. No test pass is claimed. Production readiness remains **NOT READY**.


## AI-2 reminder scheduler lease clock — 2026-11-16

- Fixed `tools/reminder_service.py` to separate the reminder planning/evaluation timestamp from operational delivery timestamps. Each outbox claim now receives wall-clock UTC at claim time; completion/denial outcomes record wall-clock UTC when finished. A historical or fixed `--now` planning override can no longer create immediately expired leases for later messages in a long send batch.
- Added `test_delivery_leases_use_wall_clock_not_planning_override` to `tests/test_reminder_service.py`, asserting claim and finish timestamps are later than the fixed planning timestamp. Existing tests in the reminder email/outbox/service modules were all present in the Tests workflow; added all three modules to the focused security matrix.
- Source commit: `964cb84`; regression commits: `9844261`, `d04e12e`; matrix commit: `72f343f`. Static registration audit: **70 matrix modules, zero duplicates, zero modules missing from the Tests workflow**. This does not mean any module executed.
- Bounded implementation: **100%**. Isolated database-runtime and session-state harnesses were successful in this continuation, but repository tests executed: **0**; GitHub Actions: **0**. SMTP staging and operational acceptance remain outstanding.


## AI-2 reminder preference schema fail-closed behavior — 2026-11-16

- Removed the broad SQLite-error fallback in `_reminder_preferences`. A missing/unavailable preference table now aborts scheduling before outbox enqueue or SMTP submission; a user with no preference row still receives the documented migration defaults. Database/schema failure is no longer interpreted as consent.
- Added `test_send_fails_closed_when_reminder_preferences_schema_is_missing`, which drops the preference table, asserts scheduler failure, zero SMTP calls and zero queued reminders. `test_reminder_service.py` is registered in both the Tests workflow and focused security matrix.
- Source commit: `3d29a0d`; regression commit: `91abca8`. Static review confirms the fallback is removed and the test is present. Repository tests and CI remain unexecuted.
- Reminder scheduler code hardening in this continuation: **100%** (lease-clock separation and missing-preference-schema fail-closed behavior). Live SMTP/provider and external scheduler acceptance remain outstanding.


- Conservative aggregate estimate after the reminder scheduler changes: AI-2 **76.6%**; whole project **75.2%**. The small increase reflects code-level hardening only. Live SMTP staging, scheduler service-manager installation/monitoring, operational recovery rehearsal, CI and independent review are still unaccepted.


- Operator contract updated in `docs/reminder_scheduler_contract.md` (commit `7e5433f`) to distinguish planning-time `--now` from wall-clock delivery leases and to document fail-closed behavior for unavailable preference schema versus first-run defaults.


- MFA transaction regression expanded in commit `7a8c953`: an injected append-only audit failure during authenticator replacement must roll back the pending credential transition and all-session MFA-proof invalidation, leaving the original enabled credential and current verified session intact.


- Aggregate estimate after MFA re-enrollment session invalidation and reminder delivery hardening: authentication/firm administration **85.9%**, AI-2 **76.7%**, whole project **75.3%**. The change is deliberately limited to the code-level controls completed here; repository tests, CI, live SMTP, live AWS, browser and independent acceptance are not credited as complete.

## AI-1 retrieval measurement integrity hardening — 2026-11-16

- Merged PRs #1658–#1662: scorer output symlink protection; focused regression registration for the Arabic retrieval scorer and Gazette importer; and expanded focused coverage for source review, lawyer-answer evaluation, evidence URLs, provisional Labour Law questions, source permissions/versioning, citation binding/polarity, synthetic retrieval, and evaluation-draft integrity.
- Merged PR #1663: Arabic retrieval measurement reports are written to a same-directory temporary file, flushed and fsynced, then atomically replaced. A failed replacement preserves the previous report and cleans the temporary file. An isolated filesystem harness exercised successful replacement and simulated replacement failure; the repository test module remains unexecuted.
- Merged PR #1664: the scorer now consumes the API runner's `invalid_citation_indices` and `citation_marker_count`. Any invalid visible citation marker is a safety failure even if another citation is correct. Legacy/manual reviewed runs missing either field cannot receive `targets_met`; the report exposes missing validation coverage. Added regression cases are committed but unexecuted.
- The focused security regression matrix now contains **70 unique modules**, all statically confirmed present in the main Tests workflow. This is registration coverage only; repository test execution remains **0** in this session.
- Isolated filesystem harness passed for atomic report replacement and failure preservation. GitHub Actions remains unavailable due runner billing/allocation; the repository cannot be cloned in this environment because outbound DNS/network access is unavailable. No repository test pass is claimed.
- **AI-1 bounded implementation estimate: 74%.** Retrieval measurement integrity and focused test registration improved; legal corpus readiness remains low and external lawyer/source dependencies remain open. Whole-project estimate remains the latest separately recorded **75.3% provisional engineering estimate**, not a test-pass rate or readiness score.

## AI-1 stable legal-evidence reads — 2026-11-16

- Merged PR #1670: manual-capture original-file hashing now uses a stable regular-file descriptor and rejects final-path symlink replacement and non-regular files.
- Merged PR #1671: the legal document collector applies the same stable-descriptor checks to preserved originals.
- Merged PR #1672: the release validator now reads extracted-text bytes once, hashes those bytes, and performs UTF-8 decoding/article-anchor checks on the same in-memory content. This closes a hash-then-reopen path race.
- Merged PR #1673: permission-register and candidate JSON metadata are read through the stable-descriptor reader; symlink swaps/non-regular inputs fail closed.
- Isolated local harnesses exercised stable reads, regular-file hashing, FIFO rejection and final-path symlink-swap rejection. The corresponding repository test modules remain unexecuted.
- PR #1674 adds a similar post-read path-identity check to the PDF bundle importer, but its merge was rejected because the base branch changed during the merge operation. It remains open pending a safe latest-main refresh; no claim of merge or test completion.
- These are file-integrity and race-resistance controls only. They do not authenticate a Gazette, grant reuse rights, establish currentness, or substitute for qualified Egyptian-counsel review.
- AI-1 implementation estimate: **79%**. Legal corpus readiness remains **10%** pending authorized original materials and counsel approval. Whole-project estimate remains **75.3% provisional** from the separately recorded project checkpoint; not a test-pass or release-readiness score.

- Merged PR #1674: the PDF bundle importer now checks post-read path/device/inode identity and uses nonblocking/no-follow opens where available; FIFO and symlink-swap regressions were added.
- Merged PR #1676: the collection manifest is read through a bounded 5 MiB stable descriptor; final-path symlink swaps, FIFOs, oversized files and read-time changes fail closed. Repository tests remain unexecuted due runner billing/allocation.

## AI-1 bounded evidence and evaluation input reads — 2026-11-16

- Merged PR #1678: manual-capture provenance sidecars now use bounded stable-descriptor reads, rejecting symlink replacement, non-regular/FIFO inputs and oversized records.
- Merged PR #1679: Arabic retrieval scoring now reads question/run JSONL, the approved reviewer registry and existing measurement reports from bounded stable file descriptors.
- Merged PR #1680: collection extraction now reads the preserved original once and feeds those exact bytes to PDF/DOCX parsers or HTML/plain-text decoding. Extraction no longer reopens a path after hashing/validation.
- Merged PR #1681: the canonical source-permission register loader now rejects symlink/path swaps, FIFOs, oversized input and changes during reading while preserving duplicate-key validation.
- Merged PR #1682: the API legal-evaluation runner now reads question JSONL through a bounded stable descriptor, preserving BOM handling and row validation.
- An isolated stable-read harness exercised regular-file reading and rejection of FIFO, symlink-swap and oversized inputs. It is not a substitute for the repository test modules.
- GitHub Actions/repository test execution remains unavailable because of runner billing/allocation. No full-suite pass is claimed.
- These controls protect local evidence/measurement inputs; they do not establish source authenticity, collection/commercial reuse permission, legal currentness, lawyer approval or product release readiness.
- Updated AI-1 implementation estimate: **82%**. Legal corpus readiness remains **10%** pending authorized original Gazette materials and qualified Egyptian-counsel review. Whole-project engineering estimate remains **75.3% provisional** pending a fresh cross-workstream audit; it is not a release-readiness score.
- Merged PR #1684: lawyer-review JSONL and private reviewer-registry inputs now use bounded stable descriptors; exact-byte provenance hashes are computed from the same bytes that are parsed.
- Merged PR #1685: the approved-answer evaluator now reads question/result JSONL and reviewer-registry inputs through bounded stable descriptors, preserving exact-byte provenance.
- Merged PR #1686: the production release gate now reads candidate evidence and reviewer registry through bounded stable descriptors; unreadable candidate evidence stays excluded and registry failures remain blockers.
- The stable-read harness also passed isolated regular-file, FIFO, symlink-swap and size-limit checks. Repository tests remain unexecuted; CI billing is still blocking hosted test runs.
- AI-1 engineering estimate after these additional evaluator/release-gate safeguards: **84%**. Legal corpus readiness remains **10%**; the whole-project estimate remains **75.3% provisional** pending cross-workstream re-audit.
- Merged PR #1688: Phase 2 legal-instrument inventory reads are now bounded and stable; symlink swaps, FIFOs and oversized files fail closed.
- Merged PR #1689: acquisition-readiness manifest and permission-register inputs reuse the hardened stable reader.
- Merged PR #1690: canonical and supplemental Labour Law evidence-card inventory/manifest reads now use the stable reader; provisional `search_eligible=false` safeguards remain intact.
- Merged PR #1691: manual-capture catalog and original-document reads now use stable bounded reads, eliminating the separate stat-then-read race for captured originals.
- Merged PR #1692: amendment-relationship and Phase 2 inventory inputs reuse the stable reader; structural validation does not claim legal effect or currentness.
- AI-1 engineering estimate: **86%** after these source/acquisition/evidence workflow safeguards. Legal corpus readiness remains **10%** because authorized Gazette evidence and qualified counsel approval are still missing. Whole-project estimate remains **75.3% provisional** pending cross-workstream reassessment.
- Merged PR #1694: the legal corpus inventory report now reads its JSON registers through the stable bounded reader; the report remains metadata-only and does not infer verification or reuse rights.
- Merged PR #1687 recorded the lawyer-review evaluator and production release-gate input safeguards; PR #1688–#1694 now extend those controls through the Phase 2 inventory, acquisition readiness, Labour Law evidence cards, manual capture, amendment relationships and corpus inventory report.
- AI-1 engineering implementation estimate: **87%**. Retrieval/Arabic matching remains **80%** pending approved benchmark-driven tuning; evaluation/scoring infrastructure **100% implemented** but awaits counsel-approved questions and real runs; ingestion/provenance tooling **98%**; evidence/release safeguards **97%**; Egyptian legal corpus readiness **10%**. Whole-project estimate remains **75.3% provisional**, not a release-readiness or test-pass score.


## AI-2 legal-PDF importer resource ceilings and timeout — 2026-11-16

- Legal-import OCR configuration can now lower, but cannot raise, the hard page-render ceilings (12,000 pixels per dimension and 40 million pixels per page). Tesseract OCR now receives a 30-second per-page subprocess timeout; runtime timeout/failure is converted to an explicit import rejection.
- Corrected the README to distinguish matter-upload OCR settings from legal-import settings and to document the actual importer environment variable names and hard defaults.
- Added regression contracts for attempts to raise either hard ceiling, Tesseract timeout propagation (including the actual `subprocess.TimeoutExpired` exception) in both the legal-corpus importer and matter-upload OCR path, huge finite page boxes that could overflow pixel conversion, and invalid DPI values. Pixel geometry is compared against the hard dimension cap before multiplication. Static re-fetch confirms the source, tests and documentation changes are present; repository test execution remains **0** because hosted runners are blocked and outbound DNS prevents a local clone. No test pass is claimed.
- Source commits: `26dd851`, `ea57362`, `be1b481`, `d8412f7`; regression commits: `aae5462`, `dd08f0c`, `04fdff1`, `b70f8d0`, `4c20cd1`; documentation commit: `d8771d6`; blocker record: `98b7e14`.
- Bounded importer-hardening implementation: **100%**. Exact-head test execution and runtime acceptance: **0%**. AI-2 estimate: **77.8%** (implementation-only, including the actual subprocess timeout handling and both OCR-path regression contracts). Whole-project estimate remains **75.3% provisional** pending a fresh cross-workstream audit. Pilot/production remains **NOT READY**.


## AI-2 S3 recovery-archive verification stream closure — 2026-11-16

- Upload-side exact-version verification now treats a failure to close the persisted-object response stream as a failed archive verification rather than leaking a raw provider exception. The focused archive test module already runs in the Tests workflow and is listed in the security-review handoff/matrix.
- Added a regression whose S3 response body reads the persisted bytes successfully but raises on close; the upload must fail with the backup-domain exception. Static inspection confirms the new source and test are present. Repository tests and hosted Actions remain unexecuted.
- Source commits: `26d2c96`, `7737b68`; regression commit: `c163af2`. **Bounded implementation: 100%; runtime test execution: 0%.** AI-2 engineering estimate: **76.9%**; whole-project estimate remains **75.3% provisional**. This failure can leave an already-uploaded encrypted object version without a returned locator; reconcile the recovery-archive prefix before retrying. Production remains **NOT READY**.


## AI-2 restore publication race hardening — 2026-11-16

- Replaced restore's check-then-`os.replace` publication with a directory-descriptor-anchored Linux `renameat2(RENAME_NOREPLACE)`. The validated parent directory identity is checked after opening, and both rename names are relative to that descriptor; if a target appears after preflight, publication fails without replacing it. Platforms lacking the required primitive fail closed.
- Added regressions for a destination appearing between preflight and publication, parent-directory replacement by a symlink during open, and missing `renameat2` support; they check that existing/outside data and the staged tree are preserved and that unsupported platforms fail closed.
- An isolated local harness exercised the exact helper logic: successful directory publication, EEXIST preservation of an existing target, and rejection of a parent-directory symlink swap without redirecting the restore. The lower-level OS dirfd/`RENAME_NOREPLACE` primitive also passed independently. These are local harnesses, not execution of the repository test module; the full restore drill remains unexecuted.
- Source commits: `8443834`, `71eab78`, `fd6a30d`; regression commits: `53d918f`, `5c179e7`, `b44bd08`, `e2a0b52`, `1945dd0`, `27182c4`; operator documentation: `46dcefca`, `d44040d`, `7c789b2`; status/harness record: `ab14694`. Restore publication implementation: **100%**; repository regression execution: **0%**. AI-2 estimate: **77.5%**; whole-project estimate remains **75.3% provisional**. Production remains **NOT READY**.


## AI-2 recovery-download directory capability fail-closed — 2026-11-16

- Removed the path-based fallback from encrypted S3 recovery downloads. Downloads now require no-follow directory opens and `dir_fd`-relative file creation/cleanup; unsupported platforms fail before versioning/KMS/S3 calls rather than attempting a weaker path-based write or cleanup.
- Added a regression that removes `os.open` directory-descriptor capability and verifies the download fails before cloud access and creates no target file. An isolated local dirfd harness also verified that cleanup after a parent-path replacement removes only the file under the originally opened directory, not a same-named outside path.
- Source commit: `36ce704`; regression commit: `2f0fca7`; operator documentation: `df3cf60`. Bounded implementation: **100%**; repository test execution: **0%**. AI-2 estimate: **77.8%**; whole project remains **75.3% provisional**. Linux production container supports the required primitives; production remains **NOT READY** pending live AWS and witnessed recovery acceptance.


## AI-2 matter-upload OCR hard-ceiling enforcement — 2026-11-16

- Matter-upload OCR now treats `OCR_MAX_PIXELS` and `OCR_MAX_DIMENSION` as operator-adjustable lower limits only; hard ceilings remain 40,000,000 pixels and 20,000 pixels per dimension even if environment values attempt to raise them.
- Added adversarial regression cases for both independent ceilings using environment values far above the hard maximum; each must reject before `get_pixmap` and Tesseract are called.
- Source commit: `6d72c60`; regression commits: `4b613ba`, `012f8a3`, `f139c7f` (the dimension and area ceilings are tested independently; non-finite and non-positive page geometry is rejected); security-matrix registration: `406939d`. Bounded implementation: **100%**; static source/test re-fetch: **100%**; repository test execution: **0%**. Matter-upload OCR resource hardening estimate: **100% implementation**. Both raster ceilings are now tested independently, invalid/non-finite page geometry is covered, and the legal-import OCR module is included in the focused security matrix. AI-2 overall estimate: **78.1%**; whole-project estimate remains **75.3% provisional**. Production/pilot remains **NOT READY**.

## AI-1 retrieval polarity and evidence-input follow-up — 2026-11-16

- Extended English modality checks so contracted is-not-required and do-not-have-to forms cannot also match positive obligation patterns. Added regressions for faithful non-obligation paraphrases and positive-to-negative reversals.
- Extended Arabic answer-claim polarity checks to recognize Egyptian ma-verb-sh circumfix forms; Arabic query expansion now recognizes ma + verb-ending-in-sh negation without treating interrogative ma-hiya as negation. Added regressions against known lexicon phrase aliases.
- Tightened the reviewed retrieval scorer to reject whitespace-padded question/run/article identifiers. The unapproved Law 14 draft structural test now exercises the production fail-closed JSONL reader and validator instead of reading the draft with a separate permissive parser.
- Ingestion follow-up rejects future retrieval dates/timestamps, caps cached OCR pages at 8 MiB, reads OCR cache pages through stable no-follow descriptors, and rejects symlink replacement. The legal document collector now uses stable bounded reads for existing originals, metadata-history entries and immutable extraction artifacts.
- Source/test commits are on main; affected modules are registered in .github/workflows/tests.yml. Isolated Python checks covered representative English/Arabic polarity and timestamp validation/UTC formatting; file-race regressions are committed but unexecuted, and repository test execution remains 0 because GitHub runner billing/allocation is unavailable and outbound DNS prevents a local clone. No test pass is claimed.
- Updated AI-1 implementation estimate: 94%. Retrieval/Arabic matching safeguards: 83% implementation, still awaiting lawyer-approved benchmark labels and real before/after retrieval runs. Evaluation/scoring infrastructure: 100% implemented, but evaluation acceptance is blocked by missing approved labels and real run records. Ingestion/provenance tooling: 99%; evidence/release safeguards: 98%; Egyptian legal corpus readiness: 10% pending authorized Gazette materials, reuse rights and qualified Egyptian-counsel approval. Whole-project engineering estimate remains 75.3% provisional; the project remains NOT READY for lawyer pilot or production.


## AI-2 retained-original corruption rejection regression — 2026-11-16

- Added a separate-database upload/download regression that mutates retained original bytes without changing length, truncates the object, and replaces it with an object larger than the endpoint's 15,000,000-byte ceiling. Each request must fail integrity verification with HTTP 503 before any download audit event is written; this complements the existing successful-integrity, cross-firm, wrong-case, and audit-write-failure coverage.
- Regression commits: `9f64be8`, `470c652`. Implementation change: none; this closes a focused verification gap in the original-evidence download path. Exact test, app route, status, blocker and security-matrix files were re-fetched from `main`; static checks confirmed all three tampering cases, three no-audit assertions, and registration of the containing test module in the security matrix. The added method also passed standalone Python syntax/bytecode compilation. Repository test execution remains **0%**. No runtime test pass is claimed.


## AI-2 S3 original integrity-stream size ceiling — 2026-11-16

- The S3 original-object adapter's streaming verifier now rejects an expected size above its configured `max_bytes` before calling S3, and reads no more than `max_bytes + 1` bytes when provider content exceeds its recorded metadata. The one-byte sentinel distinguishes an exact-limit object from an oversized response while keeping reconciliation/backup verification bounded; the body is closed on the early rejection path.
- Added fake-S3 regressions for oversized expected metadata (no remote read) and a provider body five times the configured limit (only limit + 1 bytes read, then closed).
- Source commit: `2668e8e`; regression commit: `a77a6f1`. Exact source, regression, status, blocker and security-matrix files were re-fetched from `main`; static checks confirmed the preflight rejection, max+1 read bound, remote-read avoidance, body-close assertion and matrix registration. The added test method passed standalone Python syntax/bytecode compilation. Repository runtime test execution remains **0%**. AI-2 estimate: **78.2%**; whole-project estimate remains **75.3% provisional**. No runtime pass is claimed.


## AI-2 local original reconciliation read ceiling — 2026-11-16

- The local original-file reconciler previously streamed an arbitrary-size regular file to EOF while hashing it. It now reads at most the hard 15,000,000-byte object ceiling plus one sentinel byte, closes the file on rejection, and emits a distinct `object_size_limit_exceeded` finding without modifying the object.
- Added a regression with a patched small ceiling to verify oversized objects are reported and preserved. Source commit: `1aa0a40`; regression commit: `23aa5af`; security-matrix registration commit: `c15d5b3`. Exact source, test, workflow, security-matrix, status and blocker files were re-fetched from `main`; static checks confirmed the max+1 read bound, distinct oversized-object finding, read-only regression assertion, and both workflow and security-matrix registration. Runtime suite remains unexecuted (0%). AI-2 estimate: **78.3%**; whole-project estimate remains **75.3% provisional**. No runtime pass is claimed.


## AI-2 restored-original upload TOCTOU hardening — 2026-11-16

- The restore-to-S3 importer previously hashed a path, then later called `Path.read_bytes()` for upload. A replacement between those operations could bypass the earlier digest check and trigger an unbounded read. It now opens the final file component with `O_NOFOLLOW` where supported, verifies the descriptor refers to a regular file, caps reads at the recorded size plus one sentinel byte, and rechecks SHA-256/size immediately before staging the upload.
- Added regressions for replacement after the initial digest and for a symlinked restore object; both must abort without staging/finalizing an S3 object or changing restored metadata.
- Source commits: `8b021f2`, `f89370f`; regression commits: `4199fc8`, `d456768`; security-matrix registration: `b75cbdf`. Exact importer source, regression, workflow, security-matrix, status and blocker files were re-fetched from `main`; static checks confirmed no remaining `source.read_bytes()` upload, no-follow descriptor opening, regular-file verification, recorded-size-plus-one read bound, digest revalidation, both adversarial regressions, no-stage assertions, and both workflow/security-matrix registration. Runtime test execution remains **0%**. AI-2 estimate: **78.4%**; whole-project estimate remains **75.3% provisional**. No runtime pass is claimed.


## AI-1 candidate provenance and colloquial polarity follow-up — 2026-11-16

- Candidate registration now preflights source/document/version/review record shapes before any database writes, validates the top-level record shape, identifiers/dates/SHA-256 and supported unique review types, rejects malformed/unhashable enum values and whitespace/case-obfuscated permission grants, and wraps all registry inserts in a savepoint so a late metadata conflict rolls back earlier inserts, commits successful registrations for independent connections, and preserves any existing review decision without adding a duplicate pending event, requires clean HTTPS source/terms/version/review-evidence URLs, binds each version URL to the declared source host, rejects signed/cloud credential query keys, and cannot self-grant collection/commercial-reuse permission or verification status. Existing restrictive source permissions survive idempotent re-registration. The Labour Law candidate's tokenized Manshurat review URL was replaced by the stable source page.
- The read-only legal-source review queue rejects URL fragments and signed/tokenized evidence URLs, including AWS/GCP signing parameters. This is locator validation only, not evidence authenticity validation.
- Arabic claim polarity now recognizes Egyptian colloquial `ما...ش` permission denials (e.g. `ماينفعش`, `مايحقش`, `مايسمحش`) as prohibition and removes those negative forms before positive-permission matching. A local Python regex harness confirmed seven representative variants, including diacritics and tatweel; the repository tests remain unexecuted.
- Law 14 evaluation draft SHA-256 is recorded and checked against the exact bounded bytes parsed by the validator; its CLI reports the same digest. Metrics remain null until lawyer-approved labels and actual retrieval runs exist.
- Relevant source/test/status commits include `ba4a569`, `7c7e090`, `5a8a109`, `ceb0b84`, `f1fd96e`, `40ceacd`, `566a657`, `5161eae`, `77b845f`, `5c11092`, and `06343ae`. Tests are registered; none of these repository test suites has been executed in this environment.
- Updated AI-1 implementation estimate: **94%**; retrieval/Arabic matching safeguards: **83%**; ingestion/provenance tooling: **98%**; evidence/release safeguards: **98%**; evaluation infrastructure: **100% implemented**; Egyptian legal corpus readiness: **10%**. Whole-project engineering estimate remains **75.3% provisional**. Release remains **NOT READY**.


## AI-2 restore namespace directory-descriptor hardening — 2026-11-16

- Closed the remaining final-directory race in restore-to-S3 original reads: the importer now opens the firm namespace with O_DIRECTORY | O_NOFOLLOW, then opens the object filename relative to that pinned directory descriptor with O_NOFOLLOW. Replacing the namespace path with a symlink after the earlier inventory check can no longer redirect the object read; platforms lacking the required primitives fail closed.
- Added a regression that swaps the firm namespace for a symlink to an outside directory and asserts the object opener rejects it while preserving both directories' contents. The existing restore-importer module is already registered in scripts/security_regression_check.sh and the CI workflow.
- Source commit: 0b7f440; regression commit: fef3d13. Static review confirms directory-descriptor-relative open, no-follow flags, regular-file validation, cleanup of both descriptors, and regression coverage. Repository runtime tests remain 0% executed; no runtime pass is claimed. AI-2 estimate: 78.5%; whole-project estimate remains 75.3% provisional.

- Follow-up transaction review caught and fixed two registrar lifecycle issues: successful registrations now commit (verified by a new independent-connection regression), while a failed late conflict rolls back the earlier source inserts through a savepoint. Re-registration now checks for any existing review event, not only pending events, so it cannot append a new pending event after a human pass/fail decision. The preservation fixture uses the schema's valid `pass` outcome. Candidate registry regression module now has 11 distinct tests, registered in the workflow; runtime execution remains unavailable.


## AI-2 encrypted backup ZIP member preflight hardening — 2026-11-16

- Tightened encrypted backup ZIP validation to reject non-canonical member paths (empty, dot, parent, repeated-separator, NUL, backslash, absolute and Windows drive-prefixed forms) and special filesystem entry types such as FIFOs/devices. This closes ambiguity between ZIP member names and paths created by extraction, before extractall is reached.
- Added regressions for repeated separators, dot components, Windows drive paths and FIFO metadata. The backup-bundle test module is already present in both the focused security matrix and GitHub workflow.
- Source commit: d3d5841; regression commit: 0775ba4. Static review confirms path canonicalization and file/directory mode allowlists. Repository runtime test execution remains 0%; no runtime pass is claimed. AI-2 estimate: 78.6%; whole-project estimate remains 75.3% provisional.


## AI-2 restore root/object directory-chain pinning — 2026-11-16

- Extended the restore-to-S3 importer beyond namespace pinning: it now opens the canonical restore root, objects directory, firm namespace and blob in sequence using directory-descriptor-relative opens and O_NOFOLLOW. A symlink substitution at either the objects directory or firm namespace cannot redirect digest or upload reads; unsupported platforms fail closed.
- Added an adversarial regression for replacing the objects directory with a symlink to an outside tree. Together with the namespace-symlink and final-file-symlink tests, each object-path component below the canonical restore root is covered. Source commit: 0a41996; regression commit: 56ce2d7. The importer test module remains registered in workflow and security matrix. Static source/test review only; runtime test execution remains 0%. AI-2 estimate: 78.7%; whole-project estimate remains 75.3% provisional.

- The legacy bulk candidate-catalog seeder was also hardened: it now checks existing source/document identity conflicts instead of silently hiding them with `INSERT OR IGNORE`, uses a savepoint with rollback on late conflicts, commits successful seeds, and leaves any previously tightened source-permission decisions untouched. Added regressions for late-conflict rollback and restrictive-permission preservation; the catalog test module remains workflow-registered. Runtime execution remains blocked by runner allocation.


## AI-2 isolated validation note — restore descriptor chain and ZIP preflight — 2026-11-16

- Executed two isolated Python harnesses against faithful copies of the new logic: the descriptor harness accepted a regular object and rejected symlink substitutions at both objects/ and firm namespace; the ZIP harness rejected repeated separators, dot components, Windows drive paths, traversal, absolute paths and FIFO metadata while accepting a normal directory/file archive. These are focused harnesses, not execution of the repository test modules.
- The restore importer now explicitly checks that os.open supports dir_fd before attempting the pinned hierarchy; otherwise it fails closed. Capability-guard commit: a092388. The importer module remains workflow/security-matrix registered. Repository test modules executed: 0%; Actions jobs executed: 0%.

- The shared legal-document collector's JSONL append primitive now opens non-blocking with no-follow semantics, verifies the opened descriptor is a regular file with exactly one hard link, and confirms the requested path still names that descriptor before writing. This closes a hardlink-alias write path and avoids blocking on a FIFO replacement. Added a hardlink regression and registered it in the existing collection-pipeline suite; the suite is not executed due to unavailable GitHub runners.


## AI-2 restore path full-chain descriptor anchoring — 2026-11-16

- Strengthened restore-original reads to walk every directory component from the filesystem root using dirfd-relative O_DIRECTORY | O_NOFOLLOW opens, then open objects/, firm namespace and blob relative to the pinned descriptors. This also rejects a restore-root symlink substitution and intermediate parent swaps, not only objects/ or namespace symlinks. Added a regression for a symlinked restore root.
- Source commit: 2e7a7e3; regression commit: 4c33f88. The isolated descriptor harness was rerun and accepted a regular object while rejecting symlink substitutions at restore root, objects/ and firm namespace. This remains an isolated harness, not repository test execution. The importer module is workflow/security-matrix registered. AI-2 estimate: 78.8%; whole-project estimate: 75.3% provisional; repository runtime tests: 0%.
- The Egyptian colloquial permission-negation regression now includes a fully vocalized/tatweel variant. An isolated Python check confirmed all seven forms are classified as prohibition and stripped before positive-permission matching; this is a focused helper check, not execution of the repository test module. Test commit: `cd999ad`.

- Manual capture URL validation now rejects the full AWS/GCP signed-link parameter family (algorithm, date, expiry, signed headers, credential/access-key identifiers and signatures), matching the candidate registrar, source review queue and capture-record validator. Added five cloud-signed URL regression cases plus a stable HTTPS control case; the fixture integration suite is registered. Runtime execution remains unavailable.

- The canonical source-permission register now applies the same signed-link rejection policy as the candidate registrar and manual capture: it rejects AWS/GCP signature, algorithm, date, expiry, signed-header and credential/access-key query keys, as well as URL fragments. Added six rejection cases and a clean HTTPS control. This closes a policy inconsistency where the canonical rights ledger accepted signed URLs that downstream capture paths rejected.


## AI-2 S3 original-object open stream ceiling — 2026-11-16

- S3 original-object open now rejects invalid/oversized ContentLength metadata before body reads and wraps accepted provider bodies in a bounded reader. Even read() without a size argument requests at most max_bytes + 1; the extra byte detects overflow and closes the provider body. The wrapper also exposes close and context-manager semantics so existing `with store.open(...)` callers retain deterministic cleanup.
- Added regressions for oversized streams with absent ContentLength and oversized ContentLength preflight. Source commit: 5e9f871; regression commit: d4f5d26. Both tests are in tests/test_s3_original_file_storage.py; the module is already registered in the workflow and security regression script. Static source/test review only; repository runtime tests remain 0% executed. AI-2 estimate: 78.9%; whole-project estimate remains 75.3% provisional.


- Follow-up: bounded S3 stream reads now also close the provider body if the underlying read raises, with a dedicated regression. Commits: implementation `204d5a8`; test `28c5d90`. This is source-level and regression review only; no repository runtime test has run.


## AI-2 S3 inventory cardinality ceiling — 2026-11-16

- Added a one-million-unique-key ceiling to the S3 original-object inventory, in addition to the existing 10,000-page and repeated-token guards. The importer now fails closed before retaining additional unique keys once the bound is reached.
- Added a regression with a patched two-key ceiling and a three-key page. Source commit: 0af3ef1; regression commit: 0122ec1. Test module is already registered in the workflow and security regression script. Static review only; repository runtime tests remain 0% executed. AI-2 estimate: 79.0%; whole-project estimate remains 75.3% provisional.

- The general lawyer-reviewed retrieval evaluator now exposes `wrong_article_rate`, `wrong_article_count`, and the exact emitted-pin-citation denominator globally and per practice area. It is explicitly the complement of pin-cite accuracy for emitted citations on questions that have reviewed expected pin-cites; missing citations remain separately visible through expected-pin-cite recall and citation coverage. The existing regression with one correct and one incorrect article citation now asserts a 50% wrong-article rate, and per-practice-area regressions assert 0%/100% for correct/incorrect locators. Commits: `399ca2a`, `9f46b20`, `aafb866`. The dedicated article-level evaluator `tools/score_arabic_retrieval.py` already reports the release-target wrong-article rate; no duplicate change was needed there.


## AI-2 backup creation expanded-size preflight — 2026-11-16

- Backup creation now totals snapshot file sizes before hashing them and rejects payloads above the restore-side expanded archive ceiling. It also includes serialized manifest bytes in the pre-ZIP size check, preventing oversized snapshots from consuming hash/ZIP work before eventual restore rejection.
- Added a regression that lowers the ceiling and asserts rejection occurs before file hashing or ZIP creation. Source commit: 155e284; regression commit: b41fb19. Static review only; repository runtime tests remain 0% executed. AI-2 estimate: 79.1%; whole-project estimate remains 75.3% provisional.


- ZIP portability follow-up: member preflight now also rejects Windows alternate-data-stream colons, reserved device components (CON/PRN/AUX/NUL/COM1–9/LPT1–9), and trailing dot/space aliases. Added seven unsafe-path variants to the preflight regression. Commits: source `45d5391`; tests `1119a10`. Runtime execution remains 0%.


## AI-2 recovery archive upload exact growth bounds — 2026-11-16

- Recovery archive hashing and multipart upload now request no more than the remaining verified size plus one sentinel byte. A file that grows after its initial stat/hash cannot cause a full extra 1 MiB/64 MiB read before the mismatch is detected; multipart upload aborts on the first extra byte.
- Added a tracking-file regression proving hash preflight reads exactly `max_bytes + 1` bytes before rejecting an oversized source. Source commit: 774670a; regression commit: 70b13a2. Runtime repository tests remain 0% executed.


- Recovery archive follow-up: persisted-upload verification and exact-version downloads now also read at most the declared size plus one sentinel byte, rather than overshooting by a full 1 MiB chunk. Added an oversized-download regression asserting exactly `declared_size + 1` bytes are consumed and the partial destination is removed. Commits: source `fb89aaf`; test `4b80528`. Repository runtime tests remain unexecuted.
