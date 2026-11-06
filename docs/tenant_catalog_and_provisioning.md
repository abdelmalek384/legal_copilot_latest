# Tenant catalog, database-per-firm routing, and provisioning

**Status:** Implemented in the profile-separated runtime; production acceptance is still gated.

## Architecture

The approved runtime has three database profiles:

- **Control plane:** global identities, authentication sessions, firm memberships, platform roles, invitations, the trusted tenant catalog, and platform security events.
- **Firm databases:** matter/case data and firm-scoped operational records. Each active firm resolves to its own SQLite database file.
- **Shared legal corpus:** centrally governed legal sources, versions, evidence, and retrieval chunks. It is not a tenant's private matter store.

`DatabaseRuntime` is wired into the FastAPI request path. Authentication resolves an active global identity and active firm membership, then produces a trusted `FirmContext`. Tenant routing uses the server-side catalog and configured tenant root; the client never supplies a database path or catalog filename. A selected-firm cookie is only a selector: the server validates membership and firm lifecycle state before opening the firm database.

The catalog stores a trusted positive `firm_id` to generated relative filename mapping. Resolution validates the control-plane profile marker and immutable guards, foreign-key enforcement and existing ownership references, the filename's firm binding, the storage-root boundary, symlink restrictions, lifecycle status, and file existence. A missing or invalid tenant database fails closed; it must never fall back to another firm's database or the legal corpus.

## Provisioning and lifecycle operations

Use the CLI against the configured three-profile runtime:

- `python manage.py provision-firm "Firm Name"` creates a firm and its tenant database through the trusted catalog.
- `python manage.py adduser "Name" "email@example.test" admin --firm-id ID` creates an identity and membership for an active firm through the operator CLI.
- `python manage.py disable-firm ID` disables routing without deleting retained firm data.
- `python manage.py retry-failed-provisioning ... --confirm-retry` retries only a disabled firm whose catalog records a clean failed schema-provisioning attempt and has no membership or invitation history.
- `python manage.py reconcile-interrupted-provisioning ... --confirm-workers-stopped --confirm-reconcile` handles only a confirmed interrupted, file-less provisioning attempt. It refuses to adopt, overwrite, or delete a database file or SQLite sidecar.

Provisioning initializes the trusted firm-profile migrations, checks schema/profile binding and SQLite integrity, and activates the firm only after catalog state is consistent. Failure handling is deliberately conservative. If a valid database exists but activation/audit completion fails, the firm remains disabled for reviewed maintenance rather than being silently retried. All lifecycle recovery requires explicit reasons and operator/change references.

Do not write lifecycle status values manually, reuse a database file across firms, accept client-supplied paths, or activate a firm whose catalog state is ambiguous.

## Security and operational contract

- Request handlers must derive firm identity from the validated session/membership context. Do not trust tenant IDs supplied in query parameters, request bodies, headers, or raw filenames.
- Keep the control-plane database and catalog restricted to the application/operator identities. Protect database files and sidecars with host ACLs, encryption at rest, backups, and monitoring; POSIX mode bits alone are not a deployment boundary.
- Static route-to-SQL checks are a regression gate, not proof that every query is correctly scoped. Behavioral authorization review and negative cross-firm tests remain required.
- The shared `COPILOT_DB` runtime was retired in PR #972 and is rejected in every environment. The obsolete compatibility API smoke harness was deleted in PR #968; no legacy database has been deployed or used.
- The production startup gate requires the three separate database paths and a complete accepted operational evidence manifest. Production original-file uploads are currently fail-closed; enabling them requires a reviewed code/configuration change after the deployed S3/KMS backend passes live acceptance.

## Release blockers

Do not onboard unrelated firms or store confidential production matters until all applicable gates are closed with evidence:

1. Complete behavioral route/query authorization review, including control-plane and shared-corpus routes.
2. Validate the actual S3 bucket, KMS key, IAM permissions, firm isolation, and a synthetic staged-upload/finalize/readback/cleanup round trip. The round-trip tool is an acceptance aid, not a production approval.
3. Approve jurisdiction-appropriate retention, export, deletion, and legal-hold policies.
4. Complete a witnessed encrypted backup/restore, startup/isolation, and rollback drill with an independent reviewer.
5. Validate deployment-specific secrets, host/proxy/cookie settings, monitoring, incident response, and recovery procedures.
6. Obtain an independent security review before production use with unrelated firms' confidential matters.

The profile-separated runtime and automated tests are implementation evidence. They do not substitute for live-provider validation, legal/policy decisions, witnessed operational evidence, or independent review.
