# AI-2 local end-of-day test handoff — 26 November 2026

**Status:** preparation only. No local runtime, Python tests, browser, or app startup was executed by the remote review. Use synthetic data only; this is not pilot approval.

## 0. Confirm the exact checkout and supported runtime

From the project root (the folder containing `app.py`):

```sh
git status --short --branch
git rev-parse HEAD
git log -5 --oneline
python3 --version
python3.12 --version
```

Stop if the working tree has unexplained changes: do not reset, clean, stash, or overwrite them. The repository's locked test runtime is **Python 3.12**; Python 3.13/other versions are not equivalent. If Python 3.12 is not installed, report that and defer Python test commands rather than silently substituting.

## 1. Clean, isolated Python 3.12 environment

Use an isolated virtual environment and hash-locked dependencies (do not install into the system interpreter):

```sh
python3.12 -m venv .venv-ai2-test
source .venv-ai2-test/bin/activate
python -m pip install --upgrade pip==26.2.2
python -m pip install pip-tools==7.6.2
python -m pip install --require-hashes -r requirements-py312.lock
python -m pip --version
python -m piptools --version
```

If lock installation fails, capture the full error and stop there; do not alter the lock or install unpinned dependencies to make tests proceed.

## 2. Focused tests first (fast, relevant)

```sh
python -m unittest tests.test_frontend_ux_contract
python -m unittest tests.test_route_auth_audit
python -m unittest tests.test_route_sql_access_audit
python -m unittest tests.test_tenant_route_inventory_coverage
python -m unittest tests.test_tenant_context
python -m unittest tests.test_tenant_context_transaction_boundary
python -m unittest tests.test_tenant_database_preflight
python -m unittest tests.test_tenant_catalog
python -m unittest tests.test_tenant_storage
python -m unittest tests.test_tenant_write_failure_diagnostics
python -m unittest tests.test_security_audit_read_separate_runtime
python -m unittest tests.test_app_separate_database_runtime
python -m unittest tests.test_auth_rate_limits_separate_runtime
python -m unittest tests.test_mfa_account_security
python -m unittest tests.test_document_intelligence
python -m unittest tests.test_document_review_workflow
python -m unittest tests.test_invoice_payment_routes
python -m unittest tests.test_subscription_billing_routes
```

These are prioritized coverage slices, not an assertion that each is currently green. If a test fails, record its exact command, traceback, and first failure; do not rerun unchanged failures repeatedly.

## 3. Security/tenant matrix

After focused tests, run the curated existing security matrix:

```sh
bash scripts/security_regression_check.sh
```

Use fresh synthetic Firm A/Firm B accounts. Confirm both directions of cross-firm case/document/task access are denied and reveal no sentinel values. Exercise role-restricted actions, MFA enrollment/challenge, rate limits, logout/session revocation, and recovery only through existing tests and isolated test accounts. Do not test with client data or real accounts.

## 4. Database/migration and recovery checks

```sh
python -m unittest tests.test_database_runtime
python -m unittest tests.test_tenant_fleet_migration
python -m unittest tests.test_invoice_schema_migration
python tests/test_database_recovery_drill.py
```

Recovery drill is destructive only to its own temporary synthetic fixtures; confirm the module's fixture behavior if uncertain before executing. Do not point these checks at any real/local firm database.

## 5. Frontend contracts and browser tests

```sh
python -m unittest tests.test_frontend_ux_contract
python -m unittest tests.test_subscription_audit_frontend_contract
```

Browser acceptance is optional for this first pass if its pinned browser dependencies are not already available; avoid spending the test window installing browsers until Python focused tests/security are complete. If dependencies are already installed:

```sh
python -m playwright install chromium
python -m unittest tests.browser.test_acceptance
```

The browser suite may require separate setup described in `docs/browser_acceptance_harness.md`. Do not claim accessibility certification from automated axe checks.

## 6. Full regression and release checks (only after focused tests)

```sh
python tools/run_local_test_suite.py
bash scripts/local_release_check.sh
```

The runner and release gate are Python-3.12-only. The release gate may report BLOCKED for Docker, dependency audit tools, actionlint, or recovery prerequisites; retain those statuses instead of calling the whole run a pass. Do not re-run already-passing focused modules unnecessarily.

## 7. App startup for a synthetic local workspace

Prefer the existing repository launcher/bootstrap documented in `README.md` and `docs/DEPLOY.md`; first read the launch section and choose its supported fresh-workspace flow. Do not invent environment variables or run first-firm initialization against an existing database. Keep all database/storage paths in a temporary test workspace. Confirm the app binds to loopback, then use the local browser URL printed by the launcher. Shut down cleanly after the session.

## 8. Browser acceptance checklist

- Login/logout, session expiry/revocation, MFA-required and MFA challenge/enrollment behavior.
- Firm switch and role permissions; no Firm A/Firm B data bleed.
- Client create/edit/read; case create/edit/status/search; reload and confirm persistence.
- Tasks create/assign/edit/complete/retrieve; due dates and calendar filters display Cairo-local day.
- Sessions and notes; activity history.
- Upload synthetic PDF and DOCX; validate size/type rejection; inspect extraction and page provenance; search/read/review/compare; download and confirm integrity; try unauthorized download.
- Billing/subscription/trial/seat-limit display; invoice records; manual payment submit/review with validation and visible feedback.
- Arabic ar-EG: RTL direction, long Arabic names/text, mixed Arabic/English identifiers, no clipped forms or horizontal overflow.
- English en-US: LTR, navigation and labels.
- Desktop viewport and phone viewport: buttons/forms usable, dialogs fit, keyboard focus visible, loading/error/empty states readable, no JS console errors.
- Confirm refresh/relogin preserves saved state. Avoid real client documents or payment credentials.

## 9. Report failures and evidence

For each failure send back:
- Commit SHA and clean/dirty status (redact any private paths/secrets).
- Python version, OS, browser and browser version, viewport/locale.
- Exact command, full first traceback or console error, failing assertion, and test fixture context.
- Expected vs actual behavior, whether data persisted, and whether cross-firm/authorization leakage occurred.
- Mark test **PASS / FAIL / BLOCKED / NOT RUN**. Attach only sanitized screenshots/logs with synthetic data. If an access-control leak, secret exposure, or unexpected data deletion is observed, stop testing and report immediately.

## 10. Scope / release warning

This handoff optimizes the owner's final local test window; it is not proof of readiness. Local tests, browser/device acceptance, two-firm security tests, supported runtime, clean migration, and witnessed backup/restore are still required before a supervised firm pilot. AI-1's legal evidence/retrieval validation remains a separate gate.


## Follow-up added after handoff preparation

- Backup archive preflight now rejects file/directory path collisions in either ZIP member order.
- The regression test explicitly permits a valid directory entry (for example, `folder/`) with a nested file (for example, `folder/item.sqlite3`), while rejecting a regular file used as a directory or parent.
- This is a source/test correction only. The backup-bundle test module has **not** been executed in this environment; run it in the planned local Python 3.12 session.

- A second archive preflight hardening pass now rejects ZIP member names that alias after case-folding or Unicode NFC normalization, including file-as-parent collisions in either member order. This protects restore behavior on common case-insensitive macOS/Windows filesystems. Regression fixtures cover case-only and composed/decomposed Unicode aliases; these tests remain unexecuted pending the planned local run.
