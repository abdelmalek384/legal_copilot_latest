# Tenant-scoped original document storage — design proposal

**Status:** Partially implemented in PR #671; not production-ready. The branch now includes a local development adapter and an S3-compatible adapter that requests SSE-KMS, plus firm-scoped metadata and audited authorized downloads. The S3 adapter has mocked-client regression tests, but the operational reconciler, staged-object recovery, encrypted backup/restore, deletion drills, bucket policy, KMS policy, and real-provider acceptance have not been completed. Application production uploads intentionally remain fail-closed until those paths support the same backend and pass witnessed recovery tests. This is not a complete retention policy.

## Goal and security boundary

Preserve the original bytes for each uploaded matter document so authorized lawyers can verify extraction, page references, OCR output, and later corrections. An original is private firm data: it must never be stored in the shared legal corpus or made addressable by a caller-controlled filesystem path or public URL.

The approved database architecture remains:

- Control plane: global identities, firm memberships, sessions, platform roles, and trusted firm-to-database catalog.
- Per-firm database: matter metadata, extracted text/chunks, review history, and opaque blob references.
- Shared legal corpus: public/official legal-reference data only.
- Per-firm binary storage: original matter files and, if approved, derived page images/previews.

## Recommended architecture

### Storage adapter and key namespace

The local adapter interface is implemented in `original_file_storage.py`, and the S3-compatible adapter in `s3_original_file_storage.py` provides stage/finalize/open/delete/integrity operations. The S3 adapter requires a dedicated private bucket and managed KMS key ID, resolves that identifier through KMS `DescribeKey`, and accepts object metadata only when S3 reports the matching canonical key ID or ARN (not merely any KMS key). The application, backup, reconciliation, and recovery runtime roles therefore need permission to describe the configured key in addition to the required object and encryption permissions. The read-only storage preflight also resolves the bucket's default-encryption key identifier before comparing canonical key ARNs, so a configured alias or key ID is checked by identity rather than string spelling. The adapter uses firm-namespaced opaque keys, conditional creation/copy, and SSE-KMS request parameters. Inventory checks cover the reserved `firms/` prefix, so do not share this bucket with unrelated applications or data. It never creates public URLs. The local adapter is development-only and uses restrictive permissions, opaque IDs, symlink rejection, size limits, and non-overwriting finalization. Both adapters receive a firm ID resolved from trusted server-side context, never from request payloads.

For local development, use a dedicated storage root separate from the database root. Derive each firm's namespace from the trusted catalog binding and an opaque generated object ID. For production, use a private encrypted volume or private object-storage bucket with server-side encryption/KMS, least-privilege service access, and no public object URLs. Keep original filenames as metadata only; never use them as path components.

Do not reuse `BACKUP_KEY` for document encryption. S3 backend configuration uses `COPILOT_S3_BUCKET`, `COPILOT_S3_REGION`, `COPILOT_S3_KMS_KEY_ID`, and optional `COPILOT_S3_ENDPOINT_URL`; the AWS SDK uses its standard credential chain. A successful API request is not proof that bucket policy, KMS grants, retention/versioning, or provider-specific conditional writes are correctly configured. Those settings require independent review and live staging tests. Production remains disabled until reconciliation, recovery, encrypted backup/restore, and deletion are tested against S3 end to end.

**Unresolved storage architecture conflict (release blocker):** `tools/validate_s3_original_file_storage.py` requires bucket versioning `Enabled` for recovery and incident response, while `S3PrivateObjectStore.purge_unversioned()` refuses both `Enabled` and `Suspended` and permits only a confirmed never-versioned bucket. One bucket cannot satisfy both requirements. The read-only preflight now reports these as separate, mutually exclusive checks and never treats either configuration as full production acceptance. Before deployment, the accountable storage/security owner must choose either (a) separate versioned recovery and never-versioned purge buckets with independently reviewed replication/restore and retention controls, or (b) a version-aware purge implementation that enumerates and conditionally deletes every retained version and delete marker under the approved retention policy. Do not disable versioning or enable purge to bypass this unresolved decision.

### Tenant database metadata

Migration `migrations/firm/0010_original_file_objects.sql` adds the per-firm `original_file_objects` table, firm-binding triggers, digest/size/state metadata, and a legal-hold deletion guard. Migration `migrations/firm/0011_original_file_hold_lifecycle.sql` adds mandatory release reasons, transition guards, immutable active-hold metadata, and database-triggered audit events. Migration `migrations/firm/0012_original_file_hold_event_ledger.sql` adds an immutable per-firm event ledger preserving each set/release reason, actor, and timestamp. A firm-admin-only history endpoint exposes these records for an authorized matter. Uploader metadata and full retention/deletion lifecycle fields remain outstanding.

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
- `tools/reconcile_s3_original_file_storage.py` performs a read-only comparison between the reserved S3 originals namespace and trusted tenant metadata; it reports missing, corrupt, staged, orphaned, and backend-mismatch findings without mutation.
- `tools/validate_s3_original_file_storage.py --json` checks bucket access, all four public-access-block controls, bucket-owner-enforced ACL disablement, versioning, default SSE-KMS encryption, and the configured customer-managed KMS key. It is read-only and always reports `production_ready: false`; IAM/bucket-policy review, firm isolation, key rotation, and live recovery drills remain required.
- The command exits `0` when clean, `1` when findings exist, and `2` when it cannot safely complete. `--json` emits machine-readable findings. It does not delete or repair files.
- `tools/recover_staged_original_files.py` adds a separate, conservative recovery operation for upload crash windows. It only advances metadata to `ready` when exactly one staged/final object exists and its bytes match the recorded digest and size. By default it is a dry run; mutations require both `--apply --quiesced`. It never deletes orphaned, duplicate, or corrupt objects. Local filesystem recovery is disabled in production; S3 recovery uses the configured S3 adapter and still requires a quiesced, reviewed maintenance window for mutations.
- Run only with appropriate access to all firm databases and object storage. A production operator should quiesce writes first so a concurrent upload does not create transient findings. Review and resolve findings manually; do not auto-delete orphaned objects because they may be evidence under retention or legal hold.
- Example: `COPILOT_CONTROL_DB=... COPILOT_TENANT_DB_ROOT=... COPILOT_CORPUS_DB=... COPILOT_OBJECT_STORAGE_ROOT=... python tools/reconcile_original_file_storage.py --json`.

### Restore and backup integration

- **Implemented in development backup format v2:** the encrypted multi-database bundle includes original object bytes under firm-scoped opaque paths, and its manifest checksums cover the database snapshots and object files.
- Backup creation verifies each object's firm, state, byte size, and SHA-256 against tenant metadata. It fails closed for missing or tampered objects, unfinished staged metadata, and orphaned/unrecognized files in the object root.
- Restore verifies the object inventory against the restored tenant metadata and checks byte size and SHA-256 before publishing a new restore directory. For S3 deployments, `tools/import_restored_originals_to_s3.py --restore-root PATH` performs a dry-run by default; use `--apply` only after reviewing the target bucket, then run `tools/reconcile_s3_original_file_storage.py --json` before considering the restored tenant databases for activation. The importer refuses restore roots overlapping configured live database paths and updates only the isolated restored tenant databases.
- `tools/run_database_recovery_drill.py` restores an encrypted bundle into a private temporary directory, checks SQLite integrity and foreign keys across all restored databases, reconciles original-file bytes, initializes the runtime, and exercises routing for each active firm with an active member. Run it on a protected maintenance/staging host with `COPILOT_BACKUP_FERNET_KEY` set; it refuses to run inside production application mode.
- `tools/firm_offboarding_preflight.py --firm-id N --json` is read-only and checks disabled firm/catalog state, active memberships, SQLite integrity/foreign keys, legal holds, staged/quarantined records, and original-byte reconciliation. A clear result is a gate for policy review, not deletion authorization. For S3 deployments, `COPILOT_OBJECT_STORAGE_BACKEND=s3 python tools/firm_offboarding_s3_preflight.py --firm-id N --json` performs the corresponding read-only catalog/database/S3 reconciliation and reads bucket versioning state; enabled or suspended versioning blocks preflight until an approved retention/version policy exists. This command never deletes objects and never authorizes production purge.
- `tools/purge_approved_original_files.py --firm-id N --operator-user-id ID --apply --quiesced` executes only approved requests, requires an active platform admin distinct from requester and approver, and runs only against disabled firms using the local development backend. Use dry-run mode first. If a purge is interrupted after file unlink but before database commit, the tool reports manual review instead of guessing that deletion succeeded.
- The purge operation repeats the trusted-catalog, active platform-admin, disabled-firm/catalog, revoked-membership, and clean-preflight checks. These guards are enforced inside the callable operation as well as the CLI.
- The recovery drill creates temporary plaintext databases. Temporary cleanup is not guaranteed secure erasure on SSDs or copy-on-write filesystems; use a trusted host and protected temporary storage.
- **Still required operationally:** pause application writes across all tenant databases and object storage before backup. The bundle uses an operator-supplied quiescence assertion; it does not create a distributed atomic snapshot by itself.
- **Still not production-ready:** the S3 adapter now requests SSE-KMS and is covered by mocked-client tests; read-only S3 reconciliation, staged-object recovery, encrypted backup staging, and a restore-to-S3 importer are implemented. No live provider, bucket policy, KMS policy, key rotation, or real cloud conditional-write behavior has been verified. Production application uploads remain fail-closed pending live-provider acceptance and a witnessed end-to-end restore/deletion/recovery drill. The isolated restore-drill CLI is implemented; a witnessed operational drill is still required. The firm-admin hold/release workflow is implemented and covered by integration tests in this branch.
- Tests cover bundle round-trip, object-byte integrity, firm-admin hold/release authorization, immutable hold/deletion event ledgers, two-admin deletion approval, legal-hold cancellation, disabled-firm purge gates, retained purge tombstones, and backup/restore of tombstones. Remaining acceptance work includes injected crash testing around filesystem unlink/database commit, full CLI-level maintenance tests, and a witnessed operational recovery drill.

### Access, caching, and logging

- Use the same case-membership authorization as document metadata/chunks/reviews; firm administrators retain their existing authorized access.
- Do not expose direct public object URLs or caller-selected storage keys.
- Set non-cacheable headers on downloads and previews.
- Audit upload, read/download, retention change, legal-hold change, deletion, and restore actions without recording document content, secrets, or raw storage paths in general logs.
- Use restrictive filesystem permissions in local/staging environments and verify sidecar/temp-object handling.

## Policy decisions and remaining implementation

These are product/security decisions, not safe to infer from the database architecture alone:

1. **Retention:** the interim default remains no automatic permanent deletion. Firm admins can now set a hold after verifying original bytes and release it with a mandatory reason; database triggers validate transition metadata and insert both the security audit event and immutable hold-history event in the same transaction. The event ledger retains action, reason, actor, and timestamp, and rejects update/delete attempts. Metadata deletion and quarantine transitions are blocked while held. `tools/firm_offboarding_preflight.py` now provides a read-only gate that requires disabled firm/catalog state, no active memberships, clean database integrity, verified original bytes, and no active legal holds or unresolved staged/quarantined objects. A clear result is not authorization to delete. The application supports a firm-admin deletion request and approval by a different firm admin. The S3-aware production purge path is now implemented in `s3_original_file_storage.py`, `tools/purge_approved_s3_original_files.py`, and the shared approval/state-machine logic in `tools/purge_approved_original_files.py`; the S3-aware offboarding preflight reconciles tenant metadata and object state. Physical purge deliberately refuses buckets whose versioning is Enabled, Suspended, unknown, or otherwise ambiguous; it verifies the final object's SHA-256/size and configured KMS identity, refuses a remaining staged copy, deletes the finalized key, and verifies post-delete absence and unchanged never-versioned status. The command is gated by the current database acceptance manifest and exact storage-target fingerprint, requires production mode for production apply, and requires explicit `--quiesced`. **This is implemented code, not live-provider acceptance or authorization to delete.** The `--quiesced` flag is only an operator assertion; it does not lock S3 or prevent concurrent writers. Do not run production deletion until an independent reviewer verifies an IAM-enforced no-writer control across the integrity-check/delete interval, the live bucket and KMS/IAM policies, approved retention/export/deletion rules, and the witnessed restore/rollback/staged-upload/deletion-recovery drills. Never manually delete S3 objects or treat a clear preflight as legal authorization. The local development adapter remains available for non-production use.
2. **Production backend:** private S3-compatible object storage is the approved direction, with the provider kept configurable. The S3 adapter and operational command foundations are implemented on this branch, but production application access remains fail-closed until live-provider and full lifecycle acceptance pass.
3. **Key management:** the S3 adapter requires a configured managed KMS key and requests SSE-KMS on object writes/copies. Provider-enforced bucket policy, firm-scoped cryptographic isolation, key rotation, revocation, and recovery integration remain unverified. Do not reuse the backup key.
4. **Download behavior:** approved default is case-authorized, audited downloads with no public URLs. The initial endpoint implements this for ready originals; role-specific policy review remains.
5. **Limits and allowed formats:** the current adapter/upload flow enforces a 15 MB cap; a comprehensive media-type allowlist, malware scanning and robust archive/page-count defenses remain open.
6. **Recovery objectives:** originals must be recoverable consistently with firm DB metadata; coordinated backup/restore and measured RPO/RTO remain open.

## Acceptance gates

Do not enable original-binary retention for confidential matter data until:

- The decisions above are approved and documented.
- Tenant storage namespaces and path/object authorization have regression tests.
- Upload failure and crash-window reconciliation tests pass.
- Encrypted backup/restore includes originals and verifies their digests; for S3, run the restore-to-S3 importer and verify the resulting inventory in staging.
- Legal-hold set/release, two-admin deletion approval, legal-hold cancellation, gated local purge, tombstone retention, and backup/restore are tested; retention schedules and automated offboarding orchestration remain outstanding.
- The witnessed staging recovery drill and independent security review are complete. The review must verify the live bucket's never-versioned state, exact KMS key and IAM policy, and a control that prevents concurrent object writes throughout purge; the CLI `--quiesced` flag is only an operator assertion and is not itself a lock.

This is an initial end-to-end development implementation, not release completion. Do not enable it for confidential production matter data until the production object-store/KMS adapter, complete retention/deletion/offboarding lifecycle, object/database reconciliation, coordinated encrypted backup/restore, failure/crash-window tests, witnessed recovery drill, and independent security review are complete.
