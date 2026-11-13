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


### 2026-11-13 — accessible document upload feedback

- The document upload result queue now exposes list/list-item semantics and announces per-file state changes to assistive technology.
- The existing polite live progress message and upload-panel busy state are retained.
- Added a frontend regression contract for the per-file announcement semantics.
- This is a focused accessibility improvement; it does not change upload endpoints, file validation, matter authorization, extraction, or retention behaviour.
- Legal research source cards now expose distinct accessible group names based on their recorded citation/reference, while the existing source-inspector control retains its expanded-state semantics. A regression contract covers the source-card naming.
- Follow-up static inspection found and corrected a malformed JavaScript statement in the upload panel's initial `aria-busy` setup (`let uploadPanel.setAttribute(...)`). Added an explicit regression assertion against that invalid form. Static inspection now finds no similar malformed `let object.method(...)` statements in the reviewed page source; this is not a substitute for executing the browser test suite.
- The file picker now pre-checks the selected PDF/DOCX extensions and 15 MB per-file limit before enabling upload. It reports the valid selection count and how many files will be skipped; server-side validation remains authoritative. Added a regression contract and registered the new Arabic labels for native review.
- Final static review of the picker pre-validation corrected the extension matcher to use a literal dot before `pdf`/`docx`; a focused JavaScript regular-expression check confirms PDF and DOCX filenames match while a misleading `.pdf.exe` suffix does not. Browser execution remains pending because the available workflow runs are failing and their logs/steps are not retrievable through the current GitHub integration.


### 2026-11-13 — consistent research inspector verification labels

- The source inspector now uses the same plain-language status distinctions as the source cards for secondary copies, review-pending records, user-supplied material, unverified records and metadata-only records.
- This prevents a source from appearing as generically “outdated” in the inspector when its recorded state is more specific (for example, metadata-only or user-supplied/unverified).
- Added a frontend regression contract covering every supported inspector status key and the Arabic/English labels for review-pending, unverified and metadata-only states.
- This is a presentation-only consistency correction. It does not change source metadata, legal verification, provenance, ranking or retrieval behaviour.

- The source inspector now places a concise explanation directly beneath the recorded status, distinguishing review-pending, metadata-only, user-supplied and unverified records. It explicitly states that an empty verified-passage result does not prove that no applicable law exists.
- Added regression assertions for the status explanation and the non-inference warning. No new Arabic strings were introduced; existing reviewed-inventory entries are reused.


### 2026-11-13 — extracted-page traceability in source inspector

- The inspector now reads the extracted-text `page` field as well as the alternate `page_number` field, including either value nested in provenance metadata.
- This closes a display gap: source cards already showed `s.page`, while the inspector previously looked only for `page_number`, so a page reference supplied by document-chunk retrieval could disappear when the user opened source details.
- Updated the regression contract to cover the canonical `page` fallback. Page references remain recorded extraction metadata; they are not independently verified against the retained original PDF.

- For firm-document results only, a recorded page pinpoint now carries an Arabic/English warning that it has not been independently checked against the original file. Verified-corpus results retain their separate provenance and review gates. The Arabic literal is registered as `AR-1439` and remains pending native review.


### 2026-11-13 — JavaScript parse validation and syntax corrections

- A direct JavaScript parse check found an extra closing parenthesis in the research upload-panel construction and another in the matter workspace shell. Both were corrected; the full inline script now parses successfully in the available JavaScript engine.
- Added frontend regression assertions for both call boundaries so the malformed closing sequences cannot silently return.
- The repository CI workflow already runs `node --check` against the extracted inline script. CI remains unverified because the workflow's job logs and step summaries are not available through the connected GitHub interface.

- Extended the same firm-document page-reference caveat into the OCR/extraction review cards: extracted `chunk.page` values are now explicitly marked as not independently checked when no reviewer-entered page reference is present. Added a regression test in `tests/test_document_classifications.py`.

### Latest CI observation — 2026-11-13

- At branch head `369e8fe62cc88588fcc1733ffb54c49ca84801f9`, all five PR workflow categories completed with `failure`: Tests, Non-database safety regression, Browser acceptance, Dependency security audit and CodeQL security analysis (including its Bandit job).
- The connected GitHub interface returned zero step summaries for every job and the job-log download was unavailable for every job. Therefore the failure stage and cause cannot be established from the available evidence; do not infer that these are application-test failures or that billing is definitely the cause.
- The inline JavaScript was independently parsed successfully after correcting the two extra closing parentheses. This is a targeted static parse check, not evidence that the Python suite or browser acceptance passed.
- PR #1610 remains draft, unmerged and undeployed. Release acceptance is still blocked on retrievable CI diagnostics and the outstanding manual/browser/legal review gates.

### 2026-11-13 — matter-document identity in the research inspector

- When retrieval supplies stable provenance fields, the Legal Research inspector now displays the matter-document record ID, matter ID, and original-file SHA-256 fingerprint alongside the existing original filename and page pinpoint.
- Fields are conditional: missing identifiers are omitted rather than inferred. The interface does not construct a document URL or treat a checksum as proof that OCR text is accurate.
- Added a focused frontend regression contract for the identifier and fingerprint fallbacks, and documented the provenance hand-off in the source-inspector contract.
- This improves the ability to locate and independently compare a retrieved passage with its retained matter file without changing retrieval, authorization, source ranking, or legal verification.
- CI remains non-green; job records are available but the GitHub Actions API returns no step summaries, and log downloads currently return a missing-blob response. Do not treat the new regression contract as executed validation.

### 2026-11-13 — research result to retained matter original

- Matter-document retrieval hits now include chunk/document/matter identity, original filename and stored SHA-256, extraction status, OCR-used state, and confirmed original-retention availability.
- The source inspector displays OCR caution and only offers the original-download action when the backend confirms a ready, non-purged private object. It uses the existing authorized download endpoint, which rechecks matter access and file integrity.
- Matter-linked results also provide direct navigation to the selected matter's Documents section, where the existing extracted-text review controls remain available.
- Legacy mode and purged/missing originals are not represented as downloadable. No document URL or retention status is inferred in the browser.
- Added separate-runtime regression assertions for result provenance and frontend contracts for the guarded download and OCR notice.
- This is traceability for user-supplied matter evidence, not independent legal-source verification.


### 2026-11-13 — exact research passage hand-off

- Refined the source-inspector action from matter-level navigation to document-and-chunk navigation when the retrieval result supplies those identifiers.
- The matter workspace opens the matching document's existing extracted-text review panel and focuses/scrolls to the exact chunk card. Scrolling respects the operating system's reduced-motion preference. The one-shot target is cleared after lookup; if the chunk is absent from the loaded extraction, a visible status explains that it could not be located; if the document itself is no longer listed in the matter, a separate fallback is shown and the target is cleared.
- When a chunk ID is unavailable, the action remains a matter Documents hand-off and does not claim an exact passage location.
- Added a frontend regression contract for the target identity, automatic review-panel opening, focus/scroll behavior, and missing-passage fallback. Registered all three new Arabic navigation/fallback labels in the native-review catalog (1,442 unique entries; all remain pending native review) and added a catalog consistency contract. These contracts are written but not executed because GitHub Actions is blocked by the reported billing issue.


### 2026-11-13 — matter-library original retention affordance

- The case-detail API already returns a backend-derived `original_available` value for each document. The matter Documents workspace now shows the original-download action only when this value is explicitly true; otherwise it explains that no retained original is available.
- This avoids a misleading download affordance for purged/missing originals and legacy-mode documents. The server-side authorized download endpoint remains the security and integrity authority.
- Added a frontend regression contract and registered the Arabic fallback label in the native-review catalog (1,443 unique entries; new labels remain pending native review). The regression contract has not been executed due to the reported GitHub billing issue.


### 2026-11-13 — OCR and partial-page review safeguards

- Matter-level chunk review now repeats a clear OCR warning when document metadata records OCR use or an OCR-unverified extraction status.
- When some pages could not be OCR-extracted, the panel warns that displayed passages may be incomplete and directs the reviewer to the original document.
- Page-reference display now accepts either `page` or `page_number`; it continues to label the page as extracted/provisional, not independently verified.
- Added frontend regression contracts and registered both Arabic warnings in the native-review catalog (1,445 unique entries; all new labels pending native review). No runtime test execution is claimed.


### 2026-11-13 — cross-matter search passage hand-off

- Cross-matter extracted-text search now transfers the returned case/document/chunk IDs into the same exact review navigation used by Legal Research sources.
- When identifiers are incomplete, the action falls back to the matter Documents workspace and does not claim a chunk pinpoint.
- Added a frontend regression contract and documented the shared hand-off. This does not change search scope, ranking, or verification status.


- Extended the separate-runtime cross-matter search regression to assert that each matching result carries the authorized case ID, document ID, positive chunk ID, and passage reference required by exact-review navigation. This is test coverage only; it has not been executed.


- Added a visible focus outline and scroll margin to the exact extracted-chunk review card after source navigation, plus a frontend regression contract. This improves keyboard orientation without changing the review state or implying verification.
