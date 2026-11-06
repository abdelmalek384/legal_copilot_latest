# Legal Copilot status

**Updated:** 2026-11-06  
**Scope:** engineering and evidence status only; not legal-readiness or production certification.

## Current state

- Runtime uses separate control-plane, per-firm database and shared legal-corpus profiles.
- Labour Law 14/2025 PR #1451 is merged as a provisional source-comparison package. The exact 112-page user-supplied Gazette PDF and 311-row candidate JSONL were recovered from the Library source bundle; their SHA-256 values match the recorded comparison hashes. All 311 provisions now have page locators and recorded visual comparison notes (282 earlier checks plus 29 additional full-article page-image comparisons on 2026-11-06). Every lawyer decision remains blank and every `verified` value remains 0. The candidate JSONL's legacy metadata has `in_force=1` and `as_of=2025-05-03` on all rows; those fields are not a commencement/currentness determination and must not be treated as approval. The law remains non-authoritative and retrieval-ineligible pending qualified counsel review, source-rights review, currentness/amendment/corrigenda checks and commencement analysis.
- A lawyer-supplied UTF-8 Gazette text importer and article-number audit are prepared in the current work branch. The one-sitting procedure and metadata sidecar are in `docs/gazette_text_import_runbook.md` and `docs/templates/gazette_text_metadata.template.json`. An `allowed` collection-permission claim requires an evidence reference. Output rows retain structured supplier/capture provenance and remain `verified=0`, `in_force=0`, and `as_of=null`; database staging is a separate approved operation.
- The importer now separates Arabic-ordinal issuance provisions (`المادة الأولى`–`المادة الثالثة عشرة`) from numeric attached-law articles, excludes unparsed preamble from candidate rows, and reports preamble/numbering gaps. The new ordinal-path tests are present but not executed because CI jobs fail before their first step.
- The 110-question Arabic benchmark is a curated template, not production query data or observed user questions. All rows explicitly carry `question_origin=curated_candidate_not_user_observed`. It has 82 preliminary formal labels, 28 preliminary colloquial labels and 32 preliminary synonym tags; all remain unreviewed. The runner emits law-block-scoped article IDs and explicit source-trust status; the scorer rejects curated candidates and requires at least 100 observed-anonymized or reuse-permitted public questions with privacy approval, origin reference, collection date and consent/reuse basis, plus counsel-approved expected IDs/answers. It also requires at least 20 colloquial and 20 synonym questions, at least one reviewed unanswerable question with 100% abstention compliance, and blocks targets for wrong, uncited or unverified-source answers. No actual baseline run or before/after rates exist; `MIN_SCORE` remains 0.30 and must not be tuned yet.
- Five deadline rules and the holiday calendar remain unverified drafts. The counsel packet records the assumed periods/triggers and missing primary citations; no rule values were changed.
- Repository status previously recorded three PR #1404-area English/Arabic negated-obligation regressions still failing after three attempts. PR #1470 ports a raw-text guard and regression/control tests, and restores PR #1208 finite-period coverage including the `سنة` spelling. Direct smoke probes of the extracted negation helper caught all 6 positive/negative obligation reversals and passed all 4 faithful-negation controls; these are helper-level probes, not the integrated test suite. The negation guard also strips variable whitespace in Arabic negated-obligation phrases before classifying positive obligations; regression coverage now includes spaces and tabs. This change is not runtime-verified. The latest Actions attempt on code head `6a882d4457d7a5ad9da3eb64749aaa1dc5e1aaee` ran Tests and CodeQL workflows, but both failed before any execution step; all four jobs reported zero steps and GitHub reported `runner_id=0` with no runner name. This is a runner-allocation/infrastructure failure, not evidence of code-test failures or passes. The integrated suite remains unvalidated.
- PR #1470 is the clean current-main review target. Stale drafts #1461 and #1464 have been closed without merge.
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
