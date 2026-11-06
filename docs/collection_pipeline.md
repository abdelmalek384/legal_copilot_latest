# Legal document collection pipeline

## Status
This is a controlled document retriever and review-queue generator, not a complete corpus and not a legal-status verification service. The source catalogue is a discovery registry, not evidence that documents have been collected.

## Safety model
- No crawling, search-page scraping, URL guessing, login bypass, or paywall bypass.
- Only exact direct-document URLs entered in the manifest are considered.
- Before creating output directories or making any network request, the CLI validates the central register's schema and unique source IDs, then cross-checks every manifest entry against `docs/source_permission_register.json` (override with `--register`). Every document must pass both collection and commercial-product-use gates, including separate commercial evidence and review date. Any blocked entry stops the entire batch before network access; `--process-existing` is subject to the same gate before re-extraction/re-indexing.
- A document is downloaded only when `collection_permission` is `allowed`, `permission_evidence` and a valid `terms_checked_on` date are present, approved source hosts are listed, and `permission_scope_review` records a reviewer, evidence reference, review date, reviewed source terms, the `direct_document_url` access method, and explicit approval for storage, text extraction, indexing, commercial product use, and excerpt display. These fields are self-reported metadata, not independent proof that rights were granted.
- HTTPS only; redirects are revalidated; private/local network addresses and unapproved hosts are rejected. Whitespace, invalid ports, credentials (including empty userinfo), and malformed URLs are rejected consistently by the collection, permission-register, acquisition-readiness, and legal-release validators.
- Download size and content type are checked. The raw original is preserved unchanged.
- SHA-256, source URL, retrieval time, HTTP metadata, curator-supplied dates, permission evidence, and the exact permission-scope review metadata are stored in a JSON sidecar.
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
  "permission_evidence": "Reference to the reviewed terms or written authorization; do not use this placeholder",
  "terms_checked_on": "2026-10-23",
  "permission_scope_review": {
    "status": "pending",
    "evidence": "REPLACE_WITH_REAL_AUTHORIZATION_OR_TERMS_REFERENCE",
    "reviewer_id": "REPLACE_WITH_REAL_REVIEWER_REFERENCE",
    "reviewed_on": "2026-10-23",
    "evidence_reference": "REPLACE_WITH_REAL_EVIDENCE_ID",
    "evidence_url": null,
    "access_method": "direct_document_url",
    "source_terms_reviewed": false,
    "scope": {
      "storage": false,
      "text_extraction": false,
      "indexing": false,
      "commercial_product_use": false,
      "excerpt_display": false
    }
  },
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
The example is intentionally non-authorizing: placeholder reviewer/evidence values and false scope flags fail closed. Replace them only after a real documented review confirms each intended use. Do not use the placeholder URL. Use `null` when a date is unknown. Do not guess effective dates from publication dates.

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
- `extracted/<document_id>/<original-sha256>-<extracted-sha256>.txt`: immutable searchable text, separate from original.
- `audits/<document_id>/<original-sha256>-<extracted-sha256>-<audit-sha256>.json`: immutable article-gap/duplicate and extraction diagnostics.
- `review_queue.jsonl`: items awaiting human source/legal review.
- `collection_report.jsonl`: per-document outcomes.

Reprocessing a document does not overwrite earlier extracted text or audit records. Each artifact is content-addressed and records the source original hash. Before reading existing metadata, the processor validates the document ID, requires the original path to remain inside `originals/<document_id>/`, rejects symlinks, and checks the original bytes against the recorded SHA-256. Tampered or stale sidecars fail closed instead of being used to read arbitrary files. The collector also rejects symlinked output roots, storage directories, metadata sidecars, and JSONL report/queue files before acquisition, and opens append-only logs without following a symlink target.

## Next steps
1. Populate document entries with confirmed lawful direct downloads, starting with foundational statutes and procedural laws.
2. Add Gazette metadata and amendment relationships after comparing the original.
3. Add OCR for scanned Arabic PDFs and review OCR against page images.
4. Have an Egyptian lawyer verify authenticity, current status, commencement and amendments.
5. Only then transform reviewed material into the app's legal-search import format. Never import this review queue as verified legal authority.
