# Criminal procedure law: version and commencement watchlist

**Research date:** 19 November 2026  
**Purpose:** prevent Legal Copilot from presenting an enacted-but-not-yet-effective replacement code as the current operative text.

## Primary source records located

1. **Law No. 174 of 2025 promulgating the Criminal Procedure Law**
   - Official Ministry of Justice-hosted Gazette PDF: https://moj.gov.eg/backend/api/documents/download/20F3150C-29F1-487E-A0F0-FCCE10CB207B
   - Gazette reference: Official Gazette No. 45 bis (D), 12 November 2025.
   - The law's issuance provisions include repeal language concerning Law No. 150 of 1950, and originally set commencement for 1 October following publication.
   - The Presidency announcement describes the planned commencement as 1 October 2026: https://www.presidency.eg/ar/قسم-الأخبار/أخبار-رئاسية/news12112025/

2. **Law No. 160 of 2026 amending Law No. 174 of 2025**
   - Official Amiri Press text: https://alamiria.com/Sec/TashTxt?id=Aalg37zxdcU%3D
   - It replaces the prior commencement wording with **1 October 2027** and says the amending law itself takes effect the day after publication.
   - The Court of Cassation homepage also lists Law No. 160 of 2026 among recent legislation: https://cc.gov.eg/

## Safe database representation

Represent these as distinct instruments, not as one overwritten file:

- Law No. 150/1950 — historical code, operative-status field must be time-scoped and reviewed.
- Law No. 174/2025 — enacted replacement code, commencement postponed to 1 October 2027 by Law No. 160/2026.
- Law No. 160/2026 — amending instrument and commencement-date change.

Do not simply mark Law No. 150/1950 as repealed today because Law No. 174/2025 contains repeal wording: the repeal/commencement interaction must be interpreted alongside Law No. 160/2026 and transition provisions. Until reviewed, record the status of the operative regime as **pending legal review**, not a confident automated conclusion.

## Collection and reuse gate

The source URLs are discovery references only. No automatic download is authorized by this document. Check the applicable terms and permission for local archival, Arabic text extraction, indexing, commercial use, display, and redistribution before adding either PDF/HTML URL to the executable collector manifest.

## Required lawyer review

- Confirm the effective-date amendment against the Gazette publication of Law No. 160/2026.
- Confirm the effect of postponement on repeal language in Law No. 174/2025 and the continuing application of Law No. 150/1950 before 1 October 2027.
- Identify any intervening amendments, implementing decisions, and transitional rules.
- Approve a date-aware retrieval test: a question asked as of 2026-10-23 must not receive an answer that assumes the 2025 Code is already in force.


## 19 November 2026 — new full-text findings

- Full Arabic text of Law No. 174/2025 is accessible from the Ministry of Justice-hosted Gazette PDF:
  https://moj.gov.eg/backend/api/documents/download/20F3150C-29F1-487E-A0F0-FCCE10CB207B
- A full secondary text with 3,167 extracted lines is also accessible:
  https://temp.manshurat.org/content/qnwn-ljrt-ljnyy-rqm-174-lsn-2025-0
- **Article 2 discrepancy:** the Ministry of Justice Gazette PDF reads “مواد الجنايات”; the Manshurat secondary HTML reads “مواد الجنح”. Use the official Gazette reading for the official-text field and retain the secondary variant in the audit trail. Do not silently normalize.
- The official Gazette PDF and secondary full-text page are text-accessible; no local PDF archive/hash or permission for commercial reuse is asserted by this note.
- Law 140/2014 is linked to the same deferred commencement/repeal issue. Do not mark it repealed before 1 October 2027 without a lawyer-reviewed transition determination.

## Source and legal-status discipline

The project inventory records full-text accessibility separately from local file acquisition, permission, operative legal status and lawyer review. A full text readable in a browser is not the same as an archived/hashed original Gazette file or permission to redistribute it. Keep the operative status of Law 150/1950 and the repeal of Law 140/2014 **pending Egyptian criminal-procedure lawyer review**, while preserving the statutory commencement date currently stated in Law 160/2026.
