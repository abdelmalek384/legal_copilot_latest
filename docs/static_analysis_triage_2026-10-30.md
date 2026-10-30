# Static-analysis finding triage — 2026-10-30

This is a source-level triage record for the first successful CodeQL/Bandit CI run on PR #907. It is not an independent security assessment and must be revisited when the affected code changes.

## Bandit result

[Bandit CI run #41056226787](https://github.com/abdelmalek384/legal_copilot_latest/actions/runs/41056226787) completed successfully:

- **0 high-severity findings** (the configured CI blocker).
- **17 medium-severity findings**, all rule **B608** (hardcoded/dynamic SQL construction).
- No finding was suppressed or ignored by the workflow. Medium findings are printed in the CI log for review.

The B608 results are concentrated in the following code patterns:

| Location reported | Source of interpolated identifier/fragment | Initial triage |
|---|---|---|
| `app.py:776,787` | Table names iterated from literal tuples in the case-deletion cleanup routine; record values remain bound parameters | Expected fixed-identifier SQL; inspect any edits to the tuple before accepting |
| `app.py:3260` | `metadata_filter` is selected from a fixed internal branch for metadata-only documents; request values are still bound parameters | Fixed internal SQL fragment; verify `kind` validation remains closed-set |
| `app.py:4254` | Field name comes from a fixed tuple of editable case columns; field values are bound parameters | Expected fixed-column update; never interpolate request-supplied field names |
| `tools/audit_legal_corpus.py:17` | SQLite table name passed to `PRAGMA table_info`; callers use known registry table names | Schema-inspection helper; maintain fixed caller allowlist |
| `tools/audit_legal_corpus.py:173–178,389` | Optional `case_id IS NULL AND` scope is selected from a fixed schema-column-presence check; query data remains in SQL expressions | Fixed predicate fragment; do not derive it from user input |
| `tools/audit_legal_corpus.py:226–238` | Column names are selected only from `collection_permission` and `commercial_reuse_permission` when present in introspected schema | Fixed allowlist; never interpolate arbitrary column names |
| `tools/audit_legal_corpus.py:267` | Date columns selected from a literal allowlist and filtered by actual schema columns | Fixed allowlist; do not accept external column names |
| `tools/verify_s3_original_file_roundtrip.py:62` | Table names read from SQLite's own `sqlite_master` and double-quote escaped before use | Schema-derived identifiers with escaping; confirm the source remains the local database schema, never an external input |

### Required safeguards

1. Keep all untrusted values (search terms, IDs, names, tenant input, document metadata) as bound SQL parameters.
2. Keep every interpolated table/column/predicate name on a literal allowlist or derived exclusively from the local SQLite schema with correct identifier quoting.
3. Never interpolate a request parameter, uploaded filename, JSON key, source URL, or user-controlled document field as a SQL identifier.
4. If a future change makes any of these values externally controllable, treat the B608 alert as a real injection candidate and replace the construction with a safe allowlist/identifier-quoting helper.
5. Re-run Bandit and the SQL-injection regression suite after changes. Do not add broad `# nosec` suppressions.

This is a preliminary code-path assessment based on the current source. A reviewer must confirm each call site against the exact merge commit; the finding count alone is not a security clearance.

## CodeQL result

[CodeQL run #41056226787](https://github.com/abdelmalek384/legal_copilot_latest/actions/runs/41056226787) passed the Python and JavaScript/TypeScript analysis jobs and uploaded SARIF results. The successful workflow/upload is not evidence that the alert queue is empty. Repository Security → Code scanning alerts must be reviewed on the exact release candidate. Any high/critical alert is a release blocker until fixed or explicitly reviewed and risk-accepted under the production security process.

## Release status

- Static-analysis automation: implemented on PR #907; draft/open until merged.
- Bandit high-severity gate: passing on the cited PR merge-ref run.
- Bandit medium B608: preliminary source-level triage recorded above; not suppressed.
- CodeQL alerts: manual repository alert review still outstanding.
- Independent security assessment and runtime tenant-isolation testing: still required.
