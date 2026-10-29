# Legal corpus audit report

Run against the approved legal-corpus database or a protected copy bound to the immutable `legal_corpus` profile:

```bash
export COPILOT_CORPUS_DB="/absolute/path/to/legal-corpus.sqlite3"
python tools/audit_legal_corpus.py --out-dir audit_out
```

An explicit `--db` path is also supported. The audit rejects databases without a legal-corpus profile marker, databases bound to another profile, and any run with `COPILOT_DB` compatibility mode configured.

The tool opens SQLite in read-only mode and writes \`legal_corpus_audit.json\` and \`legal_corpus_audit.md\`. It reports row counts, missing provenance, missing original files and hashes, unknown legal status, missing dates, unverified sources, and chunks not linked to a legal version.

The report includes the database file's SHA-256, but that hash identifies the database snapshot, not the authenticity of any law inside it. Global legal chunks marked `verified` or `in_force` are cross-checked against their linked legal version. Missing, unreviewed, non-operative, future-effective, or repealed version records trigger high-severity findings; the audit does not change chunk or version flags. A passing amendment-history review counts as evidence-backed only when its event contains a valid HTTPS URL without embedded credentials; this checks URL shape, not whether the source is official or its contents are correct. The audit also checks that `authenticity_verified`, `status_verified`, and `review_status='verified'` have matching passing review events with valid HTTPS evidence URLs. Missing evidence is reported as a high-severity issue; the audit never changes verification flags.

## Safety

- The audit never changes the database.
- It never downloads legal documents.
- It never changes \`verified\`, \`in_force\`, permission, or review fields.
- A count of zero issues means only that these specific metadata checks found no gaps; it is not a legal accuracy certification.
- Keep the audit output private if it reveals client or case metadata. The report itself does not dump legal text, but it includes the local database path and aggregate counts.


## Evidence URL validation

The read-only audit accepts only well-formed HTTPS URLs without whitespace, embedded credentials, malformed or empty ports, or out-of-range ports. This is a syntax check only: it does not fetch the page or prove the evidence is genuine, relevant, authoritative, or legally sufficient. It also audits review-event integrity: reviewer identity, review type/outcome, timestamp validity and future dates, passing-event evidence URLs, and links to existing version records. A malformed event is reported, never repaired automatically.
