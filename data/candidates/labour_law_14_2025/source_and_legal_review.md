# Labour Law No. 14 of 2025 — source and legal-status review

**Review state: provisional desk review only. Not a legal opinion; not approved for authoritative retrieval.**  
**Current detailed findings:** [review_report_2026-10-24.md](review_report_2026-10-24.md).

## Candidate corpus inspected

- Instrument: قانون رقم 14 لسنة 2025 بإصدار قانون العمل
- Supplied file: `law_rows_ar.jsonl`
- SHA-256: `3e964de5c9cc994aefcc29c031712e85d664febd97c428e61c2eacdccaf1c600`
- Size: 393,861 bytes
- Records: 311 valid JSONL records; 0 malformed lines
- Composition: 13 promulgation provisions and 298 articles of the accompanying law
- Every row has `verified=0`; every row has `in_force=1`. The latter is untrusted input and must never be used to establish legal status.
- The file remains outside the public repository because redistribution and commercial-reuse permissions have not been established.

## 1. Permission findings

**Outcome: unresolved; do not treat permission as granted.**

The supplied rows identify a secondary-hosted Manshurat text copy. The public page and linked PDF establish availability, not a license to reproduce, store, index, embed, display, redistribute, or use the text commercially.

The IDSC repository's [End User Agreement](https://dspace.id.com.eg/info/end-user-agreement) permits personal, non-commercial use absent express written permission, prohibits commercial exploitation without prior written permission, and prohibits systematic retrieval to compile a database without written permission. Its Official Gazette issue record identifies issue 18 (supplement), dated 2025-05-03, but the PDF is presented through a request-a-copy workflow.

No written permission was requested or obtained in this review. Keep collection, redistribution, indexing, and commercial-use permission unknown until an authorized source or express written permission is documented.

## 2. Text comparison status

**Outcome: all 311 candidate provisions have recorded Gazette page locators and page-image comparison notes; source-matched, not lawyer-reviewed.**

On 2026-11-06, the exact 112-page user-supplied Official Gazette comparison PDF and the 311-row candidate JSONL were recovered from the user's Library source bundle. Their independently computed SHA-256 values match the hashes recorded in `docs/legal_evidence/law_14_2025_source_match_record.json`:

- Candidate JSONL: `3e964de5c9cc994aefcc29c031712e85d664febd97c428e61c2eacdccaf1c600` (393,861 bytes; 311 rows).
- Supplied Gazette comparison PDF: `b0a47cefe18722d3f23e004ac7e78e6e309010e13124413e7e7018820c9581be` (112 pages).

The comparison package records:
- 311/311 provisions with page locators and page-image comparison notes.
- 38 identical-after-normalization, 221 minor-difference, 47 major-difference, five numeric-alert, and zero missing/extra machine-comparison records.
- All 221 minor-difference records and all 47 major-difference records visually checked; no confirmed textual mismatch was found in the inspected passages.
- All five numeric alerts visually examined and explained by extraction, RTL ordering, or colophon artifacts; no confirmed statutory numeric difference was found.
- All 120 quantitative provision cues visually checked (120/120).
- All six known orthography outliers checked.
- The 29 provisions that previously lacked targeted page-image review received full-article visual comparisons on 2026-11-06; the candidate wording matched on the inspected pages.

These results complete the recorded assistant visual-comparison work. They do **not** constitute a complete legal proofread, independent source-authenticity certification, counsel sign-off, amendment/currentness review, rights clearance, or approval for authoritative retrieval. The 273 machine-difference records, 120 quantitative cues, six outliers, and other visual-check groups overlap; do not add their counts together.

The supplied PDF reports copy/print restrictions. Its original upload URL and capture chain remain unknown. The matching SHA-256 values establish the identity of the recovered files against the repository's recorded hashes; they do not establish who published or uploaded the PDF, permission to copy/extract/index/redistribute it, or byte identity with separate ETA/SIS-hosted PDFs. Do not bypass the PDF restrictions or infer a reuse licence.

The 311-row JSONL remains outside the public repository because redistribution and commercial-reuse permissions have not been established. Keep every row's `verified=0` unchanged; do not treat the embedded `in_force=1` or `as_of=2025-05-03` as trusted legal-status or commencement determinations. The law remains non-authoritative and retrieval-ineligible pending the remaining gates below.

Supporting details are in [the comparison report](../../docs/legal_evidence/law_14_2025_comparison_report.md), [the lawyer review packet](../../docs/legal_evidence/law_14_2025_lawyer_review_packet.md), and [the source-match record](../../docs/legal_evidence/law_14_2025_source_match_record.json).

## 3. Commencement, repeals, and subsequent instruments

The accessible official Amiri Press text page and targeted extracted text from the government-hosted Gazette PDF state:
- Publication/issuance: 2025-05-03, Official Gazette issue 18 (supplement).
- General commencement: 2025-09-01 under Article 13's formula; this date is also reported by [Manshurat](https://manshurat.org/content/qnwn-lml-ljdyd-rqm-14-lsn-2025), [ILO NATLEX](https://natlex.ilo.org/dyn/natlex2/r/natlex/fe/results?clear=2&p2_country_filter=EGY&p2_home_flag=Y), and the [Library of Congress](https://www.loc.gov/item/global-legal-monitor/2025-07-25/egypt-labor-law-updated/).
- Specialized labour courts: 2025-10-01 under Article 13.
- Article 12 repeals Labour Law No. 12 of 2003 and Law No. 125 of 2010 on the priority of workers' rights, as well as conflicting provisions.
- Promulgation Articles 2, 6, and 8–11 contain transitional or implementation provisions; these must not be flattened into a single commencement date.

A limited discovery review found subsequent instruments that refer to or implement Law 14/2025, including Prime Minister's Decree 2652/2026 and Labour Ministry Decisions 74/2026 and 75/2026. These are separate instruments, not automatically amendments to Law 14/2025. No direct amending statute was confirmed in this limited search; this is not a complete negative certification. Each instrument's original publication, commencement, operative effect, and relation to the law still requires individual review.

## 4. Versioned registry decision

**Decision: metadata-only pending candidate; do not activate article text for search.**

`registry_candidate.json` and `tools/register_labour_law_candidate.py` are prepared to register the source, document, version, and pending review events in the application's versioned registry. The tool intentionally:
- creates metadata and pending review events only;
- keeps authenticity, legal-status, and amendment-history verification false;
- ignores the incoming `verified` / `in_force` claims;
- imports no article chunks and does not make the candidate searchable.

The candidate's general and specialized-court commencement dates remain evidence-backed leads pending primary-source comparison and Egyptian counsel review. The source file's SHA-256 is recorded only as the hash of the supplied JSONL, not the original Gazette.

This session cannot access or modify the user's local SQLite database. The registry script has therefore **not** been run against the user's application database. Do not represent the local database as updated until that operation is executed and its result confirmed.

## Required gates before activation

1. Obtain written permission covering the intended storage, extraction, indexing, embeddings, display, and commercial use, or identify a separately confirmed lawful/licensed source.
2. Complete the remaining article-by-article comparison of all 311 records, including exact wording and page-level evidence; the 120-item quantitative check is not a substitute.
3. Register and review relevant implementing instruments and their temporal effects; distinguish `implements` from `amends`.
4. Have qualified Egyptian counsel verify commencement, transition, repeal/supersession, and the relevant as-of timeline.
5. Only then record affirmative review events and consider enabling eligible version-linked chunks.

## Historical targeted review notes

Further targeted extracted-text reviews on 2026-10-28 covered selected provisions on probation, working hours, overtime, annual leave, termination, specialized labour-court jurisdiction, disciplinary investigations, dismissal, weekly rest, breaks, work schedules, paid holidays, illness, retirement age, notice-period compensation, and absence. These remain provisional summaries and are not a substitute for the complete text comparison or counsel review.
