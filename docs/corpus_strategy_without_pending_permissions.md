# Legal Copilot: Corpus Strategy Without Pending Permissions

**Status:** proposed implementation plan  
**Scope:** Egyptian-law-first MVP  
**Principle:** continue product engineering while respecting source terms and preserving legal provenance.

## Executive decision

Do not make the product roadmap dependent on a bulk license being granted. Build a multi-lane corpus that distinguishes discovery metadata, user-authorized material, individually reviewed open resources, and licensed official full text. The product can ship meaningful case management, document analysis, citation management, and source-aware research before it has a comprehensive corpus.

Never treat public accessibility as permission for scraping, bulk download, commercial reuse, indexing, or republication. Never label a source as official, complete, current, or verified based only on its URL or a successful OCR run.

## Corpus lanes

### Lane A — discovery and citation index (start now)

Store metadata and links rather than copying full text where reuse rights are unclear:
- instrument title, number/year, instrument type, issuing authority;
- practice areas and Arabic/English aliases;
- publication date, Official Gazette issue/part/page when independently evidenced;
- official-source URL, discovery-source URL, retrieval/check date;
- known amendments, repeal/replacement links, and missing evidence;
- source terms status and the evidence/reviewer who recorded it.

UI must label this lane **Citation metadata only — full text not licensed/verified**. Search results can help lawyers locate the primary source but must not fabricate the provision text.

### Lane B — user- or firm-supplied material

Allow a firm to upload a document it is entitled to use, subject to product terms and the firm's confirmation. Record uploader, firm, upload time, SHA-256, filename, source/provenance notes, extraction/OCR state, and access scope. Treat uploaded content as **unverified** until an authorized reviewer checks authenticity, completeness, amendments, and legal status. Enforce firm-level access control and provide deletion/retention controls.

Do not use customer documents to train models by default. Keep them tenant-scoped and out of global search unless the customer explicitly opts into an approved sharing arrangement.

### Lane C — individually reviewed open resources

Use public resources for discovery and limited, terms-compliant research, not as a blanket bulk-ingestion license:
- Library of Congress Egypt legal guides: a research map to primary and secondary sources.
- ILO NATLEX: labour/social-security legislation discovery; review applicable terms for each use.
- WIPO Lex: intellectual-property laws, treaties and selected judgments; its terms prohibit automated queries, scraping, bulk acquisition/storage and commercial use of its contents absent required permission.
- FAOLEX/ECOLEX: environment, agriculture, food, water and natural-resource instruments; inspect source-specific terms and verify against Egyptian primary publications.
- Official Egyptian ministry/authority pages: record links and metadata; review terms before downloading or retaining text.

The external resources are not interchangeable with an authenticated Official Gazette publication. Record which source is primary, secondary, translated, or a discovery index.

### Lane D — licensed official corpus

Keep the Amiri Press / Official Gazette and court judgment tracks open for future licensing. Acquisition is enabled only when the source-specific register records the exact permitted method and uses, evidence URL or file, effective date, expiry, attribution, and rate limits. Court judgments remain blocked from automated/bulk extraction while applicable terms require written authorization.

### Lane E — counsel-curated starter set

Create a prioritized inventory for foundational legislation, but do not manufacture missing text. For each instrument, ask a qualified Egyptian lawyer or librarian to supply or validate the original publication and amendments. If they provide a copy, record the provenance and permission basis. Prioritize labour, civil code/procedure, evidence, criminal code/procedure, constitution, tax, companies/commercial, family, administrative/procurement and property, but release only verified instrument-by-instrument coverage.

## Implementation phases

### Phase 1 — schema and status controls
1. Add explicit corpus lane and source authority fields: `primary_official`, `official_secondary_copy`, `international_discovery`, `user_supplied`, `licensed_vendor`, `manual_metadata`.
2. Keep separate enums for `access_permission`, `commercial_reuse_permission`, `text_extraction_state`, `authenticity_review`, `legal_status_review`, and `amendment_history_review`.
3. Require evidence and reviewer identity before changing a permission or legal-verification state.
4. Never infer that a source is permitted because a URL is HTTPS or an HTML page is publicly viewable.

### Phase 2 — metadata-first product
1. Seed candidate instrument metadata only; do not seed fictional sample text as legal material.
2. Add a source locator view that clearly distinguishes a source link from an indexed text.
3. Add missing-coverage states and amendment/repeal relationship gaps.
4. Enable citation-only search and source links without generating a substantive legal answer if no verified text is retrieved.

### Phase 3 — firm documents
1. Tenant-scoped upload, hashing, duplicate detection and access control.
2. Extract/OCR with page references and OCR confidence; retain original only under the product's documented retention policy and user's authorization.
3. Side-by-side source page / extracted text review, with page-level corrections and audit trail.
4. A reviewer can mark a specific document version reviewed only after checking source, completeness, dates and amendment history.

### Phase 4 — retrieval and evaluation
1. Hybrid Arabic retrieval: exact article lookup, normalized lexical search, and Arabic-capable multilingual embeddings once there is a lawful, representative evaluation corpus.
2. Retrieval returns passage text, exact document version, page/article pin-cite, source URL, review status, and as-of date.
3. Add a refusal/fallback rule: if verified relevant text is absent, return sources to check and say that the corpus did not establish the answer.
4. Build a lawyer-reviewed test set by practice area; measure recall@k, citation correctness, answerability detection, stale-law failures, Arabic spelling variants and OCR errors.
5. Do not optimize on fictional sample law or treat model confidence as legal verification.

## Release gates

- Every displayed legal proposition has an inspectable source and pinpoint citation, or is clearly labeled as general guidance rather than a statement of Egyptian law.
- No source is bulk acquired or commercially reused outside documented terms.
- No unverified passage is presented as current law.
- User-supplied content stays within the correct firm and access scope.
- Corpus coverage is reported per instrument and status, not as a misleading single percentage.
- A qualified Egyptian lawyer reviews legal-status and amendment-history claims.

## First implementation task

Implement a **Corpus Coverage & Provenance dashboard** backed by the existing source/document-version registers. Show counts for citation-only candidates, uploaded/unverified, text extracted, awaiting legal review, verified versions, missing amendment history, blocked permissions, and coverage by practice area. Every count must be derived from stored records and link to a review queue. This creates visible progress without pretending that missing law text exists.
