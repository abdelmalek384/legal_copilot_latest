# Date-aware legal retrieval

## API

Both `POST /search` and `POST /ask` accept an optional `as_of` field in `YYYY-MM-DD` form, for example:

```json
{"q":"موعد بدء العمل بالقانون","as_of":"2026-10-23"}
```

If omitted, the application uses the server's current date. The response includes `requested_as_of` so clients can display which date was used.

## Eligibility for linked versions

For a chunk whose `document_version_id` points to the version registry, retrieval requires:

- review status `verified`;
- source authenticity and legal-status verification flags set;
- a known effective date on or before the requested date; and
- no recorded repeal date on or before the requested date.

Versions labelled `in_force` are eligible when those conditions hold. Versions labelled `repealed` or `historical` may also be retrieved **for a date before their recorded repeal date**; they are excluded on and after that date. A `repealed` or `historical` version without a known repeal boundary is excluded because the system cannot safely establish its temporal eligibility. Partially repealed instruments need provision-level treatment and are not made eligible by this rule.

Exact article lookup uses the same temporal predicate. The answer prompt receives the evaluation date and recorded version provenance, including Gazette metadata and amendment relations where present. Recorded metadata is context, not independent proof; missing or conflicting dates must remain uncertain.

## Compatibility limitation: legacy unlinked chunks

Chunks without `document_version_id` retain the previous `chunks.verified=1` and `chunks.in_force=1` gating. They cannot be filtered by the registry's dates because no version link exists. This is deliberate compatibility behavior, not a guarantee of historical accuracy. A production corpus migration should link each legal chunk to a reviewed version before relying on historical `as_of` queries.

Case-specific chunks are not filtered by legislation status. The `as_of` field is a date, not a substitute for legal analysis, and this feature does not infer amendment relationships or consolidate article text automatically.

## Tests

The registry test suite checks:
- unreviewed linked versions are excluded;
- verified versions are available on/after effective date;
- future-effective versions are excluded before commencement;
- repealed versions are excluded on/after their recorded repeal date;
- malformed dates are rejected.

These are software-behavior tests, not lawyer validation of the underlying dates or legal conclusions.
