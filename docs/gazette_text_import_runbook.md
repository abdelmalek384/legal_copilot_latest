# One-sitting Gazette text import (lawyer-supplied)

**Purpose:** turn one lawyer-supplied Arabic Gazette transcription into quarantined article-level candidate rows and a review report in one local session.

**This is not OCR, source authentication, legal verification, a reuse-rights decision, or database staging.** The importer never changes `verified=0`, `in_force=0`, or `as_of=null`.

## Inputs

Create a private working directory outside the repository, for example:

```text
gazette-session/
  source/
    gazette.txt
    gazette.metadata.json
  output/                 # must not already contain importer output files
```

1. Obtain the Arabic text from an Egyptian lawyer who supplies or transcribes the relevant Gazette issue. Save it as UTF-8 plain text. Preserve headings, article numbers, schedules and numbering resets exactly; do not silently correct spelling or OCR.
2. Copy `docs/templates/gazette_text_metadata.template.json` to `source/gazette.metadata.json`.
3. Fill every required field. Use the exact title, Gazette issue/supplement and publication date. `captured_by` identifies the supplier; `supplier_role` must be `egyptian_lawyer` or `qualified_egyptian_counsel`. Set `capture_method` to `lawyer_supplied_text` or `manual_transcription`.
4. Provide either a stable `source_url` (HTTPS, without credentials, fragments or signed query parameters) or a non-empty `source_reference`. If reuse permission is unknown, leave `collection_permission` as `unknown`; do not infer permission from public availability.

## Hash the exact text bytes

Run from the repository root. Do not open/save the text file in an editor after calculating the hash.

macOS:

```bash
shasum -a 256 /absolute/path/to/gazette-session/source/gazette.txt
```

Linux:

```bash
sha256sum /absolute/path/to/gazette-session/source/gazette.txt
```

Copy the 64-character digest into `content_sha256` in the sidecar. The importer independently recomputes it and rejects any mismatch. The hash proves only that the supplied text matches the sidecar, not that the text matches the Gazette.

## Run the import

From the repository root:

```bash
python tools/import_gazette_text.py \
  /absolute/path/to/gazette-session/source/gazette.txt \
  /absolute/path/to/gazette-session/source/gazette.metadata.json \
  /absolute/path/to/gazette-session/output
```

The command is offline and needs no database credentials or network access. It validates the sidecar and exact-byte hash, reads regular non-symlink files within size limits, segments recognized Arabic/English article headings, splits article text into candidate chunks, and writes:

- `output/law_rows.jsonl` — candidate chunks with source, document, issue, date, hash and supplier provenance.
- `output/import_report.md` — article-heading count, chunk count, empty article bodies, numbering gaps/duplicates, provenance and human-review checklist.

Use a new, empty output directory for each run. The output directory must be outside the source directory. Existing output files are never overwritten.

## Same-session review

1. Open `import_report.md`. Resolve every empty body, numbering gap and duplicate; inspect numbering resets, tables, schedules and annexes against the lawyer-supplied source.
2. Inspect `law_rows.jsonl` for text loss, broken boundaries, duplicated chunks and block labels. Compare the transcription with the Gazette page images; a successful import is not a comparison.
3. Confirm the source identity, exact issue/date, page coverage, source access/reuse basis, amendments, corrigenda, commencement and currentness with counsel.
4. Preserve the original supplied text, sidecar, hash, report and reviewer notes together as the review record.
5. Stop here until the separate source-rights and legal-review gates are satisfied.

## Hard safety boundary

- Every output row is forced to `verified=0`, `in_force=0`, `as_of=null`.
- `collection_permission=unknown` is accepted only to create quarantined candidates; it is not approval to redistribute or use commercially.
- `not_allowed` permission is rejected.
- No database write, retrieval activation, currentness promotion or legal approval occurs.
- The importer requires a lawyer/counsel supplier declaration but does not independently verify the person's identity or qualification.

## Troubleshooting

| Error | Action |
|---|---|
| SHA-256 mismatch | Recompute from the exact final text bytes and update the sidecar; do not edit the text afterward |
| No recognized headings | Preserve article headings in the text; check supported `المادة`, `مادة` or `Article` heading forms |
| Empty article bodies | Compare the relevant transcription section with the original page and correct only with a recorded reviewer decision |
| Output already exists | Choose a new empty output directory; do not delete evidence from an earlier run |
| Supplier role rejected | Confirm the supplier is an Egyptian lawyer/counsel and use one of the two accepted role values |
| Permission marked not allowed | Stop; do not import or stage the material |

