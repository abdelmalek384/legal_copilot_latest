# Labour Law No. 14 of 2025 — source, commencement, and registry review

**Review date:** 2026-10-24  
**Result:** Metadata may be registered as a pending candidate. **Do not load the article text into searchable chunks or treat it as verified/current law.**

## 1. Permission and source findings

### Manshurat copy

The supplied `law_rows_ar.jsonl` records identify a Manshurat text copy. The current discoverable page is [قانون العمل الجديد رقم 14 لسنة 2025](https://manshurat.org/content/qnwn-lml-ljdyd-rqm-14-lsn-2025), which links to a PDF. This establishes that a text copy is available; it does **not** establish a license to copy, index, embed, display or commercially redistribute the text. No affirmative reuse license was located in this review. Permission remains **unknown**.

### Official Gazette evidence

The [IDSC repository record for Official Gazette issue 18 (supplement)](https://dspace.id.com.eg/items/75a95151-8a93-45c0-a607-9320863881df) identifies the publisher as Amiri Press, date 2025-05-03, and describes Law 14/2025. Its PDF is presented through a **request-a-copy** workflow rather than an immediately downloadable file.

The repository's [End User Agreement](https://dspace.id.com.eg/info/end-user-agreement) says the site's content is for personal, non-commercial use absent express written permission, prohibits commercial exploitation without prior written permission, and prohibits systematic retrieval to compile a database without written permission. Therefore the terms do **not** authorize the planned commercial legal database; written permission or a separately confirmed lawful source/license is needed. This is a permission gate, not a conclusion about the legal copyright status of the statute itself.

The [Amiri Press law text page](https://alamiria.com/Sec/TashTxt?id=vPdoWGGYwoE%3D) is an official-source lead and exposes the promulgation clauses. It does not by itself prove permission for bulk storage or commercial reuse.

## 2. What was checked in the supplied JSONL

- SHA-256: `3e964de5c9cc994aefcc29c031712e85d664febd97c428e61c2eacdccaf1c600`
- Size: 393,861 bytes
- Records: 311; malformed JSON lines: 0
- 13 promulgation/introductory articles and 298 articles of the accompanying Labour Law
- All 311 rows have `verified=0` and `in_force=1`. The `in_force=1` value is an untrusted input flag and must not be treated as legal review.

The visible opening pages of the linked Manshurat PDF contain the same enactment title, Gazette issue/date, promulgation Articles 1–13 and the commencement/repeal clauses described below. **A complete article-by-article match against the official Gazette original has not been completed.** The original issue PDF was not obtained and page-reviewed in this session; no exact official Gazette page range has been verified. Record-count agreement is not proof that every article is textually identical or complete.

## 3. Commencement and repeal provisions found

The promulgation text states:

- **Publication/issuance date:** 2025-05-03; Official Gazette issue 18 (supplement).
- **General commencement:** 2025-09-01 under Article 13's formula. This date is also listed by [Manshurat](https://manshurat.org/content/qnwn-lml-ljdyd-rqm-14-lsn-2025), the [ILO NATLEX entry](https://natlex.ilo.org/dyn/natlex2/r/natlex/fe/results?clear=2&p2_country_filter=EGY&p2_home_flag=Y), and the [Library of Congress summary](https://www.loc.gov/item/global-legal-monitor/2025-07-25/egypt-labor-law-updated/).
- **Specialized labour courts:** commencement 2025-10-01 under Article 13.
- **Repeals:** Article 12 repeals Labour Law No. 12 of 2003 and Law No. 125 of 2010 on the priority of workers' rights, along with conflicting provisions.
- **Transitional rules:** Articles 2, 6, 8–11 include transitional arrangements and implementation authority. These must remain separately represented; a single effective date is not enough to answer every temporal question.

## 4. Amendment and implementation search

No direct statute amending Law 14/2025 was confirmed in this limited search. This is **not** a complete certification that no later amendment exists. The review found later instruments made under or referring to the law, which must be registered as separate documents and linked using `implements` (or another relation only where the text supports it), not incorrectly labelled as amendments:

- [Prime Minister's Decree 2652/2026](https://alamiria.com/Sec/TashTxt?id=MWc8qnk3Yg8%3D), dated 2026-09-07, extends the period for private employment agencies to regularize their status under the final paragraph of Article 6 by six months.
- [Labour Ministry Decision 74/2026](https://alamiria.com/Sec/TashTxt?id=7RH1OgZLsC8%3D), concerning labour-market observatories.
- [Labour Ministry Decision 75/2026](https://alamiria.com/Sec/TashTxt?id=82Iv%2FEE2jDk%3D), concerning work prohibited for women for maternity or occupational safety/health reasons.
- The Ministry's [laws and legislation index](https://www.labour.gov.eg/en/laws-and-legislations/) and the official issue metadata for [Egyptian Proceedings issue 291 (supplement)](https://dspace.id.com.eg/items/37add437-802d-4848-8a24-8e064db22fcc) are additional discovery leads for implementing decisions, including decisions numbered 259, 260, 264 and 271 of 2025. Exact texts, publication pages, commencement, and later status still require individual review.

## 5. Registry decision

The accompanying `registry_candidate.json` and `tools/register_labour_law_candidate.py` create **metadata-only** records in the application's versioned legal-source registry. The version is stored as `under_review` / `pending_source_review`; authenticity, status, amendment history, licensing and lawyer approval remain unverified. No chunks are created, and nothing becomes searchable.

The script records the supplied JSONL hash in notes only; it deliberately does not mislabel that hash as the original Gazette PDF hash. It is idempotent and preserves existing reviewer decisions. Run it against the local application database only after reviewing the PR. This environment cannot access or modify the user's local SQLite database directly.

## Required blockers before activation

1. Written permission covering the intended storage, indexing, embedding, display, and commercial reuse—or a separately confirmed lawful/licensed source.
2. Authorized acquisition of the original Gazette PDF and a full 311-record article-by-article comparison with exact page evidence.
3. Individual registration and date/status review of the relevant implementing decisions and transitional extensions.
4. Qualified Egyptian lawyer approval before setting authenticity/status/amendment flags or enabling search.


## 5. Supplemental targeted primary-source review — 2026-10-28

A government-hosted PDF copy of Official Gazette issue 18 (supplement) was opened at the Egyptian Tax Authority portal:

- PDF: https://portal.eta.gov.eg/sites/default/files/2026-03/law.no_.14.of_.2025.pdf
- Printed page 2 (PDF page index 0): promulgation Article 1.
- Printed page 5 (PDF page index 3): promulgation Articles 12–13 (repeal and commencement clauses).
- Printed page 12 (PDF page index 9): accompanying-law Articles 4–6 (forced labour/harassment, non-discrimination, and worker-rights waiver provisions).
- Printed page 43 (PDF page index 41): accompanying-law Articles 89–90 (written employment contracts and probation).

This is a targeted extracted-text review, not a complete visual inspection of the PDF. The file was not downloaded or hashed. The 311-row article-by-article comparison, full amendment/currentness review, and qualified Egyptian-lawyer approval remain pending. Source collection and commercial-reuse permission remain unknown. This evidence does not change the registry's pending verification flags or make the law search-eligible.


The printed page 43 evidence is included in the four-page targeted review set; it adds two provision pinpoints to the provisional review seed but does not change pending authenticity, currentness, amendment-history, permission, or lawyer-review statuses.


Further targeted extracted-text review on 2026-10-28 covered printed page 52 (Articles 117 and 121) and printed pages 54–55 (Article 124). This extends the provisional review seed to working hours, overtime and annual leave without changing pending legal-status, amendment-history, permission or counsel-review flags.


Further targeted extracted-text review on 2026-10-28 covered printed pages 68–70 (Article 165) and 73–74 (Article 177). This adds termination-compensation and court-jurisdiction provisions to the provisional review seed while preserving all pending verification and permission flags.


Further targeted extracted-text review on 2026-10-28 covered printed pages 61–62 (Article 141) and 63–64 (Article 148). These additions document disciplinary procedure and dismissal conditions while preserving pending legal-status, amendment-history, permission and lawyer-review flags.


Further targeted extracted-text review on 2026-10-28 covered printed pages 52–53 for Article 120 (weekly rest). This extends the provisional knowledge seed without changing pending legal-status, amendment-history, permission or lawyer-review flags.


Further targeted extracted-text review on 2026-10-28 covered Articles 118–119 (printed page 52) and Article 122 (printed pages 53–54), adding break-period, daily-presence-span and schedule-posting rules to the provisional seed.
