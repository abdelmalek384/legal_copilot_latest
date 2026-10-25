# Tenant database integrity preflight

This command performs a read-only check of an existing tenant database catalog and the SQLite files it maps to:

```bash
python scripts/tenant_database_preflight.py /absolute/path/to/control-plane.db /absolute/path/to/tenant-databases
```

Exit codes:

- `0`: no problems detected by these checks.
- `1`: one or more catalog, readiness, path, schema-profile, firm-binding, SQLite integrity, or foreign-key findings.
- `2`: missing inputs or an unreadable/invalid catalog.

The report is JSON and includes per-firm finding codes. The command does not create catalog tables, provision tenants, repair mappings, run migrations, or change database contents. It opens the catalog and tenant files with SQLite read-only mode.

Run it against an authorized copy or during a quiet maintenance window. The catalog and files may change after inspection, so the output is a point-in-time report rather than a lock on the inspected state.

## Scope and limits

The preflight checks that provisioned entries use the expected `tenant-<firm-id>-<random-hex>.sqlite3` naming format, map to unique regular files directly inside the configured storage root, and pass SQLite `quick_check` and `foreign_key_check`. It verifies the catalog itself has the immutable `control_plane` profile marker and compares the catalog's `schema_migrations` ledger against the trusted control-plane migration files. For each provisioned tenant it checks the `database_profile` marker is `firm`, the embedded `tenant_database_binding.firm_id` matches the catalog firm ID, and the named update/delete triggers actually reject mutation rather than merely existing. It also compares each tenant's `schema_migrations` ledger against the trusted firm-profile migration files, reporting missing ledgers, missing/unexpected versions, and name/checksum drift without applying or repairing migrations. It reports entries left in `provisioning` or `failed` state. Disabled tenants are not opened.

A clean report is **not** proof of tenant isolation. It does not inspect application authorization, SQL query scoping, shared legal corpus separation, file/object storage, backups, deployment configuration, or concurrent changes. The migration-ledger comparison verifies recorded versions and checksums against the repository's firm-profile migration set; it does not prove every runtime query is schema-compatible or that the tenant has the correct data classification. Tenant routing must remain disabled until the authenticated identity/membership contract and full request-path integration are implemented and tested.