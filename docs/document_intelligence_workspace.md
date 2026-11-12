# Matter document intelligence workspace

## Purpose

This is the document-management and review workspace for uploaded matter files. It is reachable from the top-level Documents page and from Legal Research after selecting a matter. It reuses the existing permission-checked case, document, and extracted-chunk endpoints; it does not introduce a new tenant or document-access path.

## Current capabilities

- Dedicated Documents navigation page with an all-accessible-documents landing view, authenticated paginated matter selection, direct multi-file PDF/DOCX upload (15 MB per file) with per-file queue/progress and accessible busy state, file metadata, filename/type search, extraction-status and saved-classification filters, accessible-document and selected-matter counts derived from authorized rows, and original-file download only when the separate-database storage record is ready and not purged. Uploads use same-origin credentials and CSRF protection. Metrics are not firm-wide and do not imply legal review completion.
- Cross-matter metadata index for documents in matters the current user can access, with server-side firm and case-membership filters, pagination, case context, extraction/classification/type filters, and audited coarse search events. It returns metadata only; full-text search is provided by the separate FTS endpoint.
- Cross-matter extracted-text search across authorized matters using the firm database's FTS index. Queries are token-quoted, Unicode NFKC-normalized, and normalize common Arabic diacritics, alef/yeh variants and Arabic-Indic digits. Results are membership-filtered server-side, paginated, and return bounded excerpts centered on the matched text with document, chunk and page provenance. Search terms are not written to the audit log; results remain unverified.

- Search extracted text across the selected matter's uploaded documents in Arabic and English. Search applies Unicode NFKC normalization, removes common Arabic diacritics/tatweel, normalizes common alef/yeh forms, and normalizes Arabic-Indic digits.
- Show conservative keyword-based document-type suggestions (judgment, contract, pleading, correspondence/notice, evidence/receipt, or unclassified) from the canonical Python helper, executed by the existing authenticated matter-scoped chunks endpoint.
- Show canonical keyword-based classification suggestions separately from the saved lawyer-approved classification.
- Persist classification changes through the matter-scoped classification endpoint. Only firm administrators and matter leads can save; updates require the current version number and return HTTP 409 when a concurrent change has occurred. Each document version has at most one classification event, and parent-document deletion cascades through its classification metadata/history.
- Append every classification change to a firm/matter/document-scoped audit history with actor, previous/new category, version, note and timestamp. Other matter members can view the saved classification and history but cannot edit it.
- Resolve reviewer display names through the separate control-plane identity store; firm databases do not contain user identity tables. Database triggers reject audit-event edits and direct deletion while allowing parent matter/document retention cascades.
- Review extracted passages with explicit accept, correction, or needs-recheck decisions. Corrections require the server-issued SHA-256 digest of the source chunk and update the indexed extracted passage using compare-and-swap. The original extracted text and corrected text are both retained in the review record; the uploaded original file is not modified. Reviewer notes, page references, reviewer identity, timestamps, and before/after text are retained in the review history.
- Show the original extracted passage and latest corrected text separately. A review attention filter includes both passages with no review decision and passages explicitly marked for recheck; accepted/corrected passages are not hidden from the full view.
- Review history is bounded to the latest 200 events per document at the API and 100 combined rows in the current UI view. The extracted-passage review panel displays at most 100 chunks per view.
- Extract literal candidate mentions for dates, case references, amounts, labelled parties, legal references and event-related terms on the server. Results retain document ID, chunk ID/reference and recorded page where available.
- Preserve the document name, chunk reference and page number when the extraction endpoint supplies them. A missing page number is shown as not recorded; the UI does not infer one.
- Show possible duplicates based on exact original-file SHA-256 and normalized extracted-text equality, limited to documents returned for the selected matter.
- Offer an original-file download through the existing audited, integrity-checking endpoint when a private retained original exists.
- Compare two extracted text versions with a bounded first-difference context view.
- Keep all candidate results visibly unverified and require lawyer review. Date mentions are not automatically converted into hearings, filing dates or deadlines.

## Access and resource limits

- The panel receives the selected case ID and the case's document metadata from the existing authenticated case-detail response.
- Each document's extracted chunks are loaded through `GET /cases/{case_id}/docs/{document_id}/chunks`; the server performs the existing matter membership/authorization checks.
- Saved classification state and its latest 100 audit events are read through `GET /cases/{case_id}/docs/{document_id}/classification`; changes use `PUT` on the same route and require firm-admin or matter-lead authorization.
- Extracted passage review uses `POST /cases/{case_id}/docs/{document_id}/chunks/{chunk_id}/review`; review history uses `GET /cases/{case_id}/docs/{document_id}/reviews`. Both enforce firm, matter, and document scope. Correction requests must include the current source-chunk SHA-256 digest; stale digests are rejected.
- Review decisions do not assert that OCR or extraction is accurate. Acceptance records a lawyer's review action; the original source and extracted text remain available for comparison.
- Classification updates use an optimistic `expected_version` token. The first save uses version `0`; every successful save increments the version and appends an audit event in the same transaction.
- Client analysis is limited to the first 40 documents and 1,000,000 total extracted characters per load.
- Server analysis is limited to 1,000,000 extracted characters and 250 candidates per document; the UI displays at most 120 candidates and 50 search hits. Truncation is reported.
- Text comparison is limited to 100,000 characters per version.
- Search, duplicate grouping and comparison are confined to the selected matter. There is no cross-firm aggregation.

## Legal and provenance safeguards

- Keyword matches are suggestions, not legal document classifications or determinations of authenticity.
- Dates, amounts, party names, case references, article references and event terms are literal text candidates, not verified facts.
- The date timeline is a list of date mentions, not a procedural deadline engine.
- Text differences do not establish legal significance, amendment validity or which version controls.
- Extracted text and OCR output must be checked against the original document. OCR text remains unverified.
- Original-file retention depends on the configured private storage backend. The upload UI no longer claims that originals are never retained.

## Not yet implemented

- Semantic cross-matter retrieval and multi-document synthesis. Current full-text search returns literal FTS matches only; it does not make legal findings or synthesize across matters.
- Structured extraction of named entities and events beyond the literal candidate rules described above.
- Multi-hunk semantic/version comparison. The current comparison is a bounded first-difference view only.
- Document retention/legal-hold workflow controls in this panel.

These gaps must remain explicit. Do not describe this UI layer as a complete firm-wide document-management system or verified legal extraction. Saved categories are lawyer workflow metadata, not proof of authenticity, accuracy or legal effect.
