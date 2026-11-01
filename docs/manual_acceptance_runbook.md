# Manual acceptance runbook

**Status:** preparatory procedure only. No manual lawyer, accessibility, physical-device, or production acceptance is claimed by this document.

## 1. Purpose and separation of gates

This runbook defines how to collect reproducible human acceptance evidence for the browser UI, accessibility, device behavior, research-inspector workflows, and legal-counsel review.

Keep these outcomes separate:

1. **Automated browser acceptance** — synthetic Playwright/Chromium tests run in CI. PR #1078 passed 6/6.
2. **Manual product/accessibility acceptance** — a human tester uses the pinned build on the listed browsers, devices, keyboards, and screen readers.
3. **Egyptian-counsel legal acceptance** — qualified Egyptian counsel reviews the exact legal sources, versions, citations, and permitted uses and records an explicit decision.
4. **Production operations acceptance** — authorized operators verify staging configuration, monitoring, provider behavior, and recovery.

Passing one gate does not satisfy another. This runbook itself is not evidence that any gate has passed.

## 2. Preconditions

Before testing:

- Pin the exact Git commit SHA and build identifier. Do not test a moving branch.
- Use a non-production environment with disposable synthetic firms, users, matters, documents, and citations.
- Keep SMTP/provider delivery disabled unless a separately approved staging exercise explicitly requires it.
- Do not upload live client documents, confidential matter text, credentials, or personal data.
- Record the tester's role, test date/time, timezone, operating system, browser/version, device model, viewport, locale, and assistive technology/version.
- Confirm the test account's firm and role before each scenario.
- Use only source records whose collection and test-use permissions are documented. Discovery-only candidates must remain non-authoritative and non-retrievable.

If any precondition is missing, mark the test **BLOCKED**, not PASS.

## 3. Required environment matrix

| Environment | Minimum manual pass |
|---|---|
| Windows 11 + current Chrome | Desktop layout, Arabic RTL, English LTR, keyboard |
| Windows 11 + current Edge | Desktop layout, Arabic RTL, English LTR, keyboard |
| macOS + current Safari | Desktop layout, Arabic RTL, English LTR, keyboard, VoiceOver |
| macOS + current Chrome | Desktop layout, Arabic RTL, English LTR, keyboard |
| iOS Safari on a physical iPhone | Touch layout, orientation, RTL/LTR, VoiceOver |
| Android Chrome on a physical Android device | Touch layout, orientation, RTL/LTR, TalkBack |
| NVDA with a supported desktop browser | Names, roles, values, headings, errors, focus announcements |

Record exact OS/browser/device versions. A desktop browser resized to a phone viewport does not replace physical-device testing.

## 4. Manual UI and accessibility checks

For each applicable environment, record PASS / FAIL / BLOCKED with observed behavior and evidence.

### RTL and LTR

- Switch between Arabic and English repeatedly; labels and direction must update without duplicated or stale controls.
- Arabic headings, paragraphs, forms, menus, tables, dialogs, breadcrumbs, and action buttons must follow RTL reading and visual order.
- English content must return to LTR without mirrored punctuation or misplaced controls.
- Mixed-direction identifiers, dates, phone numbers, URLs, citation references, and Latin abbreviations must remain readable and selectable.
- Long Arabic and English strings must wrap without clipping, overlap, or horizontal page overflow.

### Keyboard and focus

- Complete primary navigation and workflows using Tab, Shift+Tab, Enter, Space, and Escape where appropriate.
- Focus order must follow the visual and semantic order.
- Every interactive control must have a visible focus indicator.
- Dialogs and menus must receive focus appropriately, support keyboard dismissal, and return focus to the invoking control.
- No keyboard trap, hidden focus, or pointer-only action is acceptable.

### Screen readers

- Verify accessible names, roles, states, and values for navigation, forms, buttons, dialogs, status indicators, and controls.
- Verify heading hierarchy and meaningful landmarks.
- Loading, empty, success, and error states must be announced without requiring visual inspection.
- Form errors must be associated with the relevant field and described in text.
- Icon-only controls must expose an unambiguous accessible name.
- Do not treat a passing automated accessibility scan as a substitute for this check.

### Responsive layout and zoom

- Test portrait and landscape on physical phones.
- Test browser zoom at 200%; test 400% where the browser/viewport supports it.
- Verify dialogs, tables, citations, action bars, and navigation do not obscure essential content.
- Verify touch targets are usable and no essential action depends on hover.
- Confirm horizontal scrolling is limited to components that genuinely require it; the page itself must not overflow.

### Loading, errors, and actions

- Verify loading and empty states are distinguishable from errors.
- Verify retry and recovery actions are clear and do not silently duplicate writes.
- Verify citation copy, passage copy, memo export, and case-note save produce the expected result and visible confirmation.
- Verify failed actions do not display success messages or silently lose user input.
- Verify copied/exported material retains its source reference and does not add unsupported legal conclusions.

## 5. Research-inspector and legal-source workflow checks

Use only synthetic matters and approved test-source records.

- Open a search result and confirm the inspector shows the exact source identity, source status, version/date metadata, and relevant passage.
- Confirm citation page/article/paragraph references match the displayed source record.
- Confirm discovery-only or rights-restricted candidates are visibly distinguished and cannot be promoted into authoritative retrieval.
- Confirm a source with unknown permission/currentness is not represented as verified, current, or commercially reusable.
- Confirm copy/export actions preserve the citation and source identity.
- Confirm an unavailable source fails closed with a clear explanation; do not substitute a secondary catalogue entry as primary-law verification.
- Confirm any memo or case note saved to a matter is attached to the correct firm and matter.

A manual UI tester must not mark a legal source as verified merely because the inspector renders it successfully.

## 6. Firm-isolation checks

Use two synthetic firms with separate users and matter records.

- Firm A cannot view, search, copy, export, download, or save Firm B's matters, documents, notes, tasks, citations, or attachments.
- Change matter IDs, document IDs, and request parameters where the test harness permits; authorization must still be enforced server-side.
- Expired or revoked sessions must not retain access through an already-open browser tab.
- A user with a platform-review role must not gain access to firm matter content beyond the explicitly authorized metadata-only workflow.
- Record both the expected denial and the actual response. Do not include real matter content in screenshots or logs.

Any cross-firm disclosure is an immediate FAIL and release blocker.

## 7. Egyptian-counsel legal acceptance

This is a separate professional review, not a UI test and not something CI can satisfy.

Before requesting counsel acceptance:

- Confirm the exact original primary-source bytes and cryptographic hash through a lawful acquisition route.
- Resolve the relevant Gazette publication reference against the original Gazette, not a secondary catalogue alone.
- Verify amendments, commencement, currentness, and relevant transitional provisions.
- Record item-specific collection, storage, display, and commercial-reuse permissions. An official locator or an all-rights-reserved notice is not a reuse grant.
- Provide counsel the exact source version, source provenance, relevant passages, citations, and known limitations.
- Verify counsel qualification and identity through an approved independent process.
- Obtain a written, explicit acceptance or rejection for the defined application scope. Preserve the signed record in the authorized private evidence store.

No counsel response, unsigned email, UI checkbox, PR approval, or passing test may be inferred to mean legal acceptance. Until written acceptance exists, the counsel-acceptance gate remains **0%**.

## 8. Evidence record

For every test, record:

| Field | Required value |
|---|---|
| Test ID | Stable identifier from the checklist |
| Build | Exact commit SHA and build identifier |
| Result | PASS, FAIL, or BLOCKED |
| Tester | Authorized tester role; identity stored only in the approved private record |
| Environment | OS, browser/version, device, viewport, locale, assistive technology |
| Date/time | ISO 8601 timestamp with timezone |
| Expected result | Test-specific assertion |
| Observed result | Concise factual description |
| Evidence | Sanitized screenshot/video/log reference and SHA-256 where retained |
| Defect | Issue/PR link for every failure |
| Sign-off | Authorized reviewer and date, stored in the private evidence record |

Evidence must be sanitized before attaching it to public repository issues or pull requests. Never attach credentials, live client data, personal data, or confidential legal material.

## 9. Decision rules

- **PASS:** every required assertion for that test is met and evidence is retained.
- **FAIL:** any required assertion is not met. Create a defect and block the relevant acceptance gate.
- **BLOCKED:** required environment, source permission, primary-source bytes, reviewer, or provider access is unavailable. A blocked test is not a pass and must not increase completion.
- **NOT APPLICABLE:** allowed only with a written scope reason and reviewer approval.

A release gate is complete only when all required tests for that gate have PASS evidence and the authorized sign-off is recorded. Manual product acceptance, legal-counsel acceptance, and production operations acceptance must be reported separately.

## 10. Current known boundaries

- Automated Chromium acceptance passed 6/6 in PR #1078; this does not complete physical-device, screen-reader, or manual lawyer-workflow acceptance.
- The verified Egyptian legal corpus remains separately measured; this runbook does not add legal content or source rights.
- Live SMTP/provider staging, external scheduler monitoring, provider reconciliation, and witnessed production recovery remain separate operational tasks.
- Final Egyptian-counsel acceptance remains a mandatory independent gate.
