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

Application startup still contains legacy `CREATE TABLE` and conditional `ALTER TABLE` statements. The new runner is a foundation for converting those operations incrementally; it does **not** yet mean every schema change is versioned. The first migration adds a review index for the ownership quarantine table created by the existing startup initialization.

This runner does not establish tenant routing, tenant isolation, backup/restore safety, or production readiness. Never run it against a production database without an approved backup, tested restore, migration review, and explicit target selection.


## Backup and restore safety checks

The CLI backup command uses unique temporary files rather than a shared `tmp.db`, validates the staged SQLite snapshot, writes encrypted output through a temporary file, and applies retention only after a completed backup. Restore authenticates/decrypts first, stages the payload in the destination directory, runs SQLite `quick_check`, and only then atomically replaces the destination. Failed validation must leave an existing destination untouched.

Run the regression suite with:

```bash
PYTHONPATH=. python tests/test_backup_restore_safety.py
```

These checks do not provide per-firm backup/restore while the application still uses a single configured database. The backup key must be stored separately from the backup files, and operators must rehearse restore against a disposable destination before any production recovery.
