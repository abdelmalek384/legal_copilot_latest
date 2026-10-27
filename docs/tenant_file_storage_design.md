# Tenant-scoped original document storage — design proposal

**Status:** Proposal only. Original upload binaries are currently not retained by the ingestion flow. Do not treat this document as an approved retention policy or as implemented storage.

## Goal and security boundary

Preserve the original bytes for each uploaded matter document so authorized lawyers can verify extraction, page references, OCR output, and later corrections. An original is private firm data: it must never be stored in the shared legal corpus or made addressable by a caller-controlled filesystem path or public URL.

The approved database architecture remains:

- Control plane: global identities, firm memberships, sessions, platform roles, and trusted firm-to-database catalog.
- Per-firm database: matter metadata, extracted text/chunks, review history, and opaque blob references.
- Shared legal corpus: public/official legal-reference data only.
- Per-firm binary storage: original matter files and, if approved, derived page images/previews.

## Recommended architecture

### Storage adapter and key namespace

Introduce a storage adapter with a small interface: stage an object, finalize it, open it for an authorized read, delete/quarantine it, and verify its digest. The adapter receives a trusted firm context resolved by the application; it must not accept a tenant ID or storage path from request payloads.

For local development, use a dedicated storage root separate from the database root. Derive each firm's namespace from the trusted catalog binding and an opaque generated object ID. For production, use a private encrypted volume or private object-storage bucket with server-side encryption/KMS, least-privilege service access, and no public object URLs. Keep original filenames as metadata only; never use them as path components.

Do not reuse `BACKUP_KEY` for document encryption. The production backend and key-management method must be chosen before implementing encryption; the storage adapter should allow the local and production implementations to differ without changing authorization logic.

### Tenant database metadata

Add a migration-managed per-firm blob metadata table (or equivalent schema) with fields such as:

- Opaque `blob_id` / object ID.
- Storage backend and opaque storage key.
- Original SHA-256 digest, byte size, and validated media type.
- Uploader identity and upload timestamp.
- Retention state, deletion timestamp, and legal-hold state if approved.
- Link to the matter document record.

The stored digest must be computed from the original bytes, not from extracted text. Keep extraction/chunk hashes separate. A missing blob must be reported as an integrity issue; do not silently substitute extracted text for the original.

### Atomic upload flow

1. Authenticate the user, resolve the active firm from trusted session/control-plane state, and authorize case membership before accepting or staging content.
2. Enforce request size and allowed media-type limits before extraction. Treat the submitted filename as untrusted display metadata.
3. Stream bytes to a temporary object inside the same firm's storage namespace; compute SHA-256 and byte size while writing.
4. Validate the staged object and perform extraction against the staged original. Preserve page markers and extraction provenance separately from the binary.
5. In one tenant-database transaction, write document metadata, blob metadata, chunks/FTS rows, and the required case event. Finalize/rename the object atomically where the backend supports it.
6. If database persistence or object finalization fails, roll back the transaction and delete/quarantine staged/final objects as appropriate. Because a filesystem/object store cannot participate in SQLite's transaction, use an explicit staging state plus a reconciliation job/report for crash windows; never claim perfect cross-system atomicity.
7. Make the object visible to download/review endpoints only after the metadata state is finalized. Require case authorization on every read and never return raw storage paths.

### Restore and backup integration

- Include original objects in the coordinated encrypted recovery bundle or use a documented, versioned object-store snapshot tied to the database recovery point.
- Include object keys, digests, sizes, firm binding, and counts in the manifest; verify all objects against the manifest before accepting a restore.
- Snapshot database and object storage under one coordinated quiescence window. A database-only backup is not a complete matter-document recovery point after originals are retained.
- Add tests for cross-firm object lookup denial, tampered/missing objects, orphaned metadata, orphaned staged objects, interrupted upload/finalization, backup/restore checksum validation, and deletion/retention behavior.

### Access, caching, and logging

- Use the same case-membership authorization as document metadata/chunks/reviews; firm administrators retain their existing authorized access.
- Do not expose direct public object URLs or caller-selected storage keys.
- Set non-cacheable headers on downloads and previews.
- Audit upload, read/download, retention change, legal-hold change, deletion, and restore actions without recording document content, secrets, or raw storage paths in general logs.
- Use restrictive filesystem permissions in local/staging environments and verify sidecar/temp-object handling.

## Decisions required before implementation

These are product/security decisions, not safe to infer from the database architecture alone:

1. **Retention:** how long originals and derived previews are retained; what happens on case closure, firm offboarding, user deletion, and legal hold; who can authorize permanent purge.
2. **Production backend:** encrypted local volume versus private object storage, and the target deployment platform.
3. **Key management:** provider KMS/managed encryption versus application-level envelope encryption; rotation and recovery requirements. Do not reuse the backup key.
4. **Download behavior:** whether all case members can download originals, whether previews are allowed, and whether downloads require an additional audit event.
5. **Limits and allowed formats:** maximum upload size, MIME/type allowlist, archive handling, malware scanning, and OCR/page-count limits.
6. **Recovery objectives:** whether object storage must meet the same RPO/RTO as the database and what consistency guarantees the deployment can provide.

## Acceptance gates

Do not enable original-binary retention for confidential matter data until:

- The decisions above are approved and documented.
- Tenant storage namespaces and path/object authorization have regression tests.
- Upload failure and crash-window reconciliation tests pass.
- Encrypted backup/restore includes originals and verifies their digests.
- Retention, deletion, legal-hold, and offboarding behavior is implemented and tested.
- The witnessed staging recovery drill and independent security review are complete.

This proposal narrows the design, but it does not implement storage, approve retention periods, or close the current production-readiness blocker.
