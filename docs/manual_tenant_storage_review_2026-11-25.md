# Manual tenant-storage source review (2026-11-25)

**Scope:** static review of `tenant_storage.py` and the documented tenant-isolation/storage acceptance boundaries. No runtime, concurrency, filesystem adversarial, or tenant-route tests were run. This is a source review—not a penetration test.

## Reviewed implementation protections

- Tenant database paths are resolved through the trusted control-plane catalog; callers must provide a trusted firm ID.
- The router revalidates the catalog on each request and revokes a thread-cached connection on catalog failure or invalid resolution.
- It rejects symlinked path components, non-regular database files, permissive POSIX file/sidecar permissions, and symlink/non-regular sidecars.
- It checks cached connection path and captured path inode identity, WAL mode, foreign-key enforcement, immutable schema-profile guards, and immutable firm-binding guards.
- It performs post-open pathname/sidecar checks to detect changes during the open window.
- This source review confirms these checks exist in source; it does not prove they withstand adversarial concurrency.

## Residual risk: pathname-based open identity

The router captures a file identity using `path.stat()`, then opens SQLite using the pathname, and subsequently re-stats the pathname. Those pathname checks do not directly establish the identity of the file descriptor SQLite actually opened. A sufficiently privileged or concurrent local filesystem actor could potentially race pathname replacement around open; the post-open path check is a useful detection control but is not descriptor-to-path identity proof.

**Disposition:** recorded as a residual local-filesystem TOCTOU risk requiring focused adversarial testing and design review before claiming protection against a concurrent local directory writer. Do not attempt production use against an attacker-controlled tenant storage root. This report does not assert an exploitable cross-firm route or a demonstrated attack.

## Additional acceptance gaps reaffirmed

- Full request-route authorization and cross-firm behavior tests have not been executed in this environment.
- Live S3/KMS/IAM and storage lifecycle acceptance are outstanding.
- Backup/restore and recovery must be witnessed and operationally recorded.
- Runtime testing is blocked/unavailable; no CI run was requested or attempted for this review.

## Recommended next technical work

1. Add a dedicated concurrency/path-replacement test harness that records which file is actually opened and probes symlink, rename, and sidecar races in a disposable directory.
2. Evaluate a descriptor-oriented open strategy or stronger storage-root ownership/permissions constraints to reduce reliance on pathname identity checks; document platform limitations.
3. Keep release and tenant onboarding blocked until isolation and lifecycle evidence is completed.

## Evidence record

- Source inspected: `tenant_storage.py` on `main` during manual review.
- No tests executed.
- No production data or real client files involved.
