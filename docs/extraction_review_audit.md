# Extraction review and correction audit (DATA-07)

## First implementation slice

The matter-document API now supports review of an extracted paragraph chunk:

- `POST /cases/{case_id}/docs/{document_id}/chunks/{chunk_id}/review` accepts `accepted`, `corrected`, or `needs_recheck`.
- A correction requires non-empty replacement text and records the original text, reviewed text, reviewer user ID, firm, matter, outcome, note, and timestamp.
- Corrected text updates the chunk used for subsequent retrieval and refreshes its FTS index.
- `GET /cases/{case_id}/docs/{document_id}/reviews` lists the latest 200 audit entries for an authorized matter.
- Existing matter authorization plus explicit document/firm/chunk checks prevent cross-firm access.

## Important boundaries

This is a text-review audit trail, **not** a page-level comparison against the source image. The current ingestion flow discards original binaries after extraction, so reviewers cannot verify text against original pages in this slice. Do not label reviewed text as authentic law or as legally validated. OCR remains unverified until a human checks it against an authoritative original.

## Follow-up before production

1. Approve a secure binary retention policy and storage architecture before adding page previews.
2. Add page-level extraction coordinates and source-page references for PDF/DOCX where available.
3. Add correction conflict/version handling so concurrent reviewers cannot overwrite each other's work silently.
4. Add reviewer UI, diff view, permissioned audit export, retention/deletion behavior, and accessibility tests.
5. Consider whether a review may change the retrieval index immediately or require a second reviewer for high-risk documents.
6. Run the complete CI suite and verify migration behavior against a database created by an earlier release.

## Test coverage

API regression tests exercise a correction, persisted original/replacement text, review listing, validation of missing correction text, and cross-firm denial.
