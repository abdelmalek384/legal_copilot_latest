# Project status

**Updated:** 2026-11-04  
**Scope:** engineering and knowledge quality; not a legal-readiness certification.

## Working

- Core case-management workflows and the profile-separated control / per-firm / shared-corpus database architecture are implemented.
- Authentication, firm access controls, MFA, audit, billing/invoices, reminders, deadline workflow, exports and first-run setup have automated regression coverage.
- Arabic/English lexical retrieval, source citation checks, abstention behavior, legal-source registry and evidence-preserving ingestion tools are implemented.
- Repository CI includes unit/integration tests, browser acceptance, dependency audit, CodeQL and Bandit.

## Not verified / blocked

- **No Egyptian law in the product is lawyer-verified.** Candidate metadata, unofficial transcriptions and fictional fixtures are not legal authority.
- Law 14/2025 source matching is waiting for the user-supplied `law_rows_ar.jsonl` (311 rows) and manually saved Gazette text. The 120 quantity-bearing provisions require individual numeric checks; six orthography outliers should be compared first.
- The draft evaluation questions have no lawyer-approved answers. Their metrics can measure retrieval and refusal, not legal correctness.
- Deadline rules and holiday coverage remain draft; calculated dates require independent legal/calendar review.
- Production email, public-origin and MFA functions require deployment-specific SMTP, HTTPS-origin and dedicated MFA-key configuration and staging.

## Next

1. Measure the existing 155-question draft set with the three legal evaluation tools; report per-category top-1/top-3, wrong-article, abstention and claim-support metrics.
2. Tune Arabic colloquial/synonym handling only if measured top-3 recall is below 80%, preserving wrong-article = 0 and must-abstain behavior.
3. Dry-run the manual-capture, article-row audit and corpus/reference comparison path on a fixture; record exact commands in the law-ingestion runbook.
4. When both Law 14/2025 files arrive, produce the comparison report and 120-article numeric tick-sheet; register the result as **source-matched, not lawyer-reviewed**.

Never describe a source-matched result as verified without qualified Egyptian-lawyer review.