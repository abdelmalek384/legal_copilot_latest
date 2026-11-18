# Research Agent 1 — checkpoint 160: normalized historical article-version event register (18 November 2026)

## 1. New structured artifact

Created:
`data/research/egypt_historical_article_version_events_2026-11-18.csv`

The file contains **44 version-event rows** with these fields:
- event ID;
- linked acquisition-register instrument ID;
- statute / regulation;
- affected article or schedule reference;
- event type (insert, replace, repeal, transitional extension, constitutional invalidation, consequential fall, deferral);
- effective date (or conditional/uncertain date);
- Gazette issue and publication date;
- source URL and source tier;
- text-normalization status and caveat.

The register is an event graph input, not a consolidated legal text. It deliberately repeats an instrument ID when one instrument changes multiple article provisions. It does not duplicate the instrument in the acquisition register or duplicate article text.

## 2. Coverage

The 44 events cover the principal known version changes for:

- **Law 114/1946:** transitional extension under Law 157/1947; amendments/repeals/inserts from Laws 69/1950, 222/1956, 82/1957, 136/1957, 181/1957, 5/1964, 25/1976, 223/1996, 186/2020, 5/2021 and 9/2022; selected executive-regulation amendments under Decisions 948/1976, 9310/2020 and 2332/2022.
- **Law 142/1964:** Article 30 replacement by Law 83/2006; constitutional invalidations and consequential effects under Cases 42/17 and 10/35; Decision 11264/2016 regulation amendment.
- **Law 143/1981:** Article 21 repeal by Law 12/1984; Article 12(2) replacement by Law 55/1988; Article 11(2) and Article 4(1) replacements by Laws 205/1991, 96/1995, 72/1996 and 11/2024; Article 22(1) invalidation by Case 101/26; seven identified amendments to Executive Regulation Decision 198/1982.
- **Law 70/1964:** statutory changes from Laws 94/1980, 6/1991, 224/1996, 225/1996, 9/2003, 3/2004, 83/2006, 163/2019 and 67/2021; constitutional invalidations under Cases 2/24 and 10/16.

## 3. Normalization limitations

- The 44 events are sourced from a mixture of official publisher text, official court pages, official repository metadata, government-hosted copies, and secondary consolidated footnotes.
- The pre-amendment and post-amendment Arabic text has not yet been entered for every event. Each row is marked “effect identified; pre/post article text not yet normalized”.
- Several dates remain conditional or disputed: Law 25/1976 commencement, Law 82/1957 metadata, Law 157/1947 Gazette issue, Law 186/2020 deferred commencement, Decision 6910/2025 date conflict, and the Decision 480/2026 extension deadline.
- Judicial invalidation and consequential fall are separate event types from statutory repeal.
- A repeated article number may have multiple successive versions; do not overwrite earlier text with the latest text.

## 4. Current counts

| Metric | Current value |
|---|---:|
| Acquisition-register rows | **241** |
| Unique acquisition IDs | **241** |
| Duplicate acquisition IDs | **0** |
| Source-permission records | **63** |
| Unique historical version events | **44** |
| Completed core unique article provisions | **1,370** |
| Additional searchable article-heading entries in Laws 114/142/68/70 | **200** |
| New legal instruments in checkpoint 160 | **0** |
| New article texts transcribed in checkpoint 160 | **0** |

## 5. Completion estimate

- Core article-number extraction: **100%** for the three defined core statutes, subject to OCR/source-image and historical-version validation.
- Broader civil/property/contract corpus: **15% provisional**.
- Whole Egyptian legal corpus: **2% provisional**.

The normalized event register improves provenance and version tracking but does not increase article-text coverage.

## 6. Next actions

1. Add exact Arabic pre/post text snapshots to each version event, starting with Law 114 Articles 21, 24, 35 bis, 23 bis, and Law 142 Articles 21, 23, 24, 30, 37 and 38.
2. Add all Law 70 Table B and Article 34 bis historical fee versions.
3. Add all Law 143 Executive Regulation Article 15, 41, 42, 45 and 50 versions.
4. Add full Gazette issue/page coordinates and hashes when authorized originals are obtained.
5. Add instrument-level commencement and repeal edges and validate the event sequence against original Gazette page images.
6. Reconcile the 44 event register against the master index and acquisition register after each update.

## 7. Rights and verification

No lawyer verification, commercial reuse permission, original publisher authentication, or bulk retrieval permission is claimed. Source tier and permission state remain source-specific.
