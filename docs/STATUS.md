# Legal Copilot — release-candidate status

**Updated:** 2026-11-14  
**Release decision:** **NOT READY for lawyer pilot or production.** This is an engineering handoff checkpoint, not legal, security, or operational certification.

## Tier A — AI-1 delivery

| Item | Status | Evidence / remaining gate |
|---|---|---|
| Answer rating contract | **Complete** | [answer_rating_contract.md](answer_rating_contract.md) is on main; defines seven review fields and UTF-8 CSV contract for AI-2. |
| Negation guard | **Implemented; runtime acceptance pending** | Always-on narrow guard is in `app.ask()` (#1588). The focused regression module and integrated `app.ask()` tests were committed directly to main (commits `92e5177` and `f988e76`) to bypass the blocked PR workflow. An isolated local harness of the helper returned PASS for all three; repository tests remain unexecuted. |
| Firm-test source-matched mode | **Draft implementation** | The fail-closed exact firm-ID + environment gate, isolated search scope, source-only fallback, non-verified label and synthetic response-path tests were committed directly to main (`ce2ebc8`, `7c5e09d`, `5ec22a1`, `b377af0`, `311287d`). The dedicated search scope intentionally returns no candidates until a permission-cleared retrieval adapter exists; tests inject synthetic hits and have not been executed. Do not enable in production. The current Law 14/2025 candidate remains ineligible because reuse permissions are unknown and source text is not committed. |
| Reviewer CSVs and how-to | **Complete as review templates** | [Law 14/2025 311-row CSV](legal_evidence/law_14_2025_gazette_comparison_template.csv) now includes all machine comparison statuses, similarity values, page locators and prior page-review notes, with explicit pending lawyer decision fields; exact candidate/Gazette text columns remain blank because source text is not authorized for repository inclusion. [Five-rule deadline CSV](legal_evidence/deadline_rules_lawyer_review.csv) and [one-page review guide](legal_evidence/lawyer_review_quick_guide.md) are also on main. All lawyer decisions remain pending. |
| Evaluation set and scorer | **Draft set complete; baseline blocked** | Added 116 unique Law 14/2025 question drafts (58 formal + 58 colloquial) with machine-proposed article IDs at [dataset](../tests/legal_eval/law_14_2025_machine_proposed_questions.draft.jsonl); structural contract at [test](../tests/test_law14_machine_proposed_eval_set.py). All are unapproved; expected answers/citations are blank. Existing scorer enforces lawyer-approved labels. [Unreviewed baseline inventory](legal_evidence/law14_2025_retrieval_baseline_unreviewed.json) records the cohort counts and null metrics; top-3/wrong-article/abstention rates are **not measurable yet**, not zero. |
| Documentation cleanup | **Complete** | Detailed prior status archived at [STATUS history](archive/STATUS_history_through_2026-11-13.md). This file is the concise release-candidate summary. |

## Legal evidence and trust boundary

- Labour Law No. 14/2025 remains **source-matched, not lawyer-reviewed**, `lawyer_reviewed=false`, `authoritative=false`, and `retrieval_eligible=false`.
- All 311 candidate rows remain `verified=0`. No commit or test mode may change that.
- The candidate manifest records collection/reuse permission as unknown; the supplied scan reports copy/print restrictions. The candidate text is not committed and must not be served through the new firm-test mode.
- Related-instrument discovery now records Labour Ministry Decisions 248–252/2026 from Gazette Supplement issue 225 (A) metadata and the Ministry announcement. Their full signed text remains restricted/unavailable; all five are metadata-only, permission-unknown, pending counsel review and retrieval-ineligible.
- Qualified Egyptian counsel must independently review the text, commencement, currentness, amendments/corrigenda, transitional effects and permission basis before any verified or authoritative status.

## Runtime and operational blockers

- Focused tests for the current AI-1 changes have not been executed in the supported Python 3.12 environment in this session. GitHub Actions previously failed before runner allocation (empty steps / runner ID 0); do not call this a code test failure or a pass.
- The rating contract is ready for AI-2, but billing/provider acceptance, real tenant isolation/recovery, browser/device accessibility, and pilot-firm workflow acceptance remain separate gates.
- The supplied ZIP's `law_rows_ar.jsonl` was structurally inventoried without committing its text: 311 rows, 13 promulgation provisions and 298 articles, no missing/duplicate article numbers, malformed rows 0, `verified=0` for all rows. See [inventory audit](legal_evidence/law14_2025_uploaded_candidate_inventory_audit.json). This is not an importer run or Gazette comparison. The importer still needs an authorized plain-text Gazette transcription; do not bypass the restricted PDF's copy/print controls.

## Next actions

1. When GitHub billing is restored or a supported local Python 3.12 environment is available, execute the focused negation and firm-test test modules; no test output is claimed now.
2. AI-2 can implement rating UI/export against the published [rating contract](answer_rating_contract.md).
3. Obtain authorized Gazette text/reuse clearance and qualified counsel review before attempting the importer or legal verification.
4. After counsel approves the 116-question answerability/article key and an authenticated corpus/API exists, run before/after retrieval exports through the scorer.

**Last formally recalculated whole-project score:** 50.10% (2026-11-01). This is not a recalculation of the work above; no newer weighted project score is asserted.
