# Matter document intelligence workspace

## Purpose

This is the first UI layer for reviewing documents already uploaded to a case. It is reachable from Legal Research after selecting a matter, and from that matter's Documents tab. It reuses the existing permission-checked case and extracted-chunk endpoints; it does not introduce a new tenant or document-access path.

## Current capabilities

- Search extracted text across the selected matter's uploaded documents in Arabic and English. Search applies Unicode NFKC normalization, removes common Arabic diacritics/tatweel, normalizes common alef/yeh forms, and normalizes Arabic-Indic digits.
- Show conservative keyword-based document-type suggestions (judgment, contract, pleading, correspondence/notice, evidence/receipt, or unclassified) from the canonical Python helper, executed by the existing authenticated matter-scoped chunks endpoint.
- Permit an in-view draft classification override. The UI explicitly says this draft is **not saved** and is discarded when the panel is rebuilt. It is not a persistent classification or an audit record.
- Extract literal candidate mentions for dates, case references, amounts, labelled parties, legal references and event-related terms on the server. Results retain document ID, chunk ID/reference and recorded page where available.
- Preserve the document name, chunk reference and page number when the extraction endpoint supplies them. A missing page number is shown as not recorded; the UI does not infer one.
- Show possible duplicates based on exact original-file SHA-256 and normalized extracted-text equality, limited to documents returned for the selected matter.
- Offer an original-file download through the existing audited, integrity-checking endpoint when a private retained original exists.
- Compare two extracted text versions with a bounded first-difference context view.
- Keep all candidate results visibly unverified and require lawyer review. Date mentions are not automatically converted into hearings, filing dates or deadlines.

## Access and resource limits

- The panel receives the selected case ID and the case's document metadata from the existing authenticated case-detail response.
- Each document's extracted chunks are loaded through `GET /cases/{case_id}/docs/{document_id}/chunks`; the server performs the existing matter membership/authorization checks.
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

- Persistent, server-side editable classifications with role checks, optimistic concurrency and an audit history.
- Firm-wide document search across multiple matters. The current workspace is deliberately limited to one selected, authorized matter.
- Persistent, server-side editable classifications with role checks, optimistic concurrency and an audit history. The server now returns canonical classification suggestions and bounded literal candidates through the existing authorized chunks endpoint, but user overrides remain view-only drafts.
- Structured extraction of named entities and events beyond the literal candidate rules described above.
- Multi-hunk semantic/version comparison. The current comparison is a bounded first-difference view only.
- Document retention/legal-hold workflow controls in this panel.

These gaps must remain explicit. Do not describe this UI layer as a complete document-management system, verified legal extraction, or persistent classification workflow.
