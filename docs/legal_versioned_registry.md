# Versioned legal document registry

## Purpose

The legal corpus must represent a law's publication, effective period, amendment history, and verification separately. A file's download date is not its effective date, and a publication record is not proof that the text remains in force.

## SQLite tables added to the application schema

- `legal_sources`: authority, source page, access and licensing status, evidence and review date.
- `legal_documents`: stable document identity and legal instrument metadata.
- `legal_document_versions`: immutable version-level provenance, original file path/hash, Gazette references, dates, legal status, and independent verification flags.
- `legal_version_relations`: explicit links such as amends, repeals, consolidates, corrects, supersedes, and implements.
- `legal_review_events`: append-only review record with reviewer, review type, outcome, evidence URL, and timestamp.

A nullable `chunks.document_version_id` column was added for a gradual connection between searchable chunks and their source version. Existing law imports continue to work; they are not automatically upgraded to verified records.

## Status vocabulary

- `unknown`: status not established.
- `under_review`: review is in progress.
- `not_yet_in_force`: enactment/publication known but commencement is future.
- `in_force`: a reviewer has established the status for the relevant as-of date.
- `partially_repealed`, `repealed`, `historical`: historical/version states that require evidence.

Review state is independent: source review, lawyer review, verified, or rejected. A version should not be treated as production authority just because its source URL is official.

## Safe next migration steps

1. Import source-register records with permission still set to unknown.
2. Register candidate documents and each amendment as distinct legal documents/versions.
3. Store the downloaded original and SHA-256 only after the retrieval permission gate passes.
4. Link extracted chunks to a version ID and keep source citations stable.
5. Add a query-time `as_of` filter using effective/repeal dates and review state.
6. Backfill only with provenance; leave unknown dates and legal statuses unknown.
7. Have Egyptian counsel review complicated commencement, repeal, and transition interactions.

## Important limitation

This PR adds schema and a nullable linkage column. It does not yet change the answer API to enforce temporal filtering, does not automatically register downloads, and does not verify the law. Those need separate changes and tests.
