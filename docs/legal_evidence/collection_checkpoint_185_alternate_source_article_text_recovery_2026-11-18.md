# Collection checkpoint 185 — alternate-source Arabic text recovery for Laws 114, 142, 68 and 70

**Date:** 18 November 2026  
**Agent:** Research Agent 1  
**Scope:** recover article wording, not merely references, where original Gazette digital binaries remain unavailable.

## Work completed

Created `alternate_source_article_text_capture_laws_114_142_68_70_2026-11-18.md` and captured 28 article/provision text entries from alternate searchable sources:

| Instrument | Text entries captured | Qualification |
|---|---:|---|
| Law 114/1946 | 8 | Articles 1, 4–7 and 9–11; mixed original/historically amended wording; PDF mirror says through 6 March 2022 |
| Law 142/1964 | 11 | Substantive Articles 1, 2, 8–11 and 26–30; full mirror says through 6 June 2018 |
| Law 68/1947 | 5 | Articles 1, 2, 4–6; Article 1 is repealed, and Articles 2, 5, 6 carry replacement/amendment annotations |
| Law 70/1964 | 4 | Articles 1–4; nominal base-law fee figures are historical and superseded |

**Count treatment:** 28 text entries include one explicit repealed marker (Law 68/1947 Article 1). Thus 27 are non-repealed text entries in the supplemental capture. These are not yet added to the core 1,370 provision count because they are outside the defined Civil Code/Evidence/Building core set and await article-ID normalization, Gazette comparison and date-effective version checks. Do not add headings, repealed markers or duplicated versions to unique operative article counts.

## Source recovery and cross-checks

- Law 114/1946: Egypt Notaries Union, LAW HUB, Ministry of Justice-hosted PDF locator and a Court of Cassation Information Centre-attributed PDF mirror. The latter identifies Egyptian Proceedings issue 85, 24 August 1946 and says its consolidated wording is through 6 March 2022. This is a secondary-hosted reproduction, not an Amiri Press digital original.
- Law 142/1964: LAW HUB, Al-Hasswa full-text mirror, EastLaws and Manshurat scan catalogue. The Al-Hasswa page says it reproduces Gazette text via the Court of Cassation legislative portal and is updated through 6 June 2018. This is not a certified original file.
- Law 68/1947: LAW HUB, EastLaws and Manshurat scan catalogue. LAW HUB annotations identify Article 1 repeal by Law 5/1964 and replacement/amendment notes under Laws 629/1955 and 103/1976.
- Law 70/1964: Egypt Notaries Union, EastLaws and Manshurat scan catalogue. The Notaries Union page also reproduces Law 83/2006 and Decision 5424/2006, which are necessary to understand why old nominal fee amounts are not current tariffs.

## Specific status corrections

1. Law 114/1946 Article 9 text is not one static version: the mirror shows 2022 wording for amended paragraphs and a repealed-paragraph marker. Article 9 version events must be separated.
2. Law 142/1964 uses repeated numbering for issuing provisions and substantive provisions. The corpus IDs must distinguish `issuing_article_1` from `substantive_article_1`, etc.
3. Law 142/1964 Articles 21 and 24 were held unconstitutional by SCC Case 10/35; Article 23 fell consequentially. These are not operative provisions. Article 37(2) and Article 38 must be mapped to the exact operative scope of SCC Case 42/17.
4. Law 68/1947 Article 1 is repealed. Articles 2 and 5/6 are shown as replaced/changed in later amendment annotations; do not label the reproduced wording as original 1947 wording.
5. Law 70/1964 Articles 1–4 are historical base-law wording. Fee tables and tariffs were subsequently amended, including by Law 83/2006 and later ministerial decisions. Do not serve the nominal amounts as current fees.

## Repository changes

- Added the supplemental Arabic text capture file.
- Updated FT-0004 through FT-0007 in `egypt_full_text_inventory_priority_2026-11-18.csv`.
- Updated acquisition records EG-0144, EG-0145, EG-0150 and EG-0151 with alternate full-text source locators and actual captured article scope.
- No new instrument or duplicate record was created.
- The 33-record priority full-text inventory count is unchanged; these are improvements to existing records.

## Progress metrics — conservative

| Workstream | Current estimate |
|---|---:|
| Whole Egyptian legal corpus | 2% provisional |
| Defined core extraction set (Civil Code, Evidence Law, Building Law) | 100% article-number extraction |
| Broader civil/property/contract corpus | 19% provisional |
| Agent 3 commercial/corporate/investment assignment | 55% provisional (separate scope; see Agent 3 checkpoint) |
| Lawyer verification | 0% |
| Confirmed commercial reuse permission | 0% |

Supplemental text-capture metrics:
- 28 text entries captured in this checkpoint;
- 27 non-repealed entries, one repealed marker;
- 200 additional searchable headings remain a separate heading count;
- 44 historical article-version events remain a separate event count;
- no increase to the 1,370 core provision count.

## Outstanding work

1. Extract the remaining articles of Laws 114/1946, 142/1964, 68/1947 and 70/1964 from alternate full-text mirrors, then compare against the 26 visually inspected Gazette scan pages.
2. Extract Law 142/1964 Articles 21–24 with their constitutional invalidation status and precise version dates.
3. Capture Law 70/1964 schedules A/B/C and the later Law 83/2006 and Decision 5424/2006 tariff text as separate instruments/version events.
4. Recover the full Law 68/1947 remaining text and its 1947 executive regulation separately.
5. Continue Decision 144/2009 complete 185-article normalization and annex/form extraction.
6. Continue Decision 825/1975 136-article extraction and amendment redline.
7. Continue the Civil Code and Evidence Law Gazette-to-text comparison and historical amendment graph.
8. Obtain authorized Amiri Press original digital binaries where available; preserve hashes only after actual file acquisition.

## Rights and verification

All captured text remains source-matched but not lawyer-reviewed. No lawyer verification, commercial reuse permission, certified Gazette authenticity or bulk-collection permission is claimed. The fallback source pages are not treated as proof of redistribution rights.
