# Legal document collection pipeline

## Status
This is a controlled document retriever and review-queue generator, not a complete corpus and not a legal-status verification service. The source catalogue is a discovery registry, not evidence that documents have been collected.

## Safety model
- No crawling, search-page scraping, URL guessing, login bypass, or paywall bypass.
- Only exact direct-document URLs entered in the manifest are considered.
- A document is downloaded only when `collection_permission` is `allowed`, `permission_evidence` is populated, `terms_checked_on` is a valid date, and approved source hosts are listed.
- HTTPS only; redirects are revalidated; private/local network addresses and unapproved hosts are rejected.
- Download size and content type are checked. The raw original is preserved unchanged.
- SHA-256, source URL, retrieval time, HTTP metadata, curator-supplied dates, and permission evidence are stored in a JSON sidecar.
- Extracted text is separate from the original. PDFs without extractable text are flagged for OCR/manual review.
- Article labels, duplicate labels, numeric gaps, and short extraction are reported as warnings, not silently repaired.
- Every document stays `pending_human_review`; authenticity, current legal status, and commercial reuse are never set true automatically.

## Install
From the repository root, use Python 3.11+ and install dependencies:
```bash
python -m pip install -r requirements.txt
```

## Configure a permitted document
Add an entry to `docs/collection_manifest.example.json` only after checking the exact source and document rights. Example structure (placeholder only):
```json
{
  "document_id": "example_law_001",
  "source_id": "EG-GAZETTE",
  "title": "Official title in Arabic",
  "document_type": "legislation",
  "direct_url": "https://approved.example.gov/documents/law.pdf",
  "allowed_hosts": ["approved.example.gov"],
  "collection_permission": "allowed",
  "permission_evidence": "Reviewed terms URL or written authorization reference",
  "terms_checked_on": "2026-10-23",
  "publication_date": null,
  "effective_date": null,
  "repeal_date": null,
  "legal_status_assessment": "unknown",
  "amends_document_ids": [],
  "amended_by_document_ids": [],
  "consolidates_document_ids": [],
  "consolidated_version_as_of": null,
  "law_number": null,
  "gazette_issue": null
}
```
The example is illustrative; do not use the placeholder URL. Use `null` when a date is unknown. Do not guess effective dates from publication dates.

## Run
```bash
python tools/collect_legal_documents.py --manifest docs/collection_manifest.example.json --out legal_corpus
```
The example manifest is deliberately empty. It processes zero documents until populated with authorized direct-file entries.

To re-run extraction and article audits for already downloaded documents without downloading again:
```bash
python tools/collect_legal_documents.py --manifest docs/collection_manifest.example.json --out legal_corpus --process-existing
```

## Output
- `originals/<document_id>/`: preserved original bytes.
- `metadata/<document_id>.json`: provenance, hash, dates, permission evidence and review flags.
- `extracted/<document_id>.txt`: searchable text, separate from original.
- `audits/<document_id>.json`: article gap/duplicate and extraction diagnostics.
- `review_queue.jsonl`: items awaiting human source/legal review.
- `collection_report.jsonl`: per-document outcomes.

## Next steps
1. Populate document entries with confirmed lawful direct downloads, starting with foundational statutes and procedural laws.
2. Add Gazette metadata and amendment relationships after comparing the original.
3. Add OCR for scanned Arabic PDFs and review OCR against page images.
4. Have an Egyptian lawyer verify authenticity, current status, commencement and amendments.
5. Only then transform reviewed material into the app's legal-search import format. Never import this review queue as verified legal authority.
