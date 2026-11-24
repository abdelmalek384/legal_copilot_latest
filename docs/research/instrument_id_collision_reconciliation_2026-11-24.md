# Research-register identifier reconciliation — 24 November 2026

## Purpose

A cross-file audit found reused identifiers in the national instrument register and priority full-text inventory. These were not harmless duplicate rows: the collisions caused different legal instruments to share keys across the classification and historical-version datasets. This reconciliation preserves existing references where possible and records every deliberate remap.

## Canonical identity decisions

### National instrument register

- Preserved EG-0395 through EG-0405 for the real-estate registration instruments already referenced by historical article-version events.
- Preserved EG-0406 through EG-0409 for the PPP and FRA instruments already used by the instrument-classification and full-text datasets:
  - EG-0406 — PM Decision 3660/2026 (PPP project data disclosure).
  - EG-0407 — FRA Decision 3195/2026 (insurance consulting experts).
  - EG-0408 — FRA Decision 3303/2026 (government insurance funds).
  - EG-0409 — FRA Decision 3132/2026 (credit and surety insurance).
- Added the missing EG-0407, EG-0408 and EG-0409 register rows from their existing inventory/classification records; EG-0406 was restored from the existing PM Decision 3660/2026 register row.
- Reassigned the five labour/worker-priority entries that had collided with EG-0406–EG-0410:
  - EG-0406 → EG-0515 — Law 90/2005.
  - EG-0407 → EG-0516 — Law 180/2008.
  - EG-0408 → EG-0517 — Law 125/2010.
  - EG-0409 → EG-0518 — PM Decision 2736/2010.
  - EG-0410 → EG-0519 — Ministerial Decision 290/2010.
- Reassigned the later state-property, public-business, water, biosafety and tax records that had reused EG-0395–EG-0410:
  - EG-0395 → EG-0520 — Law 170/2025.
  - EG-0396 → EG-0521 — Law 172/2025.
  - EG-0397 → EG-0522 — Law 203/1991.
  - EG-0398 → EG-0523 — PM Decision 1590/1991.
  - EG-0399 → EG-0524 — Law 185/2020.
  - EG-0400 → EG-0525 — PM Decision 948/2021.
  - EG-0401 → EG-0526 — Health Minister Decision 182/2025.
  - EG-0402 → EG-0527 — PM Decision 1315/2026.
  - EG-0403 → EG-0406 — PM Decision 3660/2026 (merged into the already canonical PPP identity; not a new ID).
  - EG-0404 → EG-0528 — Law 154/2026.
  - EG-0405 → EG-0529 — PM Decision 652/2026.
  - EG-0406 → EG-0530 — Presidential Decision 112/2026.
  - EG-0408 → EG-0531 — Law 76/2026.
  - EG-0409 → EG-0532 — Finance Minister Decision 396/2026.
  - EG-0410 → EG-0533 — Finance Minister Decision 342/2026.

### Full-text inventory

- Preserved FT-0112 through FT-0115 for their original earlier records.
- Reassigned the later duplicated inventory records:
  - FT-0112 → FT-0205 — PM Decision 3660/2026 (EG-0406).
  - FT-0113 → FT-0206 — FRA Decision 3195/2026 (EG-0407).
  - FT-0114 → FT-0207 — FRA Decision 3303/2026 (EG-0408).
  - FT-0115 → FT-0208 — FRA Decision 3132/2026 (EG-0409).
- Corrected the Law 76/2026 cross-reference in the public-finance research note from EG-0408 to EG-0531.

## Structural and referential checks after the changes

- National instrument register: 516 data rows, 12 columns, zero ragged rows, zero duplicate instrument IDs.
- Priority full-text inventory: 188 data rows, 11 columns, zero ragged rows, zero duplicate inventory IDs.
- Instrument classification: 412 data rows, 5 columns, zero ragged rows, zero duplicate IDs.
- Inventory → register: zero orphan acquisition IDs.
- Classification → register: zero orphan instrument IDs.
- Historical events → register: zero orphan instrument IDs after excluding the seven explicitly named `EG-CASE-*` fixture identifiers.
- Historical article-version event ledger: 350 data rows; 203 rows had been missing the `text_status` field. Added the explicit value `not separately recorded in source row` before the existing notes field, preserving all existing notes. All rows now have 12 columns. This is a structural normalization only; it does not upgrade source quality or legal verification.

## Trust and limitations

- No legal text, source tier, lawyer-review flag, or rights-clearance flag was upgraded by this reconciliation.
- All `lawyer_reviewed` and `rights_cleared` flags on the newly restored register entries remain false.
- The historical-event ledger still includes seven `EG-CASE-*` identifiers used by fixtures rather than the national instrument register; these are intentionally not treated as missing national instruments.
- These checks validate CSV shape, key uniqueness and cross-file referential integrity only. They do not establish legal correctness, currentness, completeness, source rights or retrieval quality.
