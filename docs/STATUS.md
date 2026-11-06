# Legal Copilot status

**Updated:** 2026-11-06  
**Scope:** engineering and evidence status only; not legal-readiness or production certification.

## Current state

- Runtime uses separate control-plane, per-firm database and shared legal-corpus profiles.
- Labour Law 14/2025 PR #1451 is merged as a provisional source-comparison package. The 311-row lawyer tick-sheet leaves all decisions blank and every `verified` value at 0. The law remains non-authoritative and retrieval-ineligible pending qualified counsel review, source-rights review, currentness/amendment/corrigenda checks and commencement analysis.
- A lawyer-supplied UTF-8 Gazette text importer and article-number audit are prepared in the current work branch. The one-sitting procedure and metadata sidecar are in `docs/gazette_text_import_runbook.md` and `docs/templates/gazette_text_metadata.template.json`. Output rows retain structured supplier/capture provenance and remain `verified=0`, `in_force=0`, and `as_of=null`; database staging is a separate approved operation.
- The 110-question Arabic benchmark is a curated template, not production query data. It has 82 preliminary formal labels, 28 preliminary colloquial labels and 28 preliminary synonym tags; all remain unreviewed. The API runner now emits canonical source-scoped article IDs, and the scorer can retain unlabeled run captures while excluding them from metrics. No actual baseline run or before/after rates exist; `MIN_SCORE` remains 0.30 and must not be tuned yet.
- Five deadline rules and the holiday calendar remain unverified drafts. The counsel packet records the assumed periods/triggers and missing primary citations; no rule values were changed.
- Repository status previously recorded three PR #1404-area English/Arabic negated-obligation regressions still failing after three attempts. PR #1470 ports a raw-text guard and regression/control tests, but exact-head Actions jobs fail before any execution step; no fix is claimed as validated.
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
- #1449, #1212, #1208 and #840 — closed without merge.
- #1460, #1461, #1464 and #1466 — closed without merge; superseded by PR #1470.
- #1470 — current-main combined deliverable; awaiting usable CI results and review.

Historical tracker material is retained under `docs/archive/` where appropriate. This file is the short current status entry point.
