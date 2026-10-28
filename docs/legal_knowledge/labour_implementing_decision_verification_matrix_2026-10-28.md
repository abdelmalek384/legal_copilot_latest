# Labour Law implementing-decision verification matrix — 2026-10-28

## Purpose and safety rule

This is a work queue for the Labour Law No. 14/2025 knowledge corpus. It does not certify any instrument as current, complete, legally reusable, or lawyer-approved. Keep every dependent evidence card at `search_eligible: false` until the relevant gates below are evidenced. A Gazette index entry proves bibliographic metadata only; a secondary transcription is a discovery lead, not a substitute for the official instrument.

## Evidence classes

- **G1 — Official metadata:** an official Gazette/catalogue record establishes instrument number, issue, and date, but not the complete operative text.
- **G2 — Official searchable text:** an official publisher's searchable text is available; still compare it with the Gazette image/PDF and record its exact source/version.
- **G3 — Secondary transcription/abstract:** useful for discovery and issue-spotting only; never sufficient by itself to support an authoritative answer.
- **G4 — Full verification package:** official complete text obtained; Gazette pages visually/textually compared; SHA-256 of the exact downloaded binary recorded; commencement and transitional provisions checked; later amendments/repeals searched; reuse basis documented; and any legal interpretation reviewed by a qualified Egyptian lawyer.

A record can move to G4 only when each item is independently evidenced. Do not infer that a later-numbered decision amends the Labour Law or another decision merely from its date.

## Decision-by-decision queue

| Instrument | Existing lead/status from the current workstream | Relevant candidate cards | Required next evidence |
|---|---|---|---|
| Ministerial Decision 49/2026 | Official Gazette repository metadata: issue 64 (supplement), 18 March 2026; public transcription of five articles and schedules was found. Full Gazette text comparison is outstanding. | Annual-leave cards; eligibility must be tested against the actual scheduled work and location, not a broad sector label. | Obtain the official complete text from a publicly accessible source if available; otherwise retain G1/G3 and do not infer eligibility from the transcription. Record schedule rows verbatim only after comparison. |
| Ministerial Decision 162/2026 | Official Gazette supplement record identifies issue 176 (supplement), dated 13 August 2026. A second public repository record lists Arabic and English PDF files and describes the instrument's sections. A public secondary Arabic transcription also exists. These are usable research leads, but a library-hosted copy is not automatically an official publisher original. | Workplace-regulation and discipline cards, especially Law 14/2025 Arts. 4 and 137–141. | Retrieve and compare the public Arabic PDF with the Gazette supplement page images; preserve the source and exact file hash. Check commencement, schedules, amendments, and reuse status. Until that is done, do not elevate extracted rules to authoritative evidence. |
| Ministerial Decision 187/2025 | Secondary lead for resignation-authentication procedures; complete official text unresolved. | Resignation and termination cards. | Locate official publication metadata and complete text; verify authentication method, responsible authority, effective date, and transitional rules. |
| Ministerial Decision 214/2025 | Amiri Press searchable Arabic text is available. A separate public repository record lists Arabic and English PDFs and dates the instrument 5 October 2025. The repository description confirms the four-copy Arabic contract rule, but is still descriptive metadata rather than a clause-by-clause comparison. | Employment-contract and hiring-documentation cards. | Compare the Amiri Press text against the Arabic PDF/Gazette. Record retrieval time, exact retained artifact and hash; review commencement, later changes, and reuse terms. |
| Ministerial Decision 290/2025 | Earlier notes record a Gazette metadata/public abstract lead, but the instrument's exact subject still needs to be confirmed against its full title and text. Do not conflate it with Article 290 of Law 14/2025. | No new card mapping until identity and subject are verified. | Find the exact Gazette supplement/title and full text; resolve the previous “intermittent-work” description before mapping cards. |
| Ministerial Decision 291/2025 | Gazette issue metadata only in the latest pass; subject and operative text need exact identity confirmation. | No new card mapping until identity and subject are verified. | Find the exact title, full text and schedules. Do not rely on the previous “overtime controls” label without source support. |
| Ministerial Decision 292/2025 | Gazette supplement metadata identifies Decision 292/2025 as setting maximum actual and additional hours for preparatory, complementary, guarding and cleaning work. Full text and primary comparison remain incomplete. | Working-time cards for the listed job categories only. | Verify the precise covered job titles, maximum hours, conditions/exceptions, schedules and commencement from the complete official text. Do not generalize to all workers. |
| Ministerial Decision 294/2025 | Gazette supplement metadata identifies Decision 294/2025 as determining holidays and occasions that count as fully paid leave. Full text and currentness review remain incomplete. | Paid-holiday and leave cards only after pinpoint verification. | Obtain and compare the complete official decision and any schedules; verify dates, scope, commencement and later changes before mapping cards. |

## Newly found public source leads (28 October 2026)

These links advance discovery; they do not, by themselves, satisfy G4:

- Gazette supplement 176 (supplement), dated 13 August 2026, lists Decision 162/2026 and a 2.26 MB PDF: https://dspace.id.com.eg/items/dae71be0-2519-407f-b239-08fa7a4eb536/full
- Public Arabic/English copies described as Decision 162/2026: https://dspace.id.com.eg/items/5c91a8fb-c28a-4103-86c3-76410ebd91eb/full
- Official Amiri Press searchable text for Decision 214/2025: https://alamiria.com/Sec/TashTxt?id=5EinXV37k4w%3D
- Public Arabic/English copies described as Decision 214/2025: https://dspace.id.com.eg/items/8ebcec10-0c45-4fbf-9a56-44ca409dc6c4/full
- Gazette supplement 291 (supplement), dated 25 December 2025, whose metadata lists Decisions 292/2025 and 294/2025 and their subjects: https://dspace.id.com.eg/items/37add437-802d-4848-8a24-8e064db22fcc

For records hosted by a third-party repository, record that repository as the retrieval host and the named issuing/publishing authority separately. Do not label a mirror as the official publisher. Inspect the item-specific licence before reproducing or redistributing any repository-hosted PDF; if the terms are unclear, set `reuse_status: unknown`.

## Crosswalk rules for card maintainers

For each card-to-instrument relationship, record:

1. **Exact relationship:** implements / supplements / clarifies / event-specific guidance / possible conflict / unknown. Use “unknown” until text supports a stronger classification.
2. **Pinpoint:** instrument article and schedule item, plus Law 14/2025 article. Never map an entire instrument to a card based only on a topic keyword.
3. **Temporal status:** publication date, commencement date, transitional rule, and date checked for later amendments/repeal. If any are unknown, state so explicitly.
4. **Source provenance:** source organization, canonical URL, retrieval timestamp (UTC), source class G1–G4, retained artifact path, and SHA-256 only when calculated from the exact retained bytes.
5. **Reuse basis:** public accessibility is not a commercial-reuse licence. Record the terms or legal basis actually checked; otherwise `reuse_status: unknown`.
6. **Interpretation status:** separate text extraction from legal interpretation. Mark lawyer review pending unless a named qualified reviewer actually reviewed the precise version.
7. **Retrieval control:** until G4, card remains `search_eligible: false` for authoritative legal answers. A future research interface may show a clearly labelled unverified lead only if product policy explicitly allows it and never presents it as settled law.

## Efficient public-source fallback order

When a repository's PDF download is blocked, do not repeat the same failed request. Try, in order:

1. Search the issuing Ministry's official announcements and attachments for the exact instrument number and year.
2. Search the Amiri Press official searchable text collection by exact decision number/title.
3. Search the official Gazette repository by issue number/date and use its browser-rendered pages for visual inspection if direct download is unavailable.
4. Search other government-hosted copies and archived official pages; preserve provenance and distinguish a mirror from the publisher.
5. Use secondary legal databases only to identify article numbers, schedules, and source leads. Do not promote their text to G2/G4.
6. If no public full text exists, close the research attempt with a documented blocker and a narrow unresolved question. Do not bypass access controls, claim to have obtained a missing file, or invent a hash.

## Acceptance checklist for a decision

- [ ] Official identity confirmed: exact title, number/year, issuing authority, Gazette issue and publication date.
- [ ] Full text and every annex/schedule obtained from an official public source.
- [ ] Exact retained binary hashed; if only a web page is available, identify it as a page capture/text artifact rather than a PDF hash.
- [ ] Text compared against Gazette page images; article and schedule pinpoints independently checked.
- [ ] Commencement, transitional provisions, and any expiry/temporary scope recorded.
- [ ] Later amendments, replacements, repeal, and relevant judicial treatment searched through a stated cutoff date.
- [ ] Reuse status explicitly supported or marked unknown.
- [ ] Every mapped card has a precise relationship and pinpoint.
- [ ] Focused tests cover required fields, source-class restrictions, and search-eligibility gates.
- [ ] Qualified Egyptian-lawyer review status accurately recorded.
- [ ] Only after all required gates are met may a maintainer propose changing search eligibility; the change must be separately reviewed and tested.

## Current workstream status

- Candidate cards: latest PR description reports 294 in the main file plus 15 in a separate early-article supplement (309 total records; 298/298 article numbers represented across selected ranges).
- Instrument crosswalk: eight records listed above.
- Tests: focused tests were added according to the PR description, but the latest test suite/CI was not run in that update.
- Primary-source currentness, reuse rights, complete source-file hashes, and qualified review: incomplete.
- Retrieval gate: `search_eligible: false`; no claim of legal verification.

This matrix is a work queue and control document, not legal advice and not proof that any decision remains in force.
