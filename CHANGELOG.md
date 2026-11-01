# Changelog — Legal Copilot

- Added a separate, data-driven Arabic legal retrieval lexicon with conservative spelling variants and synthetic top-three retrieval regressions (PR #1148).
- Added fictional fixture-only legal-ingestion tests for manual-capture hash integrity, article comparison, numeric mismatch detection, and commencement-date extraction (PR #1151).
- Added a policy proposal for a separately gated, production-disabled source-matched/unreviewed trust tier without weakening existing lawyer-approval gates (PR #1150).
- Added an opt-in, fail-closed factual claim-support check for cited answers, including finite-period contradiction tests; disabled by default (PR #1154).
- Added Arabic claim-support regressions for no-limitation assertions contradicted by a finite period and a faithful five-year paraphrase; feature remains opt-in and heuristic (PR #1178).
- Added an offline structural audit for candidate article-row corpora, including a quantity-bearing article checklist and CI regressions; does not establish Gazette fidelity or legal verification (PR #1158).
- Added a manual-capture provenance recorder with strict document-ID/output-path safeguards, CI tests, and a law-ingestion runbook; captures remain unverified and do not grant reuse permission (PR #1160).
- Expanded synthetic Egyptian-colloquial retrieval regressions to 51 top-three queries with six competing passages each, ten out-of-corpus abstention cases, and a no-model-call check for empty retrieval (PR #1165).
- Added public government-hosted Gazette PDF locators for Labour Law 14/2025 while preserving discovery-only status and explicitly recording the restricted DSpace copy (PR #1166).
- Documented the Article 140/141 distinction for Egyptian official legal documents and creative compilations; source permissions and release gates remain unchanged pending counsel review (PR #1167).
- Registered ETA and SIS Gazette sources with unknown permissions and required manual-capture source IDs to match the captured URL host, preventing false provenance attribution (PR #1169).
- Recorded three Labour Law 14/2025 Gazette spot-check wording discrepancies (Arts. 124, 134, 141), documented an Article 103 OCR mismatch, and retained discovery-only status pending full comparison and lawyer review (PR #1171).

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
