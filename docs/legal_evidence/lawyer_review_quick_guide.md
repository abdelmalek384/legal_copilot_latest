# Lawyer review quick guide — Legal Copilot

**These CSVs are review aids only. They are not verified legal texts or legal advice.**

## Files

1. `law_14_2025_gazette_comparison_template.csv` — one row for each of 13 promulgation provisions and 298 Labour Law articles (311 rows).
2. `deadline_rules_lawyer_review.csv` — five draft deadline rules.

## How to review

1. Import/open each CSV as **UTF-8** (UTF-8 with BOM is recommended for Arabic in Excel). Preserve row IDs, article/rule references and column names.
2. In `our_text`, enter or confirm the exact candidate/draft wording.
3. In `gazette_text`, enter the exact matching Official Gazette wording. For deadline rules, use the governing primary instrument text; do not rely on the likely-source note alone.
4. Set `match_mismatch` to `match`, `mismatch`, or `unresolved` only after comparing the full text. If the authorized source is unavailable, leave it pending/unresolved.
5. In `reviewer_notes`, record the exact correction, article/paragraph, printed page, relevant date/trigger, counting method, exception, amendment or reason for uncertainty.
6. Save/export as **CSV UTF-8**, preserving all columns and valid CSV quoting. Return the reviewed copy separately; do not overwrite the source candidate.
7. Keep every Law 14/2025 `verified` field at `0`. A worksheet entry is not a signed lawyer approval.

## What to check

Compare complete Arabic wording, including headings, negations, exceptions, dates, periods, amounts, percentages, conditions, cross-references and transitional provisions. For deadlines, also verify the governing procedure, trigger event, start/end-day counting, service requirements, holidays, extensions, exceptions and amendments.

## Estimated review time

- **311 Gazette provisions:** approximately **4–6 hours** for initial row-by-row triage when the authorized candidate text and matching Gazette pages are ready.
- **Full legal/currentness review:** plan **1–2 working days** separately, depending on amendments and interpretive complexity.
- **Five deadline rules:** approximately **2–3 hours** for primary-source confirmation and edge-case review.

These are planning estimates, not commitments. Time excludes obtaining restricted or missing source documents and any additional research required to resolve amendments or special procedures.

**Trust boundary:** Law 14/2025 remains source-matched, not lawyer-reviewed; its source/reuse permission, currentness and legal interpretation remain open. No item becomes verified or approved merely by filling this worksheet.
