# Legal Copilot status

**Updated:** 2026-11-12  
**Scope:** engineering and evidence status only; not legal-readiness or production certification.

## Current repository update — 2026-11-12

- Merged current-main PRs: #1470 (Gazette import, Arabic retrieval evaluation framework and negation guard), #1499 (document-intelligence helper foundation), #1495 (trusted-proxy/per-firm rate-limit hardening), #1500 (hybrid light Legal Research workspace), #1502 (local release/recovery tools), #1503 (temporary Mac preview), #1505 (LLM SSRF pinning and payment self-approval protection), #1506 (phone-width login readability), #1507 (cited negated-obligation guard), #1508 (matter-scoped Legal Research document workspace), #1509 (exclusive Gazette importer outputs), #1510 (Python 3.12 guard for local security regression matrix), #1511 (fail-closed local Bandit release gate), #1513 (approved reviewer registry gate for retrieval scoring), #1515 (browser setup-node v7 and optional OCR PyMuPDF minimum), #1517 (bounded server-side document classification/candidate analysis), #1518 (repeal-date schema validation in source review queue), #1519 (ambiguous Gazette source URL rejection), and #1520 (fail-closed handling of malformed release-gate enum values), #1522 (control-character rejection in legal corpus paths), #1523 (safe malformed source-permission states), #1524 (safe malformed Phase 2 inventory values), and #1530 (evaluation-runner response/question shape validation), #1532 (malformed retrieval-review enum handling), and #1533 (non-object evaluation API JSON-root rejection), #1535 (strict source URLs in the PDF/sidecar law importer), #1536 (exclusive, non-overwriting law-import outputs), and #1537 (fail-closed legal-status validation in the release source index), #1539 (strict lawyer-review evidence URLs), #1540 (DEL rejection in manual capture URLs), #1542 (strict manual-capture source URL validation), and #1544 (document-catalog structure and duplicate-ID validation), and #1546 (preserve reviewer metadata on manual-capture reruns), and #1548 (require 100 lawyer-approved benchmark questions for production release), and #1550 (write manual-capture originals immutably). Their merges are code integration only; hosted tests, physical-device acceptance, and witnessed backup/restore remain unproven because the repository's GitHub Actions billing/runner problem prevents test execution.
- Superseded drafts #1494, #1496, #1485 and #1483 were closed after current-main replacements or selective ports. Do not use their old branch heads.
- PRs #1500, #1507, #1508, #1509, #1510, #1511, #1513, #1515 and #1517 were merged after manual source review without treating billing-blocked Actions as passing tests. Exact-head tests for these changes have not been executed because the Actions billing/runner issue remains unresolved. PR #1513 now requires retrieval-scorer reviewer ID, display name, role and practice-area authorization to match the private approved reviewer registry; this is an administrative consistency check, not independent credential verification.
- The Legal Research workspace is available through the existing authenticated matter/document endpoints. PR #1517 connects the canonical Python helper to the existing firm-scoped chunks endpoint; classification suggestions and literal date/case/amount/party/legal-reference/event candidates are server-generated with 1,000,000-character and 250-candidate caps, provenance, and explicit unverified status. Draft classification overrides are still not persisted. Persistent classification/audit history, richer entity extraction, firm-wide search and multi-hunk comparison remain future work.
- Labour Law 14/2025 remains provisional and retrieval-ineligible pending qualified Egyptian counsel review, currentness/amendment/commencement checks, and source-rights review. No verified flags were changed.




## Latest engineering changes — 2026-11-12

- PR #1521 refreshes this status page to record the current merged work and the remaining Dependabot lockfile blocker.
- PR #1518 adds `repeal_date` to the source-review queue's required schema and tests the structured missing-column diagnostic. PR #1519 hardens the offline Gazette importer against whitespace/control characters and ambiguous URL authority/port forms. PR #1520 prevents malformed JSON enum values (lists/objects) from crashing the legal release-readiness audit; malformed values now produce existing fail-closed blockers.
- PRs #1518–#1520 and #1522–#1524 were manually diff-reviewed and merged. PRs #1530, #1532, #1533 and #1537 add evaluation/release-gate input-shape hardening; #1535 and #1536 harden law-source import URL validation and preserve prior import outputs; #1539, #1540 and #1542 harden evidence/source URL validation; #1544 validates catalog structure and duplicate identifiers; #1546 prevents manual-capture reruns from overwriting reviewer annotations; #1548 raises the production release benchmark minimum to 100 approved questions across at least 10 practice areas; #1550 writes originals through the immutable content-addressed writer and rejects conflicting existing bytes. Regression tests were added for these changes but not executed in this environment. Do not treat them as test passes.
- Open pull requests observed at this update: Dependabot #1490 and Legal Research document-intelligence update #1543. #1490 remains blocked until `requirements-py312.lock` is regenerated with the pinned Python 3.12 pip-tools workflow; the current main lock pins boto3/botocore 1.43.122. #1543 is an AI-2/product-workspace change and remains draft. Manual review found its new frontend contract test was placed after the module-level unittest guard, so normal discovery will not run it; the author was notified to move it into the test class and rebase onto current main. Evaluation-runner JSON-root validation from the conflicted #1529 branch was ported onto current main and merged as #1533; #1529 was closed as superseded.

## Current state

- Runtime uses separate control-plane, per-firm database and shared legal-corpus profiles.
- Labour Law 14/2025 PR #1451 is merged as a provisional source-comparison package. The exact 112-page user-supplied Gazette PDF and 311-row candidate JSONL were recovered from the Library source bundle; their SHA-256 values match the recorded comparison hashes. All 311 provisions now have page locators and recorded visual comparison notes (282 earlier checks plus 29 additional full-article page-image comparisons on 2026-11-06). Every lawyer decision remains blank and every `verified` value remains 0. The candidate JSONL's legacy metadata has `in_force=1` and `as_of=2025-05-03` on all rows; those fields are not a commencement/currentness determination and must not be treated as approval. The law remains non-authoritative and retrieval-ineligible pending qualified counsel review, source-rights review, currentness/amendment/corrigenda checks and commencement analysis.
- A lawyer-supplied UTF-8 Gazette text importer and article-number audit are prepared in the current work branch. The one-sitting procedure and metadata sidecar are in `docs/gazette_text_import_runbook.md` and `docs/templates/gazette_text_metadata.template.json`. An `allowed` collection-permission claim requires an evidence reference. Output rows retain structured supplier/capture provenance and remain `verified=0`, `in_force=0`, and `as_of=null`; database staging is a separate approved operation.
- The importer now separates Arabic-ordinal issuance provisions (`المادة الأولى`–`المادة الثالثة عشرة`) from numeric attached-law articles, excludes unparsed preamble from candidate rows, and reports preamble/numbering gaps. The new ordinal-path tests are present but not executed because CI jobs fail before their first step.
- The 110-question Arabic benchmark is a curated template, not production query data or observed user questions. All rows explicitly carry `question_origin=curated_candidate_not_user_observed`. It has 82 preliminary formal labels, 28 preliminary colloquial labels and 32 preliminary synonym tags; all remain unreviewed. The runner emits law-block-scoped article IDs and explicit source-trust status; the scorer rejects curated candidates and requires at least 100 observed-anonymized or reuse-permitted public questions with privacy approval, origin reference, collection date and consent/reuse basis, plus counsel-approved expected IDs/answers. It also requires at least 20 colloquial and 20 synonym questions, at least one reviewed unanswerable question with 100% abstention compliance, and blocks targets for wrong, uncited or unverified-source answers. No actual baseline run or before/after rates exist; `MIN_SCORE` remains 0.30 and must not be tuned yet.
- Five deadline rules and the holiday calendar remain unverified drafts. The counsel packet records the assumed periods/triggers and missing primary citations; no rule values were changed.
- Repository status previously recorded three PR #1404-area English/Arabic negated-obligation regressions still failing after three attempts. PR #1470 ports a raw-text guard and regression/control tests, and restores PR #1208 finite-period coverage including the `سنة` spelling. Direct smoke probes of the extracted negation helper caught all 6 positive/negative obligation reversals and passed all 4 faithful-negation controls; these are helper-level probes, not the integrated test suite. The negation guard also strips variable whitespace in Arabic negated-obligation phrases before classifying positive obligations; regression coverage now includes spaces and tabs. This change is not runtime-verified. The latest Actions attempt on code head `6a882d4457d7a5ad9da3eb64749aaa1dc5e1aaee` ran Tests and CodeQL workflows, but both failed before any execution step; all four jobs reported zero steps and GitHub reported `runner_id=0` with no runner name. This is a runner-allocation/infrastructure failure, not evidence of code-test failures or passes. The integrated suite remains unvalidated.
- PR #1470 merged on 2026-11-06 after manual source review. Its recorded zero-step Actions runs remain an unresolved validation gap, not a test pass. Stale drafts #1461 and #1464 were closed without merge.
- Exact-head CI recheck on `31336126193d8617ab635c203cae854e6d27db73` (2026-11-06): workflow runs `42185762958` (non-database safety), `42185763035` (dependency audit), `42185762872` (CodeQL), `42185762951` (browser acceptance), and `42185762881` (Tests) all concluded `failure`. GitHub returned one or more jobs per run, but the job-steps endpoint returned an empty step list for all seven jobs inspected. Therefore none of these failures establishes a code-level test result; the exact-head CI gate remains blocked before execution. Do not merge based on these runs.

An independent pilot security-review handoff is available at `docs/security/INDEPENDENT_REVIEW_HANDOFF.md`; it is a reviewer plan, not a completed penetration test or release approval.

## Human and release gates

1. Qualified Egyptian counsel signs the Law 14/2025 article-by-article tick-sheet and reviews currentness, source rights and effective dates.
2. Counsel labels expected articles, answers, answerability and question style/synonym tags for the Arabic benchmark.
3. Counsel approves or corrects each deadline rule and the applicable holiday calendar.
4. Run the Gazette importer against the lawyer-supplied text; review the report before separately approved staging.
5. Exact-head unit/integration tests, browser acceptance, Bandit, CodeQL and dependency audit must pass before merge or release claims.

## PR triage

- #1451 — merged; provisional evidence only.
- #1449 — closed: classifier/UI contract only; real answer-path serving remains blocked by the verified-source-only policy.
- #1212 — closed: limited seven-page/six-article spot-check retained as historical evidence; not a 311-row source verification.
- #1208 — closed as standalone; its finite-period lexical coverage and regression tests are carried into #1470.
- #840 — closed without merge after 74 issue comments: Decisions 248–252/2026 secondary transcription remains quarantined; Table 24 has 0/781 official matches and reuse rights/original Gazette bytes remain unavailable.
- #1460, #1461, #1464 and #1466 — closed without merge; superseded by PR #1470.
- #1470 — current-main combined deliverable; awaiting usable CI results and review.

Historical tracker material is retained under `docs/archive/` where appropriate. This file is the short current status entry point.


## Reusable lawyer-review files (2026-11-06)

- Added `docs/legal_evidence/law_14_2025_gazette_comparison_template.csv` with 311 stable rows (13 promulgation provisions + 298 Labour Law articles), explicit blank candidate/Gazette text fields, pending comparison status, page-locator column, reviewer notes, and `verified=0`. The blank text is deliberate: do not manufacture source wording from locator metadata.
- Added `docs/legal_evidence/deadline_rules_lawyer_review.csv` for the five existing draft deadline rules; all remain explicitly unapproved pending primary-source and counsel review.
- Added `docs/legal_evidence/lawyer_review_cover_note.md` with review procedure and estimated effort. These files are reusable handoff templates; they do not certify legal text or currentness.
- The downloadable XLSX workbook was generated for the user, but is not committed in this text-only GitHub contents workflow; the two CSV files provide the reusable repository-native data.


## Latest PR #1470 head check (2026-11-06 08:48 UTC)

- Current branch head at this check: `9c8436e5d6dee172e863f26bca21c70f7b416ee7`. The PR remains open and unmerged.
- Exact-head workflow runs: Tests `42189462330`, CodeQL `42189462314`, dependency audit `42189462233`, non-database safety `42189462358`, and browser acceptance `42189462219` all concluded `failure`.
- All seven jobs across those five runs returned an empty step list. The job-log endpoint returned HTTP 404 for the Tests job. No test, browser, Bandit, CodeQL, or dependency-audit command is evidenced as having executed. Treat this as an unresolved pre-step runner/service failure, not a code pass or code failure.
- Do not rerun these workflows repeatedly without a change in runner availability. Do not merge until the required checks execute and pass.


## Arabic scorer transparency improvement (2026-11-06)

- Added separate answerable-question abstention outputs to `tools/score_arabic_retrieval.py`: `answerable_abstained_answers`, `answerable_non_abstained_answers`, and `answerable_abstention_rate`. This makes over-refusal on questions labelled answerable visible separately from safety abstention on unanswerable questions.
- Added a focused regression test in `tests/test_score_arabic_retrieval.py` and documented the fields in `docs/arabic_retrieval_measurement.md`.
- Commits: `99979d94f73dc4e64a9aac8023957f33228fe065` (scorer), `8d89be791212c2061010368253c924e2a82f14f7` (test), `aae8e0c0d534a127bae9b0f1f8618ea02ec41620` (docs).
- Validation limitation: these changes have been reviewed via commit diffs, but the test has not been executed locally or by CI. Existing CI pre-step failure remains; no pass is claimed.


## Scorer input-validation hardening (2026-11-06)

- Hardened `tools/score_arabic_retrieval.py` so a non-string `review_evidence_url` is rejected through the same fail-closed validation path as malformed URLs, rather than leaking a parser type exception.
- Added a regression test for a numeric URL value. Commits: `dc80638e5f4c5d7cd871c11b8441abe3214e741d` (validator) and `15244fd42777aa237bd9a994b6d16061bc63c181` (test).
- Static diff review only; test execution remains unverified pending a usable local checkout/runtime or functioning CI runner.


## Scorer CLI error handling (2026-11-06)

- `tools/score_arabic_retrieval.py` now converts malformed question/run/report input and filesystem errors into concise argparse errors (exit code 2) rather than an unhandled traceback. Benchmark-fingerprint mismatch remains a deliberate hard stop.
- Added a CLI regression test for malformed JSON, asserting exit code 2 and no traceback. Commits: `2c4bdb91c082008c7933a097fa7cdf89ea0554f2` (CLI) and `b2a61de74df70a17450e7d52e998aaff7c524626` (test).
- Diff-reviewed only; no local or CI execution is claimed.


- Additional hardening: existing measurement report files must now be JSON objects with a `phases` object; malformed report structure is converted to a concise CLI validation error. Regression coverage asserts exit code 2 without traceback. Commits: `868fa9c98be192ee91b6745d92455a22a264d4b3` and `0e5bd29742975a627c810b20d21e5144534466b6`.

## Arabic negation guard whitespace hardening (2026-11-06)

- The claim-support screen now recognizes Arabic prohibitions written with repeated spaces, tabs, or newlines between `لا` and `يجوز` / `يحق` / `يسمح`. Positive permission matching strips these negated forms before classifying modality, preventing a prohibition from being misread as permission.
- Added regression cases for all four whitespace forms, including faithful negative wording and positive-claim-versus-negative-source conflicts.
- Commits: `0dccdf51a9fdec443498cbafc3d5e1ce73af639b`, `25a43b3ac28a3b31f8e34986bbc73ccecceaaed8`, `02ebbd52c285d8e84b221286fc1d90bf6f4b5f1e`, `577a943b1790777ebe4f395ad3f018fe0e2b3a7c`, `d9611009903c9a720fa317a54c0583c294603d08`.
- Static source review only. Regression tests have not executed; do not treat this as validated until the integrated suite runs.


## Retrieval benchmark fingerprint integrity (2026-11-06)

- The before/after benchmark fingerprint now includes the question-style and retrieval-tag fields that determine colloquial/synonym cohort membership. Changing those fields can no longer silently mix different cohort definitions in one comparison report.
- Retrieval tags are canonicalized as an order-independent string list; malformed non-string tag data is preserved for later validation without causing fingerprint sorting to crash.
- Added regression coverage showing counsel approval-status changes do not alter the fingerprint, while prompt/style/tag changes do. Test execution remains unverified; no pass is claimed.
- Commits: `bd05a7c819ccb99110357fcdf354076af1dad97c`, `52aec28b669b0ed0b5cee6ea823e33eb1179f5e0`, `ffd9a5db5348d0287e4ce25c2818e83a1b90b8bb`, `1f14b198313ead16b7858c95269461a232cda7bd`.


## Gazette importer URL credential delimiter hardening (2026-11-06)

- The importer now rejects URL userinfo whenever the parsed URL contains a username or password component, including an empty credential delimiter such as `https://@example.gov/item`. Previously the truthiness check could accept an empty username component.
- Added a regression test asserting the importer refuses this URL before creating output files. Test execution remains unverified.
- Commits: `bbb900f2eac2a2ce30120c95ba44e891652041fc`, `1ee9f0b06a03c6f538b3420bd43d6270e01453bc`.


## Evaluation runner redirect isolation (2026-11-06)

- The authenticated evaluation runner now refuses HTTP redirects rather than allowing urllib to follow a 301/302/307/308 response. This prevents login credentials, CSRF-authenticated evaluation requests, or question payloads from being forwarded to a different host by a redirect response.
- Added a regression test for refusal of a cross-origin 307 redirect. Test execution remains unverified.
- Commits: `314806b8c8cd21dbf9480ff6a06166ad89d2d399`, `cf624a6532c4e2aa09e16ced803a8a7d255ffb21`.

## Lawyer answer-rating backend contract (2026-11-06)

- Added firm-profile migration `0021_answer_ratings.sql` for one current rating per reviewer/assistant message, with constrained overall rating, cited-article accuracy, expected article IDs, answerability, bounded notes, and append-only rating events.
- Added `docs/answer_rating_export_contract.md` defining the authenticated firm-scoped submit/update API, admin/reviewer CSV export, required columns, benchmark-ready rules, and acceptance tests for AI 2's UI integration.
- Added `tests/test_answer_rating_migration.py` and wired it into `.github/workflows/tests.yml`. The five migration contract cases passed in an isolated local Python 3.13/SQLite run (rating insert, enum/JSON/answerability/note constraints, reviewer uniqueness, parent-message retention, and immutable event ledger). The full firm migration runner and application integration have not been executed. Runtime route handlers, role enforcement, and CSV export implementation remain outstanding.
- Ratings are not training consent, legal-source verification, or counsel approval. Keep firm data private and exclude curated candidate questions from scored benchmark results.

