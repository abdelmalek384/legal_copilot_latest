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

273 of 311 rows are non-identical under the machine comparison. These are triage results, not proof that the candidate text is wrong. The complete article-level difference export and 120-row tick sheet remain local working artifacts pending transfer; no original source file is included in this repository change.

## Numeric alerts examined individually

- Article 21: both Gazette extraction and candidate show 0.25% and «ربع في المائة»; token spacing/layout caused the alert.
- Article 82: both show 0.5% and «نصف في المائة»; token spacing/layout caused the alert.
- Article 124: both show 15, 21, 30 and 45 days; 10 years; age 50; six months; and 7 additional days; word segmentation caused the alert.
- Article 146: PDF text extraction reverses RTL list order as (2, 1); Gazette page layout and candidate show (1, 2). Both show three days.
- Article 298: extra digits are the printer/deposit colophon on PDF page 112, after Article 298 ends on page 111.

None of these five is a confirmed statutory numeric difference. Original page images should still be retained for visual confirmation.

## Required review

- All remaining non-identical machine results require inspection of original Gazette page images. Similarity classes are triage labels, not proof of error.
- The 120-row quantitative tick sheet remains unreviewed; every lawyer decision field is blank.
- Six spelling outliers (66, 103, 124, 134, 141, 278) remain first-priority visual checks.
- Publication date: 2025-05-03. Do not treat this as commencement. Project context records general commencement as 2025-09-01 and specialized labour courts as 2025-10-01 (promulgation Article 13), both subject to counsel review.

## Trust and release status

Trust tier: `source_matched_not_lawyer_reviewed`. This does not mean lawyer-verified, current, authoritative, or approved for retrieval. The instrument remains non-authoritative and retrieval-ineligible pending discrepancy resolution, source/currentness/rights checks, and qualified Egyptian lawyer review.

## Limitations

- PDF text extraction is not visual page-image review or OCR verification.
- This comparison does not establish source authenticity, amendment/corrigendum completeness, legal currentness, effective-date interpretation, or collection/commercial-reuse permission.
- Neither the original PDF nor `law_rows_ar.jsonl` is included in this repository output.
