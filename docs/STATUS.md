# Legal Copilot — current status

**Updated:** 2026-11-04

## What works
- Three-database runtime: control plane, isolated firm databases, shared legal corpus.
- Case management, collaboration, access controls, MFA, billing and operational workflows are implemented and covered by automated tests.
- Arabic lexical retrieval, source scoping, citations, refusal controls and legal-answer evaluation tooling are implemented.
- Repository cleanup and the three-database README quick start are merged.

## What is not established
- **No Egyptian law is verified or lawyer-reviewed in the product.** Candidate legal data and fictional fixtures are not authoritative legal content.
- Legal retrieval and refusal tests measure software behaviour, not legal correctness.
- Deadline rules and holiday coverage remain draft and incomplete.
- The Law 14/2025 source comparison is waiting for the user's two files: law_rows_ar.jsonl and manually saved Gazette text. Neither file belongs in Git.
- SMTP delivery, public HTTPS origin, production MFA key management and external operational configuration require deployment-side setup.
- Live production storage, independent security review, device acceptance and Egyptian-counsel acceptance remain external release work.

## Next
1. Receive both Law 14/2025 source files; compare all 311 rows against the Gazette, prioritize numeric differences, and produce the 120-article tick-sheet.
2. Run the existing legal evaluation tools against the 155 draft questions and publish measured per-category retrieval/refusal results. Draft questions are not lawyer-approved answer keys.
3. Dry-run the manual-capture, article-audit and reference-comparison ingestion path on a fixture; record exact commands in the law-ingestion runbook.
4. Keep source status explicit: candidate or source-matched only until an Egyptian lawyer reviews it.

**Release boundary:** Do not describe the corpus or legal answers as verified, legally approved, or suitable for client reliance without documented Egyptian-counsel review.
