# Legal release readiness gate

The read-only gate in tools/validate_legal_release_readiness.py is a structural safety check, not a legal opinion. It never downloads or imports legal text and cannot independently prove that permission or review evidence is genuine.

## Required extracted-text evidence

In addition to source permission, original-file hash, version metadata, and the required review records, each candidate version must provide:
- Source-level collection permission must link to direct HTTPS rights evidence; commercial reuse must have a separate direct HTTPS evidence URL and a valid terms-review date. Narrative labels or license IDs without an inspectable evidence link do not satisfy this gate.

- extracted_text_path: a relative path confined to the configured corpus/repository root.
- text_sha256: SHA-256 of the exact UTF-8 extracted-text file bytes.
- text_review_status: text_checked or lawyer_approved.
- text_review_evidence_url: HTTPS evidence for the text-completeness review.
- article_identifiers: non-empty exact article/decision anchors present in extracted text.
- expected_article_identifiers: non-empty, separately reviewed expected anchor list.

The gate checks that both identifier lists are well-formed, contain no duplicates, and match each other. It checks that each recorded actual anchor occurs in the extracted text, and blocks missing or unexpected anchors. These checks cannot prove the list of expected anchors is complete; that list must be compared with the authoritative publication by a qualified reviewer.

Each review record also needs a passing outcome, notes, HTTPS evidence URL, reviewer_id, reviewer_role, and a valid non-future reviewed_on date. The lawyer_approval review must use reviewer_role egyptian_lawyer or qualified_egyptian_counsel. These fields improve auditability but do not independently establish identity, qualifications, or evidence authenticity.

## Provenance and report semantics

- retrieved_at must be a timezone-aware ISO-8601 timestamp; a date-only value does not identify when the source was retrieved.
- publication_date and effective_date remain separate date fields. The candidate must include gazette_issue, gazette_pages (or an exact decision pinpoint), and a publication_evidence_url that identifies the publication metadata being relied upon.
- A supplied repeal_date must be a valid date no earlier than effective_date. A version labelled in_force cannot have an end/repeal date that has already arrived. Versions labelled repealed or historical require a recorded end/repeal date; without it, a downstream as-of-date check could incorrectly treat the version as active indefinitely. A recorded date is metadata and still needs authoritative legal review.
- The candidate source_id must match exactly one central permission-register record, including its normalized HTTPS hostname. Missing or duplicate exact matches block release; permission from another record on the same host cannot be borrowed.
- Each instrument report includes source authority/class, collection and commercial-reuse permission states, retrieval timestamp, Gazette pinpoint, and machine-readable blockers. Aggregate counts are separated by authority, source class, collection permission, commercial reuse permission, legal status, and review status.
- Candidate inventory counts, evidence-ready current text, and evidence-ready historical text are reported separately. The report deliberately makes no overall legal-coverage percentage claim; planning-matrix status is not verified text coverage.
- Report output is refused if it would overwrite a candidate JSON, permission register, coverage matrix, or files under originals/ or extracted/.

## Run

    python tools/validate_legal_release_readiness.py --out reports/legal-release-readiness.json

Add --require-ready to fail the command when any candidate is blocked. Keep candidates blocked until all evidence is real and independently reviewed. Do not mark a document verified merely because a file hash or article-anchor comparison passes.
