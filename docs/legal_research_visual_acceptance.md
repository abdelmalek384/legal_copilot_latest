# Legal Research visual acceptance checklist

**Status:** Not run. This document is the manual acceptance plan for the Phase 5 UI implementation. It is not evidence that the checks passed.

## Required test environments

Use the same release candidate commit for all runs. Capture the exact commit SHA, browser/version, operating system, viewport dimensions, locale, account role, firm, and corpus fixture for every screenshot.

| Viewport | Locale | Direction | Required evidence |
|---|---|---|---|
| 1440 × 900 | English | LTR | Full-page workspace and one citation-open state |
| 1440 × 900 | Arabic | RTL | Full-page workspace and one citation-open state |
| 390 × 844 | English | LTR | Full-page workspace, open upload panel, and citation-open state |
| 390 × 844 | Arabic | RTL | Full-page workspace, open upload panel, and citation-open state |

## Test identities and corpus fixtures

- Ordinary firm user without platform legal-review permission.
- Platform legal reviewer with access to the existing legal-review coverage endpoint.
- A reviewer-visible corpus fixture with zero verified operational documents.
- A reviewer-visible corpus fixture with at least one verified operational document.
- A controlled answer fixture whose backend trust_tier is source_matched; it must remain labelled as not lawyer-reviewed.
- A firm matter containing at least one permitted PDF or DOCX upload fixture.

Do not promote synthetic source records to verified legal material. The source-matched fixture must remain explicitly unreviewed.

## Visual and interaction checks

### Question-first composer

- [ ] The question composer is the first primary content area above the conversation thread.
- [ ] Four example questions are visible when the thread has no messages; clicking one populates the input and does not send it.
- [ ] The empty-state message is text only, appears above the input only when there are no messages, and disappears after the first message.
- [ ] “Research assistance, not legal advice” remains legible beside the question heading/input in both locales.
- [ ] Enter sends; Shift+Enter inserts a newline.

### Scope and matter controls

- [ ] Segmented controls show Verified law, Firm documents, and Source catalog with a clear selected state.
- [ ] The matter picker and Open document intelligence action are visible only in Firm documents scope.
- [ ] Switching away from Firm documents clears and hides the previously opened matter workspace.
- [ ] The paperclip is disabled until Firm documents scope and a matter are selected; its tooltip explains the missing prerequisite.
- [ ] The upload panel opens beside/below the composer, spans its width, and contains no large dashed drop area.

### Corpus and trust status

- [ ] A platform legal reviewer sees the count derived from verified operational documents, not raw metadata rows or merely labelled versions.
- [ ] A zero count is stated plainly and the UI explains that the assistant abstains rather than guesses.
- [ ] An ordinary firm user is told that the aggregate count is restricted to legal reviewers; the UI does not attempt the reviewer-only endpoint.
- [ ] The test-mode chip appears only when the backend returns trust_tier=source_matched and says the answer is not lawyer-reviewed.
- [ ] No model-authored text or user-supplied flag can change a source's verification status.

### History, source inspector, and ratings

- [ ] History starts collapsed and expands/collapses using its labelled control.
- [ ] Starting a new conversation does not create a server conversation until the first message is sent.
- [ ] The Conversations heading does not wrap or cause horizontal overflow in either locale.
- [ ] The source inspector is absent until a citation is selected; on wide screens it occupies the right column only while open.
- [ ] Closing the inspector restores focus to the citation control that opened it.
- [ ] Each assistant answer has Correct, Partial, and Wrong rating choices and a reviewer-notes field.
- [ ] View firm ratings and Export CSV are available inside the closed-by-default overflow menu for authorized admins only.
- [ ] The global Search matters bar is absent on Legal Research while the main application navigation remains unchanged.

## Accessibility and responsive checks

- [ ] Keyboard-only operation reaches every scope tab, example chip, input action, history toggle, citation, inspector close control, rating choice, and overflow action.
- [ ] Focus indicators are visible against the light surfaces and navy navigation.
- [ ] Selected segmented/rating states are exposed through accessible pressed state.
- [ ] No horizontal page overflow occurs at 390px in Arabic or English.
- [ ] The inspector, composer, chips, upload panel, and rating controls remain usable when stacked at phone width.
- [ ] Browser zoom at 200% does not hide the input, Send control, or active source details.
- [ ] Reduced-motion preference does not introduce unwanted transitions.

## Sign-off record

Record one row per viewport/locale run:

| Commit | Browser / OS | Viewport | Locale | Role / fixture | Result | Screenshot path | Reviewer |
|---|---|---|---|---|---|---|---|
| Pending | Pending | 1440 × 900 | English | Pending | Not run | Pending | Pending |
| Pending | Pending | 1440 × 900 | Arabic | Pending | Not run | Pending | Pending |
| Pending | Pending | 390 × 844 | English | Pending | Not run | Pending | Pending |
| Pending | Pending | 390 × 844 | Arabic | Pending | Not run | Pending | Pending |

**Acceptance rule:** Phase 5 is not visually accepted until all four viewport/locale rows are executed, screenshots are attached, keyboard/focus checks pass, and any defects are resolved. This checklist does not replace legal review or production release gates.
