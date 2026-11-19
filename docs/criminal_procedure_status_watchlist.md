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


## 19 November 2026 — amendment and article-level acquisition update

### Law 150/1950 amendments now identified

The Criminal Procedure amendment chronology is broader than the initial record. Major identified instruments include Laws 95/2003, 145/2006, 74/2007, 71/2009, 83/2013, 49/2014, 138/2014, 16/2015, 11/2017, 177/2020 and 1/2024. Older relation candidates 271/1955, 107/1962, 37/1972, 170/1981 and 23/1992 remain metadata-only pending original text acquisition.

**Critical correction:** Law 177/2020, not Law 189/2020, amended the Criminal Procedure Law. Law 177/2020 added Art. 113 bis on disclosure of victim data in specified sexual and child offences. Law 189/2020 amended the Penal Code by adding Art. 309 bis (b) on bullying. A secondary CPL consolidation misattributes Law 189/2020.

Law 1/2024, Gazette No. 2 bis, 16 January 2024, effective 17 January 2024, introduced felony appeals, including Arts 419 bis through 419 bis 9. Law 174/2025 issuance Art. 3 contains a separate transition rule tied to cases not decided by felony courts from the commencement of Law 1/2024.

### Law 174/2025 — future Book Five provisions

Selected exact Arabic provisions in the new code's Book Five have now been captured:

- Art. 511: incoming foreign judicial cooperation requests, diplomatic channel, Arabic translation, supporting documents and provisional detention.
- Art. 514: mandatory refusal grounds for extradition, including Egyptian nationality, lack of double criminality, Egyptian jurisdiction, political offences and military offences.
- Art. 515: reasoned decision and challenge within seven days.
- Art. 516: Egypt's outgoing extradition request and trial where surrender is refused.
- Art. 517: controlled delivery, subject to national-security and sovereignty safeguards.
- Arts. 518–520: conditions, refusal grounds and decision on foreign judicial assistance.
- Art. 521: exceptional presidential approval for surrender/transfer after Public Prosecutor presentation and Cabinet approval.

Arts. 508–510 and 512–513 remain to be extracted. These are **future provisions** until commencement.

### Source-text discrepancies

- Official Ministry of Justice Gazette PDF for Law 174/2025 issuance Art. 2 reads **مواد الجنايات**; the Manshurat full-text reproduction reads **مواد الجنح**. Preserve the official/secondary discrepancy.
- OCR of the official PDF appears to duplicate the label “Article 27” in the judicial-police and arrest chapters. The second label is likely Article 37 based on sequence, but visual Gazette collation is still required.
- The original Law 150/1950 Gazette No. 90 date remains conflicted: 15 October 1950 in Manshurat metadata versus 15 October 1951 in Eastlaws. Do not lock either without the original issue image.

### Project status

The Criminal Procedure amendment and article extraction material is maintained in:
docs/legal_evidence/agent2_criminal_text_acquisition_tranche_2026-11-19.md

All operative-status conclusions, repeal effects, and transitional interpretations remain subject to Egyptian criminal-procedure lawyer review. Do not mark any record lawyer-verified.

