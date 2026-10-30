# Production deployment checklist

This checklist is a release gate, not a certification. Completing it does not replace an independent security review, privacy/legal review, or testing with real operational data.

## 1. Runtime and network boundary

- [ ] Use a supported, patched Python runtime and install dependencies from the reviewed, pinned, hash-locked `requirements-py312.lock`; verify installation with `pip install --require-hashes` in a clean Python 3.12 environment.
- [ ] Pass the strict direct/transitive dependency audit against that exact lockfile on the exact release candidate; review Dependabot updates rather than auto-merging them (see [dependency security policy](dependency_security.md)).
- [ ] Review CodeQL Python and JavaScript findings on the exact release candidate; resolve high/critical findings or record a narrowly scoped, reviewed exception (see [static security analysis](static_security_analysis.md)).
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

- [ ] Configure three distinct absolute persistent paths: `COPILOT_CONTROL_DB`, `COPILOT_TENANT_DB_ROOT`, and `COPILOT_CORPUS_DB`. Keep `COPILOT_DB` unset; the shared-database compatibility harness is not an approved deployment architecture.
- [ ] Before serving production traffic, provision the profile schemas and first firm owner through the restricted maintenance/bootstrap procedure. Use the three profile-separated paths and no `COPILOT_DB`; production startup refuses to create missing/empty databases implicitly and blocks pending or drifted profile migrations and unresolved tenant-fleet lifecycle states.
- [ ] Run `python tools/deployment_preflight.py --strict` against the exact production environment and retain its output. Fix every error and warning that blocks the release.
- [ ] Keep the legacy tenant-import preflight out of first-deployment acceptance. No legacy database has been deployed or used; only run import/reconciliation tools if a separate, approved external-data import is later proposed.
- [ ] Set `COPILOT_DATABASE_ACCEPTANCE_FILE` to the controlled, completed operational-evidence manifest. Startup and the aggregate release gate both reject missing, incomplete, or stale evidence.
- [ ] On POSIX, keep the tenant database root private (`0700`) and control-plane, legal-corpus, tenant database, and SQLite sidecar files private (`0600`); the production runtime fails closed if the tenant root or profile database files are missing, symlinked, or too broadly accessible. Restrict backup directories to the application account and encrypt the underlying disk/volume.
- [ ] Do not deploy multiple hosts with separate local SQLite databases and assume rate limits or data are shared. SQLite-backed rate limits coordinate workers only when they share the same database file; separate hosts need a shared rate-limit service and an appropriate database architecture.
- [ ] Schedule encrypted backups outside the application host. Store the backup key separately from the backups.
- [ ] Complete a witnessed restore/rollback and staged-upload/deletion-recovery drill before release; code-level restore tests do not substitute for this exercise.
- [ ] Verify storage capacity, retention, export, and secure deletion policies for legal case data and audit records.

## 4. Legal-data safety

- [ ] Confirm acquisition rights and commercial reuse permission for every corpus source; a URL or public availability is not sufficient. Record separate `commercial_reuse_evidence` and `commercial_terms_checked_on` fields before marking commercial reuse allowed.
- [ ] Keep candidate/unreviewed instruments ineligible for legal retrieval. Do not mark a text verified or in force without documented source and legal review.
- [ ] Keep ALLOW_UNLINKED_LEGACY_LAW_SEARCH unset in production. Unlinked legacy-law chunks are excluded by default; the explicit =1 override is a temporary migration/testing escape hatch only and must not be used for client-facing legal answers without documented review and risk approval.
- [ ] Validate article-level extraction against the authoritative Gazette or an authorized official copy; preserve source hash, retrieval date, version and reviewer evidence.
- [ ] Have qualified Egyptian counsel review currentness, amendments, commencement dates, repeals, and representative answers before any client-facing legal use.
- [ ] Keep fictional sample data out of production and label unverified sources visibly.

## 5. Reminder delivery (code exists; production operation remains gated)

The repository now includes a tenant-local durable outbox, atomic idempotency claims, queued/sending/SMTP-accepted/failed/ambiguous states, recipient and case-access rechecks immediately before sending, and a dry-run-by-default operator scheduler. The code-level authorization and persistence paths have automated tests; this does not prove production configuration or provider behavior.

- [ ] Keep `--send` disabled until the firm has approved reminder policy, sender identity, recipient scope, retention, and operational ownership.
- [ ] Configure SMTP credentials only in the deployment secret manager; use a dedicated sender account, verified TLS, approved sender-domain SPF/DKIM/DMARC, provider quotas, and outbound firewall rules.
- [ ] Validate the tenant outbox migration on the exact staging release candidate; do not apply schema changes outside the separately approved database/storage change process.
- [ ] Test duplicate scheduler runs and concurrent workers across at least two firms against the actual staging storage configuration; verify that no reminder crosses firm boundaries.
- [ ] Exercise SMTP success, permanent failure, transient failure, ambiguous timeout, process crash/expired lease, and manual reconciliation using a controlled staging mailbox and synthetic cases.
- [ ] Deploy `tools/reminder_healthcheck.py` with an external scheduler; alert on exit codes 1 and 2, stale queued rows, expired/missing sender leases, failed/ambiguous outcomes, and unavailable tenant outboxes. Assign a named operator/on-call owner. Follow the [reminder outbox monitoring runbook](reminder_outbox_monitoring_runbook.md) for the recommended five-minute cadence, least-privilege service account, alert semantics, and reconciliation steps.
- [ ] Record the health-probe cadence, alert destination, retention, escalation path, and reconciliation evidence. Never include case content, recipient addresses, or credentials in monitoring logs.
- [ ] Confirm SMTP acceptance is not reported as inbox delivery. Keep ambiguous rows quarantined until provider evidence is reconciled; do not blindly retry.
- [ ] Complete a controlled operational rehearsal, including scheduler stop/start, alert delivery, provider outage, credential rotation, and safe disablement of sending.

## 6. Release validation

Run the repository's documented checks in a clean environment:

    python selftest.py
    python tests/test_app_separate_database_runtime.py

Also run the CI workflow and confirm all jobs pass for the exact commit being deployed. These checks are necessary but do not establish production readiness.

- [ ] Test tenant isolation with at least two independent firms and users.
- [ ] Test login throttling, session expiry/revocation, CSRF, upload limits, rate limits, and admin-only routes.
- [ ] Test backup restore and verify that deleted-case audit snapshots remain firm-scoped and admin-only. Confirm the separately managed MFA_ENCRYPTION_KEY is available before testing TOTP-secret restoration.
- [ ] Test degraded LLM behavior, timeout handling, and source-only fallback.
- [ ] Conduct an independent security assessment and remediate high/critical findings before storing client-confidential matters.

## 7. Live HTTP deployment smoke test

After deploying the exact release candidate, run the read-only public-shell probe:

```bash
python tools/deployment_http_smoke.py --base-url https://your-production-host.example --out reports/deployment-http-smoke.json
```

For local loopback testing only, add `--allow-http-loopback` and use `http://127.0.0.1:8000`. The probe requests only the public root, manifest, service worker, offline notice, and icon. It checks status/content types, no-store and security headers, HTTPS HSTS, manifest metadata, and the service-worker cache boundary. It does not authenticate, submit credentials, call matter APIs, or mutate data.

A passing probe confirms only the tested public HTTP surface at that time. It does not replace authenticated workflow tests, tenant-isolation checks, manual device QA, or independent security review.

## 8. Monitoring and incident response

- [ ] Collect access, application error, resource, disk, and backup-failure metrics without logging passwords, session tokens, case text, uploaded content, or API secrets.
- [ ] Configure alerts for repeated authentication failures, repeated 429 responses, storage exhaustion, failed backups, and elevated 5xx responses.
- [ ] Write an incident playbook for credential rotation, access revocation, evidence preservation, client notification assessment, and recovery.
- [ ] Assign an owner and review cadence for dependency updates, security patches, and legal corpus status.

## Release decision

Do not describe the product as production-ready until the unchecked items have named owners, evidence, and an explicit risk acceptance. A passing CI run alone is not a production security approval.


- [ ] Confirm every legal release candidate has a stable safe `document_id`, non-empty `official_title` and `document_type`, and links to exactly one central source record.
