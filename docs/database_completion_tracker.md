# Database completion tracker

**Last updated:** 2026-10-26  
**Estimated completion:** 56%  
**Status:** In progress — not production-ready for confidential multi-firm matter data.

This is a planning estimate across fresh-install schema/migrations, tenant isolation, operational recovery, and release validation. The product owner confirms that no legacy database has been deployed or used; migrating/reconciling historical customer data is therefore not a current project task. Any future import of external data must be separately approved and rehearsed on copies. This is not a percentage of tests passing. This is a weighted engineering estimate, not a test-pass percentage or a count of commits. The separate-database runtime and encrypted backup/restore are merged, and row-scope enforcement plus fresh-install/restart and cross-firm case tests have been added. The percentage remains a weighted engineering estimate; exhaustive route/query coverage, the still-supported explicitly configured shared-database compatibility path, invitation/account-recovery policy, platform-role grant governance, and a witnessed operational recovery drill remain open. Legacy customer-data reconciliation is not applicable to the current fresh-install development project. The latest merged tests cover cross-firm task state transitions, Unicode-canonical global email uniqueness, missing-tenant fail-closed behavior, global identity disablement, platform-role read boundaries, read-only ownership preflight, backup/catalog integrity, explicit fresh-schema firm ownership, private-corpus discovery boundaries, cached connection revocation on role changes, and an append-only control-plane platform security event ledger with atomic CLI password-reset auditing (PR #544; CI run #1446 passed). Runtime catalog creation and immutable firm-to-database binding are now migration-managed rather than silently bootstrapped (PRs #524 and #525; CI run #1388 passed). The latest merged schema tests also prove that wrong-firm inserts are rejected across cases, documents, extraction reviews, research conversations, and case-deletion audit rows (PR #530; CI run #1394 passed), and platform reviewer role revocation immediately blocks shared-corpus review-event writes (PR #532; CI run #1405 passed). The latest completed route tests additionally cover conflict checks, global password-session revocation, membership-scoped suspension, and cross-firm deadline actions. PR #537 adds restore regression coverage proving disabled-firm state and suspended memberships remain denied after recovery while active-firm data remains accessible (CI run #1425 passed). PR #539 verifies shared-corpus bulk imports require a platform reviewer, remain in review staging despite caller-supplied trust flags, and are denied immediately after role revocation (CI run #1427 passed). PR #542 adds cross-firm regression coverage for unscoped `/search` and `/ask`, ensuring another firm's private document sentinel is not returned (CI run #1433 passed). PR #543 behaviorally tests UPDATE-trigger rejection on all five firm-owned tables, proving wrong-firm firm_id changes abort and do not persist (CI run #1436 passed). PR #538 provides the operator-facing encrypted-bundle verification command, but the witnessed staging restore/rollback drill remains outstanding (CI run #1426 passed). PR #549 verifies safe one-time initial-owner bootstrap and refusal to replace an existing owner (CI run #1452 passed); PR #553 verifies the backup-verification CLI success/failure paths leave no persistent restore artifacts (CI run #1462 passed). PR #562 verifies temporary plaintext restore directories are removed on both success and wrong-key failure (CI run #1479 passed). PR #555 verifies initial bootstrap refuses to overwrite disabled existing firm/identity state (CI run #1467 passed).

## Completed and merged

- [x] Add an operator-facing backup verification command (python manage.py verify-backup-tenancy) that validates encrypted multi-database bundles using a restricted temporary restore, checks database integrity, and removes temporary plaintext. Deletion is not secure erasure; this is not a witnessed recovery drill (PR #538 merged; CI passed).
- [x] Add an append-only control-plane platform security event ledger and atomically audit CLI password resets without storing raw email/password values (PR #544 merged; CI run #1446 passed).
- [x] Extend platform audit coverage to firm provisioning/disablement, membership creation, initial-owner bootstrap and a bounded read-only audit CLI (PR #561 merged; CI passed). Membership creation now rolls back if its audit write fails; additional atomicity regression coverage is in progress.
- [x] Verify `init-tenancy` creates one firm administrator without platform privileges on a clean install and refuses a second bootstrap when an active membership already exists (PR #549 merged; CI run #1452 passed).
- [x] Exercise `verify-backup-tenancy` through the CLI for valid bundles and wrong-key rejection, asserting no persistent restore artifacts (PR #553 merged; CI run #1462 passed). PR #562 additionally directs temporary storage to an isolated test directory and verifies cleanup on success and failure (CI run #1479 passed).
- [x] Verify `init-tenancy` refuses bootstrap over disabled existing firm/identity state and preserves all existing rows (PR #555 merged; CI run #1467 passed).

- [x] Wire authenticated firm membership and trusted catalog resolution into the fresh-install runtime: control-plane authentication/session lookup, per-firm matter connections, shared legal-corpus routing, and fail-closed behavior when separate configuration is incomplete (PR #372 merged; CI passed).
- [x] Add encrypted multi-database backup/restore bundles for the control plane, shared corpus, and every cataloged firm database; validate profiles, firm bindings, SQLite integrity, catalog consistency, and manifest checksums; restore only to a new destination (PR #382 merged; CI passed).
- [x] Update deployment preflight for the three separate-database paths, rejecting partial configuration, unsafe path overlap, symlinks, and unsafe POSIX storage permissions without creating databases (PR #384 merged; CI passed).
- [x] Verify FTS5 external-content index integrity on a disposable copy so stale inverted indexes are detected without modifying the source database (PR #388 merged; CI passed).
- [x] Extend migration rehearsal to hash rows in shared source/staged columns and flag same-count row rewrites or deletions for review while allowing append-only inserts; source remains unchanged (PR #430 merged; CI run 40372094006 passed).
- [x] Add runtime regression coverage for denying non-member firm switches and revoking access after membership revocation even when a tenant connection is cached (PR #390 merged; CI passed).
- [x] Extend separate-runtime integration tests to deny cross-firm listing, reading, renaming, messaging, saving, and deleting of research conversations while preserving the source firm's record (PR #435 merged; CI run 40372780977 passed). This covers the research-conversation route family only; other route families remain under audit.
- [x] Verify `/search` and `/ask` reject a guessed case ID from another firm before retrieval and do not return the source firm's sentinel document (PR #446 merged; CI run 40374699211 passed). Other search/query paths and background workflows still require review.
- [x] Extend cross-firm integration tests for document-extraction review routes: a second firm cannot list extracted chunks/reviews or submit a correction, and the source chunk remains unchanged (PR #437 merged; CI passed).
- [x] Add a strict legal-corpus audit gate and make the read-only audit use one SQLite read snapshot while reporting main-file and existing WAL/journal sidecar hashes (PR #438 merged; CI passed).
- [x] Verify firm-scoped case-deletion audit history, security-event JSON, and CSV exports with records seeded in two firm databases; each active firm sees only its own sentinels (PR #439 merged; CI run 40373438210 passed).
- [x] Enforce database-bound firm IDs on inserts/updates for cases, documents, extraction reviews, research conversations, and case-deletion audit rows; add cross-firm case detail/update/delete tests and separate-profile fresh-install/restart persistence coverage (PR #465 merged; CI run 40379864878 passed).
- [x] Verify both insert and update tenant-binding triggers are installed for all five firm-owned tables and prove wrong-firm inserts are rejected without retaining rows (PRs #522 and #530 merged; CI runs #1370 and #1394 passed).
- [x] Extend separate-runtime route tests to reject cross-firm writes for notes, deadlines, fees, sessions, document text, case members, tasks, and uploads; assert the source tenant's records remain unchanged (PR #476 merged; CI run 40381720498 passed).
- [x] Verify a firm administrator cannot suspend an identity belonging only to another firm; the target identity and other-firm membership remain active (PR #482 merged; CI run 40382596457 passed).
- [x] Verify platform legal-review authorization is distinct from firm-admin membership and that removing a platform reviewer role denies the very next request without trusting stale session claims (PR #483 merged; CI run 40382833193 passed).
- [x] Verify dashboard, calendar export, and finance aggregates exclude another firm's case/deadline/fee sentinels after switching firm context (PR #485 merged; CI run 40383241482 passed).
- [x] Verify disabling a firm denies the next API request while retaining the tenant database file and its matter data (PR #487 merged; CI run 40383552960 passed).
- [x] Verify cross-firm conflict checks return no matter matches or conflict/admin-review signals for another firm's confidential opposing party (PR #490 merged; CI run 40384296346 passed).
- [x] Verify global password changes revoke sessions across all firm memberships while preserving memberships and allowing the new credential (PR #491 merged; CI run 40384550589 passed).
- [x] Verify suspending one firm membership leaves the global identity and its other firm's membership active, and blocks only the suspended firm's access (PR #492 merged; CI run 40384723859 passed).
- [x] Verify deadline completion by an ID from another firm's database returns not found and leaves the source deadline unchanged (PR #493 merged; CI run 40384885120 passed).
- [x] Verify task claim and completion by another firm's task ID are both denied, preserving the source task as open/unassigned (PR #498 merged; CI run 40385985884 passed).
- [x] Verify a missing provisioned tenant database fails closed without recreating the file or falling back to the legacy shared database (PR #503 merged; CI run 40386709308 passed).
- [x] Verify disabling a global identity invalidates its cached tenant connection immediately while retaining firm data and membership records (PR #509 merged; CI run 40387362059 passed).
- [x] Verify platform reviewer authorization protects the legal-review queue, coverage metrics, catalog drill-down, and version review-event history, including denial immediately after role revocation (PR #512 merged; CI run 40387772535 passed).
- [x] Verify shared-corpus bulk import requires a platform reviewer, writes only to review staging, ignores caller-supplied trust flags, and fails immediately after role revocation (PR #539 merged; CI run #1427 passed).
- [x] Verify shared-corpus review-event writes require the platform reviewer role and are denied immediately after role revocation (PR #532 merged; CI run #1405 passed).
- [x] Verify the legacy ownership preflight reports ownership anomalies while leaving database bytes, size, and modification time unchanged (PR #510 merged; CI run 40387428003 passed).
- [x] Verify encrypted backup refuses unreferenced tenant database files and cataloged tenant databases replaced by symlinks, without emitting a backup artifact (PR #505 merged; CI run 40386902056 passed).
- [x] Verify encrypted restore preserves disabled-firm/catalog state and suspended membership denial while restoring active-firm data (PR #537 merged; CI run #1425 passed).
- [x] Verify fresh firm-schema case rows require explicit `firm_id` and reject inserts that omit firm ownership (PR #515 merged; CI run 40388602779 passed).
- [x] Verify shared legal-registry discovery cannot return a private matter document from a firm database (PR #521 merged; CI run 40389391259 passed).
- [x] Verify unscoped `/search` and `/ask` cannot return another firm's private matter document chunks after switching firm context (PR #542 merged; CI run #1433 passed).
- [x] Verify insert and update tenant-binding triggers are present for all firm-owned tables with embedded `firm_id` (cases, documents, extraction reviews, research conversations, and case-deletion audit rows) (PR #522 merged; CI run 40389461819 passed).
- [x] Verify wrong-firm UPDATEs are rejected on all five firm-owned tables after seeding valid bound rows, with no changed firm IDs retained (PR #543 merged; CI run #1436 passed).
- [x] Verify changing a firm membership role closes the previously cached tenant connection and requires a freshly resolved context (PR #523 merged; CI run 40389630776 passed).
- [x] Remove runtime DDL fallback for `tenant_database_catalog`; versioned control-plane migrations are now the sole schema authority and missing catalog tables fail closed (PR #524 merged; CI run 40389656327 passed).
- [x] Verify global identity uniqueness for Unicode NFC normalization and casefold (including `Straße`/`STRASSE`) at the runtime/database boundary (PR #501 merged; CI run 40386260174 passed).
- [x] Reject stale shared COPILOT_DB configuration when the three approved separate-database paths are configured, preventing ambiguous deployment storage intent (PR #477 merged; CI run 40381467990 passed).
- [x] Verify clean-install shared legal-corpus FTS insert/update/delete synchronization using FTS5 external-content integrity checks against source chunks (PR #479 merged; CI run 40381954656 passed).

- [x] Extend tenant preflight to audit POSIX SQLite WAL/SHM/journal sidecars, and refuse to open a catalog or tenant database when a sidecar is symlinked or has unsafe permissions (PR #362 merged; CI run 40357742798 passed).
- [x] Extend the tenant router to reject symlinked or overly permissive SQLite sidecars and revoke cached connections when sidecars become unsafe (PR #363 merged; CI run 40357383129 passed).

- [x] Make deployment preflight fail when existing POSIX SQLite WAL/SHM/journal sidecars are symlinked, overly permissive, or their permissions cannot be inspected (PR #359 merged; CI run 40356578010 passed).

- [x] Make the tenant router reject POSIX tenant database files with group/other access and revoke cached connections if file permissions become unsafe (PR #355 merged; CI run 40356138402 passed).

- [x] Fail tenant provisioning when restrictive POSIX permissions cannot be applied to a newly created tenant database; verify failed provisioning cleans up the file and records failure (PR #354 merged; CI run 40355964176 passed).

- [x] Replace the fixed shared temporary SQLite file in the SEC-01 inventory test with a unique per-process temporary directory to avoid concurrent CI collisions (PR #349 merged; CI run 40355357530 passed).

- [x] Extend the read-only tenant preflight to flag POSIX control-plane and tenant database files that allow group/other access; no permissions are changed automatically (PR #344 merged; CI run 40354780649 passed).

- [x] Make FTS auditing and rebuild-on-a-new-copy profile-aware: validate external-content indexes against `chunks.norm`, preserve firm/corpus FTS schema and synchronization triggers, and verify the source remains unchanged (PR #399 merged; CI passed).
- [x] Add integration coverage that non-members cannot switch firms, revoked memberships block requests despite a still-valid login session/cached tenant connection, and a task ID from one firm's database cannot be acted on in another firm's database (PRs #390 and #401 merged; CI passed).
- [x] Add a firm-admin API for attaching an existing active global identity to another firm by normalized email, without duplicating identities or silently reactivating suspended/revoked memberships (PR #405 merged; CI passed).
- [x] Add management CLI commands to provision additional firm databases and attach existing active global identities to a firm; duplicate membership attempts fail (PR #410 merged; CI passed).
- [x] Ensure a catalog connection-open failure cannot strand a new firm in `provisioning`; failed provisioning marks it disabled and leaves no tenant DB file (PR #408 merged; CI passed).
- [x] Test that disabled global identities cannot be added to new firm memberships (PR #407 merged; CI passed).
- [x] Reject CLI user creation when the target firm is missing or inactive, atomically preventing orphaned global identities (PR #413 merged; CI passed).
- [x] Create new control-plane and shared-corpus database files with restrictive POSIX permissions and clean up incomplete newly created files if permissions cannot be enforced (PR #415 merged; CI passed).
- [x] Revalidate control-plane/corpus file permissions and SQLite sidecars before direct connection use, revoking unsafe cached direct connections (PR #418 merged; CI passed).
- [x] Revalidate attached control-plane and corpus storage on every firm request, including when tenant connections are cached (PR #420 merged; CI passed).
- [x] Revoke the current thread's cached firm connection immediately when membership, firm lifecycle, or role validation fails (PR #422 merged; CI passed).
- [x] Add a non-destructive `disable-firm` operator command that atomically disables the firm and its catalog mapping without deleting data; no re-enable path is provided (PR #419 merged; CI passed).
- [x] Serialize `/users` and `/memberships` writes with an immediate control-plane transaction and recheck active firm state before creating identities or memberships, preventing lifecycle races (PR #425 merged; CI passed).
- [x] Add regression coverage that `deployment_preflight.py --strict` fails while the shared-database multi-firm safety warning remains, without creating a database file (PR #341 merged; CI run 40354404426 passed).

- [x] Refuse to provision a tenant when pre-existing firm-binding trigger names conceal ineffective update/delete guards; validate the guards before marking the tenant provisioned (PR #340 merged; CI run 40354238518 passed).

- [x] Reject symbolic links for the configured `COPILOT_DB` path in deployment preflight before inspecting the target, with regression coverage (PR #337 merged; CI run 40353912360 passed).

- [x] Refuse to mark a tenant database provisioned unless its profile marker has effective immutable update/delete guards; failed provisioning uses the existing cleanup path (PR #336 merged; CI run 40353760086 passed).

- [x] Require the tenant connection router to verify that the tenant `database_profile` update/delete triggers effectively abort mutation before caching or returning a connection (PR #334 merged; CI run 40353397193 passed).

- [x] Add an explicit deployment-preflight warning that the shared `COPILOT_DB` boundary is not ready for unrelated firms' confidential matters; strict release-gate mode fails while the warning remains (PR #331 merged; CI run 40352850811 passed).

- [x] Make the read-only tenant preflight stop before opening tenant database files whenever control-plane profile/migration authority fails; verify the catalog firm foreign key and report orphaned mappings first (PR #330 merged; CI run 40352597192 passed).

- [x] Validate the trusted control-plane profile before any catalog schema write; reject unbound/wrong-profile catalogs without creating or modifying tenant-catalog tables (PR #314 merged; CI run 40274660734 passed).

- [x] Require the tenant catalog initializer/resolver to verify the immutable `control_plane` profile marker and effective update/delete guards before trusting tenant mappings (PR #311 merged; CI run 40274318860 passed).

- [x] Require the SQLite membership lookup to verify that control-plane profile update/delete triggers actually abort mutation, not merely exist by name (PR #306 merged; CI run 40274062209 passed).
- [x] Require the tenant connection router to verify effective immutable update/delete guards for the embedded firm binding (PR #307 merged; CI run 40274104449 passed).

- [x] Extend the read-only tenant preflight to validate the control-plane catalog migration ledger against trusted migration files, including missing history and checksum drift (PR #301 merged; CI run 40238866669 passed).

- [x] Require the read-only tenant preflight's catalog database to carry the immutable `control_plane` profile marker; report missing/wrong/mutable catalog profile bindings and test against real versioned control-plane fixtures (PR #298 merged; CI run 40238741573 passed).

- [x] Add schema acceptance assertions that global identities, firm memberships, and platform-role assignments exist only in the control-plane profile, not in firm or shared legal-corpus databases (PR #295 merged; CI run 40238588271 passed).

- [x] Extend the read-only tenant database preflight to verify the firm migration ledger's versions, filenames, and checksums against trusted migration files; missing or drifted history is reported without repair (PR #292 merged; CI run 40238470057 passed).

- [x] Require the trusted membership lookup to verify the immutable `control_plane` profile marker and reject wrong/unbound database connections; retain fail-closed user/firm lifecycle checks (PR #280 merged; CI run 40237828642 passed).

- [x] Make the read-only tenant database preflight inspect trigger SQL and flag expected-name no-op triggers that do not actually block profile/firm-binding mutation (PR #282 merged; CI run 40237979900 passed).

- [x] Extend the read-only tenant database preflight to verify the firm schema profile marker and embedded firm ID against the trusted catalog mapping (PR #271 merged; CI run 40237510600 passed).

- [x] Validate platform-role input types and reject malformed role values with a controlled error (PR #272 merged; CI run 40237519341 passed).

- [x] Deny firm-context resolution for suspended/disabled/provisioning firms even when membership is active (PR #273 merged; CI run 40237557121 passed).

- [x] Deny disabled global identities during firm membership validation, even if a membership row remains active (PR #276 merged; CI run 40237663867 passed).

- [x] Require tenant provisioning to verify the new database has the expected firm schema profile before marking the catalog entry provisioned; fail closed and clean up failed provisioning (PR #266 merged; CI run 40237378927 passed).

- [x] Verify canonical email normalization handles Unicode-equivalent identities and the fresh control-plane schema rejects normalized duplicate keys (PR #261 merged; CI run 40237094670 passed).

- [x] Reject unsupported firm roles in the trusted firm-context resolver; malformed and platform-level roles fail closed (PR #263 merged; CI run 40237149480 passed).

- [x] Add explicit platform-role lookup against `user_platform_roles`, with tests proving firm-admin membership does not imply platform privileges and platform assignments can be revoked independently (PR #264 merged; CI run 40237221190 passed). The helper is not yet wired into live routes.

- [x] Add a fail-closed SQLite membership lookup over the versioned control-plane `firm_memberships` table and integration tests for multi-firm and suspended memberships; not yet wired into request authentication/routing (PR #259 merged; CI run 40236974418 passed).

- [x] Add a fresh control-plane schema for global normalized-email identities, many-to-many firm memberships, firm-scoped roles/status, and separate platform-role assignments; schema acceptance tests pass, but runtime auth/routing is not wired (PR #253 merged; CI run 40236818594 passed).

- [x] Canonicalize login/user-creation/reviewer emails and add a read-only legacy audit for duplicate normalized global emails; existing collisions are flagged for manual resolution, never auto-merged (PR #252 merged; CI run 40236580927 passed).

- [x] Remove duplicated research-conversation ownership findings from the read-only tenant preflight and assert finding codes are unique (PR #247 merged; CI run 40235595413 passed).

- [x] Extend read-only ownership preflight to flag missing creators and cross-firm creator attribution for notes, deadlines, and fees (PR #242 merged; CI run 40234817307 passed).

- [x] Extend read-only ownership preflight to detect missing task assignees/creators and cross-firm task attribution (PR #238 merged; CI run 40234655678 passed).

- [x] Extend read-only ownership preflight to flag research messages with missing or unassigned conversation parents (PR #235 merged; CI run 40234397873 passed).

- [x] Extend the read-only ownership preflight to detect research conversations with missing/unassigned users, missing firm ownership, or unknown firm IDs (PR #231 merged; CI run 40234204885 passed).

- [x] Reject symlinked database paths in the read-only legacy ownership preflight; regression test verifies the CLI refuses the link before opening the target (PR #229 merged; CI run 40233980058 passed).

- [x] Reject symlinked migration directories and SQL files in the versioned migration runner, with regression tests proving linked sources are not executed (PR #225 merged; PR CI run 40233614310 passed).

- [x] Harden SQLite backup concurrency, staged validation, encryption output, retention ordering, and restore replacement safety (PR #138).
- [x] Extend read-only tenant ownership preflight to detect orphaned child records (PR #139).
- [x] Move six operational indexes into versioned migration 0002 (PR #140).
- [x] Add disposable-copy migration rehearsal with source read-only behavior and integrity checks (PR #141).
- [x] Move remaining operational indexes into versioned migration 0003 (PR #142).
- [x] Add read-only preflight checks for unlinked matter records (PR #143).
- [x] Add persistent database completion tracker (PR #144).
- [x] Inventory remaining startup DDL without opening a database (PR #145).
- [x] Reject symlinked tenant storage roots and explicitly test tenant catalog safety in CI (PR #146).
- [x] Expand read-only ownership preflight for cross-firm document, extraction-review, and audit inconsistencies (PR #147).
- [x] Move `legal_version_relations` and `security_audit_events` into versioned migrations 0004 and 0005, with migration-order, constraint, inventory, and rehearsal coverage (PR #148, merged).
- [x] Move six independent authentication/case-workspace tables (`auth_sessions`, `notes`, `fees`, `tasks`, `events`, and case-calendar `sessions`) into migration 0006, with migration, inventory, and disposable-copy coverage (PR #149, merged).
- [x] Add end-to-end fresh database startup and restart coverage in CI; verify the migration ledger and preservation of an existing row (PR #151, merged).
- [x] Reject out-of-order recorded migration histories in the migration runner, with regression coverage and CI (PR #152, merged).
- [x] Move `legal_sources`, FTS5 setup, and the default-firm seed into migrations 0007–0009 (PR #153, merged; CI passed). `legal_documents` remains in bootstrap because startup conditionally inspects/alters it before the migration runner. FTS migration preserves an existing virtual table and does not implicitly rebuild it.
- [x] Move non-prerequisite conditional column upgrades into migration 0010 using checksum-protected `@add-column-if-missing` directives (PR #155, merged; CI passed). Columns required by immutable migrations 0001–0003 remain in startup bootstrap.
- [x] Add read-only FTS consistency preflight for missing/orphaned rows and indexed-content mismatches, with CI coverage and repair safety guidance (PR #156, merged; CI passed).
- [x] Add a staged-copy FTS rebuild utility that leaves the source database untouched, refuses output overwrite, validates integrity/foreign keys/chunk counts, and includes regression tests (PR #163, merged; CI run 40216663954 passed).
- [x] Enable SQLite foreign-key enforcement during tenant database initialization and validate `integrity_check` plus `foreign_key_check`, with cleanup on failed provisioning (PR #165, merged; CI run 40217212814 passed).
- [x] Reject symlinked tenant storage roots in the read-only preflight before path resolution (PR #167, merged; CI run 40217356965 passed).
- [x] Add profile-binding and initial isolated-schema acceptance tests to CI; fix same-line SQL statement parsing while preserving trigger bodies (PR #171, merged; CI run 40217630357 passed).
- [x] Constrain tenant catalog entries to existing firms with a foreign key and fail-closed legacy-orphan migration; align the runtime catalog helper (PR #176, merged; CI passed).
- [x] Enforce firm document/chunk/extraction-review scope with a fail-closed migration and insert/update guards (PR #178, merged; CI run 40225478660 passed).
- [x] Preserve firm scope when parent cases/documents change, rejecting inconsistent legacy ownership and unsafe parent updates (PR #179, merged; CI passed).
- [x] Make the database profile-binding marker immutable against ordinary SQL updates/deletes (PR #184, merged; CI run 40228431913 passed).
- [x] Handle case-insensitive conditional column migration checks and add a legacy `Value`/`value` regression test (PR #187, merged; PR checks and post-merge main CI passed).
- [x] Add regression coverage ensuring tenant catalog initialization rejects a pre-existing catalog schema missing its `firms` foreign key (PR #189, merged; GitHub Actions run 40228763730 passed).
- [x] Validate existing tenant catalog rows with `PRAGMA foreign_key_check`, failing closed on orphaned firm mappings even when foreign-key enforcement was previously disabled (PR #191, merged; GitHub Actions run 40228904762 passed).
- [x] Require catalog-selected tenant databases to carry a `database_profile` marker bound to `firm`; fail closed and close the connection if the marker is missing or belongs to another profile (PR #212 merged; PR CI run 40232623791 and post-merge main CI run 40232675982 passed).
- [x] Bind each provisioned tenant database to its trusted firm ID using an immutable in-database marker, and reject copied/swapped files whose embedded firm ID does not match the catalog-selected firm (PR #217 merged; PR CI run 40232965973 passed; post-merge main CI run 40233022469 passed).
- [x] Reject symlinked migration roots and profile migration directories, including sibling-profile symlink swaps, with regression coverage (PR #214 merged; PR CI run 40232754284 and post-merge main CI run 40232810308 passed).
- [x] Extend the source-only startup DDL inventory recursively across root, control-plane, firm, and shared legal-corpus migration families; assert all 16 migration files are included (PR #209 merged; PR CI run 40232339854 and post-merge main CI run 40232382371 passed).
- [x] Reject a symlinked tenant catalog database in the read-only tenant database preflight, with regression coverage (PR #210 merged; PR CI run 40232412055 passed; post-merge main CI pending at tracker update time).

## In progress

- [x] Add a trusted active-firm context resolver and adversarial tests (PR #198 merged; CI run 40230700867 passed): accepts a caller-supplied verified server-side identity, validates active membership through a server-side lookup, and fails closed on suspended/missing/error states. This is an authorization primitive, not session authentication; it is not wired to routes until membership schema and identity semantics are approved.

- [x] Revoke a cached tenant connection when opening the tenant catalog fails, with regression coverage proving the prior connection is closed (PR #204 merged; PR CI run 40231783111 and post-merge main CI run 40231840643 passed).

- [x] Close and avoid leaking a tenant connection when connection initialization fails before caching, with injected-failure regression coverage (PR #205 merged; PR CI run 40231914349 passed; post-merge main CI pending at tracker update time).

- [x] Add catalog-backed tenant connection-router foundation (`tenant_storage.py`) with fail-closed catalog resolution, disabled-tenant revalidation, per-thread/per-firm connections, foreign-key enforcement, and cleanup. PR #195 merged; post-merge main CI run 40230147410 passed. PR #200 adds regression-tested closure of the current thread's cached connection when catalog validation fails (CI run 40230742941 passed). PR #201 adds passing CI coverage for distinct same-firm connections across threads and thread-owned cleanup (CI run 40231059405 passed). The router is not wired into app routes pending approved session/membership integration and shared-corpus migration.

## Remaining database work

### 1. Finish versioned schema migrations
- [ ] Retire the explicitly configured shared-database compatibility path only if the product decision is to remove it. Its inline `SCHEMA` and `ALTER TABLE` bootstrap are not part of the approved fresh-install runtime; no legacy database has been deployed or used.
- [x] Keep the approved fresh-install control-plane, firm, and legal-corpus schemas under versioned profile migrations. Remove runtime DDL fallbacks for the tenant catalog and immutable firm binding (PR #524 CI run #1372 passed; PR #525 CI run #1388 passed). Continue moving any remaining schema prerequisites used by the approved profiles into ordered migrations.
- [x] Add a read-only FTS5 internal index-integrity check on a disposable copy, detecting stale inverted indexes without mutating the source database (PR #388 merged; CI passed).
- [x] Add a controlled rebuild-on-a-new-copy procedure for legacy and firm/corpus profile databases, preserving external-content schema and synchronization triggers (PR #399 merged; CI passed).
- [x] Verify clean-install shared legal-corpus FTS insert/update/delete synchronization and external-content integrity (PR #479 merged; CI run 40381954656 passed).
- [ ] Conditional future import only: reconcile FTS against authoritative source content if an actual legacy corpus is deliberately introduced for import; migration 0008 itself does not rebuild stale/missing indexes.
- [x] Reject symlinked source database paths in the read-only FTS preflight before resolution/open, with regression coverage (PR #458 merged; CI run 40376020538 passed).
- [x] Document and verify the supported clean first-install path for all three profiles: README quick start configures distinct control-plane, tenant-root, and corpus paths; profile-schema tests initialize all three profiles; separate-runtime startup/restart and routing tests pass (CI run #1436 passed). Remaining application `SCHEMA` bootstrap belongs only to the explicitly configured compatibility path.
- [x] Test migration order, idempotency, checksum drift, interrupted migrations, and rollback/restore on representative disposable copies (`tests/test_db_migrations.py` and `tests/test_database_migration_rehearsal.py`; CI run #1436 passed).
- [x] Enforce migration immutability through checksum drift and missing-applied-file rejection; document forward-only corrective migrations (`docs/database_migrations.md`; CI run #1436 passed).

### 2. Approve identity and tenant contract
- [ ] Finish operational identity policy for invitations, initial firm-owner bootstrap, platform-role grant/revocation workflow, and session behavior after membership revocation; core decisions on multi-firm membership, global normalized email, and separate role domains are approved.
- [ ] Complete the deployment and storage inventory before selecting production routing behavior.
- [x] Wire control-plane identity, sessions, firm memberships, and trusted active-firm routing into the separate runtime (PR #372 merged; CI passed).
- [ ] Finish and verify invitation/bootstrap lifecycle, platform-role grant/revocation workflow, and prompt session/cache revocation across all routes after membership suspension or revocation.

### 3. Implement actual tenant storage boundaries
- [x] Implement the separate-runtime request path: authenticated session plus active membership resolves a trusted catalog entry; firm matter requests use the firm database, identity uses the control plane, and verified legal-reference search uses the shared corpus (PR #372 merged; CI passed).
- [ ] Finish route-by-route and query-by-query verification, including routes that intentionally use control-plane or corpus connections.
- [x] Add explicit three-path configuration and a fail-closed deployment preflight for the separate runtime (PR #384 merged; CI passed). Legacy `COPILOT_DB` compatibility remains available only when explicitly configured and is not approved for unrelated firms' confidential matters.
- [x] Define separate firm and corpus schema profiles and initialize separate databases.
- [ ] Conditional future import only: require legacy mixed `chunks`/FTS reconciliation if a legacy database is deliberately introduced; it is not a first-deployment task.
- [ ] Complete lifecycle acceptance for provisioning retries/reconciliation, disabled tenants, unknown catalog entries, unavailable tenant databases, and revoked memberships across all API/background paths. PRs #407, #408, #410, #413, #419, #420, and #422 cover selected onboarding, failure-cleanup, membership, disable, attached-profile, and cached-connection revocation paths. This is not exhaustive lifecycle coverage.

### 4. Conditional future legacy import (not current scope)
- [x] Add a read-only row-level legacy chunk evidence manifest with hashes but no extracted text, human-review classifications, and CI coverage; source database remains query-only (PR #443 merged; CI run 40374261835 passed). This enables evidence review but does not itself resolve ownership.
- [x] Prevent the legacy evidence-manifest output path from overwriting or aliasing its source database, including hard-link aliases, with regression coverage (PR #448 merged; CI run 40375268157 passed).
- [x] Flag legacy chunks whose linked document's firm differs from the linked case's firm as a human-review ownership anomaly; no automatic reassignment (PR #456 merged; CI run 40375774137 passed).
- [x] Exercise read-only ownership preflight on synthetic fixtures and assert byte-for-byte read-only behavior (PR #510 merged; CI run 40387428003 passed). A protected-copy audit is conditional on a future, explicitly approved legacy import.
- [x] Confirm that no production database is deployed. Production-row reconciliation and production cutover are therefore not first-deployment tasks; retain the read-only preflight and quarantine tools for any future explicitly approved legacy import.
- [ ] If a legacy database is later introduced, resolve missing/unknown ownership, orphaned rows, unlinked children, cross-firm references, and ambiguous corpus chunks from trusted evidence before import.
- [ ] If a legacy database is later introduced, rehearse import with source/target row counts, stable hashes where applicable, foreign-key checks, FTS reconciliation, and explicit quarantine for unresolved rows.


### 5. Prove tenant isolation and operational recovery
- [ ] Complete route-by-route and SQL-query-by-query cross-firm authorization tests, including exports, audit, search, legal review, background work, and administrative paths.
- [ ] Design firm-scoped original-upload object storage and retention; the current upload flow does not retain original binary objects, so recoverability must not be promised.
- [x] Implement encrypted, checksummed multi-database backup and non-destructive restore to a new directory, with two-firm isolation and tamper/wrong-key tests (PR #382 merged; CI passed).
- [x] Add `python manage.py verify-backup-tenancy` to validate an encrypted tenancy bundle through a restricted temporary restore, re-check all restored databases, and clean up temporary plaintext; deletion is not guaranteed secure erasure and this does not replace a witnessed recovery drill (PR #538 merged; CI run #1426 passed).
- [ ] Complete retention policy, tenant-specific export/deletion semantics, automated scheduling/monitoring, and operational recovery drills.
- [ ] Rehearse deployment, restore, and rollback using representative copies; validate permissions, secrets, encryption keys, monitoring, and incident runbooks.
- [ ] Obtain an independent security review before production use with unrelated firms' confidential matters.

## Release gate

**Do not describe the database as production-grade multi-tenant isolation yet.** The new configured runtime now routes through a control plane, per-firm SQLite files, and a shared legal corpus, while explicit legacy `COPILOT_DB` compatibility remains. Passing CI and adding backup code do not substitute for exhaustive route/query isolation, a witnessed restore/rollback drill, monitoring, and the remaining approval gates. Legacy-data reconciliation is conditional future work only if an external legacy database is explicitly introduced and approved for import.

## Progress update rules

- Count a code change as completed only after its PR is merged and its required CI checks pass.
- Keep open or failed-CI work in the in-progress section.
- Increase the overall percentage only when a meaningful release gate is completed; do not equate test count with database readiness.
- Preserve this tracker until every remaining task and the release gate are complete.
