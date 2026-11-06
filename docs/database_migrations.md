# Versioned database migrations

**Status:** The versioned migration runner is used for the three approved separate-database profiles. The shared `COPILOT_DB` runtime was retired in PR #972 and is rejected in every environment. All supported installations use the three profile-separated paths and versioned profile migrations. No legacy database has been deployed or used, and no import/reconciliation is planned.

## Workflow

- Store forward-only SQL migrations in `migrations/NNNN_description.sql`.
- Use monotonically increasing, unique numeric versions and lowercase underscore names.
- Run `db_migrations.apply_migrations(connection, directory)` only after explicitly selecting the intended database and arranging a maintenance window / quiescent application.
- Each pending migration runs in its own `BEGIN IMMEDIATE` transaction. The schema change and its `schema_migrations` record commit together.
- Applied migration filenames and contents are immutable. The runner verifies SHA-256 checksums and fails closed if an applied file changes or disappears.
- Conditional legacy-column operations use `-- @add-column-if-missing TABLE COLUMN` immediately before the matching `ALTER TABLE TABLE ADD COLUMN COLUMN ...;` statement. The runner validates the directive against that statement and skips only the `ALTER` when the column already exists; the raw migration file remains checksum-protected.
- Test migrations against a fresh database and a copy created by the prior release before deployment. Keep a verified backup and documented restore procedure.

## Current boundary

Application startup still contains legacy `CREATE TABLE` and conditional `ALTER TABLE` statements. The runner is a foundation for converting those operations incrementally; it does **not** yet mean every schema change is versioned. Migration `0001` adds the ownership-quarantine review index. Migration `0002` owns six operational indexes previously created inline during startup: case firm, member lookup, deadline lookup, document list, chunk-to-document lookup, and extraction-review lookup. Migration `0003` moves the remaining nine ordinary/partial indexes for login throttling, case-deletion audit, rate-limit cleanup, legal-version lookup/review, legal review history, and research conversation/message lookup out of the startup schema string. Migration `0004` moves `legal_version_relations` into versioned DDL; its prerequisite `legal_document_versions` table remains part of the legacy bootstrap. Migration `0005` moves `security_audit_events` into versioned DDL; application routes write to it after `conn()` completes the migration run. Migration `0006` moves six independent tables (`auth_sessions`, `notes`, `fees`, `tasks`, `events`, and case-calendar `sessions`) into versioned DDL. Migration `0007` moves the `legal_sources` provenance registry; `legal_documents` remains in startup bootstrap because startup currently inspects and conditionally alters it before applying migrations. Migration `0008` moves FTS5 virtual table creation for `chunks_fts` into versioned DDL. Existing FTS indexes are preserved; migration 0008 does not rebuild missing or stale index contents, matching the previous startup behavior. Migration `0009` moves the default-firm seed into versioned DDL using `INSERT OR IGNORE`, preserving an existing firm 1 row and its name. Migration `0010` moves non-prerequisite legacy column additions into a checksum-protected conditional-DDL directive and performs the existing document ownership backfill after `docs.firm_id` is guaranteed. Columns required by earlier immutable index migrations remain in the startup compatibility bootstrap. These migrations preserve existing rows. Startup still creates prerequisite tables and performs legacy conditional column upgrades before applying migrations, so this is an incremental transition—not a complete DDL cutover.

This runner does not establish tenant routing, tenant isolation, backup/restore safety, or production readiness. Never run it against a production database without an approved backup, tested restore, migration review, and explicit target selection.


## Backup and restore safety checks

The CLI backup command uses unique temporary files rather than a shared `tmp.db`, validates the staged SQLite snapshot, writes encrypted output through a temporary file, and applies retention only after a completed backup. Restore authenticates/decrypts first, stages the payload in the destination directory, runs SQLite `quick_check`, and only then atomically replaces the destination. Failed validation must leave an existing destination untouched.

Run the regression suite with:

```bash
PYTHONPATH=. python tests/test_backup_restore_safety.py
```

The legacy single-file `backup` and `restore` commands now fail closed; this test verifies they do not create output or replace a destination. Actual backup/restore integrity coverage is provided by `tests/test_database_backup_bundle.py`. The backup key must be stored separately from backup files, and operators must complete a witnessed staging restore/rollback drill before production recovery.


## Disposable-copy migration rehearsal

Before a deployment rehearsal, use the read-only source / disposable-copy helper:

```bash
PYTHONPATH=. python scripts/rehearse_database_migrations.py /path/to/protected-copy.sqlite3
```

The helper opens the source in read-only mode, checks SQLite integrity and foreign-key violations, copies it through SQLite's backup API into a temporary directory, applies pending versioned migrations only to that copy, then reports the resulting migration ledger and integrity checks. Exit status is 0 only when both integrity checks are clean and no foreign-key violations are found; status 1 means manual review is required, and status 2 means the rehearsal could not run.

This is a migration rehearsal aid, not a backup, not an authorization test, and not proof of tenant isolation. Use a protected representative copy, retain a separately verified backup, and review the report before any real migration.


## Migration rehearsal data-preservation checks

The disposable-copy rehearsal records row counts for tables already present in the source database and compares them with the staged database after migrations. If an existing table disappears or its row count decreases, the rehearsal returns `review_required` and lists the table and before/after counts. This is a guardrail against accidental deletion, not proof that row values are unchanged: a migration that overwrites rows while preserving the count still requires schema-specific validation and review.

## Read-only FTS consistency preflight

Before rebuilding or replacing the FTS index, run the read-only audit against a protected database copy:

```bash
PYTHONPATH=. python scripts/chunks_fts_preflight.py /path/to/protected-copy.sqlite3
```

The audit opens the source in SQLite read-only mode and compares chunk row IDs with FTS row IDs, detects missing/orphaned rows, and checks indexed text against the application's current tokenization. Exit status is 0 when no anomalies are detected, 1 when review is required, and 2 when the audit cannot run. It does not rebuild the index or prove that legal content itself is complete/correct. Review findings and rehearse any repair on a disposable copy before applying it to an operational database.


## Rebuild FTS only on a new database copy

When `scripts/chunks_fts_preflight.py` reports missing, orphaned, or stale FTS rows, prepare a rebuilt index on a new copy without writing to the source:

```bash
PYTHONPATH=. python scripts/rebuild_chunks_fts_copy.py /path/to/source.sqlite3 /path/to/new-rebuilt-copy.sqlite3
```

The output path must not exist; the utility refuses to overwrite it. It copies the source through SQLite's backup API, recreates `chunks_fts` on the output copy, repopulates it from `chunks.text` using the application's canonical tokenizer, and checks SQLite integrity, foreign keys, chunk counts, and FTS consistency. It deletes a failed partial output rather than leaving it looking like a successful rebuild. A successful copy is a review artifact, not an instruction to replace a live database; replacement requires an independent backup, review, and tested restore/deployment plan.

## Startup DDL inventory

Before migrating remaining startup DDL, run:

```bash
PYTHONPATH=. python scripts/database_startup_ddl_inventory.py
```

The source-only report inventories the literal `SCHEMA` string, DDL statements outside that string (including conditional legacy `ALTER TABLE` operations), and each versioned migration. It does not open a database and is not proof of runtime behavior. Review dynamic SQL and test both fresh and legacy database copies before moving any table/FTS creation or conditional column changes into migrations.
