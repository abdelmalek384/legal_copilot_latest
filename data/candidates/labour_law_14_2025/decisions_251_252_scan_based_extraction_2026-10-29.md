# Decisions 251 and 252/2026 — scan-based clause extraction

Research date: 2026-10-29  
Source route: Al-Masdar reproduces page images of *Egyptian Proceedings, supplement to issue 225 (A), 12 October 2026*. These images visibly show Gazette page numbers and instrument text, but are hosted by a secondary publisher and are watermarked. They are stronger evidence than news summaries, yet the original official Gazette PDF bytes have not been acquired or hashed here. Treat these as **reproduced primary-text page images pending official-file comparison**, not as a certified official download.

- Decision 251 scan pages: 371–377 (image sequence visible at https://www.almasdar.com/175152)
- Decision 252 scan pages: 378–398 (image sequence visible at https://www.almasdar.com/175156)
- Official catalogue confirms issue/date and lists both instruments: https://dspace.id.com.eg/items/9cf7c0e9-002a-4467-9d35-e0bb26f81657/full
- Official Ministry announcement confirms the five decisions' broad subjects: https://www.labour.gov.eg/ar/الأخبار/وزير-العمل-يصدر-5-قرارات-تنفيذية-لتعزيز-منظومة-السلامة-والصحة-المهنية-وتأمين-بيئة-العمل/

## Independent full-document routes located

- Law Hub Decision 251 page and embedded PDF preview: https://lawhub.info/eg/?p=19707 and https://drive.google.com/file/d/186XzKlQRzxILk07Fkyu4Xru6WG6gFyTE/preview
- Law Hub Decision 252 page and embedded PDF preview: https://lawhub.info/eg/?p=19708 and https://drive.google.com/file/d/1xomhpGnE2rqopVujZK9fmcPcdEQyORPo/preview

The preview page loads in this research interface, but the individual Google Drive page-image request returned 403. No access control was bypassed, and no file bytes/hash are claimed. These are useful alternate full-document links for ordinary browser access; if a PDF is downloadable through the visible page, compare and hash the exact downloaded file.


## Additional public secondary summary found — Decision 251/252

A public LinkedIn profile/post associated with the Ministry of Labour Egypt provides a more detailed summary of Decisions 251 and 252 than the initial news articles: https://eg.linkedin.com/in/ehab-abdelatty-alian. It is **not the operative decision text** and must be treated as a secondary lead only.

- For Decision 251 it repeats the consultant A/B qualification and experience thresholds, three-year licence, fees, 50% fee reduction for covered persons with disabilities, and adds a reported requirement to submit work history covering the previous three years on renewal plus possible licence-cancellation grounds. Most of these are already represented in the 17-item candidate JSON; the new summary is an independent comparison lead, not a second primary source.
- For Decision 252 it reports a six-month transition period for existing training providers; minimum training-centre net area of 90 m²; training room of at least 30 m² and 1.5 m² per trainee; trainer qualification including a suitable higher degree, eight years of OSH experience and an accredited TOT course; trainer-licence fee EGP 5,000 and three-year validity; and exemptions for establishments training only their own workers if programmes are approved and provided free of charge.
- These additional values are appended as candidate assertions 252-N033–252-N040. JSON parsed successfully and the assertion count is now 40. They are marked `secondary_profile_summary_only` / `needs_scan_and_official_file_confirmation`, not verified legal requirements.
- The profile is not a Gazette, Ministry circular, or signed decision. Confirm every value against the reproduced Gazette pages and then against the official Gazette file; do not use the summary as an authoritative source.

## Decision 251/2026 — consultant licensing

### Visible scan-derived clauses

| Article/page | Extracted content | High-impact verification point |
|---|---|---|
| Art. 1, p. 372 | Defines OSH expert/consultancy services, licensed OSH consultant, competent central administration, ministry, competent authority and Labour Law 14/2025 | Preserve source wording; the image transcription has duplicated/awkward phrases in the consultant definition |
| Art. 2, p. 372 | No person may practise OSH expert/consultancy work without Ministry licence; two licence levels: consultant A and B | Scope of covered work and any exemptions |
| Art. 3, pp. 372–373 | Consultant A: bachelor's in engineering, pharmacy, human medicine, veterinary medicine, science, applied health sciences, or environment/waste management; at least 20 years practical OSH experience, reduced to 15 with a doctorate in an OSH specialty; one or more recognized international certificates; ICDL or digital-transformation basics certificate; pass prescribed tests; no final conviction for a dishonesty/moral-turpitude crime unless rehabilitation restored | Exact field names, qualifying experience, doctorate condition, accepted certificate list and disqualification language |
| Art. 4, pp. 373–374 | Consultant B: bachelor's in the listed fields or related fields accepted by the competent committee; at least 15 years practical OSH experience, reduced to 10 with an OSH-specialty doctorate; recognized international certificate(s); ICDL/digital-transformation basics; prescribed tests; same conviction/rehabilitation condition | Committee's discretion over related fields and whether every Art. 3 condition applies identically |
| Art. 5, p. 374 | Application to the technical secretariat on the prescribed form with CV, original qualification, valid national ID, recent personal photos, current criminal record, proof of experience, ICDL/digital-transformation certificate, evidence of no outstanding dues to accredited entities, copies of recognized international certificates, and electronic copy | Verify the exact “no dues” clause and document validity requirements |
| Arts. 6–7, pp. 375–376 | Ministerial committee chaired by the head of the competent central administration; includes relevant directors-general and legal affairs; may seek specialist assistance; meets at least monthly. Technical secretariat registers applications, checks documents, seeks completion, refers to committee, and issues outcome/notification under stated periods | Exact committee membership, day-count rules, and whether application is deemed rejected on silence |
| Art. 8, p. 376 | Licence/renewal fees: consultant A EGP 30,000 issue / 25,000 renewal; consultant B EGP 25,000 issue / 20,000 renewal; persons covered by Disability Rights Law 10/2018 pay half the fee | Fee schedule and eligibility must be checked against later changes |
| Art. 9, p. 377 | Licence valid three years, renewable, with proof of recent three years' relevant experience and prescribed renewal fee | Verify renewal documents and deadline |
| Art. 10, p. 377 | Licence revoked for loss of condition, false information/documents, material breach of obligations/fees, final dishonesty/moral-turpitude conviction without rehabilitation, or death of licensee | Verify exact revocation triggers and procedural safeguards |
| Art. 11, p. 377 | Published in Egyptian Proceedings; effective from the day following publication | Publication date shown in catalogue is 12 October 2026; verify official issue scan |

### Comparison notes

1. The Al-Masdar page text extraction exposes only Arts. 1–3, but its image sequence visibly contains the continuation through Art. 11. This is a concrete workaround for the missing text layer.
2. Numeric values above were read from the reproduced page images. They remain pending direct comparison with the official bundle and counsel review.
3. No source-use/republication conclusion is made for reusing the page images themselves. The candidate record can retain source URLs and factual metadata while licensing/reuse remains separately assessed.

## Decision 252/2026 — training-provider and trainer licensing

### Page-pinned article map from the reproduced scans

The image sequence covers printed Gazette pp. 378–398. The map below replaces the earlier broad/overlapping article ranges with page-level review anchors. It is an index, not a verbatim legal transcription.

| Printed page / scan | Article(s) visible | Topic to extract | Confidence / next check |
|---|---|---|---|
| p. 378 — https://www.almasdar.com/WebP/libfiles/46/4/75.webp | Preamble / instrument opening | Enabling law, issuance basis and instrument title | Check complete opening text and issue citation |
| p. 379 — https://www.almasdar.com/WebP/libfiles/46/4/76.webp | Art. 1 | Definitions: Ministry, competent authority/administration, training programme, licensing committee, curriculum committee, provider, accredited trainer | Definition list visible; transcribe exact Arabic terms |
| p. 380 — https://www.almasdar.com/WebP/libfiles/46/4/77.webp | Arts. 2–4 | Scope and objectives; prohibition on conducting OSH training without licence; programme standardization and training modes | Check exact scope and any exemptions |
| p. 381 — https://www.almasdar.com/WebP/libfiles/46/4/78.webp | Arts. 5–8 | Eligible training entities and licensing route; public/educational bodies, NGOs and specialized companies; limited internal-training conditions | Verify legal entity categories and all exception conditions |
| p. 382 — https://www.almasdar.com/WebP/libfiles/46/4/79.webp | Arts. 9–11 | Licensing committee, technical secretariat, application submission and document review | Exact membership, application form and review deadlines needed |
| p. 383 — https://www.almasdar.com/WebP/libfiles/46/4/80.webp | Arts. 12–13 | Completion requests, decision/notification process, duties of competent administration | Confirm calendar vs working-day language and consequences of delay |
| p. 384 — https://www.almasdar.com/WebP/libfiles/46/4/81.webp | Arts. 14–15 | General licence conditions and training-facility requirements | Extract each condition, room/equipment requirements and exemptions |
| p. 385 — https://www.almasdar.com/WebP/libfiles/46/4/82.webp | Art. 15 continuation / Art. 16 opening | Inspection and facility qualification requirements; transition to fees/inspection process | Confirm article boundary on high-resolution scan |
| p. 386 — https://www.almasdar.com/WebP/libfiles/46/4/83.webp | Arts. 16–17 | Inspection/reinspection and programme-material review fees; initial provider licence and renewal | Numeric fees are candidates only; official-file match required |
| p. 387 — https://www.almasdar.com/WebP/libfiles/46/4/84.webp | Arts. 17–18 | Provider licence term, renewal timing, programme lists and provider obligations | Verify exact renewal lead time and all required records |
| p. 388 — https://www.almasdar.com/WebP/libfiles/46/4/85.webp | Arts. 19–20 | Provider duties, suspension/cancellation or related compliance provisions | Capture exact triggers and procedure |
| p. 389 — https://www.almasdar.com/WebP/libfiles/46/4/86.webp | Arts. 21–22 | Trainer licensing / curriculum committee provisions | Verify article sequence and licensing requirements |
| p. 390 — https://www.almasdar.com/WebP/libfiles/46/4/87.webp | Arts. 23–24 | Programme/curriculum committee, training-provider obligations or related implementation provisions | Transcribe article headings before assigning final topic labels |
| p. 391 — https://www.almasdar.com/WebP/libfiles/46/4/88.webp | Arts. 25–26 | Trainer licence fee, trainer licence validity and renewal | Numeric terms are scan candidates; verify exact conditions |
| p. 392 — https://www.almasdar.com/WebP/libfiles/46/4/89.webp | Arts. 27–28 | Trainer qualification and eligibility conditions | Extract degree/experience requirements by trainer category |
| p. 393 — https://www.almasdar.com/WebP/libfiles/46/4/90.webp | Arts. 29–30 | Basic and advanced training programmes; target groups and course-hour table | Basic programme hour cells visible; some advanced cells unclear |
| p. 394 — https://www.almasdar.com/WebP/libfiles/46/4/91.webp | Art. 31 | Specialized course types and durations | Eleven visible course rows; preserve exact names and hours |
| p. 395 — https://www.almasdar.com/WebP/libfiles/46/4/92.webp | Art. 32 | Theoretical/practical evaluation requirements by programme type | Exact percentages require image-to-official-file check |
| p. 396 — https://www.almasdar.com/WebP/libfiles/46/4/93.webp | Art. 33 | Attendance, pass threshold, exam retakes, record retention | High-impact numeric values; verify every number and trigger |
| p. 397 — https://www.almasdar.com/WebP/libfiles/46/4/94.webp | Arts. 34–35 | Certification, programme completion, trainer/provider obligations and/or related final requirements | Transcribe exact headings and clauses |
| p. 398 — https://www.almasdar.com/WebP/libfiles/46/4/95.webp | Art. 36 | Publication, commencement and repeal/conflict clause | Verify exact commencement and repeal wording |

### Key extracted candidate rules

- **Training hours:** the basic table shows 80 hours for OSH specialists, 80 for supervisors, 80 for technicians, 40 for OSH committee members and 16 for employers/persons supervising OSH activity.
- **Specialized courses:** the table on p.394 contains eleven rows; visible hours include 16-hour courses (fire/explosion, work at heights/scaffolds, lifting/cranes, first aid, hazardous chemicals, risk assessment, emergency plans) and 12-hour courses (PPE use/maintenance, confined/enclosed spaces, welding safety, ISO 45001 introduction). These remain scan-derived candidates.
- **Provider fees:** p.387 appears to show EGP 7,000 for inspection, EGP 2,000 for reinspection, EGP 4,000 for review/approval of each programme's training material, EGP 3,000 for initial provider licence and EGP 1,500 for renewal.
- **Trainer fee:** p.391 appears to show EGP 5,000 for initial trainer licensing.
- **Facility dimensions:** p.386 appears to specify at least 1.5 square metres per trainee and 30 square metres per classroom; verify exact scope and exceptions.
- **Attendance/evaluation:** p.396 appears to set a 65% total evaluation threshold, minimum 80% attendance, exclusion from exam when absence exceeds 20% of combined theoretical/practical hours, at most two repeat exams, and five-year retention for training/evaluation records. All are provisional pending official-file match.

### Avoiding false precision

The image scans provide a route around the HTML text-layer gap, but some cells are low resolution and the page images are watermarked. Do not treat any of the numeric candidates as a final legal rule. Keep raw scan-derived text separate from reviewed transcription, preserve the exact image/page pinpoint, compare to the official Gazette bundle, check subsequent amendments, and obtain qualified Egyptian OSH counsel approval.

## Current status

- Reproduced Gazette page images located for both decisions: yes.
- Decision 251 visible pages indexed: 371–377.
- Decision 252 visible pages indexed: 378–398.
- Full official Gazette PDF bytes downloaded/hashed: no.
- Page-by-page comparison to official bundle: no.
- Counsel approval: no.
- Eligible for authoritative retrieval: no.

## Next steps

1. Transcribe the page-image sequence into source-preserving text with printed page markers and retain raw OCR separately from reviewed corrections.
2. Cross-check against the official Gazette PDF when obtainable through ordinary authorized access.
3. Extract all Decision 252 numeric tables and programme durations into structured ledger rows.
4. Search for later amendments/circulars and validate reuse rights before corpus release.
5. Obtain qualified Egyptian labour/OSH counsel approval for all high-impact thresholds, fees, licensing requirements, and training durations.
