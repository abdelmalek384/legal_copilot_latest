# Matter document intelligence workspace

## Purpose

This is the first UI layer for reviewing documents already uploaded to a case. It is reachable from Legal Research after selecting a matter, and from that matter's Documents tab. It reuses the existing permission-checked case and extracted-chunk endpoints; it does not introduce a new tenant or document-access path.

## Current capabilities

- Search extracted text across the selected matter's uploaded documents in Arabic and English. Search applies Unicode NFKC normalization, removes common Arabic diacritics/tatweel, normalizes common alef/yeh forms, and normalizes Arabic-Indic digits.
- Show conservative keyword-based document-type suggestions (judgment, contract, pleading, correspondence/notice, evidence/receipt, or unclassified).
- Permit an in-view draft classification override. The current UI explicitly says this draft is **not saved** and is discarded when the panel is rebuilt. The server-side persistent classification API is being added separately and the UI must be connected to it before claiming this workflow complete.
- Extract literal candidate mentions for dates, case references, amounts, labelled parties, legal references and event-related terms. The server API uses the canonical Python helper plus a separately maintained extension for legal-reference and event-term mentions.
- Preserve the document name, chunk reference and page number when the extraction endpoint supplies them. A missing page number is shown as not recorded; the UI does not infer one.
- Show possible duplicates based on exact original-file SHA-256 and normalized extracted-text equality, limited to documents returned for the selected matter.
- Offer an original-file download through the existing audited, integrity-checking endpoint when a private retained original exists.
- Compare two extracted text versions with a bounded first-difference context view.
- Keep all candidate results visibly unverified and require lawyer review. Date mentions are not automatically converted into hearings, filing dates or deadlines.

## Server API integration

The authenticated API layer adds the following case-scoped operations:

- `GET /cases/{case_id}/documents/intelligence`: returns keyword classification suggestions, unverified source-located candidates, same-matter duplicate groups, a date-mention timeline, and the latest ten classification reviews per document.
- `POST /cases/{case_id}/docs/{document_id}/classification`: appends a human-selected category, the server-computed suggestion and matched terms, reviewer ID, note and timestamp. The request includes `expected_latest_id` for compare-and-swap; stale reviews return HTTP 409. Classification history rows cannot be updated.
- `POST /cases/{case_id}/documents/compare`: compares two documents in the same authorized matter, with bounded text and change-segment limits.

All endpoints call the existing case authorization check and use the authenticated tenant database/firm ID. The API does not accept a client-supplied firm ID. The browser UI is not yet connected to these server endpoints; until the follow-up UI integration, its classification selector remains an explicitly unsaved draft and its analysis remains browser-side.

## Access and resource limits

- The panel receives the selected case ID and the case's document metadata from the existing authenticated case-detail response.
- Each document's extracted chunks are loaded through `GET /cases/{case_id}/docs/{document_id}/chunks`; the server performs the existing matter membership/authorization checks.
- Client analysis is limited to the first 40 documents and 1,000,000 total extracted characters per load.
- At most 250 candidates are collected per document, 120 are displayed, and 50 search hits are shown.
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

- Connect the current UI classification editor to the persistent classification API and expose its review history in the UI.
- Firm-wide document search across multiple matters. The current workspace is deliberately limited to one selected, authorized matter.
- Connect the UI to the authenticated server-side document-intelligence API. Until that integration lands, the panel still performs bounded browser-side candidate scans using transparent keyword/regex rules; do not treat those browser results as the canonical server analysis.
- General named-entity recognition beyond labelled party-name patterns; structured event extraction beyond literal event-term mentions.
- Multi-hunk semantic/version comparison. The current comparison is a bounded first-difference view only.
- Document retention/legal-hold workflow controls in this panel.

These gaps must remain explicit. Do not describe this UI layer as a complete document-management system, verified legal extraction, or persistent classification workflow.
