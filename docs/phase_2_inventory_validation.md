# Phase 2 Egyptian Instrument Inventory — Validation Contract

The file docs/phase_2_document_inventory.json is a **metadata-only discovery inventory**. It contains instrument identifiers, Arabic titles, broad practice areas, source IDs, discovery states, permission states, legal/review states, source URLs where recorded, and unresolved follow-up requirements. It is not a corpus of legal text.

## Validation rules

The validator in tools/validate_phase2_document_inventory.py and tests/test_phase2_document_inventory.py enforce:

- Required root fields and non-empty source/document/action collections.
- Unique instrument IDs and next-action IDs.
- Every instrument references a source record already present in the inventory.
- Source records include authority, source class, an explicit permission state, and a next action; unsupported source permission values are rejected.
- Source-level permission is checked independently from instrument-level collection and reuse permission. An "allowed" source state does not promote any document's permission, review status, or legal status.
- Known source, collection-permission, legal-status, review-status and action-status values.
- HTTPS-only source links (or null where a source URL has not been verified).
- No embedded legal passage/full-text/content payloads.
- A record cannot be marked verified without explicit collection permission, commercial reuse permission, and permission evidence.
- A record cannot be labelled in force without verified review and an effective date.

The current inventory has 71 unique instrument candidates across 13 source records. That count describes registry candidates only; it is not a count of laws covered or legal texts acquired.

## Operating rules

1. Unknown stays unknown. An official publisher or discovered URL does not grant collection, OCR, storage, indexing, commercial display, or redistribution permission.
2. Source discovery and source-level terms are not item-level permission evidence. Confirm the exact instrument, intended acquisition method, storage, extraction, indexing, display, and commercial use separately.
3. Discovery status is not authenticity, current-law, amendment-history, or legal-effect verification.
4. Source indexes and secondary catalogues are discovery aids; primary text and Gazette issue/page evidence remain separate requirements.
5. The inventory validator is a structural safeguard, not legal research approval. A qualified Egyptian lawyer must review the exact instrument, amendments, commencement, repeal/transition, and relevant court rulings before a version is marked verified.
6. Do not fetch, scrape, or download source content merely to populate this inventory.
