# Collection checkpoint 9 — additional 2026 Gazette texts: state companies, stamp tax, customs, Future of Egypt Authority

**Date:** 2026-11-17  
**Source class:** Ministry of Finance-hosted Gazette PDFs. These are source-text inspections, not lawyer approval or a consolidated current-law opinion.

## 1. Law 154/2026 — remittance of profits by state-owned companies

- Official Ministry record: https://mof.gov.eg/ar/legislation/legislation-6a731fef63496600085dd865
- Official Gazette PDF (2 pages): https://media.mof.gov.eg/mof-prd/qanwn_rqm_154_lsnt_2026_ilzam_alshrkat_almmlwkt_lldwlt_aw_llashkhas_alaetbaryt_aleamt_btwryd_nsbt_mn_arbahha_alsafyt_ila_alkhzant_aleamt_lldwlt_4d6cc71c22.pdf
- Gazette issue 30 bis (A), 28 July 2026.
- PDF text inspected in full (33 extracted lines).
- Article 1 text:
  - Companies wholly owned by the State or public legal persons must set aside 5% of distributable net profits, after covering carried-forward losses and before appropriations to reserves; proceeds are treated as tax revenue and transferred to the State Treasury within four months after financial-year close.
  - For companies in which State/public legal-person participation exceeds 50% but is not 100%, the board must collect 4% of distributable net profits after covering carried-forward losses and before reserves, but not more than the State/public person's share of those profits. The provision is calculated against the State/public person's share in net profits.
  - The law allows temporary exemption of some companies for public-interest economic or social reasons by Prime Minister decision based on Finance Minister presentation.
- Article 2: effective the day after publication in the Official Gazette.
- This law must be linked to company-specific legal forms and relevant corporate statutes. Do not infer that every public-sector company is covered without checking the ownership and legal-person conditions in the text.

## 2. Law 153/2026 — Stamp Tax amendment for listed securities

- Official Ministry record: https://mof.gov.eg/ar/legislation/legislation-6a73201f63496600085dd868
- Official Gazette PDF (2 pages): https://media.mof.gov.eg/mof-prd/qanwn_rqm_153_lsnt_2026_tedyl_bed_ahkam_drybt_aldmght_alsadr_balqanwn_rqm_111_ls_1980_ela_emlyat_tdawl_alawraq_almalyt_almqydt_balbwrst_almsryt_78020a46e5.pdf
- Gazette issue 30 bis (A), 28 July 2026.
- PDF text inspected in full (39 extracted lines).
- Amends Stamp Tax Law 111/1980 by replacing Article 83 bis.
- New provision imposes tax on total sale transactions of securities listed on the Egyptian Exchange, excluding listed investment fund certificates, without deducting costs.
- For ordinary transactions, the buyer bears 0.5 per thousand and the seller bears 0.5 per thousand (resident or nonresident as applicable).
- For buy/sell transactions executed on the same day, buyer and seller each bear 0.25 per thousand, as stated in the text.
- Exempts transactions by licensed market makers under Capital Market Law 95/1992.
- The entity settling the sale transactions must withhold and remit tax to the competent tax office within five days at the start of the month following the transaction month; it is jointly liable with buyer/seller for payment and delay consideration.
- Article 2 repeals Article 5 of Law 199/2020 (which amended Stamp Tax Law 111/1980 and Income Tax Law 91/2005).
- Article 3: effective the day after publication.
- This amendment must be linked to the full Stamp Tax Law and Capital Market Law framework; it is not a standalone complete stamp-tax code.

## 3. Minister of Finance Decision 262/2026 — Customs Executive Regulation amendment

- Official Ministry detail: https://mof.gov.eg/ar/legislation/legislation-7
- Official Gazette PDF (2 pages): https://media.mof.gov.eg/mof-prd/qrar_wzyr_almalyt_rqm_262_lsnt_2026_btedyl_bed_ahkam_allayht_altnfydhyt_lqanwn_aljmark_alsadrt_bqrar_wzyr_almalyt_rqm_430_lsnt_2021_9ff726701a.pdf
- Gazette: Al-Waqa'i al-Misriyya issue 114 (supplement), 24 May 2026.
- Amends Article 232 of the Executive Regulation of Customs Law 207/2020 (issued by Minister of Finance Decision 430/2021).
- New required supporting documents for the customs declaration, subject to non-duplication where electronically submitted:
  1. Copy of bill of lading, except advance clearance (electronic or manual).
  2. Delivery order for a bill of lading "To Order".
  3. For a nominative bill of lading, a declaration in the form set by Customs Authority Chair, undertaking payment of all related dues and presentation of delivery order or electronic equivalent confirmation from carrier/shipping agent before final release.
  4. Detailed commercial invoice, which may dispense with package inspection where it contains detailed package data.
  5. Proof of origin when claiming customs preference or exemption, and other cases under the import/export implementing rules.
- Decision published in Al-Waqa'i and effective the day after publication.
- Link it to Customs Law 207/2020, Executive Regulation Decision 430/2021 and prior/later amendments.

## 4. Future of Egypt Authority — catalogue/PDF number conflict

- Ministry catalogue record: https://mof.gov.eg/ar/legislation/legislation-6a731db063496600085dd853
- Ministry catalogue title calls it "Law 47/2026".
- The linked 57-page Gazette PDF is:
  https://media.mof.gov.eg/mof-prd/qanwn_rqm_47_lsnt_2026_tnzym_jhaz_mstqbl_msr_lltnmyt_almstdamt_wakhtsasath_fy_idart_mnatq_altnmyt_walastthmar_6c1bd6b496.pdf
- PDF itself visibly identifies the instrument as **Law 147/2026**, Gazette issue 30 bis, 26 July 2026. This is a material metadata conflict: catalogue title/record number 47 vs PDF promulgation number 147.
- Do not normalize or correct the record until the official Gazette scan and Ministry metadata are reconciled. The file name alone is not authority for the law number.
- The 57-page PDF was text-indexed; its opening provisions establish a reorganization law and attached statute for the Future of Egypt Authority for Sustainable Development.
- Promulgation articles include:
  - Article 2: certain lands transferred to/vested in the Authority before commencement are designated as sustainable development areas by presidential decision within three months.
  - Articles 3–9: transitional agreements, finance, vehicles, personnel, industrial facilities and social-insurance contribution arrangements.
  - Article 10: specified general public-authority, central administration, public business sector and wage-cap laws do not apply to the Authority; other listed regimes apply only insofar as consistent with its nature and purposes.
  - Article 12: Authority must regularize its status within one year, with possible extension by presidential decision up to an aggregate three additional years.
  - Article 14: commencement the day after publication.
- Attached law starts on Gazette page 7; Article 1 defines key terms including Authority, sustainable development area, national project, economic project and funds allocated for investment.
- The attached statute continues through the 57-page PDF; complete article-level extraction is still needed.

## 5. Corrections to the collection data model

- Store catalogue law number and Gazette PDF promulgation number as separate fields.
- Add `metadata_conflict=true`, `conflict_description`, and a resolution state to the instrument record.
- Store Gazette issue/date/page and PDF page separately.
- Do not silently use portal's "in force" status when the portal itself warns that the Gazette is the legal reference.
- For amendment laws, store each amended base-law article and exact replacement text.

## Status

- Full PDF text inspected: Law 154/2026, Law 153/2026, Decision 262/2026.
- Large PDF text inspected: Future of Egypt Authority statute PDF (57 pages); only opening and transitional provisions summarized here.
- No lawyer review or rights clearance claimed.
