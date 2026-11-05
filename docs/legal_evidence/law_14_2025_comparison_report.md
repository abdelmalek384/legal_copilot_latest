# Law 14/2025 — Gazette comparison (evidence only)

**Machine label: Source-matched, not lawyer-reviewed.** This is a comparison record, not legal approval.

- Candidate JSONL rows compared: 311 (SHA-256: `3e964de5c9cc994aefcc29c031712e85d664febd97c428e61c2eacdccaf1c600`)
- Gazette PDF pages: 112 (SHA-256: `b0a47cefe18722d3f23e004ac7e78e6e309010e13124413e7e7018820c9581be`)
- Gazette article headings detected: 311
- PDF extraction: `pdftotext -layout`
- Candidate structural audit: 311 rows; 13 promulgation provisions + 298 law articles; no numbering gaps, duplicate labels or duplicate texts; 120 quantitative articles; six orthography outliers.

## Machine comparison results

| Machine status | Rows |
|---|---:|
| Identical after normalization | 38 |
| Minor difference | 221 |
| Major difference | 47 |
| Numeric difference alerts | 5 |
| Missing / extra headings | 0 / 0 |

273 of 311 rows are non-identical under the machine comparison. These are triage results, not proof that the candidate text is wrong. The complete article-level CSV with similarity/page ranges is committed in three parts (273 records total), and the 120-row quantitative cue worksheet is committed in two parts. Repository review aids also include `law_14_2025_discrepancy_article_index.md` and `law_14_2025_quantitative_review_checklist.md`. No original source file is included in this repository change.

## Visual review progress

| Review group | Completed | Remaining | Result on inspected passages |
|---|---:|---:|---|
| Numeric alerts | 5/5 | 0 | All five explained by extraction, RTL ordering or colophon artifacts |
| Major differences | 47/47 | 0 | All inspected passages match candidate |
| Minor differences | 80/221 | 141 | All inspected passages match candidate |
| Quantitative provision cues | 0/120 | 120 | Not yet manually checked |
| Known orthography outliers | 6/6 | 0 | All checked passages match candidate; this overlaps the groups above |

The minor-difference visual review contains 80 unique article records across nine CSV batches. The initial batch series contained one duplicate Article 23 row; it has been removed. The reviewed passages are not a substitute for a complete legal proofread or counsel sign-off.

## Numeric alerts examined individually

- Article 21: both Gazette extraction and candidate show 0.25% and «ربع في المائة»; token spacing/layout caused the alert.
- Article 82: both show 0.5% and «نصف في المائة»; token spacing/layout caused the alert.
- Article 124: both show 15, 21, 30 and 45 days; 10 years; age 50; six months; and 7 additional days; word segmentation caused the alert.
- Article 146: PDF text extraction reverses RTL list order as (2, 1); Gazette page layout and candidate show (1, 2). Both show three days.
- Article 298: extra digits are the printer/deposit colophon on PDF page 112, after Article 298 ends on page 111.

All five numeric-alert locations were visually inspected against the supplied Gazette page images (pages 18, 40, 54, 63, 111 and 112). The visual checks confirm the tokenization/RTL/colophon explanations above; none is a confirmed statutory numeric difference. See `law_14_2025_numeric_alert_review.csv`.

## Visual spot checks — six orthography outliers

The six known orthography outlier locations were inspected against the supplied Gazette page images (pages 35, 48, 54–55, 57–58, 61–62 and 106). All six checked passages match the candidate text. I cross-checked Article 134 against the government-hosted ETA PDF (page 57): it reads «ولم يكن في تنفيذها ما يعرض للخطر», matching the candidate. An earlier apparent suffix discrepancy was a visual misread and is not retained as a finding. The ETA URL is an independent locator, not proof that the user-supplied PDF was downloaded from that URL. See `law_14_2025_orthography_spot_checks.csv`. Government-hosted comparison locator: https://portal.eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf.

## Major-difference visual checks

All 47 machine-classified major differences were inspected against the supplied Gazette page images in two CSV batches. All 47 checked passages match the candidate JSONL on the inspected text; no major-difference record produced a confirmed textual mismatch. See `law_14_2025_major_difference_visual_spot_checks.csv` and `law_14_2025_major_difference_visual_spot_checks_part2.csv`.

## Minor-difference visual checks

Seventy-nine unique minor-difference records were inspected against the supplied Gazette page images; all 79 inspected passages match the candidate JSONL on the checked text. The remaining 142 minor-difference records have not been visually reviewed. Article 26 was removed from this group because its machine status is identical after normalization; its 500 EGP quantitative cue was instead checked and marked in the quantitative worksheet. The minor-difference checks are listed in `law_14_2025_minor_difference_visual_spot_checks_part1.csv` through `part10.csv`.

## Required review and release gates

- Visually review the remaining 141 minor-difference records.
- Review all 120 quantitative provisions against the original Gazette pages and complete the lawyer decision fields in the tick sheet.
- Obtain the exact source URL and capture date for the user-supplied PDF; the ETA-hosted PDF URL above is an independent comparison locator, not proven upload provenance.
- Verify subsequent amendments, corrigenda, currentness, legal effective-date interpretation, and source/reuse rights.
- Obtain qualified Egyptian lawyer review before any authoritative or retrieval-eligible designation.
- Publication date: 2025-05-03. Do not treat this as commencement. Project context records general commencement as 2025-09-01 and specialized labour courts as 2025-10-01 (promulgation Article 13), both subject to counsel review.

## Trust and limitations

Trust tier: `source_matched_not_lawyer_reviewed`. This does not mean lawyer-verified, current, authoritative, or approved for retrieval. The instrument remains non-authoritative and retrieval-ineligible pending the gates above.

The comparison uses PDF text extraction plus limited page-image checks. It does not establish source authenticity, amendment/corrigendum completeness, legal currentness, effective-date interpretation, or collection/commercial-reuse permission. Neither the original PDF nor `law_rows_ar.jsonl` is included in this repository output.
