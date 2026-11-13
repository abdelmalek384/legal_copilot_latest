# Law 14/2025 comparison package manifest

All files in this directory are derived review artifacts. The Gazette PDF and candidate `law_rows_ar.jsonl` are intentionally excluded.

## Complete data exports

| File | Data rows | Contents |
|---|---:|---|
| `law_14_2025_lawyer_review_tick_sheet.csv` | 311 | One lawyer decision row per promulgation provision / attached-law article; blank decisions and verified=0 |
| `law_14_2025_lawyer_review_packet.md` | — | Counsel instructions, source identity, all-311 page locators and prior assistant comparison notes, currentness leads and sign-off |
| `law_14_2025_differing_articles_part1.csv` | 100 | Difference records 1–100 |
| `law_14_2025_differing_articles_part2.csv` | 100 | Difference records 101–200 |
| `law_14_2025_differing_articles_part3.csv` | 73 | Difference records 201–273 |
| `law_14_2025_quantity_tick_sheet_part1.csv` | 60 | Quantitative provisions 1–60 |
| `law_14_2025_quantity_tick_sheet_part2.csv` | 60 | Quantitative provisions 61–120 |

The five CSV files were fetched back from the PR branch and checked for headers and row counts: 273 difference records and 120 quantitative provisions, excluding headers.

## Other review artifacts

- `law_14_2025_lawyer_review_packet.md` and `law_14_2025_lawyer_review_tick_sheet.csv`: 311-row counsel packet; every decision is blank and every verification flag is 0. All 311 rows now have page locators and page-image comparison notes. The earlier 282 comparisons plus 29 additional full-article visual comparisons on 2026-11-06 cover all 311 provisions; every lawyer decision remains blank and every `verified` value remains 0.
- `law_14_2025_comparison_report.md`: method, counts, five numeric-alert triage notes, limitations, trust status.
- `law_14_2025_numeric_alert_review.csv`: five individually inspected numeric alerts.
- `law_14_2025_discrepancy_article_index.md`: grouped list of differing article identifiers.
- `law_14_2025_quantitative_review_checklist.md`: article ID checklist for visual review.
- `law_14_2025_minor_difference_visual_spot_checks_part1.csv` through `part23.csv`: 221 unique minor-difference page-image spot checks (one duplicate Article 23 row was removed); all 221 minor-difference records are checked; none remain.
- `law_14_2025_source_match_record.json`: machine comparison metadata and release restrictions; 120/120 quantitative cues are checked; none remain.

## Trust boundary

Status is **source-matched, not lawyer-reviewed**. No row is represented as legally verified. All 311 provisions now have Gazette page locators and recorded page-image comparison notes: 282 earlier comparisons plus 29 additional full-article visual comparisons on 2026-11-06. All 221 minor-difference records, 47 major-difference records, five numeric alerts, 120 quantitative cues and six known orthography outliers have recorded visual checks; these groups overlap. No confirmed textual mismatch was found in the inspected passages. These are assistant visual checks, not counsel sign-off. The instrument remains non-authoritative and retrieval-ineligible pending qualified counsel review, comprehensive currentness/amendment/corrigendum checks, source/reuse-rights review and confirmation of the original upload provenance.

- `law_14_2025_currentness_snapshot_2026-11-05.md`: government-hosted corroborating copies and limited 2026 implementing-instrument watch list; not counsel-approved.
