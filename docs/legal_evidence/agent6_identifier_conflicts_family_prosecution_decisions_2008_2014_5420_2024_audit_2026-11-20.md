# Agent 6 — Identifier conflict audit: family prosecution Decisions 2004/2008 vs 2048/2008 and 6218/2014 vs 2218/2014

**Date:** 2026-11-20
**Purpose:** Prevent conflicting OCR and secondary catalogue numbers from being treated as separate legislation.

## 1. Damanhour family prosecution division (2008)

The following variants were located:
- **2004/2008** — EgyptianLaws catalogue title identifies “قرار وزير العدل رقم 2004 لسنة 2008” for dividing Damanhour College Family Prosecution into three college prosecutions (Waqa'i' issue 58, 10 March 2008).
- **2004/2008** — 2008 Justice Minister decisions index separately lists Decision 2004/2008 as the family prosecution division for Damanhour.
- **2048/2008** — SIS-hosted Waqa'i' issue 216/2024 search-extracted text of Decision 5420 preamble gives “2048 لسنة 2008” and says Damanhour.
- **2008/2004** — VetoGate text extraction of the same 2024 Gazette gives “2008 لسنة 2004,” likely digit/order extraction error.

**Working handling:** one Damanhour family-prosecution division instrument is established, but its identifier must remain `number_conflict_pending_primary_scan`. Do not create separate legal records for 2004/2008 and 2048/2008 until the original Waqa'i' issue 58 (10 March 2008) is inspected. The title and secondary index favour 2004/2008; SIS OCR supports 2048/2008. No definitive correction is claimed.

## 2. Marsa Matruh family prosecution (2014)

The following variants were located:
- **6218/2014** — Manshurat catalogue record and its 3-page scanned Waqa'i' reproduction, issue 196, 30 August 2014. The scan's page 12 heading itself visibly reads “قرار وزير العدل رقم 6218 لسنة 2014”; Articles 1–5 are transcribed in the Agent 6 tranche `agent6_family_courts_circulars21_22_2004_decisions6218_2014_2004_2008_arabic_text_2026-11-20.md`.
- **6218/2014** — Amiriya text extraction and the alternative full text of Decision 5420/2024 cite 6218/2014.
- **2218/2014** — SIS-hosted issue 216/2024 PDF's extracted preamble text gives “2218 لسنة 2014”; likely OCR or source-print variant, but the page image has not yet been checked.

**Working handling:** use the directly inspected 2014 scanned heading `6218/2014` as the current best primary evidence. Keep `2218/2014` as a conflicting extracted variant in the 2024 preamble; do not ingest it as a second instrument unless a Gazette page image establishes a separate decision.

## 3. Relevant source references
- Decision 2004/2008 catalogue: https://egyptianlaws.com/?p=164904
- Secondary 2008 index for Decision 2004/2008: https://ahmedazimelgamel.blogspot.com/2026/11/2008.html?m=0
- SIS-hosted 2024 Gazette issue 216 / Decision 5420/2024: https://mediadr.sis.gov.eg/bitstream/handle/123456789/74242/WQ216_20241001_9188.pdf?isAllowed=y&sequence=2
- VetoGate alternate extraction of issue 216: https://cdn.vetogate.com/UploadCache/libfiles/516/8/0x0o/845.pdf
- Manshurat Decision 6218/2014 catalogue and scan: https://manshurat.org/node/4056
- Direct 3-page Decision 6218/2014 scan: https://manshurat.org/file/7096/download?token=fMnL4lCg
- Amiriya text extraction of Decision 5420/2024: https://alamiria.com/Sec/TashTxt?id=QVqBTj6P1To%3D

## 4. Repository correction protocol
- Earlier working Agent 6 notes that stated “2048/2008 Damietta” and “2218/2014 Marsa Matruh” are not reliable identifiers.
- The jurisdiction for the 2008 instrument is **Damanhour**, not Damietta.
- The directly scanned 2014 decision is **6218/2014**, establishing a Family Prosecution in Marsa Matruh; it also creates general, traffic and child prosecution structures in the same governorate.
- Do not delete or overwrite the earlier evidence files in this pass. This addendum supersedes only their unverified identifier labels pending a page-image audit of Waqa'i' issue 58/2008 and issue 216/2024.
- Decision 5420/2024 itself is separately captured; its four operative articles remain intact. Its preamble's historical decision identifiers are preserved as source variants rather than silently normalized.

## 5. Outstanding verification
1. Acquire the original Waqa'i' issue 58/2008 page containing the Damanhour division decision; visually read the heading and all operative articles.
2. Inspect the SIS-hosted issue 216/2024 page image around the preamble to Decision 5420 and determine whether the printed numbers are 2048/2008 and 2218/2014 or extraction artifacts.
3. Compare the 2014 scanned Decision 6218 pages against a second Gazette copy if available.
4. Lawyer review remains outstanding; `verified = 0`.
