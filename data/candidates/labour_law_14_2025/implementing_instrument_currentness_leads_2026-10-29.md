# Labour Law 14/2025 — implementing instruments and currentness leads (2026-10-29)

**Scope:** Currentness discovery for instruments referring to Labour Law No. 14/2025. This is a lead register, not a certification that the instruments remain in force. Official text is linked where located; otherwise the source type is explicitly labelled.

## A. Instruments with accessible official publisher text

| ID | Instrument | Source and observed facts | Relationship to Law 14/2025 | Currentness/review status |
|---|---|---|---|---|
| EG-LAB-PM-2652-2026 | Prime Minister's Decree 2652/2026 | Amiri Press searchable text says it extends by six months the period for private employment agencies covered by the final paragraph of Art. 6 to regularize their status; issued 2026-09-07. https://www.alamiria.com/Sec/TashTxt?id=MWc8qnk3Yg8%3D | Implements/extends a deadline tied to Art. 6; do not classify as a formal amendment to the statute unless the legal text supports that relationship. | Official publisher text located. Need publication metadata/page and counsel review of the six-month calculation, trigger date, and affected agency categories. |
| EG-LAB-MOL-74-2026 | Labour Ministry Decision 74/2026 | EastLaws metadata reports issue date 2026-04-15, publication 2026-05-17 in Egyptian Proceedings issue 108, effective 2026-05-18; title concerns regulation of labour-market observatories. https://www.eastlaws.com/legislation-full-text/ar/egypt/labor/17-05-2026/no-74?id=5638752&type=1 | Candidate implementing/regulatory instrument under the new labour-law framework. | Secondary metadata only in this record; obtain the Amiri Press text and official issue/page, then map articles, commencement, and any later changes. |
| EG-LAB-MOL-75-2026 | Labour Ministry Decision 75/2026 | Amiri Press searchable text identifies the decision as concerning prohibited work for women to protect maternity or address occupational safety/health risks; issued 2026-04-15. It says it is published in Egyptian Proceedings and takes effect the day after publication. Searchable official text: https://alamiria.com/Sec/TashTxt?id=82Iv%2FEE2jDk%3D. The IDSC archive lists the decision with date 2026-05-17 and attached files. https://dspace.id.com.eg/items/56225e63-270d-4486-8336-e9d92cf6ecc9 | Implements Art. 53 and replaces conflicting earlier provisions according to its closing article. | Strong official-text lead plus archive metadata. Need exact issue/page and article/annex transcription review, then counsel review of repeal/supersession of earlier ministerial rules. |
| EG-LAB-PM-982-2026 | Prime Minister's Decree 982/2026 | Amiri Press searchable text says it applies a Sunday remote-work system during April 2026 to specified categories of establishments and entities, starting 2026-04-05. https://alamiria.com/Sec/TashTxt?id=X+ynf8GR0jI%3D | Temporary measure issued with reference to Labour Law 14/2025; it is not itself an amendment to the statute. | Superseded/extended by successive monthly decisions; never treat April terms as a permanent rule. |
| EG-LAB-PM-2590-2026 | Prime Minister's Decree 2590/2026 | Amiri Press text says Decree 982/2026 continues during September 2026; issued 2026-09-01. https://alamiria.com/Sec/TashTxt?id=HAJdFlN7HCw%3D. Archive metadata: https://dspace.id.com.eg/items/9e0f34a7-9106-4a2d-b7c4-a470967f0fc9 | Temporary extension of the remote-work decision for September only. | The September extension expired with September unless a later instrument changed the period. Do not represent it as active on 2026-10-29. |

## B. Related remote-work instruments: month-by-month version chain

The official publisher text for Decree 2590/2026 recites the prior monthly extensions: 1305/2026 (May), 1572/2026 (June), 2033/2026 (July), 2377/2026 (August), and 2590/2026 (September). The source text for the September decision is explicit that the continuation is limited to September. Keep each extension as a separate versioned instrument with its own publication/effective interval; do not flatten them into a single indefinite rule.

On 2026-09-30, news reports stated that Cabinet approved a **draft** decision to stop the remote-work arrangement under Decree 982/2026. Examples: https://www.youm7.com/story/2026/9/30/مجلس-الوزراء-يوافق-على-وقف-تطبيق-قرار-العمل-عن-بُعد/7563181 and https://gate.ahram.org.eg/News/5936695.aspx.

**Critical status distinction:** the material located in this search says Cabinet approved a draft/project; it is not, by itself, the signed/published instrument. No signed termination instrument was located in this check. Record the state as `draft_approved_official_instrument_not_yet_located`, not as a fully verified repeal/termination. Continue checking the Official Gazette/Amiri Press issue after 2026-09-30 before making a definitive statement about legal effect.

## C. Law 14/2025 Article 124 — additional annual leave

Article 124 says annual leave is increased by 7 days for workers in hazardous work, harmful-to-health work, or remote areas designated by a decision of the competent minister after consultation with relevant authorities. A Ministry of Labour announcement on Decision 49/2026 provides category-level information but does not replace the full decision and its schedules. A previously observed geographic mismatch between the announcement and a public transcription remains unresolved. See the source reconciliation addendum:
https://github.com/abdelmalek384/legal_copilot_latest/blob/docs/labour-decision-verification-matrix-2026-10-28/docs/labour_law_14_2025_source_reconciliation_addendum_2026-10-29.md

Until the complete official Decision 49/2026 and its annexes are compared, do not create authoritative eligibility records for individual jobs or locations.

## D. Registry rules for all leads above

1. Store every decision/decree as a separate document with issuer, number/year, exact title, publication issue/date/pages, issue URL, and original file/hash when lawfully obtained.
2. Keep enacted/published text separate from press announcements, draft decisions, metadata records, and secondary transcriptions.
3. Store publication, issuance, commencement, expiry, extension, and retrieval dates separately.
4. Use relations such as `implements`, `extends_deadline_under`, `temporarily_extends`, `supersedes`, or `repeals` only when the instrument text supports the relationship. Never assume every later instrument amends the parent statute.
5. Do not treat accessible text as blanket permission for bulk retrieval, commercial indexing, or redistribution.
6. Keep all cards `search_eligible: false` until source evidence, article-level transcription review, currentness analysis, rights/use review, and qualified Egyptian-lawyer review pass.

## Work performed in this batch

- Located official Amiri Press text for Decrees 2652/2026, 75/2026, 982/2026, 2377/2026, and 2590/2026.
- Located secondary publication/effective-date metadata for Decision 74/2026 and archive metadata for Decision 75/2026.
- Identified a temporal-status trap: the September remote-work extension is time-limited, and later news reports describe Cabinet approval of a draft to stop the scheme. The signed published termination instrument still needs to be located.
- Did not mark any item lawyer-approved or claim a complete amendment/currentness chain.
