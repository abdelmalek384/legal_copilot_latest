# Labour Law 14/2025 — uploaded Gazette PDF heading audit

**Audit date:** 2026-11-14  
**Input:** user-supplied `untitled folder(1).zip`, member `untitled folder/العدد-18-تابع-مومن-1.pdf`  
**Disposition:** structural heading audit only; no article-body match decision and no legal verification.

## What was inspected

- PDF: 112 pages, 665,047 bytes.
- SHA-256: `b0a47cefe18722d3f23e004ac7e78e6e309010e13124413e7e7018820c9581be`.
- PDF metadata producer: `doPDF Ver 7.2 Build 376`; creation/modification metadata: 5 May 2025.
- The PDF is encrypted; its metadata reports printing, copying and changes disabled.
- The extracted text layer contains the repeated watermark phrase `صورة إلكترونية لا يعتد بها عند التداول`.

## Structural results

| Check | PDF text-layer result |
|---|---:|
| Promulgation provisions | 13 headings; sequence 1–13 complete |
| Attached Labour Law articles | 298 headings; sequence 1–298 complete |
| Missing article heading numbers | 0 |
| Duplicate article heading numbers | 0 |
| Existing candidate JSONL rows | 311 (13 + 298) |
| Candidate JSONL malformed rows | 0 |
| Candidate JSONL `verified=0` | 311 |

The heading scan used Poppler `pdftotext 25.06.0` with `-layout`. Extracted text SHA-256: `53160b86fddea6cfdfd53541139cea7f6737f4a0f9559d756d076ef6eb30f5b2`.

## What this does and does not establish

This is an independent numbering-coverage check against the PDF's text layer. It confirms that the supplied PDF text layer exposes the expected 13 promulgation headings and all 298 attached-law article headings, with no numbering gaps or duplicates. It does **not** establish that the existing 311 candidate article bodies match the PDF. No body-by-body comparison was accepted because PDF extraction contains page furniture, repeated watermark text, RTL reading-order effects and glyph artifacts.

The extracted text was used locally only for this heading audit. It was not committed, not loaded into the legal corpus, and not treated as an authorized transcription. No importer run is claimed.

## Required follow-up

1. Obtain an authenticated Gazette copy or a source confirmation from the responsible legal owner.
2. Confirm source provenance and whether text extraction/reuse is permitted. The PDF's own copy/print restrictions and watermark must not be ignored.
3. Have qualified Egyptian counsel compare each provision/article body, commencement, amendments and corrigenda.
4. Keep every candidate row at `verified=0`; do not trust the input JSONL's `in_force=1` metadata as a currentness determination.

**Conclusion:** numbering coverage is structurally complete; text fidelity, authenticity, reuse rights and legal approval remain open.
