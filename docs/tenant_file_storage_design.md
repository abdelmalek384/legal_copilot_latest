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

Migration `migrations/firm/0010_original_file_objects.sql` adds the per-firm `original_file_objects` table, firm-binding triggers, digest/size/state metadata, and a legal-hold deletion guard. Migration `migrations/firm/0011_original_file_hold_lifecycle.sql` adds mandatory release reasons, transition guards, immutable active-hold metadata, and database-triggered audit events. Uploader metadata and full retention/deletion lifecycle fields remain outstanding.

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

### Reconciliation and interrupted-upload recovery

- `original_file_reconciliation.py` performs a read-only inventory comparison between trusted tenant-database paths, `original_file_objects` metadata, and firm-scoped local object files.
- `tools/reconcile_original_file_storage.py` is the operator entry point. It resolves tenant database paths through the control-plane catalog, checks database firm bindings, hashes object bytes, and reports missing/corrupt objects, orphaned objects, unsafe symlinks, unknown namespaces, and interrupted staged/finalization windows.
- The command exits `0` + " when clean, `1` when findings exist, and `2` when it cannot safely complete. `--json` emits machine-readable findings. It does not delete or repair files.
- Run only with appropriate access to all firm databases and object storage. A production operator should quiesce writes first so a concurrent upload does not create transient findings. Review and resolve findings manually; do not auto-delete orphaned objects because they may be evidence under retention or legal hold.
- Example: `COPILOT_CONTROL_DB=... COPILOT_TENANT_DB_ROOT=... COPILOT_CORPUS_DB=... COPILOT_OBJECT_STORAGE_ROOT=... python tools/reconcile_original_file_storage.py --json`.

### Restore and backup integration

- **Implemented in development backup format v2:** the encrypted multi-database bundle includes original object bytes under firm-scoped opaque paths, and its manifest checksums cover the database snapshots and object files.
- Backup creation verifies each object's firm, state, byte size, and SHA-256 against tenant metadata. It fails closed for missing or tampered objects, unfinished staged metadata, and orphaned/unrecognized files in the object root.
- Restore verifies the object inventory against the restored tenant metadata and checks byte size and SHA-256 before publishing a new restore directory. The returned restore result includes an object_storage path that must be configured as the application object root.
- **Still required operationally:** pause application writes across all tenant databases and object storage before backup. The bundle uses an operator-supplied quiescence assertion; it does not create a distributed atomic snapshot by itself.
- **Still not production-ready:** the local filesystem adapter is the only implementation. Production object storage/KMS, automated reconciliation after interrupted uploads, restore drills, and production retention/legal-hold acceptance remain open. The firm-admin hold/release workflow is implemented and covered by integration tests in this branch.
- Existing tests cover bundle round-trip, object-byte integrity, firm-admin hold/release authorization, mandatory reasons, deletion blocking while held, and atomic audit events. Additional acceptance tests are still required for interrupted upload/finalization, retention/deletion, and a documented full recovery drill.

### Access, caching, and logging

- Use the same case-membership authorization as document metadata/chunks/reviews; firm administrators retain their existing authorized access.
- Do not expose direct public object URLs or caller-selected storage keys.
- Set non-cacheable headers on downloads and previews.
- Audit upload, read/download, retention change, legal-hold change, deletion, and restore actions without recording document content, secrets, or raw storage paths in general logs.
- Use restrictive filesystem permissions in local/staging environments and verify sidecar/temp-object handling.

## Decisions required before implementation

These are product/security decisions, not safe to infer from the database architecture alone:

1. **Retention:** the interim default remains no automatic permanent deletion. Firm admins can now set a hold after verifying original bytes and release it with a mandatory reason; database triggers validate transition metadata and insert the audit event in the same transaction. Metadata deletion and quarantine transitions are blocked while held. Authorized object deletion/purge, retention schedules, and firm offboarding behavior remain unimplemented.
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
- Legal-hold set/release behavior and deletion blocking while held are tested; complete retention, object deletion/purge, and offboarding behavior are still required.
- The witnessed staging recovery drill and independent security review are complete.

This is an initial end-to-end development implementation, not release completion. Do not enable it for confidential production matter data until the production object-store/KMS adapter, complete retention/deletion/offboarding lifecycle, object/database reconciliation, coordinated encrypted backup/restore, failure/crash-window tests, witnessed recovery drill, and independent security review are complete.
