# Versioned database migrations

**Status:** Initial migration framework; legacy startup DDL is not yet fully converted.

## Workflow

- Store forward-only SQL migrations in `migrations/NNNN_description.sql`.
- Use monotonically increasing, unique numeric versions and lowercase underscore names.
- Run `db_migrations.apply_migrations(connection, directory)` only after explicitly selecting the intended database and arranging a maintenance window / quiescent application.
- Each pending migration runs in its own `BEGIN IMMEDIATE` transaction. The schema change and its `schema_migrations` record commit together.
- Applied migration filenames and contents are immutable. The runner verifies SHA-256 checksums and fails closed if an applied file changes or disappears.
- Test migrations against a fresh database and a copy created by the prior release before deployment. Keep a verified backup and documented restore procedure.

## Current boundary

Application startup still contains legacy `CREATE TABLE` and conditional `ALTER TABLE` statements. The runner is a foundation for converting those operations incrementally; it does **not** yet mean every schema change is versioned. Migration `0001` adds the ownership-quarantine review index. Migration `0002` owns six operational indexes previously created inline during startup: case firm, member lookup, deadline lookup, document list, chunk-to-document lookup, and extraction-review lookup. Migration `0003` moves the remaining nine ordinary/partial indexes for login throttling, case-deletion audit, rate-limit cleanup, legal-version lookup/review, legal review history, and research conversation/message lookup out of the startup schema string. Migration `0004` moves `legal_version_relations` into versioned DDL; its prerequisite `legal_document_versions` table remains part of the legacy bootstrap. Startup still creates the other prerequisite tables/columns before applying migrations, so this is an incremental transition—not a complete DDL cutover.

This runner does not establish tenant routing, tenant isolation, backup/restore safety, or production readiness. Never run it against a production database without an approved backup, tested restore, migration review, and explicit target selection.


## Backup and restore safety checks

The CLI backup command uses unique temporary files rather than a shared `tmp.db`, validates the staged SQLite snapshot, writes encrypted output through a temporary file, and applies retention only after a completed backup. Restore authenticates/decrypts first, stages the payload in the destination directory, runs SQLite `quick_check`, and only then atomically replaces the destination. Failed validation must leave an existing destination untouched.

Run the regression suite with:

```bash
PYTHONPATH=. python tests/test_backup_restore_safety.py
```

These checks do not provide per-firm backup/restore while the application still uses a single configured database. The backup key must be stored separately from the backup files, and operators must rehearse restore against a disposable destination before any production recovery.


## Disposable-copy migration rehearsal

Before a deployment rehearsal, use the read-only source / disposable-copy helper:

```bash
PYTHONPATH=. python scripts/rehearse_database_migrations.py /path/to/protected-copy.sqlite3
```

The helper opens the source in read-only mode, checks SQLite integrity and foreign-key violations, copies it through SQLite's backup API into a temporary directory, applies pending versioned migrations only to that copy, then reports the resulting migration ledger and integrity checks. Exit status is 0 only when both integrity checks are clean and no foreign-key violations are found; status 1 means manual review is required, and status 2 means the rehearsal could not run.

This is a migration rehearsal aid, not a backup, not an authorization test, and not proof of tenant isolation. Use a protected representative copy, retain a separately verified backup, and review the report before any real migration.


## Startup DDL inventory

Before migrating remaining startup DDL, run:

```bash
PYTHONPATH=. python scripts/database_startup_ddl_inventory.py
```

The source-only report inventories the literal `SCHEMA` string, DDL statements outside that string (including conditional legacy `ALTER TABLE` operations), and each versioned migration. It does not open a database and is not proof of runtime behavior. Review dynamic SQL and test both fresh and legacy database copies before moving any table/FTS creation or conditional column changes into migrations.
