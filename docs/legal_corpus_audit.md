# Legal corpus audit report

Run against a local copy of the application's SQLite database:

\`\`\`bash
python tools/audit_legal_corpus.py --db copilot.db --out-dir audit_out
\`\`\`

The tool opens SQLite in read-only mode and writes \`legal_corpus_audit.json\` and \`legal_corpus_audit.md\`. It reports row counts, missing provenance, missing original files and hashes, unknown legal status, missing dates, unverified sources, and chunks not linked to a legal version.

The report includes the database file's SHA-256, but that hash identifies the database snapshot, not the authenticity of any law inside it.

## Safety

- The audit never changes the database.
- It never downloads legal documents.
- It never changes \`verified\`, \`in_force\`, permission, or review fields.
- A count of zero issues means only that these specific metadata checks found no gaps; it is not a legal accuracy certification.
- Keep the audit output private if it reveals client or case metadata. The report itself does not dump legal text, but it includes the local database path and aggregate counts.
