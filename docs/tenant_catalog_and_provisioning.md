# Trusted tenant catalog and database provisioning

**Status:** Infrastructure primitive; not connected to request routing.

## What this adds

`tenant_catalog.py` stores a control-plane mapping from a trusted positive integer firm ID to a generated, relative SQLite database filename. Provisioning uses an exclusive file create, restrictive POSIX mode where supported, a caller-supplied schema initializer, an integrity check, and an explicit catalog lifecycle status. Failed initialization cleans up the partial database and records a generic failure code. Resolution only returns existing, provisioned database files whose names match the generated pattern and remain inside the configured storage root.

## Security contract

- Callers must derive `firm_id` from authenticated identity and server-side membership. Never pass a request's query/body/header tenant ID directly to this module.
- Do not accept database paths, filenames, connection strings, or storage roots from clients.
- The control-plane catalog itself needs restricted filesystem/DB access, backup, monitoring, and tamper protection.
- A tenant database must be initialized with the complete, reviewed tenant schema. The module does not assume the current application's mixed tenant/shared-corpus schema is safe to copy into each firm database.
- Provisioning and catalog state changes must be wrapped by an admin-only audited workflow before production use.
- POSIX mode bits are defense in depth; deployment ACLs, encryption, host access controls, secret management, and backups remain necessary.

## Deliberate non-goals

This module is not wired into FastAPI's global `conn()`, user/session handling, or routes. Current authentication still has one `users.firm_id` field and the global-versus-firm membership contract is not approved. Shared legal corpus tables and mixed `chunks/chunks_fts` have not yet been separated. Do not onboard unrelated firms or claim database-per-firm isolation from this module alone.
