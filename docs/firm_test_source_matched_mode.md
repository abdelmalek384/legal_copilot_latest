# Firm-test source-matched mode (non-production only)

**Purpose:** allow one explicitly configured test firm to exercise answer rendering for sources that have complete machine source-matching evidence but have not been reviewed by qualified Egyptian counsel.

**Visible answer label:** `Source-matched — not lawyer-reviewed`. The API tier value is `source_matched`. It must never be translated into `verified` or `lawyer_approved`.

## Environment configuration

All of the following are required:

```bash
COPILOT_ENV=test
LEGAL_FIRM_TEST_SOURCE_MATCHED=1
LEGAL_FIRM_TEST_SOURCE_MATCHED_FIRM_ID=42
```

- `COPILOT_ENV` must be one of `development`, `dev`, `test`, `testing`, or `staging`.
- `LEGAL_FIRM_TEST_SOURCE_MATCHED` must be exactly `1`.
- `LEGAL_FIRM_TEST_SOURCE_MATCHED_FIRM_ID` must be the exact positive firm ID dedicated to this test.
- The mode is unconditionally disabled when `COPILOT_ENV=prod` or `production`, even if the feature flag is accidentally set.
- If the flag is missing, malformed, or the firm ID differs, the application returns sources only and labels the candidate `unreviewed`.

## Source eligibility

The answer path accepts only a set of sources whose backend records are all explicitly marked `source_matched_unreviewed`, have `verified=false`, and carry the complete source-match evidence package checked by `tools.answer_trust_tier`:

- original and independent-copy SHA-256 values and distinct source IDs;
- complete article inventory and resolved text differences;
- publication/effective-date evidence;
- explicit collection, storage, extraction, indexing, commercial-use and excerpt-display permission evidence.

The firm-test path also runs the lexical claim-support check even if the general optional claim-support switch is disabled. Citations and existing answer contradiction/pinpoint checks remain in force. Failed or incomplete checks produce sources only.

## Law 14/2025 boundary

The current Law 14/2025 candidate is **not eligible for this mode**. Its manifest records collection/reuse permissions as unknown, the candidate corpus file is not committed, the original scan reports copy/print restrictions, and the candidate is not search-eligible. This implementation does not import or retrieve that text, alter any `verified` flag, or bypass source-rights restrictions. It provides the isolated test-firm response gate for a future source record only after all technical and permission evidence is complete.

Use synthetic fixtures for automated tests. Do not use confidential client matters or describe test-mode answers as legal advice, verified law, current consolidated law, or lawyer-approved content.

## Focused tests

```bash
PYTHONPATH=. python -m unittest tests.test_firm_test_source_matched_mode -v
```

The tests cover flag-on answer labeling, flag-off source-only behavior, exact firm scoping, and unconditional production denial. A test result is not established until this command is actually run in the supported Python 3.12 environment.
