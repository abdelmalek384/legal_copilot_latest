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
| Ministerial Decision 162/2026 | Official Gazette repository metadata: issue 176 (supplement), 13 August 2026; public secondary transcription reported to cover 66 articles. Gazette PDF access required a copy request in the prior research; none was submitted. | Workplace-regulation and discipline cards, especially Law 14/2025 Arts. 4 and 137–141. | Search alternative public official-hosted copies and Ministry/Amiri Press text. If none exists, document the access barrier and keep all derived rules non-authoritative; do not treat the secondary text as primary. |
| Ministerial Decision 187/2025 | Secondary lead for resignation-authentication procedures; complete official text unresolved. | Resignation and termination cards. | Locate official publication metadata and complete text; verify authentication method, responsible authority, effective date, and transitional rules. |
| Ministerial Decision 214/2025 | Amiri Press searchable text lead describes Arabic written employment contracts in four copies and distribution to employer, worker, social-insurance office, and competent administrative authority. Full comparison, binary hash, reuse terms, and currentness review remain open. | Employment-contract and hiring-documentation cards. | Preserve the official text URL and retrieval timestamp; obtain the exact source binary or page capture where lawful; compare each operative clause with the Gazette; hash the exact file actually retained. |
| Ministerial Decision 290/2025 | Gazette metadata and a public Article 1 abstract found; intermittent-work qualifying schedule remains unresolved. | Intermittent-work cards. | Locate the complete official decision and all schedules. Do not convert the abstract into a complete eligibility rule. |
| Ministerial Decision 291/2025 | Gazette issue metadata only in the latest pass; relates to overtime controls. | Overtime and working-time cards. | Find complete operative text, scope, limits, exceptions, commencement, and any later instrument that changes it. |
| Ministerial Decision 292/2025 | Gazette issue metadata plus secondary text lead; relates to maximum hours for specified preparatory, complementary, guarding, and cleaning work. Primary comparison incomplete. | Working-time cards for the listed job categories only. | Verify the precise covered job titles, maximum hours, conditions/exceptions, and schedules from the official full text. Do not generalize to all workers. |
| Ministerial Decision 294/2025 | Secondary text lead recorded; primary-text comparison and currentness review incomplete. | Only cards explicitly cross-referenced to the decision in the inventory. | Establish the exact subject and operative scope from official metadata first; then locate full official text before mapping additional cards. Do not infer subject matter from number alone. |

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
