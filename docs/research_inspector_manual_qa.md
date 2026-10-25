# Research Inspector — Manual QA Checklist

**Purpose:** Record live-browser checks for issue #95. This checklist is a test procedure, not evidence that any check has passed.

## Run record

- Date/time:
- Tester:
- Commit/build:
- Environment: disposable staging or local test instance only
- Browser/version:
- Viewport / zoom:
- Language and direction: Arabic / RTL; English / LTR
- Test account role and firm: synthetic test account only
- Result: Not run / Pass / Fail / Blocked
- Evidence link or notes:

## Safety prerequisites

- [ ] Use a disposable staging/local database populated only with synthetic legal and matter records.
- [ ] Confirm no production client documents or real confidential case data are loaded.
- [ ] Confirm the test corpus clearly distinguishes verified fixtures from unverified and metadata-only fixtures.
- [ ] Record the tested commit and browser; do not treat automated CI as completion of this checklist.

## Research scope and source status

| Check | Expected result | Result / notes |
|---|---|---|
| Verified legal corpus scope | Results come only from the verified-corpus scope; each result shows recorded status and provenance. | |
| Firm documents scope with an accessible matter selected | Only that matter's documents are searched; passages remain labelled user-supplied/unverified. | |
| Firm documents scope without a matter selected | A clear prompt asks the user to select a matter; no blended search runs silently. | |
| Metadata-only discovery | Shows catalog metadata only and does not imply that text was retrieved, law is in force, or reuse is permitted. | |
| No relevant result | Shows an explicit no-source state and offers separate metadata discovery; does not imply that no applicable law exists. | |
| Unverified/outdated/secondary fixture | Status and caveat match recorded metadata; no unverified item is presented as verified operative text. | |
| Exact passage and pin-cite | Displayed passage matches stored text exactly; article/page values appear only when recorded. | |
| Version/provenance fields | Title, instrument number/year, version, authority, dates, as-of date, and source link are shown only when recorded. | |

## Citation, links, copy and export

| Check | Expected result | Result / notes |
|---|---|---|
| Copy citation | Clipboard contains the recorded citation, including available pin-cite, source URL and as-of date. | |
| Copy exact passage | Clipboard contains the stored passage, not a generated paraphrase. | |
| Clipboard API unavailable | Fallback either copies successfully and reports success or reports failure; it never falsely reports success. Temporary textarea is removed even if copying fails. | |
| Valid HTTPS source link | Opens the registered HTTPS URL in a new tab/window without giving the new page access to the opener. | |
| Invalid/non-HTTPS source URL | No clickable source link is rendered. | |
| Export memo with results | Download succeeds and includes question, scope, as-of date, answer, recorded citations, source statuses, exact passages and caveats. | |
| Export memo with no results | Memo states that no relevant verified passage was found and warns that this does not prove no applicable law exists. | |
| Save research to matter | Only the authorized conversation can be saved to a matter the user may access; saved note retains citations, scope, date and caveats. | |

## Keyboard, language, layout and assistive technology

| Check | Expected result | Result / notes |
|---|---|---|
| Keyboard-only navigation | All scope, matter, search, result, copy, open-source, export and save controls are reachable in a logical order. | |
| Focus visibility | Focus is always visible; dialogs and menus do not trap or lose focus unexpectedly. | |
| Arabic / RTL | Reading order, punctuation, article/page identifiers, status labels and controls remain understandable and correctly aligned. | |
| English / LTR | Layout and reading order switch correctly; no Arabic-only control labels remain where English labels are expected. | |
| Language switch during research | The current workspace remains usable and the search scope/matter selection is not silently changed. | |
| Narrow viewports (320–420 px) | No horizontal page overflow; source metadata and action controls wrap without overlap. | |
| Tablet and desktop | Source list and passage view remain readable; sticky panels do not cover content or controls. | |
| 200% zoom | Main actions and source details remain available without clipping or loss of functionality. | |
| Forced-colors / high contrast | Focus and status distinctions remain perceivable without relying on color alone. | |
| Screen reader | Page/section headings, result status, errors, and async loading/empty states are announced meaningfully. | |
| Loading, API error, expired session | Loading ends; errors are understandable; expired sessions return to authentication without exposing private result content. | |

## Release decision

- [ ] All critical checks pass.
- [ ] Failures are recorded as issues with reproduction steps.
- [ ] A lawyer has separately reviewed representative source authenticity, current legal status, pin-cites and answer quality.
- [ ] Cross-firm authorization and tenant isolation remain covered by automated/security tests; this browser checklist does not prove tenant isolation.
- [ ] Manual QA evidence is attached before issue #95 is marked complete.

**Do not mark manual QA complete if any critical check is blocked or untested.** This checklist does not establish legal correctness, corpus completeness, production security, or permission to reuse source material.
