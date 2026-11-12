# Hybrid Legal Workspace UI

## Product direction

The workspace uses a restrained light visual system for daily legal-office operations. The dashboard prioritizes active matters, assigned work, upcoming hearings and deadlines, fees, and direct access to common actions. Legal Research uses a dedicated evidence-inspection layout rather than presenting source provenance as an afterthought.

## Dashboard

The dashboard includes a short list of active matters drawn from the same case records returned to the signed-in user by the existing cases API. Each row opens the existing case-detail view. The panel does not perform a broader search, bypass case permissions, or introduce a new data endpoint; the full case list remains available through the existing navigation.

## Legal Research layout

- **History pane:** saved conversations, filtering, rename, delete, and new conversation actions. The pane can be collapsed and expanded with a keyboard-operable disclosure control; its `aria-expanded` state tracks visibility.
- **Research pane:** scope and matter selectors, conversation thread, answer/source cards, and persistent composer.
- **Source inspector:** opens from an explicit “Inspect source” action on a returned source card. It presents the returned citation/reference, article/page locator, recorded source and legal-version metadata, search as-of date, source status/trust tier, latest review event per review type, amendment-history status, and exact passage text.

The source inspector is a view of data already returned by the research API. It does not make a new source-verification decision and does not mutate the source, answer, legal status, review state, or trust tier. The inline source card remains available, as do copy, export, correction, save-to-matter, and safe source-link actions. Opening the inspector moves keyboard focus to its region; the Clear source control or Escape key closes it and returns focus to the invoking source action. The invoking control exposes `aria-controls` and keeps `aria-expanded` synchronized with the inspector's open/closed state.

If no passage text is returned, the inspector says so explicitly; it does not invent a quotation. Metadata-only discovery remains visibly metadata-only and does not display legal text.

## Responsive behavior

- **Desktop (>1120px):** history, research thread, and source inspector are visible in three columns.
- **Tablet (801–1120px):** history and thread share the first row; source inspector occupies a second row.
- **Phone (<=800px):** history, thread/composer, and inspector stack in one column. History and inspector have bounded scroll regions to keep the thread usable.

The layout uses logical inline borders and text alignment so Arabic RTL and English LTR can share the same structure. Existing navigation landmarks, skip link, focus styles, and reduced-motion preferences remain in place.

## Evidence and security invariants

- No API route, request payload, authorization rule, tenant scope, or retrieval behavior is changed.
- Source and provenance values are inserted as text, not interpreted as HTML.
- External source links continue to require safe HTTPS URLs and use rel="noopener noreferrer".
- The displayed source status and trust tier are taken from the returned record. The UI does not promote a source to verified or infer currentness from a URL, registry link, or model output.
- Only the latest recorded review event per review type is shown in the inspector, matching the existing source-card behavior.
- Missing amendment history, review evidence, pin-cites, dates, or passage text remain visibly missing; they are not inferred.

## Acceptance coverage

The frontend contract test checks the three-pane layout, source-inspection action, latest-review selection, and responsive panel bounds. The browser acceptance test exercises source inspection using a synthetic matter-document sentinel and checks for horizontal overflow at 390px.

These tests must be run locally on the pinned Python 3.12 environment. Browser viewport assertions do not replace witnessed physical-device acceptance in Arabic and English on a phone and desktop. No test pass or physical-device acceptance is claimed by this document.
