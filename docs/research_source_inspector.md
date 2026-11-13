# Research Results & Source Inspector

## Purpose

Expose the evidence behind a research answer without treating model confidence, a URL, or a registry record as proof that text is authentic or current. Search scopes are explicit and never silently combined.

## User workflow

1. Select **Verified legal corpus**, **Firm documents in a matter**, or **Source catalog discovery (metadata only)**.
2. Search with a natural-language question, title/citation, or article number.
3. Inspect exact retrieved passage text, highlighted matched surface terms, and recorded source/version metadata.
4. Copy the recorded citation or exact passage, open the registered HTTPS source, export a plain-text research memo, or save the memo to a matter's notes.
5. If no relevant passage is found, see a no-source state and run a separate metadata-only discovery search.

## Scope contracts

- `verified_corpus`: legal-corpus retrieval only. The existing search eligibility gates remain in force.
- `firm_documents`: requires an accessible matter ID and returns only chunks from that matter. Firm passages are labelled user-supplied/unverified; they are not upgraded to law.
- `metadata_only`: the `/research/discover` endpoint searches recorded title, law number/year, and authority fields. It returns catalog metadata only, does not fetch pages, does not return passage text, and does not establish reuse permission or current legal status.
- `all_permitted` remains available only for backwards-compatible internal/API callers; the UI does not offer a blended scope.

## Source-status labels

- `verified_operative_text` requires a registry-linked version, lawyer/source review marked verified, in-force status, authenticity/status/amendment flags, and an exact source-ID plus normalized-host match against the versioned central permission register. The matched register record must independently mark collection and commercial reuse as allowed, include separate inspectable HTTPS evidence URLs and non-future terms-review dates, and agree with the database permission states. Narrative evidence descriptions alone do not satisfy this check.
- The answer generator independently abstains if any retrieved corpus passage lacks the verified-operator status or explicit chunk verification flag. The passages may still be shown as research leads with unresolved status; firm-document processing remains subject to its separate data-processing approval.
- `secondary_copy` is kept distinct from operative legal text.
- `user_supplied_unverified` applies to firm/matter passages.
- `metadata_only` has no passage text.
- `outdated_or_under_review` covers missing registry links or unmet current-law/provenance gates.
- `no_relevant_verified_source` is communicated when the selected scope has no retrieved passage. It does not mean no applicable law exists.

Each source-status label is accompanied by a plain-language explanation in the UI. The original-source link shows its registered hostname so the destination can be inspected before opening it. These labels describe recorded data only; they do not replace legal review. Malformed as-of, effective, or repeal dates, and malformed nested provenance fields, fail closed to `outdated_or_under_review`; they are not compared as arbitrary strings. Invalid source shapes in memo generation are surfaced as unresolved records rather than crashing or being presented as verified text.

## Citations and memos

- Citation strings include only recorded title, instrument number/year, article pinpoint, version label, Gazette reference, as-of date, and source URL.
- Page pinpoint is shown only when actually recorded. The chunks schema now has an optional page field with a migration for existing databases; legacy chunks and uploads without page metadata remain unpinned until a lawful, reviewed ingestion path supplies that value.
- Passage-copy uses the exact stored passage. It does not copy a generated paraphrase as a quotation.
- Memo export and save-to-matter retain the question, search scope, as-of date, answer, exact source passages, citation strings, source status, and explicit limitations.
- Matter saving is scoped to the signed-in user's own research conversation and a matter they can access; it stores the memo as a matter note and records an audit event.

## Validation and limitations

Automated tests cover conservative status gates, citation formatting, memo caveats, search-scope separation, metadata-only empty states, matter saving, frontend controls, and highlighting of the actual source-word forms matched by curated Arabic query expansion. CI is the source of truth for test status. Citation validation ignores Markdown fenced/inline code and hidden HTML comments when checking citation indices, per-sentence citations, and numeric claims; a citation shown only inside non-visible content cannot satisfy the prose citation requirement. Manual browser review, screen-reader checks, lawyer validation, and a production security review remain separate requirements.

The corpus remains incomplete. Missing metadata, page numbers, legal text, or written permission are not inferred.


### Inspector display contract

The source inspector displays a recorded page pinpoint from either `page_number` or the extracted chunk `page` field, including values nested in provenance. A page pinpoint is display metadata only: reviewer-entered page references and extracted chunk pages are not independently verified against the retained original PDF. The inspector explains each source status at the point of review, including metadata-only and no-relevant-passage states; absence of a returned passage must not be interpreted as proof that no applicable law exists.

When a page pinpoint belongs to a firm-document result (identified by its matter scope or case ID), the inspector states that the recorded page reference has not been independently checked against the original file. This is especially important for OCR-derived text and reviewer-entered page references; neither a page label nor an extracted passage proves that the original scan was transcribed accurately. The caveat is not applied to verified-corpus results, whose source status is governed by their separate provenance and review gates.

The matter-document extraction review panel applies the same warning to an extracted `chunk.page` value when no reviewer-entered page reference supersedes it. This keeps OCR/extraction page pins visibly provisional at both the source-inspection and transcription-review stages.

When the retrieval payload supplies stable document provenance, the inspector also displays the document-record ID, matter ID, and original-file SHA-256 fingerprint. These fields are shown only when returned by the source/provenance record; the UI does not infer identifiers, construct a document URL, or imply that a fingerprint alone validates OCR text. Together with the recorded original filename and page pinpoint, they provide a reproducible hand-off for locating the retained matter file and checking the extraction against it.

### Matter-document retrieval hand-off

Firm-document retrieval records now carry the matched chunk ID, document ID, matter ID, original filename, stored document SHA-256, extraction status, OCR-used flag, and a boolean indicating whether a retained original object is currently available. The separate-database query joins the document row inside the selected matter and firm boundary; the original-availability flag is derived only from a ready, non-purged object record. The legacy search path reports original availability as false because its original-download route is unavailable.

The source inspector uses those fields to show a matter/document/chunk identity, the stored file fingerprint, and an OCR caution where applicable. For matter-linked hits it now carries the exact document and chunk identity into the matter workspace, opens that document's extracted-text review panel, and focuses and scrolls to the matching chunk when it is present. If the chunk is no longer present in the loaded extraction, the interface reports that it could not locate the requested passage and clears the one-shot navigation target. If the document itself is no longer listed in the matter's available documents, the workspace reports that and clears the target rather than leaving a stale request for a later navigation. If no chunk ID was supplied, the action is explicitly labelled as opening the matter's Documents section; it does not claim to pinpoint a passage. It offers an original-file download only when the backend explicitly reports a retained original and both matter/document identifiers are valid positive integers. The existing download endpoint independently checks matter authorization, object state, byte size, and SHA-256 before returning bytes. Missing or purged originals are disclosed as unavailable rather than sending the user to a broken or guessed URL. This action is a document-access hand-off, not legal-source verification; user-supplied matter material remains unverified.


### Matter-library original retention affordance

The matter Documents review list receives an `original_available` field from the authorized case-detail response. The original-download action is now rendered only when this backend field is explicitly true (including the serialized integer form). If the object is absent, purged, or unavailable in legacy mode, the UI shows a plain retention-status note instead of presenting a download control that would predictably fail. The download endpoint remains the authority and still performs its own authorization and integrity checks; this frontend gate is a usability improvement, not a security boundary.


### OCR and incomplete-page review cautions

The matter-level extracted-text review now repeats an explicit OCR warning when the document metadata records OCR use (or the OCR-unverified extraction state). For partial extraction where OCR is unavailable on some pages, the panel warns that displayed passages may be incomplete and directs the reviewer to the original. Page labels and the reviewer page-reference field accept either `page` or `page_number`, falling back when the first field is blank, and remain explicitly provisional until checked against the source page. These warnings do not certify OCR accuracy or completeness.


### Cross-matter text-search hand-off

Cross-matter extracted-text search results already return case, document, and chunk IDs within the caller's authorized matter scope. When all three identifiers are valid, the result action now uses the same exact document/chunk review hand-off as the Legal Research source inspector. If the result lacks a chunk ID, it retains the prior matter-level Documents hand-off instead of inventing a passage location. Search results remain unverified extracted-text matches and are not legal conclusions.


Original-document download filenames in both the matter review UI and the global document library are normalized to remove path separators and control characters and are length-bounded before being passed to the browser download attribute. This is a client-side filename hygiene measure; the stored object name and server-side access checks remain unchanged.


The focused chunk card now receives a visible focus outline and scroll margin when opened from a research result, so keyboard and assistive-technology users can identify where navigation landed. The card remains a review target, not a verification status.


Pending matter/chunk navigation state is cleared when the active firm changes, including the MFA firm-switch path, and when the session expires or the user signs out. Manual navigation to another workspace or matter section also clears an unconsumed target. This prevents stale targets from surviving a change in identity, firm context, or the user's explicit navigation choice.


Each per-document extracted-text review panel is now a named accessible region and remains connected to its disclosure control with `aria-controls`. This improves navigation between document review areas for screen-reader users.
