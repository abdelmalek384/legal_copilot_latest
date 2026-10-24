# Legal Copilot — International UX Gap Audit and Roadmap

**Audit type:** code/documentation-based gap analysis, not a claim of completed live browser or screen-reader testing.  
**Benchmark references:** Lexis+ describes unified natural-language search, document upload/analysis, practice-area task organization, and answers within results; vLex Vincent emphasizes inspectable source links and citation relationships. These are product-pattern references, not a recommendation to copy proprietary visual design.

## Current baseline already implemented

- Arabic-first direction, RTL UI and Arabic text normalization.
- Case folders, team roles, notes, deadlines, fee tracking and session tracking.
- Hybrid lexical/article-number search and citation checks.
- Saved research conversations and rename/search improvements.
- Accessible skip link, named primary navigation, keyboard-operable sidebar, Escape-to-dismiss modal behavior, language switching that preserves workspace, forced-colors focus styling.
- Legal source review workbench, version provenance and evidence-backed review events.

## Highest-impact gaps to investigate or implement

### P0 — Research trust and source transparency
- A persistent source panel beside each answer: exact title, authority, instrument number/year, article/page pin-cite, publication date, as-of date, source URL, and status.
- Visible source-status labels: **Verified official text**, **Secondary copy**, **User supplied — unverified**, **Metadata only**, **Outdated/under review**, **No relevant verified source found**.
- Click-through from every citation to the exact passage and, where available, original page/PDF.
- A visible explanation of why a result was retrieved and which exact passage supports the answer.
- Clear no-source state that never fills gaps with fabricated law.
- Filters for authority, instrument type, practice area, date range, in-force/repealed/unknown, and review state.

### P0 — Search quality and workflow
- One prominent search box accepting natural language, exact article/instrument number, and title/citation search.
- Search scope selector: verified corpus, firm documents, or all permitted sources; never silently blend them.
- Search results with snippets, Arabic term highlighting, exact article numbers, source status and sorting.
- Side-by-side source passage and answer; copy citation / copy passage / open source actions.
- Recent searches and saved research, with clear firm/user boundaries.
- Query suggestions and spelling/Arabic normalization feedback without silently rewriting legal meaning.

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

## Validation plan (not yet completed)
- Run a route-by-route browser audit at desktop, tablet and mobile widths.
- Test Arabic and English, RTL/LTR switching, long Arabic titles, keyboard-only navigation, zoom to 200%, contrast, forced colors and screen readers.
- Test slow network, empty results, no source, OCR failure, expired session, upload error and permission-denied states.
- Have 3–5 Egyptian lawyers complete core tasks and record success rate, time, errors and confidence.
- Run automated accessibility checks plus manual WCAG 2.2 AA review; automated checks alone are insufficient.

## Next UI task
Build the **Research Results & Source Inspector** as a complete workflow: query -> ranked results -> answer with verified citations -> inspect exact passage/version -> save to case or export memo. Include metadata-only and no-source states. This is the strongest differentiator for a legal copilot and directly improves trust even before the corpus is comprehensive.
