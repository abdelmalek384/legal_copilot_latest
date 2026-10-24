# DB-05 — profile-aware migration harness

**Status:** Infrastructure primitive with tests; not wired into application startup or tenant routing.

## What this adds

`schema_profiles.py` supports three explicit SQLite database profiles: `control_plane`, `firm`, and `legal_corpus`. A database receives an immutable `database_profile` marker. The migration runner applies only the selected profile's migration directory, and refuses to reuse a database bound to another profile.

The caller must supply trusted deployment configuration and an existing migration root containing the selected profile directory. Profile names are allowlisted; callers cannot pass arbitrary paths. Versioned SQL remains subject to the existing checksum-verified `db_migrations.py` runner.

## What it does not add

- It does not create the actual production schemas for the three profiles.
- It does not split existing `app.py` tables or mixed `chunks/chunks_fts`.
- It does not select tenant databases from authenticated requests.
- It does not approve the proposed global identity/membership model.
- It does not migrate data, create firm-specific backups, or prove isolation.

Do not point this harness at production until each profile has a reviewed, complete migration set and deployment owners approve the identity, ownership, retention and recovery contracts.

## Tests and next gate

Tests cover profile allowlisting, profile mismatch denial, profile-specific migration selection, idempotent re-entry, missing profile directories, and failed migration rollback. Next: implement and review the initial schema migrations for each profile, using the ownership map and schema-boundary contract; then test a dry-run migration against a protected database copy. Runtime routing remains blocked until those schemas and identity semantics are approved.
