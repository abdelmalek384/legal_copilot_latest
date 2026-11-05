# Law 14/2025 comparison package manifest

All files in this directory are derived review artifacts. The Gazette PDF and candidate `law_rows_ar.jsonl` are intentionally excluded.

## Complete data exports

| File | Data rows | Contents |
|---|---:|---|
| `law_14_2025_differing_articles_part1.csv` | 100 | Difference records 1–100 |
| `law_14_2025_differing_articles_part2.csv` | 100 | Difference records 101–200 |
| `law_14_2025_differing_articles_part3.csv` | 73 | Difference records 201–273 |
| `law_14_2025_quantity_tick_sheet_part1.csv` | 60 | Quantitative provisions 1–60 |
| `law_14_2025_quantity_tick_sheet_part2.csv` | 60 | Quantitative provisions 61–120 |

The five CSV files were fetched back from the PR branch and checked for headers and row counts: 273 difference records and 120 quantitative provisions, excluding headers.

## Other review artifacts

- `law_14_2025_comparison_report.md`: method, counts, five numeric-alert triage notes, limitations, trust status.
- `law_14_2025_numeric_alert_review.csv`: five individually inspected numeric alerts.
- `law_14_2025_discrepancy_article_index.md`: grouped list of differing article identifiers.
- `law_14_2025_quantitative_review_checklist.md`: article ID checklist for visual review.
- `law_14_2025_minor_difference_visual_spot_checks_part1.csv` through `part22.csv`: 221 unique minor-difference page-image spot checks (one duplicate Article 23 row was removed); all 221 minor-difference records are checked; none remain.
- `law_14_2025_source_match_record.json`: machine comparison metadata and release restrictions; 73/120 quantitative cues are checked and 47 remain.

## Trust boundary

Status is **source-matched, not lawyer-reviewed**. No row is represented as legally verified. The instrument remains non-authoritative and retrieval-ineligible until original page review, provenance/currentness/rights checks, and qualified Egyptian lawyer review are completed.
