# Legal Copilot — release-candidate status

**Updated:** 2026-11-13  
**Release decision:** **NOT READY for lawyer pilot or production.** This is an engineering handoff checkpoint, not legal, security, or operational certification.

## Tier A — AI-1 delivery

| Item | Status | Evidence / remaining gate |
|---|---|---|
| Answer rating contract | **Complete** | [answer_rating_contract.md](answer_rating_contract.md) is on main; defines seven review fields and UTF-8 CSV contract for AI-2. |
| Negation guard | **Implemented; runtime acceptance pending** | Always-on narrow guard is in `app.ask()` (#1588). Draft PR [#1618](../pull/1618) adds the three original regressions and integrated test; supported local test output is still required. |
| Firm-test source-matched mode | **Draft implementation** | Draft PR [#1619](../pull/1619) adds exact firm-ID + environment gating, source-only fallback, non-verified label and synthetic tests. Do not enable in production. The current Law 14/2025 candidate remains ineligible because reuse permissions are unknown and source text is not committed. |
| Reviewer CSVs and how-to | **Complete as review templates** | [Law 14/2025 311-row CSV](legal_evidence/law_14_2025_gazette_comparison_template.csv), [five-rule deadline CSV](legal_evidence/deadline_rules_lawyer_review.csv), and [one-page review guide](legal_evidence/lawyer_review_cover_note.md). Candidate/Gazette text and reviewer decisions remain blank where evidence is unavailable; do not infer matches. |
| Evaluation set and scorer | **Draft set complete; baseline blocked** | Added 116 unique Law 14/2025 question drafts (58 formal + 58 colloquial) with machine-proposed article IDs. All are unapproved; expected answers/citations are blank. Existing scorer enforces lawyer-approved labels. No retrieval baseline is claimed without a local indexed corpus/API and approved labels. |
| Documentation cleanup | **Complete** | Detailed prior status archived at [STATUS history](archive/STATUS_history_through_2026-11-13.md). This file is the concise release-candidate summary. |

## Legal evidence and trust boundary

- Labour Law No. 14/2025 remains **source-matched, not lawyer-reviewed**, `lawyer_reviewed=false`, `authoritative=false`, and `retrieval_eligible=false`.
- All 311 candidate rows remain `verified=0`. No commit or test mode may change that.
- The candidate manifest records collection/reuse permission as unknown; the supplied scan reports copy/print restrictions. The candidate text is not committed and must not be served through the new firm-test mode.
- Qualified Egyptian counsel must independently review the text, commencement, currentness, amendments/corrigenda, transitional effects and permission basis before any verified or authoritative status.

## Runtime and operational blockers

- Focused tests for the current AI-1 changes have not been executed in the supported Python 3.12 environment in this session. GitHub Actions previously failed before runner allocation (empty steps / runner ID 0); do not call this a code test failure or a pass.
- The rating contract is ready for AI-2, but billing/provider acceptance, real tenant isolation/recovery, browser/device accessibility, and pilot-firm workflow acceptance remain separate gates.
- The importer can be run only on text that is lawfully supplied for extraction and use. Do not bypass the restricted PDF's copy/print controls.

## Next actions

1. Run `PYTHONPATH=. python -m unittest tests.test_negation_guard_repro tests.test_answer_source_polarity -v` in the supported local Python 3.12 checkout; record the actual output.
2. Run `PYTHONPATH=. python -m unittest tests.test_firm_test_source_matched_mode -v`; keep the real Law 14/2025 candidate excluded until source permissions and the missing evidence are resolved.
3. Connect AI-2's rating UI/export to the rating contract.
4. Obtain a lawfully usable text file and qualified counsel review before attempting the Law 14 importer or legal verification.
5. After the lawyer-approved 100+ question answer key and an authenticated local corpus/API exist, run the retrieval scorer and record top-3 hit rate, wrong-article rate and abstention rate.

**Last formally recalculated whole-project score:** 50.10% (2026-11-01). This is not a recalculation of the work above; no newer weighted project score is asserted.
