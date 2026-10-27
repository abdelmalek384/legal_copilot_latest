# Legal corpus audit report

Run against a local copy of the application's SQLite database:

\`\`\`bash
python tools/audit_legal_corpus.py --db copilot.db --out-dir audit_out
\`\`\`

The tool opens SQLite in read-only mode and writes \`legal_corpus_audit.json\` and \`legal_corpus_audit.md\`. It reports row counts, missing provenance, missing original files and hashes, unknown legal status, missing dates, unverified sources, and chunks not linked to a legal version.

The report includes the database file's SHA-256, but that hash identifies the database snapshot, not the authenticity of any law inside it. A passing amendment-history review counts as evidence-backed only when its event contains a valid HTTPS URL without embedded credentials; this checks URL shape, not whether the source is official or its contents are correct.

## Safety

- The audit never changes the database.
- It never downloads legal documents.
- It never changes \`verified\`, \`in_force\`, permission, or review fields.
- A count of zero issues means only that these specific metadata checks found no gaps; it is not a legal accuracy certification.
- Keep the audit output private if it reveals client or case metadata. The report itself does not dump legal text, but it includes the local database path and aggregate counts.


## Evidence URL validation

The read-only audit accepts only well-formed HTTPS URLs without whitespace, embedded credentials, malformed or empty ports, or out-of-range ports. This is a syntax check only: it does not fetch the page or prove the evidence is genuine, relevant, authoritative, or legally sufficient. It also audits review-event integrity: reviewer identity, review type/outcome, timestamp validity and future dates, passing-event evidence URLs, and links to existing version records. A malformed event is reported, never repaired automatically.
