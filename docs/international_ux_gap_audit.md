# Legal Copilot — International UX Gap Audit and Roadmap

**Audit type:** code/documentation-based gap analysis, not a claim of completed live browser or screen-reader testing.  
**Benchmark references:** Lexis+ describes unified natural-language search, document upload/analysis, practice-area task organization, and answers within results; vLex Vincent emphasizes inspectable source links and citation relationships. These are product-pattern references, not a recommendation to copy proprietary visual design.

For the formal bilingual keyboard, screen-reader, zoom/reflow, contrast, forced-colors and workflow acceptance protocol, see [Accessibility Manual Acceptance](accessibility_manual_acceptance.md). The checklist is a test plan only; it must be completed on an exact candidate build before any conformance claim.

## Current baseline already implemented

- Arabic-first direction, RTL UI and Arabic text normalization.
- Case folders, team roles, notes, deadlines, fee tracking and session tracking.
- Hybrid lexical/article-number search and citation checks.
- Saved research conversations and rename/search improvements.
- Accessible skip link, named primary navigation, keyboard-operable sidebar, Escape-to-dismiss modal behavior, language switching that preserves workspace, forced-colors focus styling.
- Legal source review workbench, version provenance and evidence-backed review events.

## Highest-impact gaps to investigate or implement

### P0 — Delivered: Research Results & Source Inspector

The core P0 source-inspection workflow is implemented. See [Research Results & Source Inspector](research_source_inspector.md) and its [manual QA checklist](research_inspector_manual_qa.md).

Delivered capabilities include:
- Explicit verified-corpus, firm-document and metadata-only discovery scopes; the UI does not silently blend them.
- Recorded source/version provenance and conservative status labels, including secondary, user-supplied/unverified, metadata-only, under-review and no-relevant-verified-source states.
- Exact stored-passage display and copy, recorded citation copy, registered HTTPS source links, and scope/as-of-aware research memo export.
- Save-to-matter with case authorization and audit recording.
- Arabic matched-term highlighting, exact article-number search, keyboard-operable scope/navigation controls, and automated loading/error/empty-state coverage.
- Fail-closed handling for malformed provenance, missing/invalid dates, unknown scope and malformed passage payloads.

These are implementation and automated-test claims only. They do not establish legal correctness, a complete verified corpus, semantic entailment, or manual accessibility acceptance.

### P0 — Remaining research-quality work
- Complete lawyer-labelled retrieval and answer-quality evaluation across representative Egyptian practice areas.
- Tune retrieval against approved, permission-cleared and lawyer-reviewed source material.
- Continue improving Arabic query coverage without changing source text or negation meaning.
- Preserve a clear distinction between lexical citation checks and legal reasoning; do not present either as counsel validation.

### P1 — Document analysis
- Drag-and-drop upload with file limits, supported types, progress, cancellation and clear failure recovery.
- Extracted text next to original page preview; page-level references, OCR confidence and editable corrections.
- Document compare / redline, clause and obligation extraction, deadlines and party names with explicit user confirmation.
- Exportable research memo with citations, sources, as-of date and verification warnings.
- Explicitly label user-supplied material and prevent it from being mistaken for official law.

### P1 — Navigation and workspace
- Task-oriented home page: Continue a case, Research law, Review a source, Analyze a document, Track a deadline.
- Consistent global search and command/navigation pattern.
- Practice-area landing pages and contextual empty states with actionable next steps.
- A compact but clear case timeline combining sessions, deadlines, filings, tasks and reminders; deadlines must remain visually distinct from court sessions.
- Responsive layouts for laptop/tablet/mobile, with stable RTL alignment and no horizontal overflow.
- User preference persistence for language, density, default search scope and accessibility settings.

### P1 — Trust, collaboration and enterprise controls
- Audit trail for source verification, edits, exports, document access and permission changes.
- Clear role/permission explanations and tenant context.
- Two-factor authentication, self-service account recovery, session/device management, and firm-level retention controls before production use.
- Accessible tables, predictable keyboard focus, labeled forms, error summaries and screen-reader announcements for asynchronous search/upload actions.
- A consistent design system: typography scale, spacing, buttons, form states, drawers/modals, toasts, tables and RTL tokens.

### P2 — Advanced research
- Citation graph: amended by, repealed by, implementing regulation for, and cases citing a judgment, only when evidenced.
- “What changed?” view for instrument versions and provision-level before/after diffs.
- Research trail and reusable matter-specific research folders.
- Structured outputs: issue, rule, application, uncertainty, next verification steps.
- Evaluation and feedback tools so lawyers can flag missing sources, wrong pin-cites, OCR errors and stale versions.

## Suggested visual hierarchy

1. **Top bar:** firm/workspace, global search, language, help and account.
2. **Left navigation:** Dashboard, Cases, Legal Research, Documents, Deadlines, Fees, Team, Source Review, Settings.
3. **Main work area:** user task/results with strong headings and restrained density.
4. **Research source rail:** citations, exact passages, source status and open-source actions.
5. **Contextual actions:** save to matter, copy citation, export memo, report source issue.

Use restrained color for status only; do not rely on color alone. Preserve visible keyboard focus, accessible contrast, reduced-motion preferences and Arabic RTL reading order.

## Benchmark-derived principles

- Lexis+ pattern: unified search, task/practice-area organization, upload-and-analyze workflows, answers surfaced with results.
- vLex Vincent pattern: inspectable sources and citation relationships; make verification a first-class part of the answer, not a footnote.
- Adapt these principles to Egyptian practice and Arabic-first workflows; do not copy logos, exact screens, proprietary wording or protected assets.


## Focused code-level accessibility follow-up — 2026-11-04

A targeted static inspection of `static/index.html` and `tests/test_frontend_ux_contract.py` confirms useful foundations (skip link, main landmark, keyboard-operable primary navigation, visible focus, reduced-motion rules, forced-colors focus styling, 44px touch targets, and polite toast announcements). It also identifies the following implementation work to prioritize before manual acceptance:

1. **Navigation semantics — implemented 2026-11-04:** the in-place primary workspace switcher now uses native `<button type="button">` controls, retains `aria-current="page"`, has explicit focus/active styling, and uses light inactive/white hover text against the dark sidebar to preserve contrast, and has mobile horizontal-scroll sizing (using a selector strong enough to override the base width) plus a forced-colors active-state border after the switch to native buttons. Contract coverage was updated. This resolves the previous anchor-with-button-role mismatch; exact-head CI and browser verification are still required.
2. **Dialog semantics:** the inspected new-case and client-profile dialogs already expose `role="dialog"`, `aria-modal="true"` and accessible names now reference visible headings through `aria-labelledby`; a global keyboard handler traps Tab focus, handles Escape and restores focus to the opener. Commits `604ddad` and `2778983` set the workspace shell inert while either inspected modal is open and restore it when the final modal closes; commits `5dcfbb9`/`de02165` tie dialog names to visible headings with `aria-labelledby`. Browser and contract assertions cover the behavior. Extend contract coverage to every modal variant, prefer `aria-labelledby` tied to the visible heading where practical, and test nested/edge-case focus behavior in a real browser.
3. **Disclosure state — partially implemented 2026-11-04:** document extracted-text review now exposes `aria-expanded` and `aria-controls` with state reset on close/failure. Continue auditing every other expandable panel, including navigation and result sections.
4. **Async status — partially implemented 2026-11-04:** document chunk loading and the loaded/empty completion state now use scoped polite status announcements; the global toast already has a polite live region. The global polite status toast now sits above workspace content, respects device safe-area insets, wraps long messages, and constrains width on narrow screens (commits `fc84670`/`660bf84`, contract `40bc9fe`). AI case-brief generation and deadline estimation now announce pending and successful completion states politely; AI-brief and deadline-estimation failures use assertive alerts. Continue reviewing remaining asynchronous views and ensure urgent alerts are not duplicated.
5. **Form errors and instructions — partial implementation 2026-11-04:** the shared element factory now associates adjacent `<label>` / input-select-textarea siblings with generated stable-in-view IDs and `for` attributes; placeholder fallback names remain for text inputs; tasks, calendar, case-status, feedback-category and invitation-role filters now have explicit bilingual accessible names. Billing plan/payment selectors, legal-review version/type/outcome selectors, task assignee/due date, hearing date, deadline rule/trigger/distance, case-team member/role selectors, case-consent checkboxes and document upload now have explicit accessible names; contract coverage added. Still audit controls without adjacent labels, expose required/invalid state consistently, associate inline errors via `aria-describedby`, and provide a focusable error summary or field-level error target after failed submission. Placeholder text must not be the only persistent label.
6. **Automated accessibility gate — implemented, CI validation pending 2026-11-04:** the Chromium workflow installs pinned axe-core 4.10.3 and runs WCAG 2.1 A/AA automated checks against authenticated Arabic RTL dashboard, settings, task, calendar, case, feedback and research views; the new-case dialog at phone width; and English LTR corpus coverage. The dashboard is scanned at 1440px desktop, 768px tablet, 640px reduced-layout/zoom-proxy, 390px phone and 320px narrow-phone widths, with a document-level horizontal-overflow assertion at each dashboard viewport. The gate is not yet proven green on the new commit and is not a substitute for keyboard, screen-reader, contrast and zoom review.

These are static-code findings and implementation recommendations, not evidence of a completed WCAG audit. Verify each change against the exact build and retain manual browser/screen-reader acceptance as a separate release gate.

## Validation plan (not yet completed)
- Run a route-by-route browser audit at desktop, tablet and mobile widths.
- Test Arabic and English, RTL/LTR switching, long Arabic titles, keyboard-only navigation, zoom to 200%, contrast, forced colors and screen readers.
- Test slow network, empty results, no source, OCR failure, expired session, upload error and permission-denied states.
- Have 3–5 Egyptian lawyers complete core tasks and record success rate, time, errors and confidence.
- Run automated accessibility checks plus manual WCAG 2.2 AA review; automated checks alone are insufficient.

## Next UI task — manual acceptance and lawyer usability
The next UI deliverable is not another source-inspector implementation. Complete the [manual Research Inspector QA runbook](research_inspector_manual_qa.md) against an exact build using synthetic records, then record Arabic RTL, English LTR, keyboard-only, screen-reader, responsive and clipboard/export results. Follow with a 3–5 Egyptian-lawyer usability study and log completion rate, task time, errors and trust feedback. Do not mark visual/accessibility acceptance complete from automated browser tests alone.


### Form-control boundaries and focus visibility — 2026-11-04

Static CSS inspection found control borders and focus indicators too faint for reliable identification. The effective control border `#CBD5E1` provided only about 1.48:1 against white, hover border `#9AABC2` about 2.34:1, and a 32%-opacity focus ring was unnecessarily translucent. Commits `fa94537`, `bea62eb` and `4162fab` strengthen default/hover borders to `#8292A8` (about 3.17:1) and `#7C8DA3` (about 3.39:1), ensure the legacy higher-specificity control rule actually consumes the contrast-safe token, and use a solid `#2457C5` focus ring. Contract test `7959431` guards these styles. This is a targeted CSS audit; check every control on varied backgrounds in the browser before claiming 1.4.11 conformance.

- **Native navigation keyboard regression:** browser test `53fa11b` verifies the primary workspace buttons activate using both Space and Enter, with the expected page heading; contract test `4bc0283` protects the browser test. This supplements semantic/static assertions and still requires CI execution.

- **Modal browser focus acceptance:** the axe browser test now focuses the final action in the new-case dialog, presses Tab to verify wraparound to the first field, presses Escape, verifies dialog removal, and checks focus returns to the opener. Browser test commit `a3e66cb`; contract guard `48f0182`. Exact-head CI remains pending.

- **Remaining casework field names:** task title, hearing details, deadline type/date/notes, and invoice-payment amount/reference now have explicit bilingual accessible names (commit `784e80f`); contract test `b56695c` guards them. Placeholder-derived fallback names remain in less critical fields and persistent visible-label review is still required.

- **Fee form date control:** the case-fee due-date input now has an explicit bilingual accessible name (commit `cce088e`); contract test `dcd5a85` guards it. Static scan now finds no empty-props select constructors; one fee date field identified by the scan has been named.

- **New-case required-field feedback:** empty case-title submission now sets `aria-invalid`, associates an inline alert via `aria-describedby`, focuses the field, and clears the error state as the user types (commit `51c49cc`); contract test `630d454` guards the behavior. Other dynamic forms still require a field-by-field error-association audit.

- **New-case validation browser coverage:** the axe acceptance test now submits the dialog with an empty title, checks `aria-invalid`, `aria-describedby` and visible alert state, then fills the title and verifies the error clears (browser test `dc92989`, contract guard `2aec5bd`). This test remains pending CI execution.

- The new-case inline error is rendered outside the label element (commit `d17230b`) so it remains a separate description rather than being folded into the control's accessible name; contract assertion `9cc0468` protects the structure.
