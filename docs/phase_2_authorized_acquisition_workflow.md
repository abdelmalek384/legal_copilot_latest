# Phase 2 — Authorized acquisition workflow

## Current position

The Phase 2 inventory contains source-discovery leads, not a verified legal corpus. The next step is a permission-gated acquisition workflow. The structured queue is in `docs/phase_2_authorized_acquisition_queue.json`.

## Work stages

1. **Source discovery** — identify a specific instrument and candidate official publication. Discovery alone does not imply permission.
2. **Terms and authorization** — record the exact source terms, date checked, permitted acquisition method, intended uses, and evidence. If unclear, request written authorization.
3. **Acquisition** — use only an approved direct URL or an authorized manually supplied file. Never crawl, guess URLs, bypass login/paywalls, or bulk extract a restricted court portal.
4. **Immutable provenance** — preserve the original bytes; record SHA-256, source URL, final URL, retrieval timestamp, HTTP metadata, Gazette/Proceedings issue, publication date, and page range.
5. **Text extraction** — store extracted text separately from the original. Mark OCR output and extraction quality; never silently correct legal text.
6. **Instrument relationships** — represent each amending, repealing, correcting, consolidating, superseding, and implementing instrument as a distinct record with explicit links.
7. **Provision-level comparison** — map exactly which articles/schedules changed and retain before/after text with provenance.
8. **Legal review** — qualified Egyptian counsel reviews authenticity, commencement, transitional provisions, amendments, and legal status. Review outcome is a separate append-only event.
9. **Release to retrieval** — only versions that satisfy the product's review policy may be used to answer current-law questions. Discovery-only and unreviewed texts must not be represented as current law.

## Required status dimensions

Keep these dimensions independent; one must not automatically change another:

- `source_discovery_state`: not_started / discovered
- `access_terms_state`: not_reviewed / reviewed
- `collection_permission`: unknown / permission_pending / allowed / not_allowed
- `acquisition_state`: not_acquired / acquired
- `extraction_state`: not_started / extracted / OCR_required / extraction_reviewed
- `authenticity_state`: unknown / source_checked / verified / rejected
- `amendment_history_state`: unknown / partial / reviewed
- `legal_status`: unknown / under_review / not_yet_in_force / in_force / partially_repealed / repealed / historical
- `lawyer_review_state`: not_started / pending / approved / rejected
- `commercial_use_state`: unknown / allowed / restricted / prohibited

## Acquisition release checklist

An item can enter the acquisition batch only when:
- the exact instrument and direct source are identified;
- source terms and access restrictions have been reviewed;
- written authorization is stored if required;
- intended storage, extraction, indexing, commercial use, and display are within the documented scope;
- approved hostname(s) and direct URL are recorded;
- the source is not a restricted court portal whose terms prohibit the planned method.

A downloaded item remains **pending review** until authenticity, extraction, amendment chain, commencement, and legal status have been independently assessed. The queue does not authorize collection and must never be passed directly to the downloader as if its entries were approved.

## Court judgments

The Court of Cassation source register records restrictions against automated/bulk extraction and a written-permission requirement for commercial use. Do not scrape or bulk download judgments without authorization. Request an official API, licensed export, or written exception. If no license is available, keep judgment collection blocked and use only properly sourced records supplied through a permitted method.

## Current priority

1. Resolve authorized access for core Official Gazette texts.
2. Build the first primary-law batch around the Constitution, Civil Code, civil procedure/evidence, Penal Code, Criminal Procedure (including commencement transition), and Labour Law 14/2025 with implementing decisions.
3. Add commercial/company/insolvency and tax statutes with provision-level amendment mapping.
4. Add family, administrative, property and IP statutes.
5. Add court judgments only when lawful access and reuse are documented.

## Definition of “source acquired”

A source is not “acquired” because its page was found, an index listed a PDF, or a third-party database mentions the law. Acquisition requires an actual authorized original file, immutable hash, source and publication metadata, and a stored provenance record.
