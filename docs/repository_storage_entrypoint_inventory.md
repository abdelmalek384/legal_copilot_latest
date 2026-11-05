# Repository storage entrypoint inventory

**Updated:** 2026-11-06  
**Status:** current architecture summary; not an exhaustive security audit.

## Supported runtime profiles

- **Control plane:** global identities, memberships, firm catalog and platform governance.
- **Per-firm database:** matter/case data, firm users, tasks, document metadata and firm-scoped audit events.
- **Shared legal corpus:** common legal-source registry, candidate metadata, reviewed legal texts and retrieval indexes.
- **Original-file storage:** separate tenant-scoped object storage and recovery archive, subject to the storage/recovery acceptance gates.

## Operational boundaries

- Runtime database selection is server-side and profile-bound; request data must never choose a database path.
- Legal-source ingestion writes to the shared legal-corpus profile and remains quarantined until source, rights, currentness and qualified-review gates pass.
- Firm data, shared legal material, control-plane records and original binaries must remain separate in backup, restore, authorization and audit handling.
- Production readiness still requires witnessed staging restore/rollback, live object-storage/retention acceptance, exhaustive route/query review and independent security/privacy review.

## Current references

- docs/tenant_isolation_inventory.md
- docs/database_recovery_runbook.md
- docs/tenant_file_storage_design.md
- docs/STATUS.md

The earlier static inventory is preserved at docs/archive/repository_storage_entrypoint_inventory.md for audit history.
