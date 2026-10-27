# Legal release readiness gate

The read-only gate in tools/validate_legal_release_readiness.py is a structural safety check, not a legal opinion. It never downloads or imports legal text and cannot independently prove that permission or review evidence is genuine.

## Required extracted-text evidence

In addition to source permission, original-file hash, version metadata, and the required review records, each candidate version must provide:

- extracted_text_path: a relative path confined to the configured corpus/repository root.
- text_sha256: SHA-256 of the exact UTF-8 extracted-text file bytes.
- text_review_status: text_checked or lawyer_approved.
- text_review_evidence_url: HTTPS evidence for the text-completeness review.
- article_identifiers: non-empty exact article/decision anchors present in extracted text.
- expected_article_identifiers: non-empty, separately reviewed expected anchor list.

The gate checks that both identifier lists are well-formed, contain no duplicates, and match each other. It checks that each recorded actual anchor occurs in the extracted text, and blocks missing or unexpected anchors. These checks cannot prove the list of expected anchors is complete; that list must be compared with the authoritative publication by a qualified reviewer.

Each review record also needs a passing outcome, notes, HTTPS evidence URL, reviewer_id, reviewer_role, and a valid non-future reviewed_on date. The lawyer_approval review must use reviewer_role egyptian_lawyer or qualified_egyptian_counsel. These fields improve auditability but do not independently establish identity, qualifications, or evidence authenticity.

## Run

    python tools/validate_legal_release_readiness.py --out reports/legal-release-readiness.json

Add --require-ready to fail the command when any candidate is blocked. Keep candidates blocked until all evidence is real and independently reviewed. Do not mark a document verified merely because a file hash or article-anchor comparison passes.
