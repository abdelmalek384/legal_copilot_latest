# Browser acceptance harness

The Playwright suite launches the application in a dedicated local server thread and provisions fresh synthetic control-plane, firm, and legal-corpus databases in a temporary directory. It never reads the developer's configured database paths or production records.

## Run locally

From the repository root, with Python 3.12:

    python -m pip install -r requirements.txt -r requirements-browser.txt
    python -m playwright install chromium
    python -m unittest tests.browser.test_acceptance

The suite chooses an available loopback port, creates synthetic accounts and fixtures, starts Uvicorn in-process, and deletes its temporary database directory after the run. No real legal text, client matter, external source fetch, SMTP delivery, or model API approval is used.

## Automated coverage

- Platform legal-reviewer authorization for Corpus Coverage; firm administrators without the platform role are denied.
- Metadata-only catalog drill-down, with synthetic cross-firm sentinel checks.
- Firm-document search from an uploaded synthetic text file, including the required matter selection.
- Separation between firm-document search, verified-corpus search, and metadata-only discovery.
- Cross-firm case-ID denial without returning the other firm's sentinel.
- End-to-end synthetic case-management lifecycle: two cases for one client, case metadata edits, associate assignment, task completion, court session, notes, deadline, fee record, document extraction record, activity history, member removal, and deletion of both synthetic cases with verification of the firm-scoped immutable audit snapshot; the case list is checked in Chromium.
- Arabic RTL and English LTR page direction, desktop/mobile horizontal-overflow checks, and basic keyboard focus movement.

The firm-document fixture deliberately leaves LLM_FIRM_DATA_PROCESSING_APPROVED unset. The application therefore returns matching matter passages without sending them to an LLM. This verifies retrieval scope and display without authorizing confidential matter data for model processing.

## CI and artifacts

The dedicated Browser acceptance workflow installs the pinned Playwright Python dependency and Chromium, then runs the suite with a 12-minute job timeout. Screenshots are uploaded only when the job fails, and the artifact retention is three days. Screenshots contain synthetic fixture data only. No browser trace, request body, cookie, credential, or token artifact is collected.

## Separate manual gates

Passing this suite does not complete the manual checklists in:

- docs/research_inspector_manual_qa.md
- docs/corpus_coverage_manual_qa.md
- docs/device_browser_acceptance_runbook.md

A human must still record the exact commit, browser/device, screen-reader/keyboard checks, source/pin-cite review, and lawyer acceptance. Browser CI does not establish legal correctness, corpus completeness, accessibility certification, or production readiness.
