# Manual tenant-storage source review — 25 November 2026

**Scope:** static review of tenant catalog, SQLite connection routing, and the read-only tenant database preflight after the hard-link changes. This is not a penetration test, runtime acceptance, or proof of race-free filesystem access.

## Controls now present on main

- Tenant database catalog entries remain bound to a strict firm-ID filename and an immutable firm binding stored inside the tenant database.
- The tenant catalog checks the database leaf with lstat, requires a regular file with exactly one hard link, and rejects symbolic links and special files.
- Provisioning uses exclusive file creation, checks the opened descriptor with fstat, and rechecks the database leaf before publishing the catalog row as provisioned.
- The tenant SQLite router checks database path identity, permissions, WAL mode, foreign-key enforcement, immutable schema-profile/firm-binding guards, and SQLite sidecars.
- Existing -wal, -shm, and -journal sidecars are inspected with lstat and must be regular single-link files with restrictive POSIX permissions. Unsafe metadata revokes the cached connection.
- After SQLite opens, the router rechecks the database and sidecars. A hard-link alias or metadata failure closes/revokes the new connection rather than caching it.
- The read-only preflight reports hard-linked catalog databases, tenant databases, and sidecars; it does not open tenant databases whose metadata is unsafe.

## Residual risk: pathname-based SQLite open

The router still resolves and checks a pathname before SQLite opens that pathname, then performs post-open pathname checks. These checks improve detection but do not prove that the SQLite file descriptor is the same inode that was inspected before open. A sufficiently privileged or concurrent local process able to modify the tenant storage directory may still race pathname operations.

**Disposition:** do not claim race-free filesystem isolation. Keep the tenant storage root writable only by the application service account and administrators. Do not allow firm users, unrelated processes, or untrusted jobs to write there. The current hard-link and post-open checks are defense in depth, not a replacement for directory-descriptor-relative/no-follow open semantics or an equivalent platform-specific design.

## Runtime and operational evidence still required

- Run tests/test_tenant_catalog.py, tests/test_tenant_storage.py, and tests/test_tenant_database_preflight.py on the supported Python 3.12 runtime.
- Run adversarial symlink, rename, hard-link, and SQLite sidecar race cases on the actual deployment filesystem.
- Run the two-firm direct-ID, search, original-download, export, and database-routing denial matrix.
- Confirm the tenant root owner, group, ACLs, mount options, and backup/restore handling on the intended host.
- Do not use production client data for these exercises.

## Evidence boundary

- Source changes and regression tests are merged in PR #2021 (tenant DB/sidecar hard-link protections) and PR #2022 (read-only preflight hard-link reporting).
- Repository tests were not executed in this work session. Isolated helper checks reported by the source PRs are not repository test passes.
- No local attacker exploit, concurrency acceptance, browser test, or production/staging rehearsal is claimed.

**Release disposition:** tenant filesystem hardening is improved, but tenant isolation remains unaccepted and the lawyer pilot remains NOT READY.
