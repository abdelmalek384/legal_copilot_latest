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

**Outcome: structural and spot checks only; full official-Gazette comparison remains blocked.**

The supplied file was parsed and its article numbering/counts inspected. The accessible Manshurat PDF text was checked at the promulgation provisions and sampled at the beginning and end of the accompanying law. The title, Gazette issue/date, promulgation clauses, Article 12 repeal clause, Article 13 commencement clause, and sampled opening/closing article text are consistent with those visible text extracts.

Supplemental review on 2026-10-28 located a government-hosted copy of the Official Gazette PDF at the Egyptian Tax Authority portal. Extracted text was reviewed for printed pages 2, 5, 12, and 43, covering promulgation Article 1, promulgation Articles 12–13, accompanying-law Articles 4–6, and accompanying-law Articles 89–90. The PDF file itself was not downloaded or hashed. Selected pages were later visually inspected through the browser PDF viewer, but no full scan review or row-by-row comparison was completed. Therefore, no claim is made that all 311 rows have been matched verbatim to the Gazette. The following remain outstanding:
- page-by-page and article-by-article comparison of all 13 promulgation provisions and all 298 law articles;
- exact wording, numbering, paragraph boundaries, omissions, insertions, and duplicates;
- full page-by-page and article-by-article comparison beyond the four targeted pages;
- visual scan integrity, exact PDF hash, and any corrigenda.

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
2. Obtain the exact Official Gazette issue through an authorized route and complete the 311-record comparison with page-level evidence.
3. Register and review relevant implementing instruments and their temporal effects; distinguish `implements` from `amends`.
4. Have qualified Egyptian counsel verify commencement, transition, repeal/supersession, and the relevant as-of timeline.
5. Only then record affirmative review events and consider enabling eligible version-linked chunks.


Further targeted extracted-text review on 2026-10-28 also covered printed page 43 (PDF page index 41), containing accompanying-law Articles 89–90 on written employment contracts and probation. This adds two provision pinpoints to the provisional review seed; it does not change the pending authenticity, currentness, amendment-history, permission, or lawyer-review statuses.


Further targeted text review on 2026-10-28 covered printed page 52 (Articles 117 and 121: ordinary working hours and overtime) and printed pages 54–55 (Article 124: annual leave). These are provision summaries for review, not lawyer-approved advice; no full-law comparison or currentness certification is claimed.


Further targeted extracted-text review on 2026-10-28 covered printed pages 68–70 (Article 165: compensation for unlawful termination of an indefinite-term contract) and pages 73–74 (Article 177: specialized labour-court jurisdiction). These are provisional summaries and do not certify currentness or substitute for counsel review.


Further targeted extracted-text review on 2026-10-28 covered printed pages 61–62 (Article 141: disciplinary investigation and reasoned decisions) and pages 63–64 (Article 148: dismissal authority and gross-misconduct conditions). These are provisional summaries; the full legal context and counsel review remain pending.


Further targeted extracted-text review on 2026-10-28 covered printed pages 52–53 for Article 120 (weekly rest period and limited aggregation exception). The summary remains provisional and requires review against the full text and applicable implementing rules.


Further targeted extracted-text review on 2026-10-28 covered printed page 52 (Articles 118–119: meal/rest breaks and daily presence span) and printed pages 53–54 (Article 122: posted work schedule and notice of changes). These summaries remain provisional and require counsel review.


Further targeted extracted-text review on 2026-10-28 covered printed page 55 for Article 129 (paid holidays and compensation if work is required on those days). The specific ministerial or cabinet decision designating a holiday must be verified for each query.


Further targeted extracted-text review on 2026-10-28 covered printed page 71 (Article 173: termination due to illness) and page 72 (Article 171: retirement age and fixed-term contracts). These remain provisional summaries pending review of connected laws and case-specific conditions.


Further targeted extracted-text review on 2026-10-28 covered printed page 69 (Article 164: notice-period compensation) and page 70 (Article 166: absence deemed resignation and required warnings). These summaries remain provisional and require case-specific procedural review.
