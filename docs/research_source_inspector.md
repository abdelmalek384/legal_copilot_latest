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
