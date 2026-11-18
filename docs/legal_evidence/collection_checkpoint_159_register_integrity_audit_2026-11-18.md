# Research Agent 1 — checkpoint 159: acquisition and source-permission register integrity audit (18 November 2026)

## 1. Acquisition register validation

File: `data/research/egypt_initial_statute_acquisition_register_2026-11-17.csv`

A full parse of the current CSV confirms:

- Header columns: **12**.
- Non-header data rows: **241**.
- Unique instrument IDs: **241**.
- Duplicate instrument IDs: **0**.
- Malformed rows / wrong column counts: **0** (all 241 data rows have exactly 12 columns).
- Numeric ID gaps: **EG-0076, EG-0077, EG-0078, EG-0079**.
- Highest ID: **EG-0245**.
- `lawyer_reviewed=false`: **241/241**.
- `rights_cleared=false`: **241/241**.

EG-0245 initially lacked the two terminal flags during append; this was repaired and the entire register was re-parsed. All rows now conform to the 12-column schema.

The four missing IDs remain historical sequence gaps. They are not presumed to represent missing legal instruments and were not filled.

## 2. Source-permission register validation

File: `docs/source_permission_register.json`

- Source records: **63**.
- Unique source IDs: **63**.
- Duplicate source IDs: **0**.
- Every source record has both `collection_permission` and `commercial_reuse_permission` fields.
- Permission-state distribution:
  - **57** records: unknown collection / unknown commercial reuse.
  - **5** records: collection not allowed without explicit exception or licence; commercial reuse requires prior written permission.
  - **1** record: unknown collection / commercial reuse not allowed without explicit exception or licence.

These are source-specific assessments. No general reuse permission is inferred from official publication or public access.

## 3. Separate corpus measures

| Metric | Audited value |
|---|---:|
| Acquisition rows | **241** |
| Unique acquisition IDs | **241** |
| Duplicate acquisition IDs | **0** |
| Malformed acquisition rows | **0** |
| Source-permission records | **63** |
| Duplicate source IDs | **0** |
| Completed core unique article provisions | **1,370** |
| Additional searchable article-heading entries in Laws 114/142/68/70 | **200** |
| Lawyer-reviewed instruments | **0** |
| Rights-cleared instruments | **0** |

## 4. Completion estimate

- Core article-number extraction: **100%** for the three defined core statutes, subject to OCR/source-image and historical-version validation.
- Broader civil/property/contract corpus: **15% provisional**.
- Whole Egyptian legal corpus: **2% provisional**.

No percentage increase is justified by a register-integrity audit.

## 5. Next actions

1. Reconcile EG-0076–EG-0079 against repository history and prior acquisition snapshots; do not create speculative entries.
2. Maintain the 12-column schema and re-run duplicate/row-width checks after every acquisition-register update.
3. Maintain source-specific permission fields and never promote unknown rights to permitted without documentary evidence.
4. Continue Gazette acquisition, article extraction and historical versioning.

## 6. Verification and rights

This checkpoint is a data-integrity audit only. It is not legal verification, lawyer review, source authentication or rights clearance.
