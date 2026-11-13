# Lawyer-facing UI/UX audit and v1 design direction

## Scope reviewed
The current frontend is a single-file, right-to-left Arabic-first application with an English language toggle. The existing product has dashboard, clients, cases, legal research, case tabs, settings, and an administrator-only legal-source review workbench.

## Changes in this PR
- Refined the visual hierarchy: more consistent spacing, readable headings, calmer surfaces, clearer card boundaries, and improved form controls.
- Improved desktop navigation with a more distinct active state and a compact sticky navigation treatment on smaller screens.
- Added visible keyboard focus indicators and a reduced-motion preference.
- Improved legal research conversation and composer spacing while retaining the existing conversation and citation behavior.
- Added dashboard shortcuts for creating a case, opening legal research, and viewing cases. These call existing frontend flows rather than introducing mock functionality.
- Preserved the existing Arabic-first RTL layout, English toggle, and existing API contracts.

## Competitive product patterns worth adapting (not copying)
- **Harvey**: persistent navigation, quick access to recent work, secure matter context, and clear separation between assistant, knowledge, documents, and workflows. Reference: https://help.harvey.ai/articles/getting-started-with-harvey and https://www.harvey.ai/platform
- **Lexis+ with Protégé**: research integrated with drafting and document analysis, natural-language entry, and visible citation validation. Reference: https://www.lexisnexis.com/en-us/products/lexis-plus-protege/legal-research.page
- **Thomson Reuters CoCounsel**: worth evaluating as a third workflow benchmark during user research, particularly for document-centric legal tasks. Validate current capabilities before implementing specific parity claims.

These are interaction patterns and product directions, not a claim that our application has equivalent data coverage, citation validation, security certifications, or workflow completeness.

## Follow-up work merged — 2026-10-28

The following follow-up PRs passed their recorded Tests and non-database safety workflows before merge:

- **#700:** Arabic/English labels for case creation and the client/conflict-check view.
- **#701:** Arabic/English case-detail input placeholders, validation feedback, and fee formatting.
- **#702:** Arabic/English document-review actions, OCR warnings, review labels, and correction feedback.
- **#703:** Arabic/English case tabs, team roles, summary labels, and locale-aware activity timestamps.
- **#704:** keyboard focus trapping inside the case-creation modal and focus restoration when dismissed.

These are frontend implementation and automated contract-test improvements, not proof of visual quality or accessibility conformance. Manual browser, screen-reader, responsive, and lawyer workflow QA remains outstanding.

## Remaining gaps to address in follow-up PRs
1. **Navigation and information architecture:** add dedicated, real routes for saved research, documents, tasks/deadlines, and account/team administration only where backend support exists; clearly mark unavailable functionality rather than showing dead controls.
2. **Research trust UX:** show legal-source provenance, verification state, effective date, and warning states beside each citation; make citation-to-source inspection one click; distinguish current law from historical/unverified material.
3. **Case workflow:** create a guided first-run journey and empty states; make case creation, search, source-backed research, and saving research to a case feel like one continuous workflow.
4. **Conversation management:** improve rename, delete confirmation, search/filter, and recovery feedback for saved conversations; ensure all actions are tenant-scoped and tested.
5. **Accessibility:** validate contrast, keyboard-only navigation, screen-reader labels, zoom/reflow, and Arabic/English language switching with automated and manual checks.
6. **Responsive QA:** test at narrow mobile, tablet, and desktop widths; test long Arabic titles, mixed Arabic/Latin legal citations, and overflowing source text.
7. **Design system:** extract shared spacing, typography, status, button, form, and card tokens from the single HTML file before the interface grows further.

## Acceptance checklist
- [ ] Existing login/signup, case CRUD, client views, legal research, source review, and settings still work.
- [ ] Arabic RTL and English LTR layouts both render correctly.
- [ ] Dashboard shortcut buttons open the existing flows.
- [ ] Keyboard focus remains visible and reduced-motion preference is respected.
- [ ] Test at 360px, 768px, 1024px, and 1440px widths.
- [ ] Run the repository's automated tests and CI; review screenshots before merge.
- [ ] Do not imply the legal corpus is verified merely because the UI displays a status badge.


## 2026-11-13 — simplified Arabic-first workspace implementation

The implementation branch `ux/simplified-arabic-first-workspace` applies the accepted information architecture without deleting existing workflows:

- Primary navigation is grouped into **Workspace** and **Firm administration**. Matters, clients/conflicts, legal research, documents, tasks and calendar remain reachable; finance, setup, feedback, settings and authorized legal-source review remain available in the administration group. Reviewer/platform-only entries retain their existing permission gates.
- Navigation groups collapse into a horizontally scrollable, touch-friendly row on narrow screens. Arabic RTL and English LTR continue to use the same logical layout.
- The dashboard now leads with an actionable **Needs your attention** panel for overdue tasks and legal deadlines. Redundant quick-access tiles and the finance summary cards were removed from the dashboard; finance remains available in its existing workspace.
- Legal-source labels now distinguish **Verified operative text**, **Needs review**, and **Unverified** states. Secondary copies and metadata-only records are not presented as verified. A verified label continues to depend on the source status returned by the legal-source workflow; the UI does not manufacture verification.
- The implementation preserves the existing APIs, case authorization, tenant boundaries, matter-scoped document intake and legal-source review routes.

### Validation status

- Added frontend contract tests for navigation grouping, dashboard attention hierarchy and the three legal-source states.
- Automated tests, browser screenshots, Arabic/English responsive checks, screen-reader checks and lawyer usability acceptance have **not yet been executed** on this branch. Do not treat this implementation as release acceptance.
- The README's corpus limitation remains controlling: the product does not currently contain a lawyer-verified Egyptian legal corpus. No real Egyptian authority should be displayed as verified unless the legal-source acquisition and reviewer process has actually recorded that status.


### Matter-centred navigation refinement

- Reorganized the 12 matter detail destinations into five task-oriented sections: Overview, Work, Documents & research, Finance, and Team & activity.
- The selected section reveals only its relevant sub-pages. Existing tab identifiers, renderers, API routes, matter authorization and workflow logic are unchanged.
- Replaced clickable anchors without link destinations with native buttons, `aria-pressed` section state and `aria-current="page"` for the selected sub-page.
- Added responsive horizontal scrolling for the section selector on narrow screens and visible keyboard focus.
- Added a regression contract ensuring all matter work areas remain reachable through the grouped navigation.


### Research and document-intake clarity refinement

- The Legal Research screen and matter-level Ask panel now explicitly state that no lawyer-verified Egyptian legal corpus is currently available. The verified-corpus selector is labelled accordingly; candidate metadata and source-only results must not be mistaken for verified operative law.
- The Documents workspace keeps its common name search visible and moves file type, extraction status, classification status and filter reset into a collapsed native disclosure control. This reduces the initial visual density without removing filters.
- New Arabic interface copy is registered in the native-review catalog. Existing catalog omissions were also brought into the catalog; all entries remain marked `pending_native_review` and are not represented as linguistically approved.
- A static contract/catalog consistency scan found no unregistered Arabic literals in the current frontend. This is not a substitute for executing the Python test suite or native-speaker review.

### Latest validation observations

- The GitHub Actions run associated with an earlier branch commit reported failures in the Tests and Non-database safety regression workflows. The available connector did not return the job logs, so the failure cause is unresolved and must not be guessed.
- New workflow runs were queued for the latest commits at the time of this update. Their completion and any failure diagnostics still need inspection.
- No merge or production deployment has been performed.
