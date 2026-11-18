# Agent 3 checkpoint 31 — stop the loop, new regulatory text capture (18 November 2026)

## Actual status
- Running inventory before this pass: 241 unique documents/instruments; 2,275 fully normalized units.
- New official FRA instruments captured/added in this pass: Decision 137/2018, Decision 191/2018, Decision 192/2018, and Decision 100/2020.
- Updated running minimum: **245 unique documents/instruments; at least 2,281 fully normalized article/contract/circular units**, plus the previously reported 1 partial provision and 3 identified provisions outstanding. This is a lower-bound count; the newly transcribed solvency rules are not separately counted because their rule-unit denominator has not been reconciled.
- Assigned-domain completion remains **55% provisional**; denominator not validated. This percentage is not a measure of currentness or legal validation.
- Whole Egyptian legal corpus estimate remains **about 2% provisional**.
- 13/13 families touched; 0/13 fully currentness-complete; lawyer review 0%; commercial republication permissions 0.

## New source captures

### Decision 137/2018 — licensing and continued licensing
- Official current consolidated PDF: https://fra.gov.eg/wp-content/uploads/2021/04/137-2018.pdf
- Official FRA page: https://fra.gov.eg/en/regulations/قرار-رقم-137-لعام-2018-2/
- Current consolidation is updated through 12 April 2023 by Decision 91/2023.
- Transcribed substantive text for Articles 1–5, including preliminary incorporation approval, capital/shareholder requirements, application documents, licensing capital and management experience requirements.
- Remaining Articles 6–16 identified by title but not fully transcribed. File explicitly marks itself partial.
- Repository record: `agent3_fra_decision_137_2018_licensing_current_consolidation_2023_arabic_text.md`.

### Decision 191/2018 — financial leasing solvency
- Official FRA current page: https://fra.gov.eg/regulations/قرار-رقم-191-لعام-2018/
- Official current PDF (8 pages): https://fra.gov.eg/wp-content/uploads/2021/04/191-2018.pdf
- FRA lists Decisions 69/2020 and 161/2022 in its amendment history and labels the text updated in 2022.
- Extracted substantive Arabic rule text from FRA's 2021 official industry guide: capital adequacy, core/ancillary capital, subordinated loan conditions, risk weights, operational-risk capital, concentration limits, leverage and asset-liability maturity matching. The 2021 guide predates the 2022 amendments; its figures are discovery text only until compared against the 2022 consolidated PDF.

### Decision 192/2018 — factoring solvency
- Official FRA current page: https://fra.gov.eg/regulations/قرار-رقم-192-لعام-2018/
- Official current PDF (9 pages): https://fra.gov.eg/wp-content/uploads/2021/04/192-201888.pdf
- FRA lists Decisions 70/2020 and 161/2022 in its amendment history and labels the text updated in 2022.
- Extracted substantive Arabic rule text from FRA's 2021 official industry guide: capital adequacy, capital tiers, risk weights, operational-risk capital, concentration limits, delinquency/interest treatment, debt write-offs, creditworthiness assessment and periodic reporting. The guide predates 2022 amendments; current consolidated PDF still needs article-by-article comparison.
- The 192/2018 consolidated PDF timed out when opened in the browser, but the official link and FRA landing page are confirmed. Not treated as blocked: alternative official FRA guide text was obtained.

### Decision 100/2020 — NBFI governance
- Original Gazette PDF: https://fra.gov.eg/wp-content/uploads/2020/06/alamiria_2020_100.pdf (Gazette issue 159, 14 July 2020, p.22 onward).
- Current consolidated official PDF: https://fra.gov.eg/wp-content/uploads/2024/08/100-2020-%D9%88%D9%81%D9%82%D8%A7-%D9%84%D8%A7%D8%AE%D8%B1-%D8%AA%D8%B9%D8%AF%D9%8A%D9%84.pdf
- Current through 28 August 2024; amendment chain: Decisions 167/2023, 178/2023, 47/2024, 115/2024 and 185/2024.
- Captured official preamble and Article 1, which expressly includes leasing and factoring companies among entities subject to governance as a condition of continued licensing.
- Decision 100/2020 repeals the dedicated Decision 164/2018 governance rules; Decision 164/2018 must not be treated as current standalone governance rules.
- Full governance annex and remaining articles are not yet transcribed. Repository record marks partial status.

## New collection tool/source that reduces future loops
- FRA's official 2021 guide has 1,579 searchable lines and compiles licensing, governance, core operating controls, factoring rules, leasing rules, solvency, reporting, accounting and company lifecycle requirements.
- Guide URL: https://www.fra.gov.eg/wp-content/uploads/2021/06/%D8%AF%D9%84%D9%8A%D9%84-%D8%A7%D9%84%D9%82%D9%88%D8%A7%D8%B9%D8%AF-%D9%88%D8%A7%D9%84%D9%85%D8%B9%D8%A7%D9%8A%D9%8A%D8%B1-%D8%A7%D9%84%D9%85%D9%86%D8%B8%D9%85%D8%A9-%D9%84%D8%B9%D9%85%D9%84-%D8%B4%D8%B1%D9%83%D8%A7%D8%AA-%D8%A7%D9%84%D8%AA%D8%A3%D8%AC%D9%8A%D8%B1-%D8%A7%D9%84%D8%AA%D9%85%D9%88%D9%8A%D9%84%D9%8A-%D9%88%D8%A7%D9%84%D8%AA%D8%AE%D8%B5%D9%8A%D9%85-.pdf
- Its own introduction states the underlying FRA decisions and circulars remain authoritative and the guide is an aid. It is a discovery/index source, not a replacement for current consolidated texts.

## Next distinct work — no repeated checkpoint loop
1. Compare Decision 191/2018 and 192/2018 2022 consolidated PDFs against the 2021 guide and capture the changes in Decisions 69/2020, 70/2020 and 161/2022.
2. Transcribe the complete annex to Decision 100/2020 and map governance requirements to the five NBFI sectors.
3. Capture Decision 138/2018 financial statements and filing deadlines; Decision 139/2018 leasing-contract register; Decision 195/2018 cessation/liquidation/merger/acquisition; Decision 163 amendments 197/2018 and 25/2021.
4. Move to Companies Law 159/1981 and Executive Regulation 96/1982 using GAFI's official text; avoid repeating FRA leasing/factoring material already indexed.
5. Then capture Investment Law 72/2017 / Executive Regulation 2310/2017, Trade Register Law 34/1976, Commercial Code 17/1999, and remaining assigned statutes.

## Trust and rights
- All material remains `source-matched, not lawyer-reviewed`.
- Official/public access does not establish permission for commercial republication.
- Never label a provision `verified` until qualified Egyptian lawyer approval is recorded.