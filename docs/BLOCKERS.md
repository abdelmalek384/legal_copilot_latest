
- Fixture maintenance after URL hardening: synthetic packets used by the non-string-use, unknown/duplicate-use, and boolean-flag tests now carry a valid neutral HTTPS rights-evidence locator. This preserves the intended test boundary rather than having those cases fail earlier on missing URL metadata. Tests remain unexecuted.

## AI-1 rights-evidence locator safety — 2026-11-26

- The source-match adapter now rejects rights-evidence URLs that are not stable HTTPS locators or that contain credentials, fragments, malformed ports, control/whitespace characters, or known signed/session/token query parameters. The migration's simple `https://` prefix CHECK is not treated as sufficient protection at the read boundary.
- Added malformed-locator cases to the synthetic packet regression matrix. This is URL-shape validation only: a safe URL does not establish that its contents are authentic, current, legally sufficient, or permission-granting. Tests remain **not executed**.

## AI-1 evidence-row identity validation — 2026-11-26

- The source-match adapter now validates the evidence row's primary key as a positive integer (explicitly rejecting booleans and string coercion) before using it to query approved-use scope rows. This keeps malformed legacy/alternate-adapter row identities from reaching the second database lookup.
- Added synthetic regressions for zero, boolean, and string evidence IDs. The repository test module remains **not executed**; this is source review and manual GitHub read-back only.

- Added explicit orphan/mismatched independent-source registry join cases to the malformed-packet regression matrix, including absent and wrong join identities. These are source-authored regressions only; they have not been executed.

- Regression-fixture alignment follow-up: all synthetic evidence packets that proceed to approved-use or boolean-flag checks now explicitly model the independent-source registry join result. This prevents the new orphan-source guard from causing unrelated tests to pass for the wrong reason. Tests remain unexecuted.

## AI-1 independent-copy registry binding — 2026-11-26

- Tightened the exact-version evidence query to require the independent-copy source identity to resolve to an actual `legal_sources` registry row. A syntactically valid but orphaned independent-source ID now yields no evidence packet rather than relying only on a foreign-key declaration that may not have been enforced by a legacy/imported database.
- Aligned the source-ID guard to the shared compiled identifier pattern and repaired the hash-mismatch regression fixture so it supplies the newly required independent-copy identity, digest, and revision. The test now reaches the intended primary-hash mismatch condition.
- Manual GitHub read-back only; tests and GitHub Actions remain **not run**. This proves registry-row presence only, not independent-source authenticity or independence.

## AI-1 exact-version provenance packet integrity — 2026-11-26

- Strengthened the source-match evidence read adapter beyond version/hash equality: it now requires canonical ISO calendar dates, 64-character hexadecimal SHA-256 values for both the primary capture and independent copy, a valid bounded independent-source identifier distinct from the primary source, and a positive integer evidence revision (excluding booleans).
- Added synthetic regressions for malformed digests, impossible/non-canonical dates, invalid or self-referential independent-source IDs, and invalid revision values. Tests are authored but **not executed**.
- This validates packet shape only; it does not authenticate either source, establish that the independent copy is truly independent, grant rights, or certify legal accuracy. No source records or permission states changed.

## AI-1 exact-version evidence adapter identifier boundary — 2026-11-26

- Applied the same bounded ASCII source-ID grammar at the source-match evidence read boundary, before any database query. This prevents malformed identifiers from reaching SQL lookups and keeps the evidence adapter consistent with the candidate seeder and permission-register validator.
- Added a focused no-database-access regression for malformed identifiers plus a valid identifier control. Test is authored but **not executed**; this is manual source review/read-back only.
- Existing evidence packet semantics, rights flags, trust tiers, and verified-corpus retrieval are unchanged. No evidence is synthesized and no candidate source is enabled.

## AI-1 permission-register identifier validation — 2026-11-26

- Extended the canonical permission-register validator to enforce the same bounded ASCII source-ID grammar as the candidate seeder (`[A-Za-z0-9][A-Za-z0-9._-]{0,127}`). This closes a validator asymmetry where whitespace, delimiters, non-ASCII identifiers, or overlong IDs could be accepted by the register validator even though the seeder rejects them.
- Added regression cases for invalid identifiers and a valid mixed-punctuation identifier. Tests are authored but **not executed**; this is a source-level/manual integration only.
- No source rights, permissions, legal content, or candidate status changed.
# Delivery blockers and closure register

Last reviewed: 2026-11-26
Scope: Legal Copilot release work. This register separates work that can be closed by repository changes from work that requires external execution, licensed/legal review, operational access, or real users.

## Closure policy

A task is 100% only when its acceptance criteria are met and the evidence is recorded. A code change or passing unit test alone does not establish production readiness. Do not mark legal content verified without qualified Egyptian-lawyer sign-off. Do not mark tests passed unless they were executed in the stated environment.

## Manual integration checkpoint — 2026-11-25

- Mainline now includes manually reviewed corrections in PRs #2010, #2012, #2001, #2016, #2018, #2019, #2020, #2021, #2022, #2023, #2026 and #2027. Current summary and AI-1 implementation estimates are recorded in docs/STATUS.md.
- Corresponding stale drafts were closed as superseded after their changes were consolidated onto current main. Dependency update PRs #1873, #1874, #1876 and #1877 were closed unmerged because they changed requirements.txt without regenerating the Python 3.12 hash lock. Reopen only after lock regeneration, clean install, compatibility tests, and pip-audit evidence.
- No repository test modules were executed in this work session. Added regression tests are authored but not passed until run in a supported Python 3.12 environment. GitHub Actions remain excluded due runner billing.
- Legal source-status and permission-register date checks now use Africa/Cairo (PR #2026). The negation guard now scopes polarity comparisons to distinct obligation clauses (PR #2027). Tenant database and SQLite sidecar hard-link checks are defense in depth. Pathname-based SQLite opening is not descriptor-to-path identity proof; the storage root must remain writable only by the application service account and administrators. See docs/manual_tenant_storage_review_2026-11-25.md.
- Lawyer pilot remains NOT READY. Legal verification, source-currentness review, supported-runtime execution, two-firm authorization acceptance, and witnessed backup/restore remain separate gates.



- 2026-11-25 provenance trace: `citation_provenance` is registry-linked and returns source/version/review/permission relations, but corpus hits do not carry the full source-match evidence package. The firm-test mode remains intentionally fail-closed; do not bridge this gap by synthesizing evidence. Static trace recorded in `docs/legal_answer_provenance_trace_2026-11-25.md`; runtime remains untested.

## Highest-priority work that can reach 100% in-repository

| Work item | Owner | Closure evidence | Current disposition |
|---|---|---|---|
| DEL/control-character rejection in Gazette source URLs | AI-1 | Validator rejects C0 and DEL; focused regression test exists | C0/DEL, fragment delimiters, raw backslashes, signed/credential query parameters, and empty user-info delimiters rejected; importer changes merged in #1556/#1563 and follow-up direct-main hardening; focused tests still unexecuted |
| Gazette text importer input contract and deterministic output | AI-1 | Input/schema/provenance/duplicate/error-path tests; documented CLI | Importer and operator contract merged in #1563/#1567; duplicate JSON keys now fail closed at every nesting depth in the Gazette text importer, legacy PDF importer, collection manifest, manual-capture catalog/existing provenance sidecars canonical source-permission register and both legal-candidate seeder inputs; source-reviewed, regression tests still unexecuted |
| Retrieval scorer safety-status ordering | AI-1 | Known wrong/uncited/unverified/non-abstention failures always report below-target; focused tests executed | Fix merged in #1560 and carried with URL hardening in #1566; focused tests still unexecuted |
| Arabic obligation-negation guard | AI-1 | Final answer path invokes guard; English/Arabic reversals, faithful negatives, unrelated clauses and whitespace have regression coverage | Source integration is complete in `app.ask` (#1588); focused reproducer and integrated app-path tests are committed directly to main (`92e5177`, `f988e76`); tests remain unexecuted due GitHub billing/runtime access |
| Benchmark evaluator data-integrity contract | AI-1 | Unlabeled data excluded, reviewer registry required, stable fingerprint, malformed input rejected | Implemented in repository; execution and integration remain unverified |
| Arabic evaluation question inventory | AI-1 | At least 100 unique formal/colloquial Egyptian Arabic drafts, uniform schema, all unreviewed and answer fields empty | 116 unique Law 14/2025 drafts (58 formal + 58 colloquial) are present; all labels and answer keys remain unapproved; scoring requires counsel-approved labels and real retrieval exports |
| Documentation and ownership handoff | AI-1 / AI-2 | Each known blocker has owner, acceptance evidence, and no false completion claim | Register merged in #1562 and refreshed in this update; operational blockers remain open |
| Legal evaluation report evidence-path integrity | AI-1 | Scorer, release-gate and legal-readiness report outputs cannot overwrite candidate/run/reviewer/acceptance inputs, including hard links | 100% merged (#1593); regression tests committed but not executed |
| Legal report output-path integrity | AI-1 | JSON/Markdown report destinations cannot alias their database/register inputs or each other through direct paths, symlinks or hard links | 100% source implementation merged across source-review queue, corpus inventory, acquisition readiness, amendment relationships, OCR reports, legal audits, corpus comparison, evidence-card reports and draft builder (#1599/#1609); regression tests committed but not run |
| Remaining legal audit output-path integrity | AI-1 | Canonical OCR evaluator, article-row audit and corpus database audit cannot overwrite their inputs through direct paths, symlinks or hard links | 100% source implementation merged in #1609; regression tests committed but not executed |
| Additional legal CLI report-path integrity | AI-1 | Corpus/reference comparison, Labour Law evidence-card report, and structured legal-draft output cannot overwrite source inputs or inventory manifests | 100% source implementation merged in #1609; regression tests committed but not executed |
| Tenant database path ancestry and SQLite-open race hardening | AI-2 | Strict preflight, runtime profiles, tenant catalog and tenant router reject symlinked path components before/after storage access | 100% source implementation merged in #1700–#1704; isolated helper/race harnesses exercised; repository regressions not executed |
| Tests workflow hash-lock enforcement | AI-2 | CI installs the Python 3.12 lock with --require-hashes; workflow contract prevents unhashed fallback | 100% implementation merged in #1705; clean install and CI execution pending |
| pypdf 7.1.0 dependency/lock alignment | AI-2 | Direct pin and Python 3.12 lock match PyPI wheel/source SHA-256 hashes | 100% implementation merged in #1706; pip-tools regeneration, clean install, compatibility suite and pip-audit pending |

## AI-1 evaluation JSONL duplicate-key rejection — 2026-11-15

- The Arabic retrieval scorer and API evaluation runner now reject duplicate JSON object keys at every nesting depth while reading question/run JSONL rows. Previously, Python's default JSON decoder silently retained the last duplicate value, allowing ambiguous reviewer labels, article identifiers, or question metadata.
- Added focused regressions for duplicate top-level and nested keys in both loaders. The existing test modules were already registered in `.github/workflows/tests.yml`; no workflow change is needed.
- Source implementation and test additions are committed on the current-main branch `ai1/reject-duplicate-jsonl-keys-mainline`. Tests remain unexecuted because GitHub runner allocation/billing is unavailable; no pass is claimed.
- This is input-integrity hardening only. It does not approve labels, change any source trust tier, or produce retrieval-accuracy metrics.

## Deployment dependency blocker

- **Python 3.12 lock release validation (implementation aligned):** the current lock pins `boto3==1.43.123` and `botocore==1.43.123`; all eight direct requirements statically satisfy their lock pins, and a regression test now enforces that contract. The local/hosted audit commands require hashes. Still open: regenerate with the pinned Python 3.12 resolver, clean Python 3.12 install, pip-audit, full suite and exact release-check output. Do not describe this as a completed release audit.

## AI-2 release-evidence integrity hardening — 2026-11-14

- Device/browser acceptance evidence now rejects duplicate JSON object keys, duplicate device/browser/locale identities, and evidence paths reused across records. The release-gate integration calls the same validator; unit and integration regressions cover these cases.
- Database/staging operational acceptance manifests now reject duplicate JSON object keys at every object depth instead of silently accepting the last value.
- Added the database acceptance, device acceptance, release-gate integration, production release-gate, and encrypted archive tests to the focused security regression script, with a workflow-contract regression.
- These are source/test implementation changes only. The test modules are registered but have not been executed in this environment; no runtime pass is claimed.

## AI-2 migration-ledger integrity hardening — 2026-11-16

- Added versioned `schema_migrations` update/delete guards to control-plane migration `0024`, firm migration `0024`, and legal-corpus migration `0004`. New version rows remain insertable; previously applied name/checksum evidence cannot be changed through ordinary SQL.
- The guards are installed through profile migrations so existing deployments can update through the normal control-plane/corpus and tenant-fleet maintenance procedures. A pre-existing same-name weakened trigger makes the migration fail atomically.
- Regression coverage includes immutable update/delete behavior, idempotent re-entry, refusal of a pre-existing weakened guard, installation across all three actual profile migration directories, and tenant-preflight detection of missing/weakened control-plane and tenant guards. `tests/test_db_migrations.py`, `tests/test_schema_profiles.py`, and `tests/test_tenant_database_preflight.py` are registered in the Tests workflow; execution remains blocked by runner billing. Implementation is committed but not runtime-validated.


## AI-2 recovery archive integrity hardening — 2026-11-14

- Recovery source opening now rejects symlinks and special files, uses nonblocking/no-follow flags where available, validates the opened inode against the pre-open identity, and hashes/uploads through the same open descriptor. The uploader requires an expected SHA-256; the tenancy archive flow supplies the checksum returned by verification.
- Backup verification now hashes the exact encrypted bytes it verifies and reports that digest. The upload path compares the same opened bytes against the required digest before any object upload. Missing or mismatched checksums fail closed before AWS client creation/upload.
- Added regressions for FIFO/symlink rejection, path replacement, truncation, missing verification checksum and checksum mismatch. Static/custom isolated harness checks passed for the critical descriptor/hash invariants; repository test modules remain unexecuted. This closes the bounded source implementation, not the witnessed staging recovery acceptance.

## AI-2 current-main implementation — 2026-11-14

- The answer-rating contract is now integrated: firm-local submit/update/read handlers, admin-only listing/export, append-only events, bilingual per-answer UI, trust-tier fallback badge, and focused backend/frontend tests are committed on `main`. The export now carries a conservative message-time trust_tier field compatible with the AI-1 adapter. Execution is pending.
- Added encrypted-PDF rejection, parser-level tests for encrypted files and the 500-page ceiling, and multipart route regressions for oversized, over-500-page, malformed, and encrypted PDFs with no-retention assertions. Concurrent OCR and PDF rasterization work are bounded to two jobs with a five-second admission wait and fail-closed 503 before page rendering; saturation and timeout-release regressions are committed. A subprocess-timeout propagation and semaphore-release regression is now committed; The uploaded-DOCX and scanned-PDF/OCR-fallback-to-tenant-retrieval regression now covers hostile text, cross-firm isolation, the matter-data LLM approval gate, and JSON untrusted-data serialization. A real Tesseract/PDF image-quality acceptance run remains open. Storage finalization-failure coverage already exists but remains unexecuted.
- Added an import-to-invoice-export CSV formula-injection regression covering formula-like case titles and client names. The import remains data-only; export neutralizes spreadsheet formula prefixes. Test execution remains pending.
- Added a case-scoped retrieved-passage/provenance prompt-injection regression. Actual uploaded DOCX and scanned-PDF/OCR-fallback-to-retrieval attack-path coverage is now committed, including hostile content, malicious filename metadata, firm isolation, approval gating and prompt serialization. Real OCR-engine/image-quality acceptance remains open.
- Clean-clone first-login and rating export steps are in the test-firm runbook. No clean-clone rehearsal has been executed.
- The security regression script now includes rating-route and frontend contract modules and exits if Python is not 3.12. It has not been run.
- The local release checker now explicitly includes the focused security matrix, isolated encrypted multi-tenant backup/restore drill with a real original-file object and tamper-rejection fixture, placeholder-only Compose validation, dependency lock regeneration/drift comparison, pip-audit, and optional workflow lint/Bandit scans. All remain unexecuted. No release-readiness or pilot acceptance claim is made.

- **Owner source package inspected (AI-1):** `docs/legal_evidence/law14_2025_import_operator_handoff.md` and `law14_2025_import_metadata.template.json` document the import contract. The newly supplied 112-page PDF's text layer exposes all 13 promulgation headings and all 298 attached-law article headings in sequence; see `docs/legal_evidence/law14_2025_uploaded_pdf_heading_audit.md`. This is a heading-only audit: the PDF reports copy/print restrictions and carries a watermark that the electronic copy is not valid for circulation. Do not treat it as authenticated or reuse-cleared, do not commit extracted text, and do not fabricate supplier role/permission evidence. Article-body comparison and the importer run remain open pending an authenticated/authorized transcription and truthful provenance metadata. The importer supports expected heading counts and detects internal gaps, missing trailing article numbers, out-of-range headings, and an entirely absent expected provision/article block. Regression coverage is committed but remains unexecuted while the runner is unavailable.

## Remaining legal JSONL duplicate-key hardening — 2026-11-15

- Extended strict JSON object parsing to the Law 14/2025 draft inventory validator and OCR-quality evaluator. Duplicate keys at any nesting depth now fail closed, matching the Arabic retrieval scorer and API evaluation runner.
- Added top-level and nested duplicate-key regression cases to `tests/test_validate_law14_eval_draft.py` and `tests/test_ocr_quality_evaluation.py`. Both test modules are already in `.github/workflows/tests.yml`.
- Implementation is on branch `ai1/strict-jsonl-legal-validators-mainline`; tests remain unexecuted due runner/billing unavailability. This change does not alter the draft inventory or any legal verification state.

## Human-review input ambiguity hardening — 2026-11-15

- The qualified-human answer-review evaluator now rejects duplicate JSON object keys in both review JSONL records and the private reviewer registry, including nested score/rationale objects. Previously, the default decoder could silently select the last conflicting value in a review record or registry entry.
- Added focused regressions for duplicate top-level/nested review keys and duplicate reviewer-registry keys. The test module is already registered in the Tests workflow.
- Source/test implementation is on branch `ai1/strict-review-record-json`; tests remain unexecuted due runner/billing unavailability. No reviewer is approved by this change; registry identity checks remain administrative assertions, not independent credential verification.

## Additional evidence-evaluator JSONL integrity — 2026-11-15

- Extended duplicate-key rejection to the general retrieval-quality evaluator (question/run JSONL and reviewer registry), Arabic OCR evaluator, article-row audit, and candidate/reference corpus comparator.
- Added focused top-level/nested duplicate-key regressions to the existing registered test modules. Malformed article-audit/comparison rows are excluded and counted/warned rather than silently using a last duplicate value.
- Changes are on branch `ai1/strict-jsonl-evidence-evaluators`; tests remain unexecuted because runner/billing access is unavailable. No legal corpus status or evaluation result is promoted.

## Legal release-gate and drafting JSON ambiguity hardening — 2026-11-15

- The production release gate now rejects duplicate keys in candidate legal-source JSON and the private reviewer registry. Ambiguous candidate records are excluded from the ready-source index; duplicate reviewer-registry keys fail the CLI before release evaluation.
- The legal draft builder rejects duplicate keys in structured draft input rather than silently selecting the last value. Added focused regressions to the existing production-gate and draft-builder test modules.
- Source/test changes are on `ai1/strict-release-json-inputs`; tests remain unexecuted due runner/billing unavailability. This does not approve any candidate source or draft.

## Amendment and legal-foundation register ambiguity hardening — 2026-11-15

- The amendment-relationship validator now rejects duplicate keys in both the amendment relationship register and document inventory JSON.
- The legal-data foundation validator now rejects duplicate keys in the source manifest and Arabic evaluation question seeds, with controlled validation errors.
- Added regressions for duplicate relationship-register keys and duplicate top-level/nested source/question keys. Existing test modules are workflow-registered; execution remains unavailable.

## Acquisition permission-register ambiguity hardening — 2026-11-15

- The acquisition-readiness validator now rejects duplicate keys in both collection manifests and the canonical source-permission register. Ambiguous permission or scope fields cannot be silently resolved with last-key-wins behavior.
- Added CLI regression coverage for duplicate manifest and register keys in the existing acquisition-readiness test module. Tests remain unexecuted because runner/billing access is unavailable.

## Collection provenance metadata ambiguity hardening — 2026-11-15

- The legal document collector now rejects duplicate keys when reading an existing current metadata pointer. It refuses to archive/overwrite ambiguous provenance rather than silently selecting one conflicting field value.
- Added a regression asserting the ambiguous metadata remains byte-for-byte untouched. Test execution remains blocked by GitHub runner/billing availability.

## Labour Law evidence-card report input integrity — 2026-11-15

- The provisional evidence-card report generator now rejects duplicate keys in the canonical inventory, inventory manifest, supplemental card files and protected-path manifest reads. Conflicting metadata cannot silently change report output.
- Added regressions for duplicate keys in the canonical inventory and manifest. Test execution remains blocked; evidence cards remain provisional and non-search-eligible.

## Legal corpus inventory report input integrity — 2026-11-15

- The read-only legal corpus inventory report now rejects duplicate JSON keys in source/permission/candidate/evidence/queue registers instead of silently choosing conflicting values.
- Added top-level and nested duplicate-key regression coverage. Existing test module is already registered; tests remain unexecuted due runner/billing unavailability.

## Legal release-readiness JSON ambiguity hardening — 2026-11-15

- The legal release-readiness validator now rejects duplicate keys in both the canonical source-permission register and candidate legal-source JSON. Duplicate candidate inputs are explicitly blocked as unreadable; duplicate register input prevents any candidate from passing.
- Added regressions for conflicting permission-register and candidate-document fields. Tests remain unexecuted due runner/billing unavailability.

## Phase 2 instrument inventory parser integrity — 2026-11-15

- The Phase 2 legal instrument inventory validator now rejects duplicate JSON keys at every nesting depth before evaluating source permissions, legal status or review labels.
- Added top-level and nested duplicate-key regressions; test module is already registered. Tests remain unexecuted due runner/billing unavailability.

## Arabic scorer reviewer-registry integrity — 2026-11-15

- The Arabic retrieval scorer now parses its private reviewer registry and any existing comparison report with duplicate-key rejection, in addition to the question/run JSONL guard already merged in #1621.
- Added a CLI regression proving duplicate reviewer-registry keys fail before scoring. Test remains unexecuted due runner/billing unavailability.

## Existing collection sidecar read hardening — 2026-11-16

- The collector's `--process-existing` path now uses a bounded regular-file reader with `O_NOFOLLOW`, inode identity checks, and strict duplicate-key JSON parsing for prior metadata sidecars. A symlink swap or ambiguous provenance record cannot silently redirect reprocessing.
- Added regressions for top-level/nested duplicate keys and symlinked sidecars. Tests remain unexecuted because hosted runners are unavailable.

## Manual capture sidecar integrity — 2026-11-16

- The manual-capture rerun path now uses bounded regular-file reads, `O_NOFOLLOW` where available, inode/metadata-change checks, and strict duplicate-key JSON parsing for existing sidecars. It refuses ambiguous or symlinked provenance rather than overwriting it.
- Added regressions for duplicate top-level/nested keys and symlinked sidecars. Tests remain unexecuted because hosted runners are unavailable.

## Labour Law candidate registration input integrity — 2026-11-16

- `tools/register_labour_law_candidate.py` now validates its candidate JSON as a bounded regular file, rejects symlinks and duplicate keys at all object depths, and refuses non-object roots before opening the shared corpus connection.
- Added duplicate-key, non-object-root and symlink regressions. Runtime tests remain unexecuted because hosted runners are unavailable.

## Legal evaluation API response integrity — 2026-11-16

- The authenticated legal-evaluation runner now rejects duplicate JSON keys in API responses, including nested objects, instead of accepting the Python JSON parser's last-key-wins behavior. Added a regression for top-level and nested ambiguity.
- Tests remain unexecuted because hosted runner billing is unavailable.

## Candidate seeder input-file integrity — 2026-11-16

- Candidate catalog and canonical source-permission register reads now require stable regular files, reject symlinks, cap input at 4 MiB, and verify descriptor identity/size/timestamps. Duplicate-key rejection remains active. Added symlink/oversize regressions.
- Runtime tests remain unexecuted because hosted runner billing is unavailable.

## External blockers: do not spend repeated effort looping

### Test execution / CI runner availability
- Current limitation: GitHub Actions runner allocation/billing has previously failed before test steps start.
- Owner: repository administrator / available local Python 3.12 runner; AI-1 owns source fixes for concrete failures.
- Exit criteria: execute focused tests and full suite in a clean Python 3.12 hash-locked environment; preserve command, interpreter, dependency-lock hash, exit status and test counts.
- Exact-head recheck for reviewer-URL/scorer change head `ef90b56ed489be214150f1b86dac0930d814e7b8` on 2026-11-12: Tests run `43252117918`, dependency audit `43252117654`, CodeQL `43252117717`, and browser acceptance `43252117642` all failed before any job step. The inspected jobs returned empty step lists (0 executed steps); this is runner/service allocation evidence, not a code-test failure or pass.
- Latest exact-head recheck on `main` commit `bf5ddf5d8a04c889f03b010202f4e0db054ddfe4` (2026-11-14): Tests run `43602358989`, Browser acceptance `43602359120`, Dependency audit `43602359046`, and CodeQL `43602359089` all concluded failure before any job step; each inspected job reports `runner_id=0` and `steps=[]`. The preceding exact-head check on `8955b38d564932fc908073eb230e9940b893e230` had the same result. This is runner/service allocation evidence, not an application test failure or pass.
- Until then: PR source review is not a test pass.

### Python 3.12 dependency lock
- Related PR #1490 was inspected on 2026-11-13: it proposes raising the direct Boto3 floor from `>=1.43.123` to `>=1.43.125` without updating `requirements-py312.lock`. Current `main` is internally aligned at Boto3/Botocore 1.43.123 for the current direct requirement; PR #1490 is a separate dependency upgrade and must not be merged alone. If that upgrade is adopted, regenerate the lock with authentic hashes, install it in a clean Python 3.12 environment, and run import/startup plus tests.
- Owner: repository administrator / available local Python 3.12 environment; AI-1 can review resulting diffs and evidence.
- Exit criteria: regenerate lock using pinned pip-tools, include authentic hashes, install successfully from lock in a clean environment, and run import/startup plus tests. Never invent hashes.

### Live negated-obligation answer guard — implementation complete, validation open
- Related issue #1561 is closed. The current `app.ask` final-answer path invokes `has_negated_obligation_conflicts` before returning an answer; PR #1588 added service-path regressions.
- The helper and service-path test inventory covers English and Arabic positive/negative reversals, faithful negative wording, unrelated clauses, and Arabic variable whitespace.
- Do not reopen implementation or repeat speculative rewrites. Remaining closure evidence is execution of focused `tests/test_claim_support.py` and the full suite in a clean Python 3.12 environment, with exact commit, command and test counts.
- Owner: repository administrator / available local Python 3.12 runner for execution; AI-1 for any concrete source regression discovered by an executed test.

### Billing / payment provider
- Owner: AI-2 / account owner.
- Exit criteria: sandbox success/failure, duplicate webhook idempotency, invalid signature rejection, cancellation, expired subscription, invoice creation, firm isolation, and audit evidence. Do not infer billing readiness from UI implementation.

### Tenant isolation / production data safety
- Owner: AI-2 and repository administrator/local Python 3.12 runner.
- Exit criteria: adversarial cross-firm access tests across cases, documents, sessions, exports, search, background jobs and audit logs; backup/restore drill; deployment secrets and persistent storage review.

### Egyptian legal authority and counsel validation
- Owner: qualified Egyptian lawyer / legal content owner.
- Exit criteria: compare against authenticated Official Gazette source, record amendments/currentness/corrigenda, validate article text and citations, sign off each source/article scope.
- Labour Law No. 14/2025 comparison remains provisional. Preserve `verified=0`; machine comparison is not legal verification.

### Real lawyer pilot
- Owner: product owner / AI-2.
- Exit criteria: three firms complete unaided onboarding in under 15 minutes, use on mobile, and demonstrate owner-visible usage; later gate remains five firms using weekly and two willing to pre-pay.
- This cannot be completed by repository edits alone.

## Evidence URL validation parity — 2026-11-14

- Hardened `tools/research_inspector.py::_valid_review_evidence_url` to reject DEL, raw backslashes, query strings and fragments, in addition to its existing HTTPS/authority checks; added direct regression cases.
- Hardened `tools/evaluate_legal_answers.py::_valid_review_evidence_url` to reject raw backslashes; added a regression fixture alongside existing DEL/control-character coverage.
- Source changes and tests were committed directly to main (`8b0dbc1`, `2396247`, `1d615fc`, `752d724`). Static source review only; tests unexecuted.

## Cross-tool evidence URL validation parity — 2026-11-14

- Closed additional raw-backslash/DEL gaps in `research_inspector`, `evaluate_legal_answers`, the app review-evidence API validator, deadline-rule evidence validation, and `collect_legal_documents` source/manifest URL validation. The inspector, app and deadline validators also reject query strings/fragments where review evidence is required.
- Added regression cases in corresponding tests. Direct-main source/test commits include `8b0dbc1`, `2396247`, `1d615fc`, `752d724`, `d40f188`, `0701780`, `498fde9`, `f8f890c`, `3b416b6`, and `24ee02e`.
- Static source review only. Tests remain unexecuted; do not treat this as runtime validation.

## Manual-capture URL parity — 2026-11-14

- The manual-capture recorder and its read-only provenance validator now reject raw backslashes in source, terms and permission-evidence URLs; added regression cases for both ingestion and metadata validation.
- Direct-main source/test commits: `6b3e86a`, `72f8430`, `5dc40b1`, `4568760`. Tests remain unexecuted.

## Legal ingestion and source-rights URL parity — 2026-11-14

- Hardened additional evidence/source URL consumers: `manage.py` deadline-rule attestation, `tools/answer_trust_tier.py` source-match rights evidence, `tools/build_legal_draft.py` citation eligibility, and `tools/import_laws.py` PDF bundle metadata. Raw backslashes are rejected; attestation/draft eligibility also rejects query/fragment ambiguity and malformed ports.
- Added focused regression cases. Direct-main commits: `adb7ea8`, `8c47783`, `86eba26`, `a36f14a`, `46d7823`, `42b1a74`, `5d6d896`, `8df2fcf`, `d0608be` (test-case isolation follow-up). Tests remain unexecuted.

## Evaluation runner and candidate source URL validation — 2026-11-14

- `tools/run_legal_eval.py::validate_base_url` now rejects DEL and raw backslashes before URL parsing. Regression tests include single-backslash and DEL cases.
- `tools/seed_legal_candidates.py` now validates candidate and canonical permission-register `source_page` URLs plus optional terms, official-PDF and secondary-metadata URLs as clean HTTPS URLs, rejecting credentials (including empty user-info), fragments, signed/credential query parameters, malformed ports, controls and raw backslashes before comparing hosts. Regression fixtures cover HTTP, embedded/empty credentials, malformed authorities, fragments, signed query strings and backslashes. The Phase 2 inventory validator applies the same fail-closed URL policy to nested source/document URL fields.
- Direct-main commits: `27976cf`, `9fc0f19`, `279b761`, `54d31f8`, `66b2e6b`, `d0dafda`, `2b89b06`, `6913a76`, `a5874d7`, `b99d549`, `e457aca`, `480fb93`, `049bf30`, `2fb889a`, `9d09f0f`. Tests remain unexecuted.

## Gazette importer runbook execution reliability — 2026-11-14

- The documented direct command `python tools/import_gazette_text.py ...` previously depended on repository-root `PYTHONPATH` for its shared numeric-heading parser import. Added a direct-execution fallback and changed the CLI regression to remove `PYTHONPATH` from the subprocess environment.
- This closes a repository-side invocation defect only; it does not run the importer on the restricted Gazette scan or authorize any transcription. Direct-main commits: `7bc24e3`, `3750f4c`. Tests remain unexecuted.
- Follow-up static review fixed the nested-output regression fixture (it now targets a directory actually inside the source folder) and closed the empty-user-info URL bypass in the importer and candidate seeder. The candidate-catalog assertions were aligned with the current evidence-note wording; no legal source metadata or trust status was changed. Direct-main commits include `f00db64`, `e5c3a35`, `e457aca`, `480fb93`, `137c9d8`, and `e724763`. Execution remains blocked.

## Law 14/2025 evaluation-draft structural guard — 2026-11-14

- Added `tools/validate_law14_eval_draft.py` and `tests/test_validate_law14_eval_draft.py`. The validator checks JSONL shape, >=100 Arabic questions, unique IDs and question text, one formal/one colloquial variant per proposed article pin, expected article-number/ID consistency, and fail-closed unapproved/reviewer/release fields.
- It deliberately permits the already recorded limited targeted-PDF text spot-check flag (48 rows) while requiring full visual review, Gazette page review, amendment-history verification and release eligibility to remain false. It does not approve legal pins or create answer keys.
- Static inspection of the current dataset found 116 rows (58 formal, 58 colloquial), 58 distinct article IDs, and zero mismatches against the validator's safety invariants. This is not an executed test or legal-content review.
- The lawyer workflow is documented in `docs/legal_evidence/law14_2025_evaluation_review_guide.md`. Direct-main commits: `6445aa7`, `0e1be3b`, `332a390`, `07838b1`, `ea16242`, `4af16ba`, `40f8fd5`, `8fb6c2f`, `bb4b669`, `5c6d4b7`, `9d2170f`, `a90f246`, `f05145b`, `a964350`, `8ec24e2`, `26946aa`, `a224925`. Tests remain unexecuted.

## AI-1 test discovery registration — 2026-11-14

- Added explicit workflow steps for `test_validate_answer_ratings.py`, `test_adapt_answer_rating_export.py`, `test_validate_law14_eval_draft.py`, `test_negation_guard_repro.py`, and `test_firm_test_source_matched_mode.py`.
- Static workflow inspection confirms all five filenames are invoked by `.github/workflows/tests.yml`; no tests were run. Direct-main commits: `da160ea`, `0cda7a9`, `e406bed`.

## Answer-rating contract integration boundary — 2026-11-14

- Compared the canonical seven-column AI-1 contract with the richer AI-2 firm export contract. The firm export currently lacks `trust_tier`, uses `partially_correct` rather than `partial`, and permits `not_applicable` for cited-article accuracy.
- Added an explicit mapping in `docs/answer_rating_contract.md` and implemented `tools/adapt_answer_rating_export.py` with regression tests: map `partially_correct` to `partial`; never coerce `not_applicable`; derive rater from opaque `rated_by`; serialize the current rating's `updated_at` with timezone; and add message-time trust tier from saved answer metadata. Rich benchmark columns remain in the firm export.
- AI-1 contract is complete; AI-2 export adapter remains open until trust tier is exported and enum handling is implemented. Direct-main commits: `2b887ad`, `5a8e953`, `019ae2e`, `cd63439`, `8be387e`, `b8d3bad`, `6ced6d1`, `3af8468`, `69fb3dc`, `31f8be0`, `68ca68d`, `f4376e4`, `974efcb`, `800fcbd`, `ed13251`. Adapter/validator tests remain unexecuted.

## Recent AI-1 and Legal Research integration

- #1576 — merged fixture corrections for the Gazette importer and Arabic retrieval scorer.
- #1577 — merged AWS/GCP signed-URL companion-parameter rejection.
- #1578 — superseded by current-main PR #1584 and closed; the replacement adds provenance control-character rejection and requires any explicitly supplied `source_reference` to be a non-empty string.
- #1580 — merged retrieval-evaluator malformed-enum and ambiguous evidence-URL validation.
- #1581 — merged fail-closed device-acceptance metadata validation.
- #1582 — merged the Figma-aligned Legal Research/Document Intelligence workspace onto current `main`, preserving the 18 newer main commits by carrying only the 16 changed files. The older #1564 branch was closed as superseded.
- #1583 — merged retrieval scorer rejection of non-object question/run rows.
- #1584 — merged Gazette provenance metadata hardening on current `main`.
- #1558 and #1543 — closed as superseded by #1582; their relevant classification/document-intelligence work is included in the integrated workspace.
- #1561 is closed after confirming the narrow guard is called in `app.ask` and merging #1588 service-path regressions for Arabic polarity reversal, faithful negative wording, and unrelated obligation clauses. Runtime tests remain unexecuted.

All of these merges are source-reviewed code integration only. Their tests remain unexecuted unless an explicit runtime result is recorded; do not infer passing tests from a successful merge.

## Next execution order
1. Finish static audits and close deterministic importer/scorer defects that have bounded acceptance criteria.
2. Complete focused unit tests and docs for those changes; keep each direct-main commit small and isolated while the owner-authorized GitHub billing workaround remains active.
3. Hand off any live answer-path, billing, database, tenant, UI or deployment change to AI-2.
4. Use the repository administrator's supported local Python 3.12 runner for dependency-lock verification, adversarial security tests and production acceptance; AI-1 reviews concrete failures.
5. Do not tune `MIN_SCORE`, publish retrieval quality scores, or mark legal sources verified until approved labels/source evidence exist.


## Release-gate benchmark inventory follow-up — 2026-11-13

- The default `tools/production_release_gate.py` benchmark is `tests/legal_eval/multi_area_questions.draft.jsonl`. Its draft inventory previously contained 94 questions, below the gate's configured minimum of 100 even before counsel review.
- The inventory and lawyer worksheet have been expanded to 100 questions across the same ten practice areas. This removes the structural count shortfall only; all 100 remain unreviewed and cannot satisfy the release gate until counsel supplies approved answers, dates, source/pin citations and reviewer evidence.
- Repository administrator/local Python 3.12 runner must execute the focused inventory/retrieval tests and full suite in the clean Python 3.12 locked environment. This branch has not been runtime-tested.


## Evaluation inventory distinction — 2026-11-13

- The production release gate consumes the separate 100-row `multi_area_questions.draft.jsonl` queue (PR #1573), not the 120-row general-plus-labour inventory.
- The 120 rows are 59 general seed questions plus 61 Labour Law draft questions. The 58-row `labour_law_14_2025_provisional_review_questions.draft.jsonl` is another separate provisional review queue. File counts can overlap; they are not a deduplicated unique-question total.
- The release-gate queue now meets its structural 100-row minimum, but still has zero lawyer-approved questions. The 100-approved-question release criterion, 10-practice-area coverage from reviewed rows, answer keys, source/pin-cite checks and approved reviewer evidence remain external counsel-dependent blockers.


## Current AI-1 PR validation checkpoint — 2026-11-13

- #1576 head `81f90fc13b9843df7f4af5e1ebb7b5441153927f`: Tests workflow run `43325788669` failed before exposing any job steps (`steps: null`).
- #1577 head `a745b35913e155c3608c86ebab4e763dac285500`: Tests workflow run `43326626506` failed before exposing any job steps (`steps: null`).
- #1578 head `89e5bdac8fa1f11571bf70b1087b7a6ae56b89ad`: Tests workflow run `43327265469` failed before exposing any job steps (`steps: null`).
- These are runner/service execution failures, not code-test failures or passes. Local Python 3.12 hash-locked validation is the next usable path.
- During static review of #1578, explicit `source_reference: null` was found to bypass the stated non-empty-string rule. The PR branch was corrected and a regression case added; the revised head has not been runtime-tested.
- Merge order remains #1577 before #1578. #1576 is independent. Do not merge these as validated until the focused Python 3.12 tests execute successfully.


## Retrieval evaluator malformed-enum follow-up — 2026-11-13

- PR #1580 guards untrusted `review_status` and `reviewer_role` JSON values before set membership. Malformed list/object values now enter the evaluator's invalid-question report rather than raising `TypeError`. It also rejects raw backslashes and empty query/fragment delimiters in reviewer evidence URLs.
- Regression tests cover unhashable list values for both fields. Static source/diff review only; runtime tests remain unexecuted.
- Latest exact-head Tests workflow run `43328429442` (head `53eed6cfa7ab6601f6cdd13b4c362a25c6095f7f`) failed before exposing job steps (`steps: null`), consistent with the current runner-allocation blocker. An earlier head's run `43328171760` had the same result.


## Merge checkpoint — 2026-11-13 (current main)

- Merged #1577, #1576, #1580, #1582, #1584, #1583 and #1581. The large Legal Research redesign was rebased at file level onto current main: its old branch was 306 commits ahead and 18 behind; the replacement branch had 0 commits behind and retained newer main-side evaluation/importer work.
- Closed superseded drafts #1578, #1564, #1558 and #1543. #1578's remaining provenance hardening was recreated as #1584 and merged.
- No GitHub Actions test execution or browser acceptance is claimed. The Actions runner/billing issue still prevents jobs from exposing executable steps. Run focused importer, retrieval scorer/evaluator, device acceptance, document classification, app runtime, export and frontend contract tests in the clean Python 3.12 hash-locked environment when available.
- Legal Research implementation is merged, but browser acceptance (Arabic RTL, English LTR, keyboard-only, mobile/desktop), end-to-end PDF/DOCX upload/download/review, and adversarial tenant-isolation checks remain open.


## Current-main implementation progress — 2026-11-13

| Workstream | Repository implementation | Validation / acceptance | Overall status |
|---|---:|---:|---:|
| Figma-aligned Legal Research UI and application shell | 100% merged (#1582) | Browser/RTL/LTR/accessibility QA not run | 80% |
| PDF/DOCX upload, accessible document library, metadata and Arabic/English text search | 100% merged (#1582) | End-to-end upload/download and adversarial tenant checks not run | 80% |
| Persistent classification, audit history, extraction review and literal multi-hunk correction comparison | 100% merged (#1582/#1591) | Python 3.12 integration tests and browser review flow not run | 85% |
| Cross-document version comparison API and Documents workspace integration | 100% merged (#1592) | Matter-scope/page-provenance runtime tests and browser acceptance not run | 80% |
| Gazette importer and provenance hardening | 100% merged (#1576/#1577/#1584) | Focused Python 3.12 tests not run | 80% |
| Retrieval scorer/evaluator and device-evidence input hardening | 100% merged (#1580/#1581/#1583) | Focused Python 3.12 tests not run | 80% |
| Live Arabic/English negated-obligation guard | Runtime call site confirmed; Arabic service-path tests merged (#1588) | Tests not run | 85% |
| Structured candidate extraction (labelled entities, bilingual case/legal references, event mentions, explicit relationships, date and amount candidates) | 100% merged (#1594/#1600/#1602/#1603/#1604/#1606/#1608) | Helper/API/browser tests not run; limited deterministic rules; official-law verification remains external | 88% |
| Matter-wide date/event mention timeline | 100% merged (#1596) | API/browser acceptance and tenant-scope runtime checks not run | 80% |
| Cross-document exact repeated-mention grouping | 100% merged (#1598) | Exact-match groups require human review; no identity resolution; tests/browser not run | 70% |
| Advanced multi-document synthesis and cross-document entity resolution | Not implemented | Requires evidence conflict model, provenance policy and counsel evaluation | 20% |
| Full Arabic RTL/LTR, keyboard, mobile/desktop acceptance | Not complete | Requires browser/device execution | 0% |
| CI / clean Python 3.12 suite | Not complete | Runner/billing allocation prevents hosted jobs; local execution not available in this session | 0% |
| Adversarial tenant-isolation and backup/restore acceptance | Foundations and targeted tests exist | Full cross-firm route/job/export/search and witnessed restore remain | 40% |
| Payment-provider and paid-pilot acceptance | Existing billing UI/API foundations | Provider sandbox, webhook, real-firm and revenue evidence remain | 30% |
| Egyptian-law source verification and counsel sign-off | Review inventories and tooling exist | Qualified counsel and authenticated Gazette evidence required | 0% |

Percentages distinguish repository implementation from validation and operational acceptance. A merged PR is not a test pass or production-readiness certification.


## Follow-up hardening — 2026-11-13

- #1588 merged Arabic service-path tests for the live negated-obligation guard; issue #1561 is closed. The tests are committed but not executed.
- #1589 merged an additional explicit-source-reference validation check; #1590 then removed a duplicate earlier check, retaining one fail-closed validation point. The importer still rejects explicitly supplied null/empty/non-string references even when a valid source URL exists.
- Neither merge establishes a passing test result. Focused Python 3.12 execution remains blocked by unavailable hosted runners and was not run locally in this session.


## Document review comparison integration — 2026-11-13

- PR #1591 exposes bounded multi-hunk literal comparison for corrected extraction passages in the authorized chunk API and review UI. Each hunk shows before/after text and an explicit lawyer-review requirement; oversized comparisons fail closed with a warning.
- The uploaded original remains unchanged. This is a transcription-difference view, not semantic legal analysis or a finding that the correction is accurate.
- Runtime and frontend contract tests were added but not executed because hosted runner/billing allocation remains blocked.

## Cross-document version comparison — 2026-11-13 (merged #1592)

- Added `GET /documents/compare` for two document IDs within one authorized matter. It verifies both document records against the selected case and active firm; cross-matter/missing IDs return the same 404 response.
- Text is assembled in stored chunk order with source chunk IDs, references, page numbers and character offsets. Each version is bounded to 100,000 characters; the shared helper caps output at 200 literal change hunks.
- The Documents workspace now uses the server comparison endpoint and renders each before/after hunk, both versions' source-chunk/page references, and an explicit lawyer-review warning. It no longer presents a local first/last-difference approximation as the comparison result.
- Added separate-database runtime coverage for a real two-document comparison, page provenance, cross-matter denial and same-document rejection, plus frontend contract assertions.
- PR #1592 merged at `531315955078fb01febfc6f36c61a0fa09edd6e9`. Static source/diff review only; no Python tests or browser execution has run. Merge is code integration, not a passing test or production acceptance.

## Structured entity, event and relationship candidates — 2026-11-13 (merged #1594)

- Added bounded bilingual rule-based structuring for labelled-party and literal identifier/amount/date entities, event triggers with same-sentence date/party mentions, and explicit Arabic/English relationship phrases.
- Integrated results into the authorized document-chunk API with document/chunk/page provenance and per-kind caps; the Legal Research UI now renders separate candidate cards and warnings.
- Added helper, separate-database API and frontend contract regressions. PR #1594 merged at `600dea925d95f8bccdec79dad9157a4aec78a1e0`. No tests or browser runs were executed because hosted runner/billing allocation remains blocked.
- This is not general NER, entity resolution, event verification, or a legal relationship conclusion. All records remain unverified candidates; OCR/extraction errors may propagate.

## Matter-wide date and event mention timeline — 2026-11-13 (merged #1596)

- Added an authorized case-scoped endpoint that aggregates date and event mentions across documents in the selected matter only, preserving document/chunk/page provenance and source offsets.
- Caps: 200 documents, one million extracted characters, 1,000 date mentions and 500 event candidates. Every view records a security audit event.
- The Documents workspace can request the matter-wide index and displays parseable dates, unparsed dates and same-sentence event mentions. It explicitly warns that this is not a verified chronology and creates no deadlines.
- Added helper, separate-database runtime and frontend contract tests. PR #1596 merged at `27409eedaa042c3b54abdb4fe547ce396751c5b4`. No tests or browser execution were run because hosted runner/billing allocation remains blocked.

## Cross-document repeated-mention index — 2026-11-13 (merged #1598)

- Added exact normalized mention grouping for labelled parties and case/legal references within one authorized matter. Matching is limited to Unicode NFKC, case-folding and whitespace collapse; no fuzzy or semantic identity resolution is attempted.
- Added a matter-authorized API and UI action, with member-level document/chunk/page provenance, 200-document/one-million-character/1,000-candidate/500-group bounds and audit logging.
- Same-firm nonmembers are denied by the matter authorization gate. Added helper, API, authorization and frontend contract tests; PR #1598 merged at `5d4b9516cfdebe13d5c99053a50145e968e39ea0`. None were executed because hosted runners remain unavailable.
- All groups are possible repeated mentions only, not proof of identity, common ownership or legal relationship.

## Arabic/English named-month date extraction — 2026-11-13 (merged #1602)

- Added named Gregorian month recognition for Arabic and English day-first/month-first date mentions, including Arabic-Indic digits, to the shared extraction and matter timeline helper.
- Valid four-digit-year dates are normalized; ambiguous two-digit years and invalid calendar dates remain unparsed. Hijri conversion is explicitly unsupported.
- PR #1602 merged at `f7f9f2e083f700d81f8ad0c6cac584ff19f5035b`. Helper regression coverage is present; tests/browser acceptance remain unexecuted, so merge is not a test pass.


## Open pull requests reviewed — 2026-11-13

- #1610 (AI-2 workspace UX) remains draft. It is not 100%: the PR reports no confirmed green Actions run, no full local suite, and outstanding responsive RTL/LTR, accessibility and lawyer usability acceptance. Keep validation with AI-2 and the repository administrator/local runner; do not merge based on the static catalog scan.
- #1607 (Labour Decisions 248–252/2026) is correctly metadata-only. The source PDF is permission-restricted and operative text is unavailable; no repository-only action can close the legal-content/currentness gate. Leave quarantined and retrieval-ineligible.
- #1490 (boto3 Dependabot) remains blocked on a matching Python 3.12 hash lock and clean installation. Do not merge the requirements-only change.
- The user's uploaded patch bundle 0002–0009 maps to capabilities already present on current `main` (comparison, catalog, evaluation drafts, manual capture, deadline calculator, article-row audit, CI coverage guard and safe validation errors). Reapplication would duplicate existing work. Focus on the remaining validation/acceptance evidence instead.


## Exact-head runner evidence — 2026-11-13 (#1610)

- Workspace PR head: `fc5e6e99716fb7fbcada8b2ac5b93a3d62ebca5f`.
- Latest associated workflows: Browser acceptance `43502036586`, Tests `43502036507`, Non-database safety regression `43502036492`, CodeQL `43502036375`, and dependency audit `43502036312`; all concluded `failure`.
- Inspected all six jobs across those runs through the GitHub Actions jobs API. Every job reported `runner_id=0`, an empty runner name, and an empty `steps` array; jobs completed within roughly two seconds. No test, browser, Bandit, CodeQL, or dependency-audit step is evidenced as having executed.
- This is runner-allocation/service evidence, not a code-test failure or pass. Do not repeat the same workflow reruns until runner availability changes. PR #1610 remains draft and still requires product-owned responsive RTL/LTR, accessibility, and lawyer-workflow acceptance.


## Legal evidence URL control-character parity — 2026-11-13

- PR #1616 merged at `bcdfc516d167a6e8ef342964b124e222433eb572`. Both `tools/validate_legal_release_readiness.py` and `tools/validate_source_permission_register.py` now reject DEL (0x7F) and raw backslashes in HTTPS evidence URLs; focused regression fixtures cover both cases.
- Static source and diff review only. Tests remain unexecuted under the current pause on test runs. Do not count this as runtime validation or legal-source verification.


## Remaining legal evidence URL validator parity — 2026-11-13

- PR #1617 merged at `e7f3fcd781bc7370842f3ce6d55edd2f664da54e`. Acquisition readiness (direct and scope-review evidence), legal source review queue, legal corpus audit, amendment relationship validation, and corpus inventory URL helpers now reject DEL (0x7F) and raw backslashes. Regression fixtures were added for each affected path.
- Source/diff review only; tests remain unexecuted under the current test-run pause. No runtime pass or legal verification is claimed.


## Answer rating contract — 2026-11-14

- **Closed for AI-1:** `docs/answer_rating_contract.md` is present on main (commit `8820ea617c5bb8fcbf72bb77e7470a9828fe4a44`). It defines answer ID, correct/partial/wrong, cited-article right/wrong, notes, rater, ISO-8601 timestamp, trust tier, and UTF-8 CSV export. `tools/validate_answer_ratings.py` validates exported CSV headers, required fields, enum values and timezone-aware timestamps. AI-2 can integrate against this contract. This does not approve any legal source or rating data.


## AI-1 owner checklist — 2026-11-13

| Deliverable | Current status | Closure boundary |
|---|---|---|
| Answer rating contract | Complete on main; AI-2 handoff ready | Contract exists at `docs/answer_rating_contract.md`; `tools/validate_answer_ratings.py` and its regression tests provide a UTF-8 CSV validator. The firm export is implemented but does not yet include the canonical `trust_tier` field; its `partially_correct` and `not_applicable` enums also require the documented adapter. AI-2 UI/export integration is therefore not fully closed. |
| Three negation regressions | Guard integrated in `app.ask()`; focused reproduction/integration tests committed directly to main (`92e5177`, `f988e76`) | Still open until the exact Python 3.12 local command is executed and output is recorded. |
| Firm-test source-matched mode | Fail-closed response gate and explicit `source-matched, not lawyer-verified` answer label committed directly to main (`ce2ebc8`, `7c5e09d`, `5ec22a1`, `b377af0`, `311287d`, `2009b9f`, `29e4a13`); candidate retrieval remains intentionally disabled | Synthetic test path only. The actual Law 14/2025 candidate remains ineligible because collection/reuse permission is unknown, source text is not committed, and the manifest says search_eligible=false. |
| Reviewer CSVs | Complete as templates | Gazette 311-row CSV includes all machine comparison classifications, similarity and page locators plus prior page-review notes; our-text/Gazette-text cells and lawyer decisions remain blank pending authorized text. Five-rule deadline CSV and one-page UTF-8 guide exist. |
| Law 14/2025 evaluation drafts | 116 unique question drafts created (58 formal, 58 colloquial); article IDs machine-proposed and unapproved | Structural validator and lawyer review guide added. Static inventory inspection found 116 rows, 58 distinct proposed article pins, 58 formal/58 colloquial questions and zero article-ID/status invariant mismatches; tests remain unexecuted. Do not treat article labels as ground truth or run the reviewed scorer on these rows. |
| Retrieval baseline | Blocked | Existing scorer requires lawyer-approved labels, reviewer registry and actual retrieval results. No authenticated local indexed corpus/API is available here. `docs/legal_evidence/law14_2025_retrieval_baseline_unreviewed.json` records 116 questions, zero approved labels, zero run records and null metrics; null is not zero or a measured baseline. |
| Status documentation | Complete | Detailed history copied to `docs/archive/STATUS_history_through_2026-11-13.md`; `docs/STATUS.md` is now the concise release-candidate summary. |

The owner has explicitly requested a non-production firm-test implementation. That instruction authorizes the isolated feature work only; it does not grant source reuse rights, lawyer approval, currentness certification, or permission to enable source-matched answers in production. All Law 14/2025 `verified` flags remain 0.

- Negation follow-up: an isolated local harness using the current helper logic returned PASS for the three original English/Arabic reversal cases. This is not the repository unittest run or app.ask integration result; The direct-main tests remain unexecuted pending a supported Python 3.12 runtime.

- Firm-test scope clarification: The direct-main synthetic tests inject a source-matched hit into `app.ask()`; the `firm_test_source_matched` search scope currently returns no candidates. A separate permission-cleared candidate retrieval adapter is still required, and the current Law 14/2025 candidate is not eligible due unknown reuse permissions. This is not a completed Law 14/2025 serving path.


## Database acceptance manifest parser hardening — 2026-11-14

- The loader caps the bytes actually read at 1 MB, preventing a concurrent file-growth race after the initial metadata check.
- Invalid UTF-8, malformed JSON, duplicate keys and excessive JSON nesting now fail closed with a generic manifest blocker. Added regressions for invalid encoding and deeply nested input; repository tests remain unexecuted.


## Acceptance evidence input hardening — 2026-11-14

- Database operational manifests now use a bounded binary read tied to the pre-open file identity; they reject symlink/special-file inputs, concurrent path replacement, payloads over 1 MB, invalid UTF-8, duplicate object keys and excessive JSON nesting. Valid JSON remains decoded from bytes before parsing.
- Device/browser evidence input now uses a stable regular-file descriptor, rejects symlink/special-file inputs, caps the read at 5 MB, rejects invalid UTF-8 and converts excessive JSON/JSONL nesting into a fail-closed evidence error. Existing duplicate-key rejection remains active for JSON and JSONL.
- Added focused regressions for valid and invalid manifest encoding, deep nesting, manifest path replacement, and device evidence symlink/FIFO/size/encoding/nesting cases. These tests are committed but unexecuted; no validation pass is claimed.


## AI-2 Arabic-first workspace PR #1610 and session-state reset — 2026-11-14

- File-level comparison shows PR #1610 is divergent from main (218 ahead / 527 behind at review time) and changes four files. Its `static/index.html` diff deletes the answer-rating panel and save/load controls, a regression against the mainline answer-rating API/UI contract and frontend regression test. Do not merge or cherry-pick wholesale; revisit only isolated improvements after a current-main rebase and explicit preservation tests.
- Fixed stale one-shot matter/document/chunk review targets surviving session expiry and both ordinary/MFA firm switches. Regression contract committed; static review only, with test execution and browser acceptance still open.
- PR #1610 validation evidence does not show executed test or browser steps. The application remains NOT READY for pilot or production.


## Evaluator JSON ambiguity hardening — 2026-11-14

- The approved-question/result JSONL parser and reviewer-registry JSON loader now reject duplicate object keys at every nesting depth. Previously, Python's default JSON decoder silently retained the last duplicate value, allowing ambiguous evaluation labels or reviewer metadata.
- Added regressions for top-level and nested JSONL duplicates, valid distinct nested keys, and duplicate reviewer-registry keys. The test module is registered in the Tests workflow.
- Static source review only; these tests were not executed because hosted runner allocation remains unavailable. No evaluation metric or legal approval status changed.


## Manual-capture provenance JSON ambiguity hardening — 2026-11-14

- The read-only manual-capture validator now rejects duplicate JSON object keys at every nesting depth instead of silently accepting Python's last-key-wins behavior. Conflicting permission/provenance fields therefore fail closed.
- Added CLI regressions for duplicate top-level and nested keys; the test module is registered in the Tests workflow.
- Static source review only; no test execution is claimed. No permission state or legal verification flag changed.


## Fake billing-provider idempotency boundary — 2026-11-14

- The in-memory `FakeBillingProvider` now returns the original request for an identical merchant-reference retry and rejects reuse of the reference with a changed amount, currency or metadata. Added regression contracts.
- This closes only the fake-provider request-creation contract; it is not a live gateway, webhook, signature, refund, settlement or reconciliation implementation.
- Tests are registered but unexecuted while GitHub Actions runner allocation/billing is unavailable. Live billing remains blocked on provider/merchant selection, operator-owned sandbox credentials and end-to-end provider acceptance evidence.

## Manual-capture evidence URL policy alignment — 2026-11-14

- The local provenance validator now applies the same fail-closed evidence URL shape rules as the legal candidate/source checks: fragments, empty user-info, signed/credential query parameters, malformed ports, raw backslashes, whitespace and controls are rejected.
- Added URL-shape regressions for source, terms and both permission-evidence URL fields. Tests remain unexecuted; no permission decision is inferred from URL validity.


## Client-profile required-field accessibility — 2026-11-14

- New/edit client-profile dialogs now associate the required client-name control with a bilingual inline alert, set/clear `aria-invalid` during validation/correction, and keep the alert separate from the label. A frontend regression contract is committed and registered through the existing UX test workflow.
- Static source/contract/workflow inspection only. No test or browser execution is claimed; remaining form-by-form error review and manual screen-reader acceptance are still open.


## Product-feedback form accessibility — 2026-11-14

- Feedback title/details now have persistent bilingual labels and inline validation descriptions linked through `aria-describedby`, with `aria-invalid` set on native invalid events and cleared after correction. A frontend contract test was added to the existing workflow.
- Static review only; no test/browser execution. This closes the bounded feedback-form implementation, not the remaining form audit or manual accessibility acceptance.


## Account and invitation field labels — 2026-11-14

- Current/new/confirm password fields and firm-invitation email now have persistent bilingual labels rather than relying on placeholders. A frontend regression contract is committed in the existing UX test module.
- Static review only; tests and screen-reader/browser acceptance remain unexecuted. The bounded labeling change is complete; the broader form audit remains open.


## Matter-search document provenance hand-off — 2026-11-14

- Integrated the backend-only part of the workspace PR's retrieval enhancement: firm hits now carry document/chunk identity, filename, SHA-256, extraction/OCR state and ready/non-purged original availability, using document/case/firm-scoped joins. Added false/true retention-path regressions and updated the source-inspector contract.
- This does not merge PR #1610 or its UI diff. PR #1610 is still draft and now compares as 218 commits ahead / 483 behind; its branch `static/index.html` still lacks the answer-rating UI present on main. No wholesale merge or stale UI transplant is safe.
- Static review only. The separate-runtime route tests and browser hand-off were not executed because runner allocation/billing remains blocked.


## Source-inspector matter hand-off — 2026-11-14

- The inspector now shows backend-supplied firm-document provenance and offers exact-chunk navigation when a valid chunk ID is returned, falling back to a matter-level Documents hand-off otherwise. It does not treat original availability as download authorization.
- Frontend regression contract is committed and workflow-registered. Static source review only; browser and test execution remain unavailable. Answer-rating controls remain on main and were not removed.


- A static follow-up corrected the settings label element construction (`1714b2a109400807f598cf51aaeeb46fd4cee46f`). The JavaScript syntax workflow check remains unexecuted under the runner pause.


## Exact research-passage navigation — 2026-11-14

- The inspector now hands a matter/document/chunk identity into the matter Documents view, auto-expands the matching extraction panel, and focuses/scrolls to the exact chunk when present. One-shot state is cleared on missing document/chunk, failed load, panel close, manual section navigation, firm switch and session expiry. No passage-level claim is made when the chunk ID is absent.
- Static source and regression-contract inspection only. Browser interaction, keyboard focus behavior and screen-reader acceptance remain blocked by unavailable runner/browser validation.


## Extracted page-reference caveat — 2026-11-14

- The extraction review now explicitly states in Arabic and English that a recorded extracted page reference has not been independently checked against the original file. A workflow-registered frontend contract protects the warning.
- Static inspection only. Actual browser/screen-reader review and lawyer verification of page locations remain outstanding.


## AI-2 identity throttle privacy and route authorization guards — 2026-11-15

- Production login-attempt identifiers, account-recovery email/IP identifiers, and configured API middleware IP rate-limit keys now use purpose-separated HMAC-SHA-256 with the dedicated `COPILOT_IDENTITY_RATE_LIMIT_KEY`. Production/staging login and API throttling fail closed if the key is absent or invalid; recovery throttling also fails closed. Firm scoping and the distinct 5-attempt email / 20-attempt IP lockout thresholds are preserved.
- Added regressions for login/recovery pseudonymization, cross-worker lockout state, production missing-key behavior, API middleware HMAC storage, and the preserved IP threshold. Updated production environment/deployment/tenant-isolation guidance.
- Added an AST-based authentication dependency inventory across `app.py` and mounted platform/identity routers, with an exact 12-route public allowlist and fail-closed discovery for new router modules. Added source-level case-ID and document-ID route guard regressions and registered the auth audit in CI and the focused security matrix. Added firm/document/case filters and fail-closed integrity validation to original-file export, with a corruption fixture that bypasses the database trigger and confirms no successful export audit is emitted.
- Source/test/documentation changes are committed to `main`; **no tests or audits were executed** because GitHub runner billing remains unavailable. These guards do not prove role authorization, every SQL predicate, browser behavior, or live operational acceptance. Do not treat them as release approval.

## AI-1 follow-up hardening — 2026-11-16
- Candidate registration now validates the complete record before writes, rejects malformed/unhashable review enums and whitespace/case-obfuscated permission grants, commits successful registrations, and rolls back late conflicts atomically. Re-registration preserves existing counsel review decisions instead of adding a fresh pending event. The legacy bulk seeder now checks identity conflicts and preserves restrictive rights decisions instead of silently ignoring conflicts. Regressions are registered; none were executed.
- The document collector's JSONL append now uses no-follow/nonblocking open semantics and checks the opened inode is a single-link regular file still bound to the requested path. A hardlink alias regression is registered but unexecuted.
- AWS/GCP signed-link parameter rejection is now consistent across manual capture, candidate registration, source review, capture-record validation and the canonical source-permission register. These URL checks establish locator hygiene only; they do not prove source authenticity, public availability or reuse rights.
- The general reviewed retrieval evaluator exposes wrong-article rate/count/denominator globally and per practice area, with explicit pin-cite precision semantics. The article-level scorer already reports the benchmark's wrong-article answer rate and target.
- Local execution attempt: a shallow Git clone could not resolve github.com from this environment. No repository test modules were executed. GitHub Actions latest exact-head jobs continue to fail with runner_id=0 and zero steps; this is infrastructure allocation failure, not test evidence.

- Exact-head runner recheck after AI-1 follow-up commits: main `a202cc6bee4bb6de192feaa57d0206c1c27409f4`; Tests run `43948912741` and Browser acceptance `43948912737` each failed with a single job reporting `runner_id=0` and zero steps. CodeQL `43948912966` has zero-step jobs (one job not yet allocated); dependency audit `43948912813` returned no jobs at inspection. This is not test execution and does not establish code failure/pass.

## Source-matched status gate — 2026-11-23

- Draft PR [#1902](https://github.com/abdelmalek384/legal_copilot_latest/pull/1902) adds a distinct `source_matched_unreviewed` status for the isolated non-production test scope.
- The status requires the evidence package and permission gates already used by the answer trust-tier classifier. It now also binds the provenance `source_id` and `version_id` to the exact retrieved corpus row; evidence from a different source/version is rejected. Any recorded lawyer-approval event, failed review event, or malformed review record leaves this machine-only status and requires review.
- Focused regression cases cover missing/incomplete evidence, original-capture hash mismatch, permission loss, source/version mismatch, future effective dates, secondary material, lawyer decisions, and attempts to set `verified=true`.
- **Still blocked:** `app.search(..., scope="firm_test_source_matched")` intentionally returns no candidates; the corpus schema/adapter does not yet expose a version-bound `source_match_evidence` package to the search path. AI-2 integration is tracked in [issue #1903](https://github.com/abdelmalek384/legal_copilot_latest/issues/1903). Law 14/2025 remains ineligible while reuse rights are unknown.
- The tests are registered in the existing Python 3.12 workflow but have not been executed in this session. No test pass, lawyer review, verified status, or pilot acceptance is claimed.



## Manual checkpoint — 24 Nov 2026 (GitHub billing unavailable)

- GitHub Actions results are not available for validation in this checkpoint; the repository commit queried returned no workflow runs. Do not treat that as a pass.
- The dependency-update PRs #1873 (FastAPI), #1874 (python-multipart), #1876 (boto3), and #1877 (pypdf) remain open. Each proposes a direct requirement change only. The checked-in Python 3.12 hash lock was not regenerated and the README explicitly records the current Boto3/Botocore pin. These upgrades are **not applied to main** to avoid breaking hash-lock consistency or claiming untested dependency resolution.
- Draft AI-2 PRs #1911 and #1912 are closed unmerged. They are intentionally not considered complete: exact-head Python tests, migration rehearsal, browser acceptance, and two-firm/two-matter authorization acceptance are still missing.
- Direct-main dependency consistency is preserved: `requirements.txt` remains at the versions corresponding to the checked-in lock. No tests, deployment checks, accessibility acceptance, or legal validation are claimed as executed.
- Next unblocked work: audit and improve source-register metadata/validators, small static test contracts, and release documentation without adding legal text to the production retrieval corpus or marking any sources lawyer-verified.


## Manual checkpoint — 2026-11-24 (billing-blocked CI)

- GitHub Actions execution is unavailable because of the billing issue. No CI/test results are inferred or claimed; validation must be performed locally or through another authorized runtime before merge/release decisions.
- Re-read `docs/source_permission_register.json` and counted 199 records. Source IDs are non-empty and unique (199/199). Collection permission states: unknown 186, not_allowed_without_explicit_exception_or_license 9, allowed_limited 4. Commercial reuse states: unknown 185, prior_written_permission_required_per_published_terms 7, not_allowed_without_explicit_exception_or_license 3, allowed_limited 4.
- The 4 limited-permission records are not promoted to unrestricted permissions. No legal content or source rights were upgraded. This is a static inventory count only; the existing validator and regression suite were not executed in this environment.
- Dependency PRs remain deferred until the hash-locked Python 3.12 requirements file can be regenerated and a clean install/test/audit can run. Do not merge based on version-only edits.
- Next available in-repository work: document actionable, non-CI release checks and maintain accurate owner/evidence status; avoid retrying blocked GitHub Actions or the closed AI-2 draft PRs.

## Draft PR cleanup — 2026-11-24

- Closed draft PRs #1913, #1918, #1921 and #1929 unmerged after manual patch review.
- #1913's validator change is narrow but its focused Python regression and validator were not executed.
- #1918, #1921 and #1929 modify the AI-2 matter-document frontend. Their branches were not mergeable in all cases and their frontend Python/browser acceptance was not run; V8 parsing/static assertions are insufficient to establish safe behavior.
- Branches are preserved. None of these changes is present on `main`; no feature/security claim should be made as if integrated.
- Open PRs should remain at zero. Re-open only after exact-head tests and the relevant browser/two-firm acceptance can be run.


## Browser inline-script parse failure diagnostics — 2026-11-26

- `tests/browser/test_acceptance.py` now preserves the full JavaScript `pageerror` stack (`c1d51ca`). The previous listener retained only the error message and dropped the source URL and line/column details needed to pinpoint the inline-script parse failure.
- The current `static/index.html` inline script still fails V8 compilation with `SyntaxError: missing ) after argument list`; inspected historical mainline snapshots also fail. No speculative source edit was made without a parser location.
- This is diagnostic instrumentation only, not a browser fix. Run browser acceptance in the supported runtime, capture the stack location, and fix the exact syntax defect. No test execution is claimed.


## AI-2 document-panel JavaScript parse correction — 2026-11-26

- Current-main source review found that the existing case-document panel expression in `static/index.html` left the outer `body=h('div',...)` call unclosed after the upload row and retention note. Added the missing closing parenthesis in commit `5be1c592f12525be4e33a44b7ee077e314a91af3`.
- This is a narrow syntax correction to an existing document workflow; no feature or UI redesign was added. The prior browser diagnostic identified a JavaScript compilation failure, but this exact source correction has **not** yet been validated by Chromium, the repository browser suite, or the Python frontend contract suite in this environment. Do not mark browser acceptance passed until those tests execute on Python 3.12.
- Next acceptance: run `tests/browser/test_acceptance.py` and `tests/test_frontend_ux_contract.py` under the supported Python 3.12 environment; retain the full `pageerror` stack if any parse error remains.


## AI-2 local object publication rollback — 2026-11-26

- Source review found a partial-publication failure in `LocalPrivateObjectStore.finalize`: after creating the final hard link, a failure removing the staging name could leave both names linked to the same inode. The final object reader correctly rejects that two-link state, but the object could remain stuck until manual recovery.
- Updated `original_file_storage.py` to attempt a narrowly guarded rollback of the newly created final link only when both names still identify the original staged inode with the expected two-link count. Unexpected or changed filesystem state is left untouched for operator recovery.
- Added synthetic regression `test_finalize_rolls_back_final_link_when_staging_unlink_fails` in `tests/test_original_file_storage.py`. It injects a staging-unlink failure and asserts that the staged object remains intact, the final object is absent, and staged integrity verification still succeeds; it then retries finalization and verifies that the object becomes readable.
- Commits: `0dd2a8a` (implementation), `e9419d3` (initial regression), `6de1544` (retry/recovery assertion). GitHub read-back confirmed both changes are on `main`.
- Test execution: **not run** in this environment. The regression is authored, not passed. Run `python -m unittest tests.test_original_file_storage` under the supported Python 3.12 environment. No tenant-isolation or production-storage claim is made by this local-adapter correction.


## Candidate catalogue / canonical permission-register identity parity — 2026-11-26

- Static comparison found 21 discovery-catalog source IDs without canonical permission-register rows. The candidate seeder's permission-parity gate would reject the catalog; the existing regression requiring every candidate ID to have a register record would also fail.
- Reconciled by adding 21 source-family metadata rows to `docs/source_permission_register.json`. Every added row retains `collection_permission=unknown` and `commercial_reuse_permission=unknown`; source-page locators and access observations are copied from the existing candidate catalog only. No permission or legal verification was inferred.
- Candidate seeder now rejects surrounding whitespace and non-ASCII/delimiter characters in source/document identifiers; focused regression cases were added.
- Manual JSON/static read-back: 43 candidate sources and 548 document candidates; source IDs unique and present in the canonical register; source/document IDs conform to the bounded identifier contract. Python validator and test modules remain unexecuted. Do not describe these checks as a test pass.


## Candidate source-register parity follow-up — 2026-11-26

- Follow-up manual parity review identified two existing edge cases after the 21-row identity repair: the Egyptian Tax Authority's candidate locator uses an explicitly related `portal.eta.gov.eg` host while the canonical source record uses other ETA hosts; MKSEgypt's candidate record carried custom CC BY strings outside the seeder's accepted permission-state vocabulary while the canonical register correctly remained unknown.
- Added the ETA candidate PDF locator to the canonical record's `related_source_pages`; the parity validator now accepts only the canonical host or a clean HTTPS host explicitly listed in that field. Arbitrary host mismatches remain fail-closed.
- Reset the MKSEgypt candidate collection/commercial permission fields to `unknown`, retaining the observed CC BY notice as evidence but explicitly declining to infer bulk ingestion or unrestricted commercial rights.
- Manual read-back verified zero candidate/register parity mismatches, 43 unique candidate source IDs, 548 discovery-only document records, and 220 unique permission-register source IDs. No Python test or validator was executed.

- Follow-up test-fixture maintenance: updated adapter fakes to provide valid independent-copy identity/digest and positive evidence revision, ensuring existing approved-use and boolean-flag regressions still exercise their intended downstream checks after stricter packet-shape validation. Tests remain unexecuted.

- 2026-11-26 follow-up: retrieval previously nested the source-match packet under citation provenance while the firm-test preflight read only a top-level hit field. The source projection and preflight now carry/read the same packet without reconstructing it. Regression authored, not executed. Remaining: runtime verification of actual corpus search, exact-version DB adapter, answer abstention behavior, and counsel/legal review.

## AI-1 explicit test-mode policy approval boundary — 2026-11-26

- Source-matched test-mode answering now requires a distinct `LEGAL_FIRM_TEST_SOURCE_MATCHED_POLICY_APPROVED=1` environment setting in addition to the existing test environment, feature flag, and exact firm-ID gate. The previously implicit code-path policy approval is no longer enough to activate the answer tier.
- Updated the synthetic response-path regressions to model the explicit approval setting and added a fail-closed case when policy approval is absent. Regression files remain unexecuted; manual code review only.
- This is a test-only experimental tier; production remains blocked, and the approval flag does not establish legal correctness, rights, or readiness.


## AI-1 explicit policy-approval helper hardening — 2026-11-26

- Extracted the source-matched test policy-approval switch into a small fail-closed helper that accepts only mapping-like configuration and the trimmed string value `1`. Integers, booleans, nulls, malformed values, and non-mapping inputs are denied.
- Updated the application gate to call this helper and added synthetic malformed-setting regressions. Tests are authored, not executed; GitHub Actions are not run.
- This is defensive configuration parsing only; no source evidence, legal content, permissions, or production eligibility changed.
