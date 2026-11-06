# Initial Egyptian legal release scope and exclusions

**Status:** scope defined; no instrument is approved for current-law retrieval by this document.  
**Assessment date:** 2026-10-31

## Purpose

The first legal-content release is deliberately narrow. It is not a claim to cover all Egyptian law or legal advice. A source URL, public viewer, search result, file hash or successful extraction is not enough to make an instrument verified or searchable.

**Current decision: NO-GO for all legal content.** Every listed candidate remains `discovery_only` and `search_eligible=false` until its instrument-specific gates are satisfied.

## Priority scope

| Priority | Instrument family | Intended first-release coverage | Current source evidence | Decision |
|---|---|---|---|---|
| P0 | Constitution of Egypt (2014, amended 2019) | One exact consolidated text, with the 2014 promulgation and 2019 amendment separately traceable | Two official locators are recorded: the Presidency-hosted 2019 PDF and the National Elections Authority's 63-page PDF. Both official pages display all-rights-reserved notices. No local original bytes/SHA-256, full Gazette-page comparison, written collection/reuse permission or post-2019 currentness review is recorded. The Presidency PDF's embedded Gazette issue 16 repeated (w) reference belongs to a referendum-results notice; secondary metadata points to issue 15 repeated (c) for the amendment instrument, still unverified against the Gazette. | **NO-GO.** Resolve the exact 2014/2019 Gazette publications, later amendments, source rights and counsel review. |
| P0 | Labour Law No. 14 of 2025 | The promulgating law and complete 298-article annex, with commencement and repeal provisions separately reviewed | The ETA-hosted Official Gazette issue 18 (supplement), dated 2025-05-03, is visible in the public PDF viewer. Article 13 and printed pages 94–111 have limited visual locator checks; the local download attempt failed and no local SHA-256 exists. Collection and commercial reuse are unknown. The Ministry of Labour index lists the law but its page returned HTTP 502 in the latest review and no direct Ministry PDF URL was obtained. | **NO-GO.** Obtain authorized original bytes, hash them, complete article-by-article Gazette comparison, resolve the 3 May/5 May publication-date discrepancy, verify currentness and rights, and obtain counsel approval. |
| P0 | Labour Law implementing Decisions 248–252/2026 | Five separate instruments, each with its own version and amendment trail | The Ministry's 2026-10-20 announcement identifies the five decision numbers. The Gazette supplement catalogue lists the package, but the original PDF is request-copy restricted. Decision 249 has a 2026-10-27 Ministry clarification lead, not the complete decision or a Gazette amendment. Secondary reporting on Decision 248 is not authoritative text. | **NO-GO.** Obtain authorized Gazette copies and item-specific rights evidence; compare each decision independently and secure counsel approval. |
| P1 | Core civil/commercial statutes: Civil Code 131/1948, Civil Procedure 13/1968, Evidence 25/1968, Commercial Code 17/1999 | A small foundational civil/commercial set, not the entire statutory corpus | These instruments are candidate records against the Amiri Press source family. Direct item-level originals, source-specific permission, amendment chains and complete text comparisons are not recorded for this release scope. | **NO-GO.** Prioritize exact Gazette locators and item-specific rights review; do not borrow permission from a generic source-family record. |
| P2 / excluded | Court of Cassation judgments and principles | A selected sample only if lawful public product use is established | The official Court portal exposes judgment/principle search, including labour appeals. Its May 2026 use policy requires a Court-created personal account and current subscription, limits copying to legal/academic/research/documentation purposes, and requires prior written approval for commercial use/publication. Automated/bulk extraction is not authorized absent a separate written exception. | **EXCLUDED from ingestion/indexing and commercial display.** Manual lookup/link-out only unless written permission covers the product's intended use. |
| P2 / excluded | Supreme Constitutional Court judgments and principles | Potential future browse-only discovery, not an initial indexed corpus | An official recent-judgments page is discoverable. A third-party repository describes API routes, but endpoint availability, completeness, official terms and commercial reuse rights were not independently validated. | **EXCLUDED from automated acquisition.** Keep rights/API status unknown until official terms and written permission are obtained. |

## Instrument-level release checklist

An instrument may enter the first release only when all of these are complete for that exact instrument and version:

1. **Authenticity:** canonical official source and original publication identified; original bytes acquired through an authorized route; SHA-256 recorded.
2. **Publication metadata:** Gazette issue, supplement, date, page range and exact article/decision pinpoints verified against the original publication. A Ministry announcement or search result is not a substitute for the Gazette.
3. **Text completeness:** extraction reviewed against every page; expected and actual article identifiers match; missing, duplicate, reordered or unexpected provisions resolved.
4. **Legal status:** commencement, repeal, amendments, transitional provisions and relevant later instruments checked as of a stated date. Publication and effective dates remain separate.
5. **Rights:** collection, local storage, extraction, indexing, excerpt display, commercial use and redistribution assessed separately. Written permission is retained where terms require it; public availability is not permission.
6. **Review events:** latest event per required review type passes with non-empty reviewer and notes, valid HTTPS evidence and a non-future timestamp. Latest lawyer approval carries the operator-managed qualified-counsel account marker.
7. **Counsel:** qualified Egyptian lawyer independently reviews authenticity, completeness, currentness, interpretation and release suitability. Operator attestation is not independent credential verification.

## Explicit exclusions

- No blanket activation of the candidate catalogue.
- No scraping, automated retrieval or bypass of request-copy, subscription, login or other access controls.
- No commercial display or redistribution where terms require prior written approval unless approval is obtained and recorded.
- No secondary transcription, media report, search snippet or third-party API claim as operative legal text.
- No synthetic fixture test as evidence of legal correctness.
- No database schema change or destructive corpus import is authorized by this scope document.

## Measurement

Track these separately rather than collapsing them into one coverage percentage:

- Candidate inventory.
- Authorized original files with bytes and SHA-256.
- Gazette-matched text with full page/article comparison.
- Rights-cleared sources for each intended product operation.
- Current-law eligible versions with complete authenticity, extraction, status, amendment, licensing and lawyer-approval evidence.
- Historical-only versions.
- Blocked instruments and their exact blockers.

This scope document does not make any candidate current-law eligible. Final Egyptian-counsel acceptance remains a mandatory external gate.
