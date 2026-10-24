# Tenant database integrity preflight

This command performs a read-only check of an existing tenant database catalog and the SQLite files it maps to:

```bash
python scripts/tenant_database_preflight.py /absolute/path/to/control-plane.db /absolute/path/to/tenant-databases
```

Exit codes:

- `0`: no problems detected by these checks.
- `1`: one or more catalog, readiness, path, SQLite integrity, or foreign-key findings.
- `2`: missing inputs or an unreadable/invalid catalog.

The report is JSON and includes per-firm finding codes. The command does not create catalog tables, provision tenants, repair mappings, run migrations, or change database contents. It opens the catalog and tenant files with SQLite read-only mode.

Run it against an authorized copy or during a quiet maintenance window. The catalog and files may change after inspection, so the output is a point-in-time report rather than a lock on the inspected state.

## Scope and limits

The preflight checks that provisioned entries use the expected `tenant-<firm-id>-<random-hex>.sqlite3` naming format, map to unique regular files directly inside the configured storage root, and pass SQLite `quick_check` and `foreign_key_check`. It reports entries left in `provisioning` or `failed` state. Disabled tenants are not opened.

A clean report is **not** proof of tenant isolation. It does not inspect application authorization, SQL query scoping, shared legal corpus separation, file/object storage, backups, deployment configuration, or concurrent changes. It does not verify that the database schema is the expected application schema. Tenant routing must remain disabled until the authenticated identity/membership contract and full request-path integration are implemented and tested.