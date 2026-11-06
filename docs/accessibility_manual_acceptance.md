# UI and accessibility manual acceptance checklist

**Status:** Not yet executed. This document is a test protocol, not evidence of conformance.  
**Target:** Exact candidate build deployed to a controlled staging environment.  
**Standard:** WCAG 2.2 AA, with Arabic RTL and English LTR coverage.

## 1. Test identity and evidence

Record before testing:

- Build/commit SHA, deployment environment and browser versions
- Tester name/role, date, time zone and test device
- Screen-reader and assistive-technology versions
- Locale, direction, viewport dimensions and zoom level
- Screenshots or short recordings for visual defects; sanitized DOM/console evidence where useful
- Each test result as Pass, Fail, Blocked or Not Run; include reproduction steps and linked issue IDs

Do not record real client names, matter contents, personal data or confidential legal documents in evidence. Use synthetic pilot fixtures.

## 2. Required environment matrix

| Area | Minimum coverage |
|---|---|
| Language/direction | Arabic RTL and English LTR |
| Widths | 320, 360, 390, 640, 768, 1024 and 1440 CSS px |
| Zoom/reflow | 200% and 400% browser zoom; verify no loss of content or two-dimensional scrolling for ordinary content |
| Browsers | Current Chrome/Edge and Firefox; Safari where supported by the pilot device fleet |
| Screen readers | NVDA with Firefox or Chrome; VoiceOver with Safari on macOS/iOS |
| Input | Keyboard only, mouse, touch; no pointer-only workflow |
| Preferences | Forced-colors/high-contrast mode and reduced motion |

Automated axe-core checks are regression support only. They do not replace this matrix.

## 3. Keyboard and focus

- [ ] Every navigation item, tab, filter, disclosure, action and form control is reachable in a logical order.
- [ ] Native buttons activate with Enter and Space; links activate with Enter.
- [ ] Focus indicator is visible and not obscured by sticky navigation, dialogs or banners.
- [ ] Opening a dialog moves focus into it; Tab and Shift+Tab remain inside it.
- [ ] Escape closes dismissible dialogs; focus returns to the invoking control.
- [ ] Background content cannot be operated while a modal dialog is open.
- [ ] No keyboard trap exists outside modal focus containment.
- [ ] Skip link moves focus to the main content landmark.
- [ ] Sticky headers, horizontal navigation and scrollable panels do not hide focused elements.

## 4. Screen-reader semantics and dynamic updates

- [ ] One clearly named primary navigation landmark and one main landmark are present.
- [ ] Heading levels describe the page hierarchy without skipped levels used only for styling.
- [ ] Every input, select, textarea, checkbox and file input has a persistent visible label or an appropriate accessible name.
- [ ] Required fields and invalid fields are exposed programmatically.
- [ ] Validation errors are associated with their fields; submission failures provide a discoverable summary or focused error.
- [ ] Disclosure buttons expose accurate `aria-expanded` and `aria-controls` values.
- [ ] Dialogs expose dialog semantics, an accessible name and modal state.
- [ ] Loading, success and empty states are announced politely; urgent errors use alert semantics without duplicate announcements.
- [ ] Tables expose meaningful header relationships; icon-only controls have accessible names.
- [ ] Arabic labels, mixed Arabic/Latin citations, numbers and dates are read in a comprehensible order.

## 5. Visual accessibility and responsive behavior

- [ ] Normal text meets 4.5:1 contrast; large text meets 3:1.
- [ ] Required component boundaries, state indicators and focus indicators meet applicable non-text contrast requirements.
- [ ] Status is not communicated by color alone; labels/icons/text distinguish status.
- [ ] Text remains readable at 200% and 400% zoom without clipping or overlapping.
- [ ] At 320 CSS px, ordinary content reflows without page-level horizontal scrolling.
- [ ] Long Arabic and Latin legal citations wrap without covering actions or breaking card layout.
- [ ] Touch targets meet the product's 44px target contract and remain sufficiently separated.
- [ ] Forced-colors mode preserves focus, active navigation, borders and status distinction.
- [ ] Reduced-motion preference suppresses nonessential animation and smooth scrolling.

## 6. Critical workflow scenarios

Run every scenario in both Arabic RTL and English LTR:

1. Sign in, complete MFA challenge/enrollment where applicable, and recover from a validation error.
2. Navigate dashboard, cases, tasks, calendar, legal research, corpus coverage, review workbench and settings using keyboard only.
3. Open and dismiss new-case and client-profile dialogs; verify focus containment and restoration.
4. Create/edit a synthetic case and use case tabs, team controls, deadlines and document upload.
5. Review extracted document chunks; verify loading, loaded count, empty state and errors are announced.
6. Run an AI brief with synthetic authorized data; verify authorization checkboxes, progress, completion and error announcements.
7. Use legal research search/results/source inspector; verify result updates, citation links and empty/error states.
8. Use billing/payment and account forms; verify field names, required state, errors and confirmation announcements.
9. Use filters, sorting, pagination and empty states at narrow widths and zoom.
10. Switch language while on each major workspace; verify content, direction, labels and focus remain coherent.

## 7. Exit criteria

- All critical workflow checks pass in both languages.
- No unresolved critical/high accessibility defects; all remaining defects have an owner, severity and mitigation.
- Automated axe-core WCAG 2.1 A/AA and 2.2 AA scans pass on the exact candidate build, with justified exceptions documented.
- Keyboard, screen-reader, zoom/reflow, contrast, forced-colors and reduced-motion checks are recorded.
- Product owner and accessibility reviewer sign the exact build record.

**Release rule:** Until the above evidence exists, describe the product as having accessibility improvements and automated regression coverage—not as WCAG 2.2 AA conformant.
