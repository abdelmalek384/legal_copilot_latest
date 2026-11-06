# Legal Copilot status

**Updated:** 2026-11-06  
**Scope:** engineering and evidence status only; not legal-readiness or production certification.

## Current state

- Runtime uses separate control-plane, per-firm database and shared legal-corpus profiles.
- Labour Law 14/2025 PR #1451 is merged as a provisional source-comparison package. The exact 112-page user-supplied Gazette PDF and 311-row candidate JSONL were recovered from the Library source bundle; their SHA-256 values match the recorded comparison hashes. All 311 provisions now have page locators and recorded visual comparison notes (282 earlier checks plus 29 additional full-article page-image comparisons on 2026-11-06). Every lawyer decision remains blank and every `verified` value remains 0. The candidate JSONL's legacy metadata has `in_force=1` and `as_of=2025-05-03` on all rows; those fields are not a commencement/currentness determination and must not be treated as approval. The law remains non-authoritative and retrieval-ineligible pending qualified counsel review, source-rights review, currentness/amendment/corrigenda checks and commencement analysis.
- A lawyer-supplied UTF-8 Gazette text importer and article-number audit are prepared in the current work branch. The one-sitting procedure and metadata sidecar are in `docs/gazette_text_import_runbook.md` and `docs/templates/gazette_text_metadata.template.json`. An `allowed` collection-permission claim requires an evidence reference. Output rows retain structured supplier/capture provenance and remain `verified=0`, `in_force=0`, and `as_of=null`; database staging is a separate approved operation.
- The importer now separates Arabic-ordinal issuance provisions (`المادة الأولى`–`المادة الثالثة عشرة`) from numeric attached-law articles, excludes unparsed preamble from candidate rows, and reports preamble/numbering gaps. The new ordinal-path tests are present but not executed because CI jobs fail before their first step.
- The 110-question Arabic benchmark is a curated template, not production query data or observed user questions. All rows explicitly carry `question_origin=curated_candidate_not_user_observed`. It has 82 preliminary formal labels, 28 preliminary colloquial labels and 32 preliminary synonym tags; all remain unreviewed. The runner emits law-block-scoped article IDs and explicit source-trust status; the scorer rejects curated candidates and requires observed-anonymized or reuse-permitted public questions with privacy approval, origin reference, collection date and consent/reuse basis, plus counsel-approved expected IDs/answers. It also requires at least one reviewed unanswerable question with 100% abstention compliance and blocks targets for wrong, uncited or unverified-source answers. No actual baseline run or before/after rates exist; `MIN_SCORE` remains 0.30 and must not be tuned yet.
- Five deadline rules and the holiday calendar remain unverified drafts. The counsel packet records the assumed periods/triggers and missing primary citations; no rule values were changed.
- Repository status previously recorded three PR #1404-area English/Arabic negated-obligation regressions still failing after three attempts. PR #1470 ports a raw-text guard and regression/control tests, and restores PR #1208 finite-period coverage including the `سنة` spelling. Direct smoke probes of the extracted negation helper caught all 6 positive/negative obligation reversals and passed all 4 faithful-negation controls; these are helper-level probes, not the integrated test suite. The latest available Actions attempt (code-bearing head `6210a181ebca4b7fd805dee82c358fb8d2b01a38`) failed before any execution step; all seven jobs reported zero steps. The integrated suite remains unvalidated.
- PR #1470 is the clean current-main review target. Stale drafts #1461 and #1464 have been closed without merge.

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
