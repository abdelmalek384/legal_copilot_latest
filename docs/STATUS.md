# Legal Copilot status

**Updated:** 2026-11-06  
**Scope:** engineering and evidence status; not a legal-readiness or production certification.

## Current state

- Runtime architecture requires separate control-plane, per-firm database and shared legal-corpus profiles.
- Law 14/2025 PR #1451 is merged. Its 311-row machine comparison is in docs/legal_evidence/: 282 unique provisions have prior page-image review records and 29 have no targeted page-image review record. The new 311-row lawyer tick-sheet leaves every decision blank and every verified value at 0.
- Law 14/2025 remains source_matched_not_lawyer_reviewed, non-authoritative and retrieval-ineligible. Counsel review, full currentness/amendment/corrigenda analysis, effective-date interpretation and source/reuse-rights review remain outstanding.
- PR #1461 contains a lawyer-supplied UTF-8 Gazette text importer, 110-question Egyptian-Arabic benchmark template, article-specific scorer and deadline-rules approval packet; it remains unmerged and has not been locally executed.
- Existing retrieval evaluation supports Recall@3/MRR and citation/abstention metrics. Wrong-article answer scoring is added separately. All 110 questions remain unlabeled; no before/after metrics are available and MIN_SCORE remains 0.30.
- Five deadline rules and the fixed-date holiday list remain unverified drafts. The holiday calendar has no dated movable holidays and no complete years.
- Negation guard PR #1464 adds raw-text checks before normalization. It remains draft; exact-head CI failed before any job step ran.

## PR decisions

- #1451 — merged; provisional evidence only.
- #1449, #1212, #1208 and #840 — closed without merge with documented reasons.
- #1460 — closed without merge; superseded by current-main port #1464.
- #1464 — open draft; requires green exact-head tests and security checks.

## Mandatory human gates

1. Qualified Egyptian counsel signs the 311-row Law 14/2025 comparison and reviews currentness, rights and commencement.
2. Counsel labels expected articles/answers for the Arabic evaluation set.
3. Counsel approves or corrects each deadline rule and the applicable holiday calendar.
4. Exact-head CI, staging and deployment acceptance pass before release claims.

Historical progress and database trackers are archived under docs/archive/. This short file is the current status entry point.
