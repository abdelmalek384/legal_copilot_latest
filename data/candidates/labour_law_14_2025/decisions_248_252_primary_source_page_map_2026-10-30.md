# Consolidated primary-source review page map — Decisions 248–252/2026

**Prepared:** 2026-10-30  
**Purpose:** Speed up review when the original Official Gazette supplement is supplied. Page references below are *candidate printed-page locators from secondary reproductions*, not official-file verification. Always read the printed page label on the actual uploaded PDF and record the corresponding PDF page index separately.

## Candidate printed-page map

| Instrument/section | Candidate printed pages | Review target | Current evidence state |
|---|---:|---|---|
| Decision 248/2026 | Precedes Decision 249; likely pp. 1–18, **confirm on original** | Full operative text, commencement clause, attached tables/forms, any repeals | Locator not yet confirmed against original |
| Decision 249/2026 | pp. 19–44 | Articles 1–22 and Tables 1–3; exact worker thresholds, committee cadence, staffing counts, risk-classification and monitoring rows | Reproduced secondary page images located; full official-file comparison incomplete |
| Decision 250/2026 — Table 23 | starts around p. 242 | Hazardous-substance threshold quantities, CAS identifiers, units and row groupings | 137 Arabic candidate labels; official matching not performed |
| Decision 250/2026 — Table 24 | around pp. 249–360 | All chemical exposure limits, column labels, units, surface-vs-air limits, footnotes, child entries and rows marked removed | 617/745 candidate entries structured; 128 unextracted; official matching not performed |
| Decision 250/2026 — registers/templates | begins around p. 361 | Required register forms, fields, retention/signature requirements and any annex notes | Secondary transcription locator only |
| Decision 251/2026 | begins around p. 372 | Licensing, eligibility, degree fields, experience thresholds, exceptions, fees and effective/transition terms | 17 candidate assertions; 12 have secondary image locators, 5 page-only locators |
| Decision 252/2026 | candidate pages include pp. 386–396 | Training-provider licensing, hours, facilities, fees, pass/attendance thresholds, records, exemptions and transition provisions | 40 candidate assertions; 32 have secondary scan/page locators, 8 summary-only leads |

## Suggested comparison order after the original PDF arrives

1. **Verify file identity first:** preserve original bytes, record acquisition route and retrieval timestamp, calculate SHA-256, and confirm the PDF is the exact supplement containing Decisions 248–252.
2. **Confirm printed-page alignment:** find the printed labels in the PDF; record both printed page and zero-based/one-based PDF page index according to the review tool used. Do not assume secondary reproduction pagination equals the uploaded PDF's PDF index.
3. **Decision 248 and Decision 249:** capture operative text and attached tables. For Decision 249, prioritize Table 2 staffing counts and Table 3 pollutant combinations because errors could create unsafe compliance advice.
4. **Decision 250 Table 23:** compare all 137 candidate labels and threshold quantities; verify CAS identifiers, decimal separators, units, group entries and footnotes.
5. **Decision 250 Table 24:** compare candidate rows 1–617 and transcribe rows 618–745 from the actual page text. Prioritize malformed CAS/formula tokens, numeric/unit anomalies, surface limits, high-risk chemicals and rows noted as removed.
6. **Decision 250 forms, then Decisions 251 and 252:** confirm every fee, qualification, exception, effective date and transition period against exact text. Keep summary-only assertions quarantined unless the original page contains the operative wording.
7. **Currentness and source-use review:** separately check amendment/corrigendum/repeal status, legal-text reuse scope, and source-site terms. The Gazette comparison does not itself clear these gates.
8. **Counsel acceptance:** after the technical build, have qualified Egyptian labour/OSH counsel test the exact app and corpus version using the in-app acceptance plan. App sign-off does not replace row-level source matching.

## Hard stops

- Do not fill missing rows or unclear numbers from memory, chemical reference tables, or another country's exposure-limit schedule.
- Do not treat a secondary scan as official provenance, even if its printed page appears to match.
- Do not mark any candidate verified/current/approved merely because the PDF hash is known.
- Do not enable authoritative retrieval until the source match, currentness, source-use and required counsel gates are documented.
