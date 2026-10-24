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
