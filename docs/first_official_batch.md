# First official Egyptian legal-document batch

This batch contains four individually identified documents from Egyptian government portals. It is intentionally small enough to review end-to-end before scaling.

## Documents

| ID | Instrument | Official source |
|---|---|---|
| \`EG-CONSTITUTION-2019-OFFICIAL-PDF\` | Constitution text amended in April 2019 | [Presidency PDF](https://www.presidency.eg/media/46122/%D8%AF%D8%B3%D8%AA%D9%88%D8%B1-%D8%AC%D9%85%D9%87%D9%88%D8%B1%D9%8A%D8%A9-%D9%85%D8%B5%D8%B1-%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9-2019.pdf) |
| \`EG-LABOUR-LAW-14-2025-OFFICIAL-TEXT\` | Labour Law No. 14 of 2025 | [Amiri Press text](https://www.alamiria.com/Sec/TashTxt?id=vPdoWGGYwoE%3D) |
| \`EG-LABOUR-MINISTER-DECISION-214-2025\` | Ministry of Labour Decision No. 214 of 2025 | [Amiri Press text](https://www.alamiria.com/Sec/TashTxt?id=5EinXV37k4w%3D) |
| \`EG-JUSTICE-LABOUR-COURTS-4621-2025\` | Ministry of Justice Decision No. 4621 of 2025 on labour-court locations | [Amiri Press text](https://www.alamiria.com/Sec/TashTxt?id=7FYalJBNQ2s%3D) |

The Presidency PDF identifies itself as the Constitution as amended in April 2019 and references Official Gazette issue 16 bis (w) of 23 April 2019. The labour law states it was issued on 3 May 2025 and contains its own commencement rule. Do not derive the effective date from the publication date alone.

## Why these entries are collectable

Egyptian Law No. 82 of 2002, Article 141(1), excludes official documents—including laws, regulations, resolutions and decisions—from copyright protection. See the [WIPO Lex entry for the Egyptian law](https://www.wipo.int/wipolex/en/legislation/details/1301) and its [text of Article 141](https://www.wipo.int/wipolex/en/text/126540).

The manifest records this as a narrow, document-specific legal rationale. It does not authorize crawling the whole website, copying third-party annotations or a protected creative collection, bypassing access controls, or assuming a site's technical or contractual conditions do not apply. The source page and exact URL are restricted to four individual documents, and the collector retains rate limiting and host checks. Obtain Egyptian legal review before relying on this interpretation for a commercial deployment.

## Run the first collection

After merging this change and installing the project's requirements:

\`\`\`bash
python tools/collect_legal_documents.py --manifest docs/collection_manifest.example.json --out legal_corpus --delay 3
\`\`\`

The collector should save original files, metadata, SHA-256 hashes, extracted text, article-number audit output, a collection report, and a human review queue. It will not mark a document legally authentic or current.

The command needs network access from the machine where it is run. A successful CI test only validates manifest structure and safeguards; it does not download these files or establish that the source is reachable at runtime.

## Review before using in search

For every item:

1. Confirm the downloaded file's identity against the title and the issuing authority.
2. Compare the document against its Official Gazette reference where available.
3. Inspect extraction quality and article numbering; Arabic PDF text can be misordered or malformed.
4. Verify publication, commencement, transitional provisions, amendment history, and repeal/supersession.
5. Record lawyer review before importing its articles into the production legal search corpus.

All four records deliberately leave \`legal_status_assessment\` as \`unknown\`. A collected document is not automatically the current consolidated law.
