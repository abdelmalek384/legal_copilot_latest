# Legal PDF import and provenance runbook

**Scope:** offline extraction of law PDFs that the operator already has a lawful basis to store and process. This is a candidate-ingestion workflow, not legal verification or activation.

## 1. Source acquisition and rights

- The repository does not provide a general Official Gazette downloader. There is no `download_egypt_laws.py` workflow.
- Do not bypass login, access controls, rate limits, or technical restrictions. Publicly viewable material is not automatically licensed for bulk downloading, redistribution, commercial reuse, or model ingestion.
- Use a source that is publicly accessible and whose applicable reuse terms permit the intended handling. If permission is unknown, preserve that uncertainty in the source register and keep the material quarantined; do not label it approved.
- Keep original PDFs and sidecar metadata outside Git. Never commit client documents, private source files, or the generated local OCR cache.

## 2. Prepare one PDF and one JSON sidecar per document

Place each PDF and its matching JSON file in one input directory, with the same filename stem:

```text
source/
  labour_law_14_2025.pdf
  labour_law_14_2025.json
  decision_123_2026.pdf
  decision_123_2026.json
```

Each JSON sidecar must be an object with these fields:

```json
{
  "document_id": "labour_law_14_2025",
  "source_url": "https://example.gov.eg/publication/item",
  "retrieved_at": "2026-10-30T10:30:00+02:00",
  "content_sha256": "64-character SHA-256 of the exact PDF bytes",
  "review_status": "pending_human_review"
}
```

The example URL is illustrative only. Replace it with the actual source URL. Use the SHA-256 of the exact local PDF, not a hash copied from a webpage or a different edition. The importer accepts an ISO date or datetime for `retrieved_at`, requires an HTTPS URL without embedded credentials, fragments, or signed/credential query parameters, and rejects symbolic links, mismatched file pairs, invalid PDF signatures, duplicate document IDs, and hash mismatches before extraction begins.

## 3. Install optional extraction dependencies

The generic PDF importer needs PyMuPDF. Install the optional package set:

```bash
python -m pip install -r requirements-ocr.txt
```

For PDFs whose text layer is unusable, the importer can use OCR. The Python wrapper is included above; install the system Tesseract executable and the English language data on the host. OCR output is only recognized text and must be compared page-by-page with the original. The generic importer targets English translations and uses Tesseract's `eng` language setting.

## 4. Run local extraction

```bash
python tools/import_laws.py /path/to/source /path/to/output
```

The output directory must be outside the source directory. The tool writes:

- `law_rows.jsonl` — article-level candidate rows for staging.
- `import_report.md` — page counts, OCR use, article ranges, missing article numbers, and source/hash metadata.
- `.ocr_cache/` — resumable local OCR text, if OCR is needed. Cache directories are keyed to the exact PDF SHA-256, so a changed source file does not silently reuse old OCR; symlinked cache paths/pages are rejected.

Every generated row is explicitly `verified: 0`, `in_force: 0`, and `as_of: null`. The recorded SHA-256 confirms that the local PDF matches its sidecar hash; it does not prove that the PDF is an authentic Gazette publication or that reuse is permitted.

## 5. Review before staging

A human reviewer must compare the PDF against the relevant official publication and check:

- Correct instrument, issuing authority, issue/date, supplement, and publication identifier.
- PDF page count, missing pages, article boundaries, numbering restarts, schedules, annexes, and tables.
- OCR/transcription accuracy against page images; do not rely on the completeness report alone.
- Original Arabic text and any translation relationship; an English translation is not authoritative where the Arabic original governs.
- Source access and reuse terms, including whether extraction, storage, redistribution, and commercial use are permitted.
- Publication, commencement/effective date, amendments, repeals, suspension, transitional provisions, and current status.
- A qualified Egyptian-lawyer review record before any legal status or verification flag is promoted.

A clean hash check, successful extraction, no missing article numbers, or a public URL is not legal verification.

## 6. Database staging is a separate controlled action

`python manage.py importlaws <law_rows.jsonl>` writes rows to the shared legal-corpus staging table; it is a database mutation, not a read-only extraction step. It requires the profile-separated control-plane, tenant-root, and legal-corpus configuration and refuses the legacy `COPILOT_DB` mode. Do not run it against production or change database configuration as part of this document-preparation workflow. The database/storage workstream owner must approve the staging target and timing first.

Staging does not activate rows as verified law. Keep the legal review queue, permission evidence, original-source comparison, and counsel approval gates intact.

## 7. Labour Law No. 14 of 2025 and Action 1 intake

`tools/fetch_arabic_law.py` is a separate convenience fetcher for an unofficial republication of Labour Law No. 14 of 2025. It is not an Official Gazette downloader and its output must remain a candidate until compared with the original Gazette issue and reviewed.

For the specific Action 1 source intake, use the dedicated evidence-only hash/intake tools and preserve the original Gazette PDF and `law_rows_ar.jsonl` locally. Do not commit the source bytes. Keep primary-source matching, source rights, legal status, and lawyer review as separate gates.
