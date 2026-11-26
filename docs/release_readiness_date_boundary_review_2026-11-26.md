# Release-readiness date boundary review — 2026-11-26

## Scope
Read-only source review of `tools/validate_legal_release_readiness.py` and `tests/test_legal_release_readiness.py`. No runtime tests or CI were executed. This is a structural review, not a legal validation.

## Finding: date-only and timestamp checks use different clock semantics
- `valid_date` accepts ISO calendar dates only when they are no later than `datetime.date.today()`, which uses the host's local date.
- `valid_timestamp` requires a timezone-aware ISO-8601 timestamp and compares the instant against the current time expressed in the timestamp's own timezone.
- The project's legal-source work is generally framed around Egypt/Cairo-local legal dates. The host's configured timezone is not guaranteed to be Cairo, so `valid_date` can potentially evaluate the same date differently around midnight across environments.

## Assessment
This is a **potential consistency issue, not a confirmed defect**. Date fields may represent review dates or legal effective/publication dates, and the appropriate timezone convention needs to be defined before modifying behavior. Avoid silently changing the gate to Cairo or UTC without clarifying semantics.

## Recommended targeted acceptance coverage
1. Freeze the clock in tests and explicitly test a UTC instant whose date differs from Cairo's date.
2. Test review-date validation at the Cairo midnight boundary while the test host timezone is set to a different timezone, if the gate is intended to use Cairo.
3. Test future-date rejection and calendar-date parsing independently.
4. Document whether date-only metadata is evaluated as Cairo-local dates or host-local dates; keep timestamp validation as absolute instants.
5. Do not treat a structural pass as verification of source authenticity, legal status, or counsel approval.

## Safe disposition
No production code change made: the semantics are not sufficiently specified to justify altering a fail-closed legal release gate based on source review alone. Tests remain manual/local and unexecuted; GitHub Actions is not used.


## Additional cross-check
- Repeal-date validation also mixes date-only helpers and host-local `date.today()`: historical/repealed status requires a non-future date via `valid_date`, and an `in_force` status with a reached repeal date is blocked using host-local today. This reinforces that the timezone/date-only convention should be made explicit before code changes.
- Source-to-register linkage currently requires matching source_id and normalized hostname, rather than exact URL path. This is not inherently incorrect: rights may apply to a domain or portal. It is an unresolved policy choice; review whether evidence scopes to the host, path, portal, or individual item before tightening the comparison. Host matching should not be interpreted as independent permission verification.
- Existing synthetic tests appear to exercise many fail-closed cases, including malformed JSON, unsafe URLs, permission parity, counsel-attestation markers, symlink swaps and FIFOs. They are source-inspected only and remain unexecuted.
