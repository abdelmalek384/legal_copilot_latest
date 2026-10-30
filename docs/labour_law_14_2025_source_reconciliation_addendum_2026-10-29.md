# Labour Law No. 14/2025 — source reconciliation addendum

**Checked:** 2026-10-29  
**Scope:** Public-source discovery and currentness leads only. This document does not certify the law, a transcription, an amendment chain, or reuse rights.

## Source records

| ID | Source | What it supports | What it does not prove | Next action |
|---|---|---|---|---|
| EG-LAB-14-2025-MOL | Egyptian Ministry of Labour, “Laws and Legislations” | The Ministry lists Labour Law No. 14/2025 and the former Labour Law No. 12/2003 among its legal resources. | The search result alone does not establish the exact binary bytes, full text identity, complete amendment chain, or rights for bulk download/commercial indexing. | Open the Ministry's law download, preserve the original bytes and response metadata if accessible under its terms, compute SHA-256, and compare page/article text to the Gazette. |
| EG-LAB-14-2025-AMIRIA | Amiri Press, searchable text page “قانون رقم 14 لسنة 2025 بإصدار قانون العمل” | Official publisher's searchable Arabic text is available and can be used as an article locator and textual cross-check. | Searchable HTML is not the Gazette binary; it does not by itself prove every character matches the printed issue or establish redistribution permission. | Capture the exact page URL and retrieval time; compare the complete text article-by-article to the Gazette scan. |
| EG-GAZ-2025-05-03-18-SUPP | IDSC document repository record “الجريدة الرسمية - العدد 18 (تابع)” dated 2025-05-03 | An archive record identifies the Official Gazette supplementary issue and describes it as publishing Labour Law No. 14/2025. | The record/metadata alone does not prove the downloaded PDF is complete or byte-authentic; its SHA-256 has not been recorded here. | Retrieve the attached original PDF through the normal public interface if available; retain bytes and compute SHA-256; record pages and issue metadata. |
| EG-LAB-DEC-49-2026-MOL-NEWS | Ministry of Labour news item dated 2026-03-26 concerning Ministerial Decision No. 49/2026 | The Ministry states that the decision addresses hazardous/difficult work and remote areas for the additional seven days of annual leave under Labour Law Art. 124. It gives category counts, including 37 chemical-industry jobs, 7 heavy engineering/metal jobs, 8 high-risk food-industry jobs, 9 textile/dyeing jobs, 5 precision-electronics jobs, 6 natural-resource/non-metallic extraction and energy jobs, 7 energy/radiation jobs, and 5 environmental/waste-management jobs. | The announcement is not the complete decision schedule. It cannot certify every covered job or geographic boundary. | Obtain the full decision and annexes from a publicly accessible official source; compare every listed job/area and effective date to the Gazette. |
| EG-LAB-DEC-49-2026-TRANSCRIPTION | Public transcription of Decision No. 49/2026, reported as published in Egyptian Proceedings on 2026-03-18 | A secondary transcription can help locate the decision and identify text to compare. | It is not a substitute for the official issue; do not use it alone to assert exact wording, completeness, or legal currentness. | Compare against the official Gazette/Proceedings issue and retain any discrepancies as unresolved until primary-source resolution. |

## Concrete discrepancy to resolve: Decision 49/2026

The current workstream reports a geographic-boundary inconsistency: the Ministry's announcement uses **أبو رمادة**, while an accessible transcription uses **الزعفرانة**. Treat this as an unresolved source conflict. Do not silently choose either place name, and do not infer that one source is authoritative for the exact schedule merely because it is official news. The signed/published decision and its annexes must resolve the point.

**Current status:** conflict pending primary source; no covered-location record should be promoted to authoritative on this basis alone.

## Article 124 legal timeline

- Law No. 14/2025 was published in the Official Gazette on 2025-05-03.
- Article 13 states that the law takes effect from the beginning of the month following expiry of 90 days from publication; the Ministry of Labour and Library of Congress sources identify 2025-09-01 as the general commencement date.
- Article 13 separately sets specialized labour courts to take effect on 2025-10-01.
- Decision No. 49/2026 is reported by the Ministry as dated 2026-03-26, while a public transcription reports publication in Egyptian Proceedings on 2026-03-18. The issue/date/decision metadata must be reconciled from the actual published instrument before treating these as verified timeline fields.

Do not use a source record's as_of or retrieval date as an effective date. Keep publication, commencement, amendment, repeal, and review dates separate.

## Safe ingestion gate

Until the evidence package is complete, all related cards must remain search_eligible: false. A card may be labelled **source-located** or **secondary-source cross-checked**, but not **verified current law**. To promote it, require:

1. Original Gazette/Proceedings bytes and SHA-256, or an explicit record explaining why the primary binary is unavailable.
2. Exact document/issue/page and article or annex pinpoint.
3. Text comparison results, including discrepancies and extraction method.
4. Publication and effective dates with evidence for each.
5. Amendment/currentness review, including the relationship between Art. 124 and Decision 49/2026.
6. Reuse/redistribution assessment for the actual intended product use.
7. Qualified Egyptian-lawyer review before any lawyer_approved state.

## Public references discovered on 2026-10-29

- Ministry of Labour laws and legislation: https://www.labour.gov.eg/en/laws-and-legislations/
- Amiri Press searchable law text: https://www.alamiria.com/Sec/TashTxt?id=vPdoWGGYwoE%3D
- IDSC Gazette archive record: https://dspace.id.com.eg/items/75a95151-8a93-45c0-a607-9320863881df
- Ministry of Labour announcement for Decision 49/2026: https://www.labour.gov.eg/ar/الأخبار/لتَحقِق-التوازن-بين-متطلبات-الإنتاج-وصون-حقوق-القوى-العاملة-وزير-العمل-يصدر-قرارًا-وزاريًا-بتحديد-الأعمال-الخطرة-والمناطق-النائية-التي-تُزاد-فيها-الإجازات-السنوية-7-أيام-للعاملين/

**Rights note:** These links are source leads, not a blanket licence to scrape, store, index, commercially process, display, or redistribute their contents. No access restrictions should be bypassed.


## Follow-up from inspecting the archive and the Decision 49 transcription

**Archive access outcome:** The IDSC record exposes a “Request a copy of the file” page for the 3 May 2025 Gazette PDF and marks the files as restricted access. This is not a public direct-download route. No request was submitted and no restriction was bypassed. The archive metadata remains a locator only until an authorized copy is obtained.

**Decision 49/2026 secondary-text pinpoint:** The accessible legal transcription states:
- It identifies the instrument as Ministerial Decision No. 49/2026.
- It reports publication in Egyptian Proceedings on 18 March 2026.
- Its closing lines state the decision was issued on 3 March 2026.
- Article 3, lines 256–273 of the accessible transcription lists the remote areas and uses the wording “من قرية الزعفرانة / رأس غارب حتى الحدود المصرية السودانية بمنطقة حلايب جنوبًا وبعمق خمسة كيلومترات”.
- Article 5, lines 275–282 says the decision is published in Egyptian Proceedings and takes effect the day after publication.

These are pinpointed observations from a **secondary transcription**, not a source-authenticity finding. They make the geographic discrepancy concrete but do not resolve it against the official instrument. The Ministry news page is an official announcement, yet it is not the full schedule. Therefore, do not mark Article 124's implementing area list as fully verified.

**Current disposition:** The primary-copy request page is a genuine acquisition blocker for the Gazette PDF. Continue with the official searchable Amiri Press text and accessible secondary transcription for comparison work, but preserve the distinct source labels and unresolved primary-source gate. Do not claim a Gazette-byte hash when the bytes have not been obtained.
