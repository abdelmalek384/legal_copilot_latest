# Firm-Supplied Document Ingestion and Provenance (DATA-06)

## What is recorded

Each successful matter document upload or text-document creation receives a stable database document ID and a SHA-256 digest. The document record includes the matter ID, firm ID, uploader user ID, safe display filename, content type, byte size, creation timestamp, extraction status, and OCR-used flag. Every extracted paragraph chunk is linked to the document ID.

- Binary uploads hash the original uploaded bytes. Text-only documents hash their UTF-8 text.
- A normal PDF/DOCX extraction is marked `text_extracted`; OCR-derived text is marked `ocr_unverified` and retains the `ocr_used` flag.
- Hashes support identity and integrity checks; they do not prove authorship, authenticity, legality, or correctness.
- Original binaries are processed in memory and are not stored by this workflow.
- Identical files uploaded twice intentionally create separate document records. No cross-matter or cross-firm deduplication is performed.
- Existing document rows are migrated with nullable provenance fields where historic uploader/hash/type/size cannot be reconstructed. Do not infer historic metadata.
- Matter access remains guarded by the existing case authorization check. Case deletion removes the matter's document rows and derived chunks through the existing deletion workflow; the existing case-deletion audit stores aggregate counts and case/event snapshots, not uploaded binaries.

## Limits and follow-up

This change does not implement retention schedules, a binary archive, malware scanning, OCR confidence scoring, page-level previews, extraction correction, or a reviewer audit trail. Those need explicit policy and separate acceptance tests. OCR output is not authoritative evidence until checked against the original pages. The application currently discards uploaded binaries after extraction, so later page-level review will require a separately approved storage and retention design.

## Validation

Run `python tests/test_app_separate_database_runtime.py`, `python tests/test_original_file_storage.py`, and the repository CI workflow. The profile-separated tests cover metadata/hash persistence, chunk linkage, intentionally separate duplicate uploads, OCR status, original-file lifecycle, and cross-firm matter access denial.
