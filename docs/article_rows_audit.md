# Auditing a JSONL corpus of article rows

`tools/audit_article_rows.py` checks that a candidate corpus is internally consistent and produces a targeted checklist for the human comparison with the official text.

```bash
python tools/audit_article_rows.py --input law_rows_ar.jsonl --out-dir audit_report
```

Outputs: `audit.md` (summary), `audit.json` (details), `quantity_checklist.csv` (every article that states a period, amount, percentage or count, for a reviewer to tick against the official text; articles with orthography outliers are marked "check first").

## What it checks
- Numbering per law/group: gaps, duplicates, order, non-numeric labels.
- Empty or very short text, hidden/replacement characters, mixed digit systems, double spaces, Latin fragments, Gazette header or page artifacts, repeated words.
- Rows that end without punctuation (shown with their last words; a trailing law citation is a natural ending).
- Exact duplicate article texts.
- Numeric cross-references past the highest article number.
- Orthography outliers: when one spelling style dominates (for example the Gazette's typographic "فى/التى/الذى"), the few rows in the other style may have been re-typed or taken from a different version.
- The embedded `verified`, `in_force` and `as_of` flags, which are reported and never trusted. In particular, an `as_of` equal to the publication date is not an effective date.

## What it does not do
A clean audit does not prove that the text matches the Official Gazette, that the law is in force, or that reuse is permitted. After the audit, run `tools/compare_corpus_to_reference.py` against the official text saved by hand.
