# Device and browser acceptance runbook

**Purpose:** collect reproducible manual evidence for the Arabic-first web application and installable PWA. This is a test procedure, not a claim that any device has passed.

## Safety rules

- Use a dedicated test firm and synthetic clients/cases only. Never use real client-confidential files or production credentials.
- Test against a staging or local environment, not a public production tenant.
- Record the exact application commit, configuration profile, OS/build, browser/version, locale, viewport, and test date.
- Do not capture screenshots containing passwords, session cookies, tokens, real personal data, or secret configuration.
- Stop immediately and record a security defect if one firm can access another firm's records, offline mode exposes matter content, or an unauthorized user can perform a privileged action.

## Required device matrix

| Platform | Minimum manual run | Key acceptance points |
|---|---|---|
| macOS (Apple Silicon) | Current supported Safari and Chromium browser | Mac launcher, fresh first-run setup, Arabic/RTL, keyboard, installability where supported |
| Windows 10/11 | Current supported Edge and Chrome | Windows launcher, path handling with spaces, fresh first-run setup, Arabic/RTL |
| Android phone | Current Chrome | Add to Home Screen/install flow, portrait/landscape, touch targets, offline privacy |
| iPhone/iPad | Current Safari | Share → Add to Home Screen, standalone launch, viewport/safe-area behavior, offline privacy |
| Tablet/large viewport | One supported browser | Responsive navigation, two-column layouts, no clipped controls |

At minimum, record desktop and phone runs. For a release-gate pass, cover desktop and phone in both ar-EG and en-US (four distinct device-class/locale cells) against the same application commit and environment. Additional OS/browser combinations in this table remain separately tracked; passing the minimum matrix does not certify every listed platform. Do not mark untested platforms as passed.

## Test sequence

### A. Installation and startup

1. Start from a clean test workspace with no existing application virtual environment.
2. Run the platform's documented launcher. Confirm it refuses unsupported Python versions and legacy `COPILOT_DB` mode.
3. Confirm the first-firm bootstrap runs once, prompts only when no active firm owner exists, and does not reset or delete existing database files.
4. Restart the launcher with an existing active firm owner. Confirm it does not create a duplicate firm or owner.
5. Confirm the server binds to loopback for local development and the browser reaches the login screen.
6. Record setup duration, exact error text (if any), and whether a restart succeeds.

### B. Authentication and firm isolation

1. Create two synthetic firms with distinct users and unique synthetic case titles.
2. Log in as Firm A. Confirm Firm A's dashboard and case list contain only Firm A data.
3. Attempt direct navigation/API access to Firm B case, document, task, and audit resources using Firm A's session. Every attempt must be denied without revealing Firm B data.
4. Repeat in the opposite direction.
5. Test logout, session revocation, browser restart, and MFA enforcement using the configured staging policy.
6. Confirm the UI does not reveal hidden admin/reviewer actions to a user lacking those server-authorized capabilities.

### C. Primary case-management workflow

Using synthetic data, perform and record each operation:

1. Create one client and two separate cases for that client.
2. Edit case number/year, court, circuit, stage, status, and opposing-party metadata.
3. Add lead, associate, and junior team members; verify role-specific access.
4. Create, assign, edit, complete, and reopen tasks where permitted.
5. Record a court session with date and notes.
6. Create a legal deadline with type and date; verify it remains distinct from a court session.
7. Add case notes and fees; verify totals and due dates.
8. Upload a small synthetic PDF and Word document; review extracted chunks and OCR status before relying on the text.
9. Confirm activity history records the relevant actor and action without exposing another firm's events.
10. Remove a case member and confirm access is revoked immediately.
11. Delete only a synthetic test case; confirm the immutable deletion snapshot preserves the expected audit metadata and that its retrieval/export remains firm-scoped and admin-only.

### D. Legal research and abstention

1. Search the verified legal corpus with an exact Arabic article reference and confirm the answer's citation opens the matching source.
2. Search with Arabic-Indic digits, alef/hamza variants, and a common Arabic phrase.
3. Search a case's own documents with the case selected; confirm the scope is visibly identified and access is case-authorized.
4. Run a metadata-only source discovery query. Confirm it does not present metadata as legal text.
5. Ask a question for which the selected corpus has no source. Confirm the assistant abstains or reports not found rather than inventing a statute or citation.
6. Ask a question with a source outside the selected scope. Confirm it is not silently used.
7. Verify that fictional sample data is visibly marked and never presented as authoritative law.

### E. Arabic, English, accessibility and responsive layout

1. Switch Arabic → English → Arabic on dashboard, clients, cases, tasks, calendar, research, review queue, and settings. Confirm labels, status, dialogs, and validation messages follow the selected language.
2. Confirm Arabic screens use RTL direction and English screens use LTR direction; mixed Arabic/English case titles remain readable.
3. Navigate every primary action using keyboard only. Confirm visible focus and logical focus order.
4. Open and close dialogs using keyboard; confirm focus is trapped while open and returned to the opener when closed.
5. Test 200% browser zoom, narrow phone width, landscape orientation, and reduced-motion preference.
6. Use a screen reader on the login screen, primary navigation, form validation, and research status announcements. Record the screen reader and OS version.
7. Confirm no horizontal page overflow or clipped buttons at supported viewport widths.

### F. PWA installation and offline privacy

1. Serve the app over HTTPS (or localhost for a local test) and confirm the manifest, icons, and service worker load without console errors.
2. Install from Android Chrome, iOS Safari's Add to Home Screen flow, and desktop browser where supported.
3. Launch from the installed icon. Confirm the Arabic app name/icon and standalone behavior.
4. With DevTools/Application storage open, inspect the service worker's cache. Only the fixed static offline notice may be cached.
5. Go offline and reload the top-level page. Confirm the offline notice appears and no previously viewed client, case, legal research, API, upload, account, or session data is available.
6. While offline, attempt a case/API route and confirm it is not served from cache.
7. Restore network and confirm normal login is required before matter data becomes available.
8. Clear site data and confirm cached offline content is removed.

### G. Deployment smoke probe

Against a controlled HTTPS staging URL, run the read-only probe:

```bash
python tools/deployment_http_smoke.py https://staging.example.invalid
```

Replace the example hostname with the approved staging origin. The probe must be run by an authorized operator; it does not log in or access matter APIs. Record its JSON report and the exact deployed commit. A successful public-shell probe does not prove authenticated workflows or tenant isolation.

## Evidence record template

Create one record per device/browser/locale combination. Set device_class to desktop, phone, or tablet. Use `PASS`, `FAIL`, `BLOCKED`, or `NOT_TESTED`; never infer a pass from automated CI.

```json
{
  "record_version": 1,
  "tested_at": "YYYY-MM-DDTHH:MM:SS+02:00",
  "application_commit": "full-git-commit-sha",
  "environment": "local-or-staging",
  "os_and_build": "exact OS/build",
  "device": "device model",
  "device_class": "desktop",
  "browser_and_version": "browser/version",
  "locale": "ar-EG or en-US",
  "viewport": "width x height; orientation",
  "network": "online/offline cases tested",
  "tester_role": "synthetic firm administrator/lawyer/associate/junior",
  "results": {
    "installation": "NOT_TESTED",
    "authentication_and_isolation": "NOT_TESTED",
    "case_management": "NOT_TESTED",
    "legal_research_and_abstention": "NOT_TESTED",
    "arabic_and_english": "NOT_TESTED",
    "keyboard_and_screen_reader": "NOT_TESTED",
    "pwa_offline_privacy": "NOT_TESTED",
    "deployment_smoke": "NOT_TESTED"
  },
  "defect_ids": [],
  "evidence_paths": [],
  "notes": "No secrets or client data"
}
```

Store completed evidence in the restricted release workspace, not in a public repository if it contains internal hostnames, account details, or screenshots.

## Acceptance rule

The device workstream is complete only when the minimum desktop/phone × Arabic/English matrix is present for one exact commit/environment, all mandatory tests pass, and no unresolved high/critical usability, privacy, or authorization defect remains. A runbook, static contract test, or CI pass is not a substitute for a manual run.
