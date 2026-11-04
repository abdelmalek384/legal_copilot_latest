# Changelog — Legal Copilot

- Extend Chromium acceptance at 390px and desktop widths to calculate deadlines from an explicitly draft rule, inspect its explanation, issue an invoice, and download the audited firm export.

- Pin the production container to the CI-tested Python 3.12 image and block Dependabot major/minor Python image updates pending explicit version-specific CI (PR #1366).

- Resolve client IPs through an explicit trusted-proxy allowlist for rate limits, login lockouts, and recovery throttles; document the required forwarded-header overwrite.

- Extended the evidence-only corpus comparator to accept official PDF references directly, preserve per-article PDF page ranges, hash the source file, and warn on pages without extractable text; does not authenticate or verify legal content.

- Reject future-dated qualified-counsel answer reviews so evaluation reports cannot count assessments dated after the current day.

- Added a separate, data-driven Arabic legal retrieval lexicon with conservative spelling variants and synthetic top-three retrieval regressions (PR #1148).
- Added fictional fixture-only legal-ingestion tests for manual-capture hash integrity, article comparison, numeric mismatch detection, and commencement-date extraction (PR #1151).
- Added a policy proposal for a separately gated, production-disabled source-matched/unreviewed trust tier without weakening existing lawyer-approval gates (PR #1150).
- Added an opt-in, fail-closed factual claim-support check for cited answers, including finite-period contradiction tests; disabled by default (PR #1154).
- Added Arabic claim-support regressions for no-limitation assertions contradicted by a finite period and a faithful five-year paraphrase; feature remains opt-in and heuristic (PR #1178).
- Added `ask()` integration regressions proving the optional claim-support screen returns sources only on failure when enabled and is bypassed when disabled (PR #1182).
- Set `must_abstain_if_unverified=true` across all 94 unreviewed multi-area questions and separated the seven inherently out-of-scope cases into a distinct `must_abstain` field (PR #1177).
- Added a cross-dataset CI invariant requiring all 251 currently unreviewed legal evaluation questions to default to abstention when sources are unverified (PR #1183).
- Required the retrieval-quality evaluator to validate reviewer identity, counsel role, practice-area authorization, review date, and HTTPS evidence against the approved reviewer registry before scoring labels.
- Enforced canonical `YYYY-MM-DD` dates for legal `as_of` retrieval inputs so ISO week-date/compact forms cannot reach lexicographic SQL date boundaries.
- Made evaluation-runner abstention records fail closed when an API response contains no usable answer but incorrectly reports `abstained=false`; added regressions for contradictory response fields.
- Added an offline structural audit for candidate article-row corpora, including a quantity-bearing article checklist and CI regressions; does not establish Gazette fidelity or legal verification (PR #1158).
- Added a manual-capture provenance recorder with strict document-ID/output-path safeguards, CI tests, and a law-ingestion runbook; captures remain unverified and do not grant reuse permission (PR #1160).
- Expanded synthetic Egyptian-colloquial retrieval regressions to 51 top-three queries with six competing passages each, ten out-of-corpus abstention cases, and a no-model-call check for empty retrieval (PR #1165).
- Added public government-hosted Gazette PDF locators for Labour Law 14/2025 while preserving discovery-only status and explicitly recording the restricted DSpace copy (PR #1166).
- Documented the Article 140/141 distinction for Egyptian official legal documents and creative compilations; source permissions and release gates remain unchanged pending counsel review (PR #1167).
- Registered ETA and SIS Gazette sources with unknown permissions and required manual-capture source IDs to match the captured URL host, preventing false provenance attribution (PR #1169).
- Recorded a limited text-extraction spot-check for selected passages in Labour Law 14/2025 Arts. 21, 54, 62, 71, 82, 103, 124, 134, and 141; corrected earlier unsupported discrepancy/OCR claims and retained discovery-only status (PRs #1171 and #1180).

## Prepared update
- Improved login form: trims/lowercases email, supports Enter-to-submit, displays clearer errors, and adds show/hide password.
- Added `manage.py resetpw EMAIL` to reset a forgotten password safely through a hidden terminal prompt.
- Clarified that terminal password input is intentionally invisible while typing.
- Added Egyptian case metadata fields: case number, year, court, circuit, opposing party.
- Added per-case internal notes.
- Added legal deadlines separate from court hearing dates.
- Added fee tracking with total/paid/remaining display and validation that paid does not exceed total.
- Added a basic text-match conflict-screening feature with an explicit warning that it is not a definitive legal conflict determination.
- Added a Mac local-start script and GitHub `.gitignore` exclusions for databases, virtual environments, and secrets.
- Documented the Arabic law data generator and Gazette verification requirement; the generated dataset is not bundled in this repository.

## Verification
- `python selftest.py` — passed.
- `python api_test.py` — passed, including added feature endpoint checks.
- Python compilation — passed.
- JavaScript syntax check — passed.
- Mac launcher shell syntax check — passed.

## Important limitations
This is still an MVP, not a production-hardened legal system. No independent security audit, two-factor authentication, password-reset email flow, encrypted application database, scanned-PDF OCR, official legal-data verification, or full conflict-of-interest workflow is included. Run locally only; do not expose it to the public internet without a security review and HTTPS deployment.


## Historical date-aware retrieval and citation provenance
- Permit reviewed, dated repealed/historical versions to be retrieved for dates before their recorded repeal boundary, while excluding them on and after that boundary.
- Apply the same historical eligibility rule to exact article lookup; historical records without a known repeal boundary remain excluded.
- Include recorded version, Gazette, review, and amendment-relation metadata in the answer-model context, with explicit warnings that metadata is not independent proof.
- Add regression cases for historical retrieval boundaries and provenance-aware prompts.


## Historical retrieval flag consistency
- Allow registry-linked, reviewed versions to pass the initial search and exact-article gates based on version-registry date eligibility rather than the legacy chunk `in_force` flag.
- Preserve legacy behavior for unlinked chunks.
- Expose `applies_as_of` and use it for API warnings and UI badges so historically applicable repealed versions are not mislabeled.
- Add a regression case where the chunk flag is false but the reviewed version applies before its repeal date.
- PR #1283: add privacy-preserving weekly pilot metrics, platform-admin dashboard, CSV export, and isolation tests.
- PR #1285: add a clearly marked fictional Arabic demo firm, sample cases/deadlines/fees/invoice, and guarded removal.
- PR #1289: add firm profile setup, six-step first-run checklist API, configuration health explanations, and safe test reminders.
- PR #1292: store weekly pilot usage as counts-only aggregates, exclude demo firms, and harden validation errors.
- PR #1291: add the firm-admin first-run wizard, setup-health explanations, and browser acceptance coverage.
- PR #1297: expose weekly aggregate pilot metrics and CSV export through platform-admin-only navigation, with browser visibility coverage.
- PR #1302: add audited, admin-only firm data ZIP export with tenant isolation, CSV formula neutralisation, rate limiting, and tests.
- PR #1307: add a source-linked Arabic UI string review inventory covering 894 unique Arabic-bearing literals, with completeness regression coverage.
- PR #1309: complete the Arabic UI review inventory for firm data export; additions remain pending native-speaker review.
- PR #1311: add measured phone-width accessibility checks and correct 44px language/firm switch targets.
- PR #1313: add Chromium end-to-end owner workflow coverage for login, case creation, deadline creation and invoice issuance at 390px and desktop widths.
- Enforced reversible firm read-only mode after subscription expiry while preserving firm switching, payment recovery and exports; exposed owner countdown and seat capacity (PR #1308).
