# Bootstrap the Egyptian legal research workspace

The repository is the current starting point. It does not contain a complete legal corpus, and the included \`sample_law.jsonl\` is fictional test data. This bootstrap creates a catalogue of candidate instruments only; it does not pretend the underlying law text has been acquired.

## 1. Validate the candidate catalogue

\`\`\`bash
python tools/seed_legal_candidates.py
\`\`\`

This is a dry run. It checks duplicate identifiers, unknown source references, candidate state, and basic permission metadata.

## 2. Seed metadata into the local SQLite registry

After installing the project requirements and ensuring \`app.py\` can initialize the schema:

\`\`\`bash
python tools/seed_legal_candidates.py --apply
\`\`\`

It writes only to the shared legal-corpus database through the profile-separated runtime. Set `COPILOT_CONTROL_DB`, `COPILOT_TENANT_DB_ROOT`, and `COPILOT_CORPUS_DB`, and keep `COPILOT_DB` unset. The script uses `INSERT OR IGNORE`, so repeated runs do not overwrite existing source permission decisions or candidate records.

This creates source and document identity records only. It does not create legal versions because no direct downloadable document URL has yet passed the permission gate. It does not import article text or mark any source or law as verified.

## 3. Next collection workflow

For each candidate instrument:

1. Identify an exact official document or Gazette issue and capture its publication metadata.
2. Confirm applicable access terms and permission for local storage, text extraction, indexing, display, and intended commercial use.
3. Add a direct-document entry to \`docs/collection_manifest.example.json\` only after the evidence is recorded.
4. Run the collector, preserving the original, final URL, retrieval timestamp, response metadata, and SHA-256.
5. Review Arabic extraction and article numbering.
6. Register a version with known dates and leave legal status unknown until verified.
7. Have a qualified Egyptian lawyer review commencement, amendments, repeal history, and any transitional provisions before treating it as authority.

## Scope and caveats

The candidate list is a prioritization aid, not legal advice and not proof that the listed law remains in force. A title/number/year may need correction or more precise identification. Historical or replaced instruments must not be presented as current. The criminal-procedure candidate is deliberately flagged for an explicit current-law/commencement check. The catalogue should grow by verified sources and instrument families, not by guessed download URLs or bulk scraping of restricted services.
