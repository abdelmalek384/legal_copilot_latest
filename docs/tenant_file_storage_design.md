# Tenant-scoped original document storage — design proposal

**Status:** Partially implemented in PR #671; not production-ready. The branch adds a local development adapter, firm-scoped metadata migration, upload retention and audited authorized downloads in separate-database mode. This is not a production object-store/KMS integration, and restore/retention acceptance gates remain open. Do not treat it as production-ready or as a complete retention policy.

## Goal and security boundary

Preserve the original bytes for each uploaded matter document so authorized lawyers can verify extraction, page references, OCR output, and later corrections. An original is private firm data: it must never be stored in the shared legal corpus or made addressable by a caller-controlled filesystem path or public URL.

The approved database architecture remains:

- Control plane: global identities, firm memberships, sessions, platform roles, and trusted firm-to-database catalog.
- Per-firm database: matter metadata, extracted text/chunks, review history, and opaque blob references.
- Shared legal corpus: public/official legal-reference data only.
- Per-firm binary storage: original matter files and, if approved, derived page images/previews.

## Recommended architecture

### Storage adapter and key namespace

The initial adapter interface is implemented in `original_file_storage.py`: stage an object, finalize it, open it for an authorized read, delete it, and verify its digest. The local adapter is development-only and uses restrictive permissions, opaque IDs, symlink rejection, size limits, and non-overwriting finalization. The adapter receives a trusted firm context resolved by the application; it must not accept a tenant ID or storage path from request payloads.

For local development, use a dedicated storage root separate from the database root. Derive each firm's namespace from the trusted catalog binding and an opaque generated object ID. For production, use a private encrypted volume or private object-storage bucket with server-side encryption/KMS, least-privilege service access, and no public object URLs. Keep original filenames as metadata only; never use them as path components.

Do not reuse `BACKUP_KEY` for document encryption. The production backend and key-management method must be chosen before implementing encryption; the storage adapter should allow the local and production implementations to differ without changing authorization logic.

### Tenant database metadata

Migration `migrations/firm/0010_original_file_objects.sql` adds the per-firm `original_file_objects` table, firm-binding triggers, digest/size/state metadata, and a legal-hold deletion guard. Remaining schema work includes audited hold lifecycle transitions, uploader metadata, and retention/deletion lifecycle fields.

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
5. The current separate-database upload path stages the original, writes document/blob metadata, chunks/FTS rows and the case event in a tenant transaction, finalizes the object, then marks metadata ready before commit. This narrows the failure window but cannot provide cross-system atomicity.
6. If database persistence or object finalization fails, roll back the transaction and delete/quarantine staged/final objects as appropriate. Because a filesystem/object store cannot participate in SQLite's transaction, use an explicit staging state plus a reconciliation job/report for crash windows; never claim perfect cross-system atomicity.
7. The current download endpoint requires case authorization, serves only ready metadata, verifies size and SHA-256, audits before release, and sends no-store headers. Raw storage paths are not returned.

### Restore and backup integration

- **Not yet implemented:** include original objects in the coordinated encrypted recovery bundle or use a documented, versioned object-store snapshot tied to the database recovery point.
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

1. **Retention:** the interim approved default is no automatic permanent deletion; explicit authorized deletion plus legal-hold override. Implemented hold metadata currently blocks metadata deletion but does not yet implement the complete audited hold/release/purge workflow or firm offboarding behavior.
2. **Production backend:** private S3-compatible object storage is the approved direction, with the provider kept configurable. Only the local development adapter exists; production fails closed.
3. **Key management:** managed KMS with firm-scoped access controls is the approved direction, but provider configuration, encryption policy, rotation and recovery integration remain unimplemented. Do not reuse the backup key.
4. **Download behavior:** approved default is case-authorized, audited downloads with no public URLs. The initial endpoint implements this for ready originals; role-specific policy review remains.
5. **Limits and allowed formats:** the current adapter/upload flow enforces a 15 MB cap; a comprehensive media-type allowlist, malware scanning and robust archive/page-count defenses remain open.
6. **Recovery objectives:** originals must be recoverable consistently with firm DB metadata; coordinated backup/restore and measured RPO/RTO remain open.

## Acceptance gates

Do not enable original-binary retention for confidential matter data until:

- The decisions above are approved and documented.
- Tenant storage namespaces and path/object authorization have regression tests.
- Upload failure and crash-window reconciliation tests pass.
- Encrypted backup/restore includes originals and verifies their digests.
- Retention, deletion, legal-hold, and offboarding behavior is implemented and tested.
- The witnessed staging recovery drill and independent security review are complete.

This is an initial end-to-end development implementation, not release completion. Do not enable it for confidential production matter data until the production object-store/KMS adapter, audited retention and legal-hold lifecycle, object/database reconciliation, coordinated encrypted backup/restore, failure/crash-window tests, witnessed recovery drill, and independent security review are complete.
