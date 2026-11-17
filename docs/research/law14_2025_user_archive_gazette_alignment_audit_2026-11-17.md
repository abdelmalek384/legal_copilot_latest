# Labour Law 14/2025 — 311-row supplied-corpus alignment audit against Gazette issue 18

Audit date: 17 November 2026  
Scope: compare the user-supplied `law_rows_ar.jsonl` (311 rows) with the user-supplied Gazette issue 18 supplement PDF dated 3 May 2025. Per the user's instruction, the supplied Gazette copy is treated as the source copy for this provisional comparison. This is a text-alignment audit, not a legal opinion, authenticity certificate or lawyer sign-off.

## 1. Source identity and hashes

| File | SHA-256 | Size / structure |
|---|---|---|
| Uploaded archive `untitled folder(1).zip` | `01ae7862fd78688bcd264ae31177123d9cf3df8686fe61f90fdd0e57535c8fca` | 801,176 bytes |
| `law_rows_ar.jsonl` | `3e964de5c9cc994aefcc29c031712e85d664febd97c428e61c2eacdccaf1c600` | 311 JSONL rows |
| `العدد-18-تابع-مومن-1.pdf` | `b0a47cefe18722d3f23e004ac7e78e6e309010e13124413e7e7018820c9581be` | 665,047 bytes; 112 A4 pages |
| `audit.json` | `f301857031a368fea83e9a29fb54029961b35d5df29b47ca81d9b8d0c9ef6955` | Structural audit metadata |

The PDF metadata reports encryption and permissions `print:no / copy:no / change:no`; every page also carries the watermark “صورة إلكترونية لا يعتد بها عند التداول”. The copy is treated as the supplied Gazette source for this provisional comparison, but it is not a certified Gazette original for court filing or official dealings. The PDF's copy restriction and watermark remain explicit source-rights/authenticity caveats.

## 2. Structural completeness

| Corpus section | Rows | Article numbering | Result |
|---|---:|---|---|
| Promulgation provisions | 13 | 1–13 | Complete; no gaps or duplicates |
| Attached Labour Law | 298 | 1–298 | Complete; no gaps or duplicates |
| **Total** | **311** | **311 numbered items** | **Complete numbering** |

Additional checks from the supplied structural audit:
- No malformed JSONL lines.
- No exact duplicate article texts.
- 168 numeric cross-references detected; none point beyond the highest article in the supplied file.
- Four rows lack terminal punctuation; this is a formatting observation, not a legal-text defect.
- Orthographic variants are present (e.g. فى/في, التى/التي, الذى/الذي); preserve the source text and normalize only in a separate search field.
- The source audit flags 120 articles containing quantitative values/periods/thresholds.

## 3. Automated text-alignment method

The 311 article texts were compared to the 112-page PDF text layer using Arabic normalization and two RapidFuzz measures:
- Unicode NFKC normalization; removal of diacritics, tatweel, directional controls and punctuation; normalization of alef/hamza and ya/alef-maqsura variants; whitespace normalization.
- Numeric tokens were excluded from the fuzzy comparison because the PDF's RTL text layer reverses or fragments some digit sequences. Therefore these scores do **not** certify numeric values, dates, article references, periods, monetary amounts or thresholds.
- `partial_ratio` measures sequence-level similarity against the full extracted Gazette text.
- `token_set_ratio` measures word-set overlap and is less sensitive to page breaks and line ordering.

### Results

| Sequence similarity (`partial_ratio`) | Rows |
|---|---:|
| 99–100 | 66 |
| 95–less than 99 | 124 |
| 90–less than 95 | 99 |
| 85–less than 90 | 17 |
| Below 85 | 5 |
| **Total** | **311** |

| Word-set overlap (`token_set_ratio`) | Rows |
|---|---:|
| 99–100 | 191 |
| 95–less than 99 | 116 |
| 90–less than 95 | 4 |
| Below 90 | 0 |
| **Total** | **311** |

The minimum word-set score was 93.04. A strict normalized substring check matched only 31 rows because page headers, watermark overlays, ligatures, line breaks and RTL extraction disrupt continuous substrings; it is not an appropriate sole acceptance test.

## 4. Five low sequence-score rows manually checked against their Gazette pages

| Corpus item | Sequence score | Word-set score | Gazette pages inspected | Finding |
|---|---:|---:|---|---|
| Promulgation Art.13 | 64.71 | 100.00 | p.5 | Text is present; the signature/effective-date block and line layout reduce sequence score |
| Labour Law Art.210 | 83.82 | 100.00 | pp.82–83 | Text is present across a page break |
| Labour Law Art.262 | 83.18 | 99.03 | pp.99–100 | Text is present across a page break; PDF extraction has RTL/line fragmentation |
| Labour Law Art.275 | 84.71 | 97.77 | pp.104–105 | Text is present; split heading and body across pages |
| Labour Law Art.294 | 83.45 | 100.00 | pp.109–110 | Text is present across a page break; numeric references are RTL-reordered in extracted text |

No substantive wording discrepancy was identified in these five manual spot checks. This is not a manual review of all 311 articles and does not establish that every number or footnote is exact.

## 5. What this audit establishes — and what it does not

**Established provisionally**
- The supplied JSONL contains exactly 13 promulgation provisions and 298 attached-law articles, with complete numbering.
- Every one of the 311 rows has strong word-set overlap with the supplied Gazette copy (minimum 93.04).
- The five lowest sequence-score cases were checked at their corresponding Gazette pages and appear to be page-break/RTL extraction artifacts rather than missing text.
- The JSONL is suitable for the next controlled numeric/source review stage without committing the raw JSONL to GitHub.

**Not established**
- Exact numeric equivalence for the 120 quantitative articles.
- Complete comparison of every punctuation mark, footnote, schedule, table or signature block.
- Certified authenticity of the electronic PDF copy; the visible watermark says it is not valid for official circulation.
- Currentness, amendments, repeal status or legal interpretation.
- Lawyer approval or commercial reuse rights.

## 6. Next validation stage

1. Run a separate numeric-token audit for the 120 quantitative articles using Gazette page images and a reviewer-approved Arabic-digit/RTL normalization procedure; never normalize away numbers in production text.
2. Manually compare the highest-risk thresholds, deadlines, monetary amounts, percentages, age limits, work/rest periods and statutory commencement dates.
3. Reconcile the four punctuation/orthography outliers and preserve both exact source text and normalized search text.
4. Obtain an authorized/certified Gazette copy if the current electronic copy is to be used as primary evidence in court or as a commercial source.
5. Have a qualified Egyptian labour lawyer sign off on legal accuracy/currentness before changing any `verified` flag.

## 7. Import and trust status

- Raw `law_rows_ar.jsonl` and the PDF are not committed to this repository by this audit.
- This report records only hashes, counts, match statistics and review locators.
- Keep all 311 rows `verified=0`; do not promote them to lawyer-reviewed.
- Keep source-rights status unchanged; no commercial reuse licence is asserted.
- Do not use this alignment score as a substitute for legal validation.
