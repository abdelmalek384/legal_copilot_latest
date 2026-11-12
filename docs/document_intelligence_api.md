# Document intelligence API

## Authentication and tenant scope

Every endpoint requires the existing authenticated user dependency and a case membership check. The firm ID is taken from the trusted authenticated context, never from the request body. Document queries require the exact document ID, case ID and firm ID to match. The routes operate only in the selected firm's tenant database.

## Case analysis

### GET /cases/{cid}/documents/intelligence

Returns at most 40 documents and processes at most 1,000,000 extracted characters and 1,000 candidates across the selected case. Documents exceeding the per-document text budget or remaining case budget are returned with a skipped analysis status; the top-level truncated flag is set.

Each analyzed document includes existing metadata, a transparent classification suggestion, literal unverified candidates for dates, case references, amounts, labelled party names, legal references and event-term mentions, and the latest ten append-only classification reviews. Candidate page/chunk provenance is retained where available; missing page metadata remains null. The response does not return full extracted document text.

The response also includes same-matter duplicate groups, a date-mention timeline, analysis limits and explicit limitations.

## Persistent classification

### POST /cases/{cid}/docs/{document_id}/classification

Request body:

```json
{
  "category": "pleading",
  "expected_latest_id": 12,
  "note": "Reviewed against the original document"
}
```

For a document with no prior classification, send `expected_latest_id: null`. Categories are limited to `unclassified`, `court_judgment`, `contract`, `pleading`, `correspondence`, and `evidence_or_receipt`.

Each successful request appends a row to `document_classification_reviews`; it does not overwrite an earlier review. The row records reviewer user ID, selected category, server-computed suggested category, matched keyword evidence, note and timestamp. An immutable-update trigger prevents history rows from being edited. There is no classification-history delete endpoint; rows are removed only through the existing document/case deletion cascade.

The handler serializes writes with `BEGIN IMMEDIATE`, rechecks the extracted-text digest, and compares the expected latest review ID. A stale review or changed extracted text returns HTTP 409; callers must reload and retry. Unauthorized or cross-matter document IDs return 404.

## Version comparison

### POST /cases/{cid}/documents/compare

Request body:

```json
{
  "before_document_id": 41,
  "after_document_id": 42,
  "context_chars": 100
}
```

Both documents must belong to the selected authorized matter. Extracted text is limited to 100,000 characters per version. Results are text-only review candidates and do not determine authenticity, legal effect or which version controls.

## Candidate semantics

- Date candidates are mentions, not hearing dates, filing dates or appeal deadlines.
- Legal references are literal article/law-number mentions, not verified citations or statements of current law.
- Event terms are mentions, not structured or verified events.
- Party-name candidates depend on explicit labels such as plaintiff/defendant; this is not general named-entity recognition.
- Amounts and case references are literal text matches, not verified facts.
- Duplicate hashes identify possible byte-identical originals or normalized-text matches only within one matter. Matching extracted text does not prove original-file identity.
- OCR text remains unverified and must be checked against the original.

## UI follow-up

The current browser panel still contains a local, unsaved classification draft and bounded client-side candidate scan. A follow-up UI change must consume the case analysis endpoint, persist classifications through the POST endpoint using the returned latest review ID, display classification history, and call the server comparison endpoint. Until that work lands, do not represent the current panel as fully connected to the canonical API.
