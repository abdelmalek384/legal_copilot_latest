# Legal-corpus artifact inventory

Run from the repository root:

```bash
python tools/report_legal_corpus_inventory.py
```

Write reproducible JSON and Markdown reports:

```bash
python tools/report_legal_corpus_inventory.py \
  --out reports/legal-corpus-inventory.json \
  --markdown-out reports/legal-corpus-inventory.md
```

Use `--strict` to return a nonzero exit code when cross-register identifier inconsistencies are found. The command is read-only with respect to the source registers; it writes only to explicitly requested report paths.

The report compares the source manifest, source permission register, candidate document catalogue, phase-two source evidence register, acquisition queue, and practice-area coverage matrix. It counts their records and status labels, and reports missing cross-register identifiers.

**This is not a legal corpus audit.** It does not scan SQLite, search for acquired PDFs, verify file hashes, test live URLs, or certify permission, authenticity, currentness, amendment history, or lawyer review. An acquisition state in a planning queue is only a declared status. Use the acquisition-readiness audit before any collection and the legal-corpus audit for the local database. Never use candidate counts as a claim about the number of collected or verified legal documents.
