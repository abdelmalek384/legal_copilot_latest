# Lawyer review handoff — Legal Copilot

## Purpose
These are review aids, not legal opinions, verified legal texts, or production approval. Record corrections and source references; do not rely on draft values until signed off.

## Gazette comparison — Law 14/2025
- Scope: 13 promulgation provisions plus 298 Labour Law articles (311 rows).
- The comparison CSV is a template. Candidate and Gazette text columns are blank because the repository review tick sheet contains locator/review metadata, not complete text in comparison columns.
- For each row, compare exact candidate wording against authorized Gazette text/page image. Record `match`, `mismatch`, or `unresolved`; quote/correct affected passages and record printed page.
- Check negations, exceptions, dates, periods, amounts, percentages, article references and transitional provisions.
- Do not set `verified=1` or approve currentness/reuse rights from this worksheet.

## Deadline rules
- Five draft rules are listed with assumptions and likely source families.
- Every period, trigger, applicable procedure, counting rule, holiday extension and exception requires confirmation against current primary legislation and amendments.
- Record exact article/paragraph, authoritative source, scope, trigger event, counting method, exceptions and review date.
- No rule is approved; do not enable automated deadline advice until signed approval is recorded.

## How to use the CSV worksheets (one-page quick guide)

1. Open the CSV in a spreadsheet application and import it as **UTF-8** (UTF-8 with BOM is recommended for Arabic text in Excel). Do not change the stable row IDs or article/rule references.
2. In `our_text`, confirm the exact candidate/draft wording against the candidate record. In `gazette_text`, transcribe the exact corresponding primary Gazette wording; for deadline rules, use the governing primary instrument text and note that the column is serving as the primary-source text field.
3. Set `match_mismatch` to `match`, `mismatch`, or `unresolved` only after comparing the wording. If the source text or applicable instrument is unavailable, leave the status pending/unresolved; do not infer a match from article/page metadata.
4. Use `reviewer_notes` for the exact correction, article/paragraph, printed page, date/trigger, exception, amendment or unresolved issue. Record the reviewer identity and review date in the designated metadata fields where available.
5. Save/export as **CSV UTF-8**. Preserve all columns, keep quoted commas/newlines valid, and return the reviewed file without changing the original. Never change `verified=0` or mark a deadline rule approved through the worksheet alone.

## Suggested review effort
- Initial triage of 311 Gazette rows: approximately 4–6 hours if authorized candidate text and Gazette pages are immediately available.
- Full legal/currentness review: plan separately; likely 1–2 working days depending on complexity and amendments.
- Five deadline rules: approximately 2–3 hours for source confirmation and edge-case review, excluding unresolved special laws or court-specific practice.

These are planning estimates, not commitments. Adjust after sampling the source material.

## Reusable deliverables
- `docs/legal_evidence/law_14_2025_gazette_comparison_template.csv`
- `docs/legal_evidence/deadline_rules_lawyer_review.csv`
