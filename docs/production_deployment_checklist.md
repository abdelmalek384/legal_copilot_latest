# Production deployment checklist

This checklist is a release gate, not a certification. Completing it does not replace an independent security review, privacy/legal review, or testing with real operational data.

## 1. Runtime and network boundary

- [ ] Use a supported, patched Python runtime and install dependencies from a reviewed, pinned deployment lockfile.
- [ ] Run the app as a dedicated unprivileged OS account. Do not run it as root.
- [ ] Bind Uvicorn to loopback or a private interface only; do not expose port 8000 directly to the public internet.
- [ ] Terminate TLS at a maintained reverse proxy and redirect HTTP to HTTPS.
- [ ] Set `COPILOT_ENV=production` and configure `COPILOT_ALLOWED_HOSTS` as an explicit production host allowlist; verify runtime middleware rejects unlisted Host headers. Do not rely on reverse-proxy routing alone; strict deployment preflight must block a missing or invalid allowlist.
- [ ] Configure the proxy to overwrite, not append blindly to, forwarded headers. The application currently uses the direct peer address for rate limiting and does not trust X-Forwarded-For; do not enable proxy-header trust without an explicit trusted-proxy allowlist and deployment tests.
- [ ] Set a request-body size limit and upload timeout at the proxy as well as the application's upload validation.
- [ ] Restrict inbound traffic to the proxy and restrict outbound traffic to required services (including the configured LLM endpoint).

## 2. Secrets and identity

- [ ] Set ADMIN_TOKEN to a randomly generated secret of at least 32 characters using the deployment secret manager. Never put it in source control, images, tickets, or logs.
- [ ] Keep LLM_KEY and any other credentials in the secret manager; do not expose them to the browser.
- [ ] Generate MFA_ENCRYPTION_KEY with python manage.py gen-mfa-key and store it in the secret manager. Never reuse BACKUP_KEY or another application credential. Keep the same key available for restore of the control-plane database; loss of this key prevents decryption of enrolled TOTP secrets.
- [ ] Set MFA_ENFORCEMENT=admins_required or all_required in production. Production preflight rejects optional enforcement and rejects a missing/invalid MFA key.
- [ ] Keep LLM_DATA_PROCESSING_APPROVED unset until the exact configured endpoint/model and its data-handling terms have been reviewed and approved for the intended data class. Set it to 1 only with documented approval; the setting is an operator attestation, not a technical privacy guarantee.
- [ ] Use unique administrator credentials, a strong password, and least-privilege role assignment.
- [ ] Establish a documented process for administrator offboarding, password reset, and secret rotation.
- [ ] Verify MFA enrollment and recovery-code handling with a test administrator; confirm recovery codes are shown once and stored only as salted hashes.
- [ ] Rehearse lost-authenticator recovery, recovery-code rotation, required-admin MFA enforcement, and the two-admin MFA reset command. Document and approve a separate offline two-person procedure for the last-platform-admin case before production. Do not permit an administrator to disable MFA while policy requires it.

## 3. Database, uploads, and backups

- [ ] Configure all three fresh-install database paths as distinct absolute paths: \`COPILOT_CONTROL_DB\`, \`COPILOT_TENANT_DB_ROOT\`, and \`COPILOT_CORPUS_DB\`. Keep the control-plane and corpus database files outside the tenant directory.
- [ ] Leave \`COPILOT_DB\` unset. It is a non-production compatibility path, not the approved database architecture for this greenfield project.
- [ ] Run `python tools/deployment_preflight.py --strict` against the exact release environment and retain the output. **The production object-store/KMS adapter is not implemented. PR #671 adds an explicit preflight blocker for this gap, but that guard is not yet merged into `main`; until both the guard and a fully integrated backend are merged and verified, treat production release as blocked even if the current preflight passes.**
- [ ] Run the read-only tenant preflight against the initialized staging control plane and tenant directory; retain the JSON report and resolve catalog-authority, migration-ledger, foreign-key, path, and file-permission findings. Example: `python scripts/tenant_database_preflight.py /absolute/path/to/control-plane.sqlite3 /absolute/path/to/tenants`. A clean report does not prove route-level isolation.
- [ ] Restrict control-plane, corpus, tenant database, WAL/SHM, object-storage, and backup locations to the service/operator accounts; encrypt underlying volumes and restrict operator access.
- [ ] Do not deploy multiple hosts with separate local SQLite files and assume data or rate limits are shared. Multi-host operation requires a designed shared rate-limit service and an architecture tested for concurrent access.
- [ ] Configure the encrypted multi-database bundle backup and keep the backup key separate from backup files and application secrets. Keep writes quiesced for the entire multi-file snapshot window.
- [ ] Restore a bundle to a new protected staging location, then run \`python tools/run_database_recovery_drill.py --bundle /protected/backup.bundle.enc --temp-parent /protected/plaintext-temp --json\` with \`COPILOT_BACKUP_FERNET_KEY\` set. Record reviewer-witnessed evidence using \`docs/database_recovery_drill_record_template.md\`.
- [ ] Confirm the drill verifies the control plane, every tenant database, the legal corpus, firm routing, and original-file bytes. Temporary plaintext cleanup is not secure erasure on SSD or copy-on-write storage.
- [ ] Obtain counsel-approved retention schedules and verify legal-hold, export, deletion, and audit-retention procedures before authorizing any purge.
- [ ] **Do not use confidential production matter data until the production object-store/KMS adapter, backup/restore integration, retention lifecycle, witnessed recovery drill, and independent security review are complete.**

## 4. Legal-data safety

- [ ] Confirm acquisition rights and commercial reuse permission for every corpus source; a URL or public availability is not sufficient. Record separate `commercial_reuse_evidence` and `commercial_terms_checked_on` fields before marking commercial reuse allowed.
- [ ] Keep candidate/unreviewed instruments ineligible for legal retrieval. Do not mark a text verified or in force without documented source and legal review.
- [ ] Keep ALLOW_UNLINKED_LEGACY_LAW_SEARCH unset in production. Unlinked legacy-law chunks are excluded by default; the explicit =1 override is a temporary migration/testing escape hatch only and must not be used for client-facing legal answers without documented review and risk approval.
- [ ] Validate article-level extraction against the authoritative Gazette or an authorized official copy; preserve source hash, retrieval date, version and reviewer evidence.
- [ ] Have qualified Egyptian counsel review currentness, amendments, commencement dates, repeals, and representative answers before any client-facing legal use.
- [ ] Keep fictional sample data out of production and label unverified sources visibly.

## 5. Reminder delivery (not yet production-ready)

- [ ] Keep email delivery disabled until recipient authorization and firm-scoped filtering are integrated.
- [ ] Configure SMTP credentials only in the deployment secret manager; use a dedicated sender account, verified TLS, and approved sender-domain SPF/DKIM/DMARC.
- [ ] Implement an atomic durable idempotency claim and persistent queued/sent/failed state through the database workstream before scheduling sends.
- [ ] Test duplicate scheduler runs and concurrent workers across two firms; test ambiguous timeouts and manual reconciliation.
- [ ] Alert on failed sends, retry exhaustion, scheduler lag, and stale queued records without logging message bodies or secrets.
- [ ] Confirm SMTP acceptance is not reported as inbox delivery; use a controlled staging mailbox before enabling production.

## 6. Release validation

Run the CI workflow and confirm all jobs pass for the exact commit being deployed. In particular, verify the separate-database runtime, cross-firm API suite, identity lifecycle, profile migrations, encrypted backup/restore bundle, original-file integrity, and release-preflight tests. The legacy `selftest.py` and `api_test.py` suites exercise compatibility behavior and are not substitutes for separate-database tests. Passing tests do not establish production readiness.

- [ ] Test tenant isolation with at least two independent firms and users.
- [ ] Test login throttling, session expiry/revocation, CSRF, upload limits, rate limits, and admin-only routes.
- [ ] Test backup restore and verify that deleted-case audit snapshots remain firm-scoped and admin-only. Confirm the separately managed MFA_ENCRYPTION_KEY is available before testing TOTP-secret restoration.
- [ ] Test degraded LLM behavior, timeout handling, and source-only fallback.
- [ ] Conduct an independent security assessment and remediate high/critical findings before storing client-confidential matters.

## 7. Monitoring and incident response

- [ ] Collect access, application error, resource, disk, and backup-failure metrics without logging passwords, session tokens, case text, uploaded content, or API secrets.
- [ ] Configure alerts for repeated authentication failures, repeated 429 responses, storage exhaustion, failed backups, and elevated 5xx responses.
- [ ] Write an incident playbook for credential rotation, access revocation, evidence preservation, client notification assessment, and recovery.
- [ ] Assign an owner and review cadence for dependency updates, security patches, and legal corpus status.

## Release decision

Do not describe the product as production-ready until the unchecked items have named owners, evidence, and an explicit risk acceptance. A passing CI run alone is not a production security approval.


- [ ] Confirm every legal release candidate has a stable safe `document_id`, non-empty `official_title` and `document_type`, and links to exactly one central source record.
