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

However, the exact Official Gazette PDF was not obtained and page-reviewed. The secondary PDF is not a substitute for an authorized copy of the primary issue. Therefore, no claim is made that all 311 rows have been matched verbatim to the Gazette. The following remain outstanding:
- page-by-page and article-by-article comparison of all 13 promulgation provisions and all 298 law articles;
- exact wording, numbering, paragraph boundaries, omissions, insertions, and duplicates;
- official Gazette page references and any corrigenda.

## 3. Commencement, repeals, and subsequent instruments

The accessible promulgation text states:
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
