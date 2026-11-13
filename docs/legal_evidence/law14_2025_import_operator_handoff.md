# Law 14/2025 Gazette importer — owner handoff

**Current state:** importer implemented; no production Gazette-text import has been run in this session. No source text is assumed to be present in the repository. This handoff does not authenticate a document or grant permission to collect/reuse it.

## What the owner must supply

Provide these two files together:

1. A UTF-8 plain-text transcription of the exact source pages covering all 13 promulgation provisions and Articles 1–298, with headings retained. Prefer a lawyer-supplied transcription checked against the Gazette pages. Do not silently normalize, summarize, repair, or omit text.
2. A completed metadata JSON based on `law14_2025_import_metadata.template.json`. The supplier role must truthfully identify an Egyptian lawyer or qualified Egyptian counsel. Include the official Gazette issue/date, capture method, source URL or stable source reference, and a SHA-256 calculated from the exact text bytes. The template declares the expected inventory (13 promulgation provisions and 298 attached-law articles); the importer reports missing trailing numbers and out-of-range headings against those counts. Set collection permission to `allowed` only when documentary evidence actually supports that status; otherwise leave it `unknown`.

Do not send passwords, signed download URLs, or private access tokens. The importer rejects credentials and signed-query URLs.

## Prepare and run locally

From the repository root, after saving the supplied text as `/secure/input/law14_2025_gazette.txt` and completing the metadata file:

```bash
sha256sum /secure/input/law14_2025_gazette.txt
# Copy the resulting 64-character digest into content_sha256.
python tools/import_gazette_text.py \
  /secure/input/law14_2025_gazette.txt \
  /secure/input/law14_2025_import_metadata.json \
  /secure/output/law14_2025_import_candidate
```

Use a new, empty output directory outside the source directory. On macOS, if `sha256sum` is unavailable, use:

```bash
shasum -a 256 /secure/input/law14_2025_gazette.txt
```

The command writes `law_rows.jsonl` and `import_report.md`. The report lists recognized headings, numbering blocks, missing/duplicate numbers, empty article bodies, and excluded preamble text. Check that the expected inventory is 13 promulgation provisions and 298 attached-law articles; investigate every deviation against the original Gazette pages. A count match alone is not proof of textual accuracy.

## Safeguards and acceptance

- Every imported row is emitted with `verified: 0`, `in_force: 0`, and `as_of: null`.
- The importer creates quarantined candidate rows only. It does not certify authenticity, reuse rights, currentness, amendments, or legal interpretation.
- Do not copy imported rows into the production legal corpus or enable retrieval solely because the import succeeded.
- Preserve the original supplied text, its SHA-256, metadata, output report, and reviewer corrections as separate evidence artifacts.
- A qualified Egyptian lawyer must compare the full text against the primary Gazette and independently approve legal content before any verification promotion.

## Current blocker

The importer cannot be run on the requested real Gazette text until the owner supplies the actual UTF-8 text file and truthful source/supplier metadata. No substitute transcription will be fabricated.
