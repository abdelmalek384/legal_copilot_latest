# First-batch source and permission assessment

**Assessment date:** 2026-10-23  
**Purpose:** identify an initial Egyptian law batch and record what is known before collection. This is a source assessment, not a corpus. No legal files were downloaded by this assessment, and no permission is inferred from public visibility alone.

## Key finding

The General Authority for Amiri Press (الهيئة العامة لشئون المطابع الأميرية) provides an official Egyptian legislation search portal and displays full-text legislation on individual pages. Its website also advertises subscriptions to the Official Gazette and Egyptian Proceedings. The exact permission and terms for bulk downloading, local archival, indexing, and commercial use in Legal Copilot must be confirmed before using the collector.

The Court of Cassation's published site terms are explicit: access is subscription-controlled; automated/bulk extraction is prohibited; commercial use or republication requires prior written permission. Do not use the collector on `cc.gov.eg` for judgments or legislation unless the Court grants a written exception/license.

The Presidency publishes a direct PDF of the Constitution. This is a promising first candidate because the source is an official government website, but the page itself does not establish bulk-reuse or commercial indexing permission. Treat it as **permission pending**, not approved.

## Candidate first batch

| Priority | Document / batch | Candidate source | Source status | Collection permission | What is needed |
|---|---|---|---|---|---|
| P0 | Constitution of the Arab Republic of Egypt (2014; amendments including 2019 must be represented accurately) | [Presidency official Constitution page](https://www.presidency.eg/ar/مصر/الدستور/) and [official PDF](https://www.presidency.eg/media/46122/دستور-جمهورية-مصر-العربية-2019.pdf) | Official publication located; check amendments and any later constitutional changes before asserting current version | Unknown / pending | Check reuse terms and whether this PDF is a consolidated text; preserve version date and amendment provenance |
| P0 | Official Gazette issue containing the original Constitution and subsequent amendment instrument(s) | Amiri Press / Official Gazette | Official publication channel identified; access may require subscription or paid archival request | Unknown / pending | Ask Amiri Press about licensed digital access and permitted local indexing |
| P0 | Civil Code (Law No. 131 of 1948) and amendments | Amiri Press legislation search / Gazette archive | Candidate; exact official document/version not yet pinned | Unknown / pending | Locate original publication and all amending laws; establish consolidated-text provenance |
| P0 | Code of Criminal Procedure (Law No. 150 of 1950) and amendments/replacement transition | Amiri Press / Gazette archive | Candidate; must research status and transition provisions as of collection date | Unknown / pending | Confirm current legal status and any newly enacted/replacement code commencement dates before indexing |
| P0 | Code of Civil and Commercial Procedure (Law No. 13 of 1968) and amendments | Amiri Press / Gazette archive | Candidate; exact official document/version not yet pinned | Unknown / pending | Locate original and amendment chain; verify article numbering against Gazette |
| P0 | Penal Code (Law No. 58 of 1937) and amendments | Amiri Press / Gazette archive | Candidate; exact official document/version not yet pinned | Unknown / pending | Locate original and amendment chain; confirm current provisions |
| P1 | Labour Law (Law No. 14 of 2025) | [Amiri Press official text page](https://www.alamiria.com/Sec/TashTxt?id=vPdoWGGYwoE%3D) | Official text page located; commencement, regulations and transitional provisions require separate review | Unknown / pending | Confirm applicable terms for retrieval/reuse; collect executive regulations and amendment/implementation instruments |
| P1 | Social Insurance and Pensions Law (Law No. 148 of 2019) and amendments | Amiri Press / relevant authority / Gazette | Candidate; exact official document/version not yet pinned | Unknown / pending | Locate original and amendments, executive regulations and current implementing decisions |
| P1 | Companies Law (Law No. 159 of 1981) and amendments | Amiri Press / GAFI / Gazette | Candidate; exact official document/version not yet pinned | Unknown / pending | Locate original and amendment chain; distinguish regulator guidance from binding text |
| P1 | Consumer Protection Law (Law No. 181 of 2018) and executive regulations | Amiri Press / Consumer Protection Agency / Gazette | Candidate; exact official document/version not yet pinned | Unknown / pending | Locate original, regulations, and amendments |
| P1 | Personal Data Protection Law (Law No. 151 of 2020) and implementing decisions | Amiri Press / relevant regulator / Gazette | Candidate; exact official document/version not yet pinned | Unknown / pending | Locate official text and implementation instruments; do not infer commencement from publication alone |
| P2 | Court of Cassation judgments and principles | [Court of Cassation search](https://cc.gov.eg/judgments_search/) and [site terms](https://cc.gov.eg/terms) | Official source, subscription-controlled | **Automated/bulk extraction prohibited by published terms; commercial reuse/republication requires prior written consent** | Do not scrape. Ask the Court for a licensed bulk/API export and permitted use. Until approved, store citation metadata manually only if terms allow |
| P2 | Decisions/judgments from the Supreme Constitutional Court and State Council | Official court portals | Candidate; source-specific access and rights not yet assessed | Unknown / pending | Review each court's terms and licensing separately; do not extrapolate Court of Cassation terms to other courts |

## Required permission statuses

Use these controlled statuses in the working register:

- `unknown`: terms have not been reviewed.
- `permission_pending`: request sent or clarification needed.
- `allowed_limited`: only the exact use stated in the permission evidence is allowed.
- `allowed`: exact collection and intended processing/reuse is authorized, with evidence recorded.
- `prohibited`: terms prohibit the intended collection or reuse.

Only entries with explicit `allowed` status, a permission evidence reference, a review date, and an approved hostname can be placed in the executable collector manifest. A legal text being readable in a browser does not satisfy this requirement.

## Questions to send to source owners

Request written confirmation covering each of these separately:
1. May we download and preserve complete original PDF/HTML files locally?
2. May we extract and index the Arabic text in a private database?
3. May the database be used by a commercial legal-assistance product?
4. May excerpts and citations be displayed to end users?
5. Are there rate limits, subscription restrictions, attribution requirements, or redistribution restrictions?
6. Is an API, bulk download, or licensed data export available?
7. How are corrections, replacement files, amendments and withdrawals communicated?

## Collection gate

Do not populate the executable manifest until the permission fields are resolved. For each approved document, record the exact URL, original title, source authority, publication date, Gazette issue/page, hash, retrieval timestamp, and a human-reviewed amendment/effective-date chain. A source record and a downloaded file are not proof that a law is currently in force.
