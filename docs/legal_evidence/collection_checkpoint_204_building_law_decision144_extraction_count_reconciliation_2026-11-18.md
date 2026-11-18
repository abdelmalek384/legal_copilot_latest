# Collection checkpoint 204 — Building Law / Decision 144 text-count reconciliation

**Date:** 18 November 2026  
**Repository:** `abdelmalek384/legal_copilot_latest`  
**Purpose:** correct stale extraction counts in the master index and full-text inventories after re-reading the actual article-bearing checkpoints.

## 1. Finding: Law 119/2008 base article extraction is complete

The master index and full-text inventory had been carrying a stale statement that only 9 of 114 substantive Law 119/2008 articles were captured and 105 remained. That statement confused the 9 text units newly included in checkpoint 189 with cumulative corpus extraction.

The cumulative article-bearing checkpoints show:
- Checkpoint 93: selected original text for Articles 17, 24, 38, 39, 89, 98, 102 and 114 (8 distinct substantive articles).
- Checkpoint 108: Articles 6–16, 18–23 and 25–32 (25 new articles).
- Checkpoint 109: Articles 33–37 and 40–59 (25 new articles).
- Checkpoint 110: Articles 60–88, 90–97, 99–101 and 103–113 (51 new articles).
- Checkpoint 111: Articles 1–5 (5 new articles).

These are 114 distinct substantive article numbers, with no overlap between the enumerated sets. Together they cover all base Law 119/2008 Articles 1–114. The source is the official Ministry of Housing-hosted Gazette reproduction, Official Gazette issue 19 bis (A), 11 May 2008. The official PDF has 942 extracted lines and includes the promulgation provisions and full substantive statute text.

Checkpoint 189's “9 complete statutory provisions” means four issuing provisions plus five substantive provisions captured in that checkpoint; it is not the cumulative total. Checkpoint 202's eight Articles 2, 4–10 from the 1 December 2020 secondary consolidation are alternate-source/historical-current snapshots for eight already represented article numbers, not evidence that eight base Gazette articles were missing. Keep them as distinct source-version evidence, but do not add them to the 114 unique base provisions.

**Correct current status:** 114/114 substantive base article bodies captured in the repository. This does not mean the 2008 text is a current consolidated version. Law 23/2015 and subsequent legal changes, OCR fidelity, page-image validation, commencement/repeal effects and historical/current version mapping remain outstanding. The PDF bytes and SHA-256 are not archived locally.

## 2. Finding: Decision 144/2009 extraction count

The master index and FT-0012 record said four regulation article bodies were captured (177 remaining). That was also a checkpoint-local/cumulative-count confusion.

- Checkpoint 164 captures substantive Decision 144/2009 Articles 36–38, 59–63 and 144: nine distinct regulation articles.
- Checkpoint 189 captures substantive Articles 175, 176, 179 and 180: four further distinct regulation articles.
- These article sets do not overlap.

**Correct current status:** 13/185 substantive base regulation article bodies captured; 172 remain to be transcribed/normalized. Four issuing provisions are separately captured and are not included in the 185 article denominator. The searchable full text is available at LAW HUB; the government-bank-hosted NIB Gazette reproduction identifies Egyptian Proceedings issue 82 supplement (A), 8 April 2009, and the regulation through Article 185 with forms/schedules. Neither is an archived Amiri Press original binary in this repository. Annexes/forms and all amendments remain to be reconciled.

## 3. Amendment and currentness implications

- Law 23/2015 remains a separate amending statute, not a new base-law count. Its substitutions to issuing Article 4 and substantive Article 38, plus addition of Article 39 bis, must be represented as temporal versions.
- Decision 144/2009 amendments already mapped include Decisions 200/2010, 109/2013, 67/2014, 774/2014, 954/2022, 120/2025 and 1505/2025, alongside the Ministry's early list of 200/2009, 188/2010, 397/2010 and other implementing decisions. The chain is not asserted complete. Full before/after text, Gazette page images, forms and superseded/repealed markers remain necessary.
- A secondary consolidated text reports 198 current provisions after amendments; this is not substituted for the 185 base-article count until inserted provisions and editorial/version annotations are audited.

## 4. Corrected count ledger

| Measure | Correct count/status |
|---|---:|
| Law 119/2008 substantive base articles | 114/114 captured |
| Law 119/2008 promulgation provisions | 5; separately represented |
| 2020 secondary source snapshots | 8 (Articles 2, 4–10); alternate versions, not additional base articles |
| Decision 144/2009 substantive base articles | 13/185 captured |
| Decision 144/2009 substantive articles remaining | 172 |
| Decision 144/2009 issuing provisions | 4; separately represented |
| Unique core article provisions | 1,370; unchanged |
| New legal instruments | 0 |
| New unique article provisions in this reconciliation | 0 |

The 1,370 core unique provision total remains Civil Code 1,093 + Evidence Law 163 + Building Law 114. Decision 144/2009 is tracked separately as executive-regulation text, not folded into the core statute total.

## 5. Rights and verification

The MHUC and NIB PDFs are official-government-hosted Gazette reproductions; the NIB PDF is a government-bank-hosted copy. Neither is represented as a direct Amiri Press DSpace original binary downloaded and hashed locally. No lawyer verification, commercial reuse permission, bulk collection permission or redistribution permission is claimed.
