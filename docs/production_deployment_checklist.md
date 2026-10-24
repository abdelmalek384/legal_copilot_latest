# Production deployment checklist

This checklist is a release gate, not a certification. Completing it does not replace an independent security review, privacy/legal review, or testing with real operational data.

## 1. Runtime and network boundary

- [ ] Use a supported, patched Python runtime and install dependencies from a reviewed, pinned deployment lockfile.
- [ ] Run the app as a dedicated unprivileged OS account. Do not run it as root.
- [ ] Bind Uvicorn to loopback or a private interface only; do not expose port 8000 directly to the public internet.
- [ ] Terminate TLS at a maintained reverse proxy and redirect HTTP to HTTPS.
- [ ] Configure the proxy to overwrite, not append blindly to, forwarded headers. The application currently uses the direct peer address for rate limiting and does not trust `X-Forwarded-For`; do not enable proxy-header trust without an explicit trusted-proxy allowlist and deployment tests.
- [ ] Set a request-body size limit and upload timeout at the proxy as well as the application's upload validation.
- [ ] Restrict inbound traffic to the proxy and restrict outbound traffic to required services (including the configured LLM endpoint).

## 2. Secrets and identity

- [ ] Set `ADMIN_TOKEN` to a randomly generated secret of at least 32 characters using the deployment secret manager. Never put it in source control, images, tickets, or logs.
- [ ] Keep `LLM_KEY` and any other credentials in the secret manager; do not expose them to the browser.
- [ ] Keep `LLM_DATA_PROCESSING_APPROVED` unset until the exact configured endpoint/model and its data-handling terms have been reviewed and approved for the intended data class. Set it to `1` only with documented approval; the setting is an operator attestation, not a technical privacy guarantee.
- [ ] Use unique administrator credentials, a strong password, and least-privilege role assignment.
- [ ] Establish a documented process for administrator offboarding, password reset, and secret rotation.
- [ ] Until 2FA and self-service recovery are implemented and reviewed, document this limitation and apply compensating controls to administrator access.

## 3. Database, uploads, and backups

- [ ] Set `COPILOT_DB` to an absolute path on a persistent, access-controlled volume.
- [ ] Restrict database, WAL/SHM files, and backup directories to the application account; encrypt the underlying disk/volume.
- [ ] Do not deploy multiple hosts with separate local SQLite databases and assume rate limits or data are shared. SQLite-backed rate limits coordinate workers only when they share the same database file; separate hosts need a shared rate-limit service and an appropriate database architecture.
- [ ] Schedule encrypted backups outside the application host. Store the backup key separately from the backups.
- [ ] Test restoration to an isolated location before release and at regular intervals; document recovery-point and recovery-time objectives.
- [ ] Verify storage capacity, retention, and secure deletion policies for legal case data and audit records.

## 4. Legal-data safety

- [ ] Confirm acquisition rights and commercial reuse permission for every corpus source; a URL or public availability is not sufficient.
- [ ] Keep candidate/unreviewed instruments ineligible for legal retrieval. Do not mark a text verified or in force without documented source and legal review.
- [ ] Keep `ALLOW_UNLINKED_LEGACY_LAW_SEARCH` unset in production. Unlinked legacy-law chunks are excluded by default; the explicit `=1` override is a temporary migration/testing escape hatch only and must not be used for client-facing legal answers without documented review and risk approval.
- [ ] Validate article-level extraction against the authoritative Gazette or an authorized official copy; preserve source hash, retrieval date, version and reviewer evidence.
- [ ] Have qualified Egyptian counsel review currentness, amendments, commencement dates, repeals, and representative answers before any client-facing legal use.
- [ ] Keep fictional sample data out of production and label unverified sources visibly.

## 5. Release validation

Run the repository's documented checks in a clean environment:

```bash
python selftest.py
python api_test.py
```

Also run the CI workflow and confirm all jobs pass for the exact commit being deployed. These checks are necessary but do not establish production readiness.

- [ ] Test tenant isolation with at least two independent firms and users.
- [ ] Test login throttling, session expiry/revocation, CSRF, upload limits, rate limits, and admin-only routes.
- [ ] Test backup restore and verify that deleted-case audit snapshots remain firm-scoped and admin-only.
- [ ] Test degraded LLM behavior, timeout handling, and source-only fallback.
- [ ] Conduct an independent security assessment and remediate high/critical findings before storing client-confidential matters.

## 6. Monitoring and incident response

- [ ] Collect access, application error, resource, disk, and backup-failure metrics without logging passwords, session tokens, case text, uploaded content, or API secrets.
- [ ] Configure alerts for repeated authentication failures, repeated 429 responses, storage exhaustion, failed backups, and elevated 5xx responses.
- [ ] Write an incident playbook for credential rotation, access revocation, evidence preservation, client notification assessment, and recovery.
- [ ] Assign an owner and review cadence for dependency updates, security patches, and legal corpus status.

## Release decision

Do not describe the product as production-ready until the unchecked items have named owners, evidence, and an explicit risk acceptance. A passing CI run alone is not a production security approval.
