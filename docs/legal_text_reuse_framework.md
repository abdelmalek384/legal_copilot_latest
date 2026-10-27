# Egyptian official legal texts: reuse-rights review framework

**Status:** research aid for a qualified Egyptian-law reviewer, not a legal opinion or blanket permission to collect, republish, or commercially use any website or dataset.

## Why this distinction matters

Article 141 of Egypt's Law No. 82 of 2002 on the Protection of Intellectual Property Rights excludes specified official documents from copyright protection, including laws, regulations, resolutions, decisions, international conventions, court decisions, arbitral awards, and decisions of administrative committees with judicial competence. The same article states that collections of such documents may be protected when their selection or arrangement is creative. Article 140(3) separately lists databases among works eligible for protection.

A consolidated English text of Law No. 82 of 2002 is available through WIPO Lex, which reports amendments through Law No. 178 of 2020:
- https://www.wipo.int/wipolex/en/legislation/details/22066

This is a research reference, not a substitute for the current official Arabic text, the Official Gazette, or qualified legal review. Confirm the current wording and relevant amendments before relying on this framework.

## Keep four questions separate

1. **Underlying legal document:** Is the item itself an official law, regulation, decision, or judgment covered by Article 141?
2. **Website/database/collection:** Is the site providing a protected compilation, creative selection or arrangement, editorial headnotes, summaries, annotations, translations, or other separately protected material?
3. **Access and collection method:** Do current site terms, authentication requirements, rate limits, or technical restrictions govern downloading, automation, bulk extraction, or reuse? Do not bypass access controls or scrape a portal whose published terms prohibit it.
4. **Product use:** What will Legal Copilot do with the item—store the original, extract text, index it, show excerpts, redistribute files, or use it commercially? A conclusion about copyright in the underlying official text does not automatically answer all of these questions.

## Practical handling rules

- Prefer a direct, individually identified official Gazette or government-issued document over copying a third-party site's curated database.
- Treat official portals as discovery sources until the exact instrument, publication details, and direct document URL are captured.
- Do not copy editorial summaries, annotations, headnotes, proprietary indexes, or creative collections from a third-party provider unless their reuse rights are established.
- Do not scrape the Court of Cassation portal or another source with restrictive terms absent an applicable documented authorization or reviewed legal basis.
- Preserve the exact direct source URL, retrieval timestamp, original-file SHA-256, Gazette issue/pages, document number, and any amendment or commencement instrument.
- Keep authenticity, completeness, effective-date/currentness, source rights, and lawyer approval as separate review decisions.
- If a source is publicly accessible but the reuse position is unclear, keep its collection and commercial-reuse states unknown and quarantine it from acquisition/release workflows. Public availability alone is not a rights grant.

## What Article 141 does not do

Article 141 is a potential legal basis for using the underlying official document; it is **not** a blanket authorization to copy an entire portal, reproduce a protected compilation, ignore site terms, bypass technical restrictions, or assume that a third-party copy is authentic and current. Do not change a source to `allowed` solely because this statute has been identified.

## Release-gate implication

The current acquisition gate deliberately requires explicit evidence and human scope review before a source is marked ready for collection or commercial product use. Do not weaken that gate or mark permissions as approved based on this document alone. A qualified Egyptian-law reviewer should determine whether Article 141 and any other applicable law support a documented statutory-rights basis for a specific direct official document and intended use. If that workflow is later supported by code, it should record the legal basis, exact scope, reviewer, evidence URL, review date, and limitations separately from written permission.

## Review checklist

- [ ] Confirm the current Arabic text of Law No. 82 of 2002 and amendments relevant to Article 141.
- [ ] Identify whether the candidate is an official document or a protected third-party compilation/derivative.
- [ ] Review the source's current terms and the proposed collection method.
- [ ] Decide separately on local storage, text extraction, indexing, excerpt display, commercial use, and redistribution.
- [ ] Record a named reviewer, evidence URL, date, exact scope, and restrictions.
- [ ] Keep the candidate quarantined until the relevant gate accepts the recorded basis.
