# Tenant fleet schema migrations

The firm-per-database architecture needs an explicit deployment step for schema evolution across already-provisioned tenant databases. Application startup migrates the control plane and legal corpus; it must not opportunistically perform DDL against every tenant while serving requests.

`tools/migrate_tenant_fleet.py` provides a fleet-level plan/apply workflow. It is intentionally separate from request handling and requires a coordinated maintenance window.

## 1. Plan (read-only)

Run from the repository root with the same database paths configured for the deployment:

```bash
python tools/migrate_tenant_fleet.py \
  --control-db "$COPILOT_CONTROL_DB" \
  --tenant-root "$COPILOT_TENANT_DB_ROOT" \
  --migrations-root ./migrations
```

The plan lists eligible `provisioned` and `disabled` tenant databases, pending migration versions, and catalog rows excluded due to lifecycle state. It validates immutable control-plane and tenant profile bindings, exact catalog filename-to-firm association, file permissions, SQLite integrity, foreign keys, and migration history/checksums. A preflight failure blocks the entire run before schema changes.

## 2. Apply during a coordinated maintenance window

1. Stop all web workers, schedulers, and background workers that can access tenant databases.
2. Create or select a protected backup location outside both the tenant storage root and control-plane database.
3. Review the plan and approved migration change.
4. Run:

```bash
python tools/migrate_tenant_fleet.py \
  --control-db "$COPILOT_CONTROL_DB" \
  --tenant-root "$COPILOT_TENANT_DB_ROOT" \
  --migrations-root ./migrations \
  --backup-dir "$TENANT_MIGRATION_BACKUP_DIR" \
  --apply \
  --confirm-workers-stopped
```

The command re-preflights the fleet, snapshots every database that has pending migrations before it changes any schema, verifies each snapshot's integrity, and writes a private JSON run manifest into the backup directory. It then applies migrations sequentially. Each target is checked for file identity, profile binding, firm binding, integrity, and foreign-key integrity. A failure stops subsequent migrations; the tool does not automatically restore a partially migrated fleet.

## Release gate integration

When production control-plane and tenant-root paths are configured, `tools/production_release_gate.py` runs the read-only fleet plan. Production release is blocked if any eligible tenant has pending schema migrations, the fleet preflight cannot be completed safely, or unresolved catalog lifecycle rows are skipped. This prevents deploying code that expects a schema version the tenant fleet has not yet received. The release gate does not run migrations; use the explicit maintenance-window apply procedure above.

## Safety and recovery boundaries

- The backup directory and snapshots use restrictive permissions on POSIX systems.
- A tenant database is never created, renamed, adopted, deleted, or rebound by this tool.
- `provisioning`, `failed`, and other non-eligible catalog states are reported as skipped and require their lifecycle-specific recovery workflow.
- Disabled tenants with a valid catalog mapping are migrated too, so a future reactivation does not expose an outdated schema.
- If any migration fails after earlier databases have been updated, keep the maintenance window active. Use the manifest to identify the exact applied versions and snapshots; assess the migration's reversibility and restore only under a separately approved recovery plan.
- The confirmation flag is an operator assertion, not a process-level lock. Deployment orchestration must ensure all writers are actually stopped.
- This workflow does not replace live backup-restore drills, production object-storage/KMS acceptance, or independent security review.
