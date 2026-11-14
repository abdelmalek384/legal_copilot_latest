# Legal Copilot — release-candidate status

**Updated:** 2026-11-14  
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
| Staging and recovery | The local release checker now requires Python 3.12 before starting Python gates and explicitly runs the focused security matrix, isolated encrypted multi-tenant backup/restore drill with a real firm-owned original binary and tamper-rejection fixture, placeholder-only Compose configuration validation, lock regeneration/drift comparison, pip-audit, and optional workflow lint/Bandit scans when installed. All remain unexecuted. Credential-only preflight failures must be recorded separately from missing infrastructure/configuration. |
| Validation | GitHub Actions runner allocation/billing prevents hosted test execution. Latest exact-head check on `main` commit `bf5ddf5d8a04c889f03b010202f4e0db054ddfe4`: Tests run `43602358989`, Browser acceptance `43602359120`, Dependency audit `43602359046`, and CodeQL `43602359089` all concluded failure before any job step; inspected jobs report `runner_id=0` and `steps=[]`. The prior exact-head check on `8955b38d564932fc908073eb230e9940b893e230` showed the same pattern. This is runner/service allocation evidence, not a code-test failure or pass. A static GitHub directory/workflow audit finds all 186 top-level `test_*.py` modules registered in the workflow or known-unrun register; this is not execution. No newly added local tests have been executed in this work session. Direct-main commits are implementation evidence, not test passes or pilot acceptance. |

## Repository tasks closed at implementation level

The following bounded repository tasks now meet their source-change acceptance criteria. Their percentages describe implementation only; the linked runtime/release gates remain separate.

| Task | Implementation | Validation boundary |
|---|---:|---|
| Align all eight direct dependency pins with the checked-in Python 3.12 lock | **100%** | Static consistency check completed; clean resolver/install/audit still open |
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

## AI-2 implementation completion estimate

These are unweighted engineering estimates for the seven AI-2 delivery workstreams, not test-pass rates or production-readiness scores.

| Workstream | Estimated implementation completion | Remaining acceptance |
|---|---:|---|
| Local release baseline | 20% | Release-check implementation exists; exact local checker output and all Python 3.12 gates remain unavailable |
| Security integration | 75% | Exact-head security verification remains blocked |
| Security regression coverage | 91% | Additional backup source no-follow, same-descriptor upload, mandatory checksum and verification-to-upload byte-binding regressions plus duplicate device-record, reused-evidence-path, and duplicate-key rejection for both device and database release manifests are committed; all repository tests remain unexecuted, real OCR-engine/image-quality acceptance still pending |
| Lawyer rating UI/export | 95% | Browser acceptance and adapter execution remain pending |
| Test-firm package | 90% | Clean-clone first-login rehearsal remains unexecuted |
| Repository cleanup/accessibility | 83% | Bilingual form labels/errors, source-inspector metadata and passage navigation are implemented; run hygiene scan and finish manual accessibility review |
| Staging/recovery | 38% | Recovery upload now binds the exact verified bytes and fails closed without checksum; recovery drill, Compose gate, provider configuration and witnessed restore remain unexecuted |

**Unweighted implementation estimate: 65%.** The application remains **NOT READY** for lawyer pilot or production. No test pass is inferred from committed test code.

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
- PR #1610 head `fc5e6e99716fb7fbcada8b2ac5b93a3d62ebca5f` is divergent from current main (218 ahead / 525 behind; four net changed files). Its frontend diff deletes the existing answer-rating panel and save/load controls, so do not merge or transplant it wholesale. Any desired navigation changes need a narrow current-main rebase preserving answer ratings and newer document/session safeguards.
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
