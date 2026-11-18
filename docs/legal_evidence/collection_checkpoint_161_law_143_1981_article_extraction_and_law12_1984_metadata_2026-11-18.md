# Research Agent 1 — checkpoint 161: Law 143/1981 Arabic extraction and Law 12/1984 metadata correction (18 November 2026)

## 1. Article extraction

Created `docs/legal_evidence/law_143_1981_articles_1_29_arabic_extraction_v1_2026-11-18.md` containing the Arabic text of Law 143/1981 Articles 1–29 from the official Ministry of Agriculture PDF:
https://moa.gov.eg/media/sf1heyme/143.pdf

- Article headings: 29.
- Complete transcriptions: **27**.
- Partial transcription: **1** (Article 2; subparagraphs (ب) and (د) are quarantined pending high-resolution reading).
- Repealed marker: **1** (Article 21).
- PDF page images visually inspected: 8 (indices 0,1,2,3,5,6,7,8).
- PDF page index 4 did not render; Articles 12–13 are from the text layer only and still require page-image verification.
- Article 4(1) includes the Law 72/1996 amendment; Article 11(1) includes Law 205/1991. Law 11/2024 replacements to Articles 11(2) and 12(2) are not integrated.

This is an official Ministry-hosted historical text, not a fully current consolidated law and not an original 1981 Gazette binary. OCR/punctuation require review.

## 2. Law 12/1984 publication correction

The official Ministry of Agriculture PDF footnote to Article 21 states that Law 12/1984 repealed Article 21 and was published in Official Gazette **issue 9 dated 1 March 1984**.

This conflicts with an earlier secondary search snippet saying issue 9 supplement, 1 January 1984. The acquisition record EG-0236 now uses the official Ministry PDF's issue/date and preserves the conflict. Effective date remains **uncertified** pending the original Law 12/1984 text and commencement clause. Version event EV-0020 has also been corrected to issue 9 / 1 March 1984.

## 3. Article status and versioning

- Article 21: repealed by Law 12/1984.
- Article 4(1): amended by Law 72/1996.
- Article 11(1): amended by Law 205/1991.
- Articles 11(2) and 12(2): later amended by Law 11/2024; not integrated into this MOA-source extraction.
- Article 22(1): invalidated by SCC Case 101/26.
- The extraction is a historical source version with separate amendment/judicial events, not a current consolidated statute.

## 4. Separate counts

| Metric | Value |
|---|---:|
| Acquisition register rows | **241** |
| Unique acquisition IDs | **241** |
| Source-permission records | **63** |
| Completed core unique article provisions | **1,370** |
| Law 143 complete article texts | **27** |
| Law 143 partial article texts | **1** |
| Law 143 repealed markers | **1** |
| Unique complete article texts across core set + Law 143 extraction | **1,397** |
| New legal instruments in checkpoint 161 | **0** |
| New article texts in checkpoint 161 | **27** |

The 1,397 is a source-version extraction count, not a count of currently operative provisions. The 1,370 core count remains separately defined.

## 5. Completion estimate

- Core article-number extraction: **100%** for the three defined core statutes, subject to OCR/source-image and historical-version validation.
- Law 143/1981: 27/28 non-repealed articles fully transcribed, one partial; Articles 12–13 need image verification and 2024 versions need integration.
- Broader civil/property/contract corpus: **15% provisional**.
- Whole Egyptian legal corpus: **2% provisional**.

## 6. Next actions

1. Obtain high-resolution page index 4 for Articles 12–13.
2. Re-read Article 2(b) and 2(d) from high-resolution images.
3. Obtain original Law 12/1984 issue 9 and verify effective date.
4. Integrate Law 11/2024 text into Articles 11(2) and 12(2).
5. Map Case 101/26 exact operative effect to Article 22(1).
6. Continue extraction for Law 114 Articles 1–70 and Law 142's 66 substantive articles.

## 7. Rights and verification

No lawyer verification, commercial reuse permission, certified Gazette authentication or bulk retrieval permission is claimed. The source is an official Ministry PDF, not an authenticated Amiri Press original binary.
