# Project status

**Updated:** 2026-11-04

## What works
- Arabic-first case and firm workflows, including matters, teams, tasks, sessions, fees, notes, files and activity history.
- Separate control-plane, per-firm tenant databases, and shared legal-corpus database.
- MFA, account lifecycle, audit controls, billing/invoices, reminders, exports, pilot metrics and first-run setup are implemented and have substantial automated coverage.
- Legal ingestion, provenance, comparison, retrieval, citation and abstention tooling exists.
- Draft multi-area evaluation set contains 155 questions; no lawyer-approved answer key is present.

## Blocked / not accepted
- No Egyptian law is source-matched against its Gazette text or lawyer-verified in the product.
- Law 14/2025 comparison requires the user's law_rows_ar.jsonl and manually saved Gazette text.
- The 120 numeric/period-bearing Law 14/2025 articles require Gazette-by-Gazette human ticks; spelling variants need targeted comparison.
- Deadline rules and holiday coverage remain draft; calculated dates are not authoritative.
- Production acceptance still depends on deployment-specific SMTP, public HTTPS origin, MFA secret, and operational/legal review evidence.

## Next
1. Establish retrieval/refusal baseline from the 155 draft questions; report metrics without claiming legal correctness.
2. Tune only colloquial/synonym gaps below the specified 80% threshold, preserving abstention and zero wrong-article answers.
3. Dry-run manual capture, article audit, reference comparison, numeric checklist, effective-date extraction and source-matched registration on a fictional fixture.
4. When both Law 14/2025 files arrive, run the source comparison and prepare the numeric tick-sheet; label the result **source-matched, not lawyer-reviewed**.
