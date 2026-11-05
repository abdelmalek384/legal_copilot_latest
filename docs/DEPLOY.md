# Deploy Legal Copilot

This is the short operator guide for a **single-host, single-app-replica** production deployment. It is not certification or permission to use client data: finish the production checklist, legal review, independent security review, and witnessed recovery gates first. See [the full release checklist](production_deployment_checklist.md) and [container template](container_deployment.md).

## 1. Prepare the host and persistent storage

Use patched Linux, Docker/Compose or Python 3.12, a dedicated unprivileged service account, and a TLS reverse proxy. Keep the three SQLite profiles on one persistent host; do not run multiple replicas or share SQLite files across hosts. Keep secrets outside Git and protect them from Docker/socket administrators.

Set these three **distinct, absolute** paths (the legacy `COPILOT_DB` must be unset):

- `COPILOT_CONTROL_DB`: control-plane SQLite file.
- `COPILOT_TENANT_DB_ROOT`: directory containing firm databases.
- `COPILOT_CORPUS_DB`: shared legal-corpus SQLite file.

Also set `COPILOT_ENV=production`, `COPILOT_ALLOWED_HOSTS` to the exact public hostnames (comma-separated), `COPILOT_SECURE_COOKIES=1`, and `COPILOT_PUBLIC_ORIGIN=https://your-host.example` (origin only: no path, credentials, query or fragment). Set `COPILOT_DATABASE_ACCEPTANCE_FILE` to the protected, complete, accepted operational-evidence manifest. Production startup also requires `ADMIN_TOKEN` (random, at least 32 characters), a valid Fernet `BACKUP_KEY`, and `MFA_ENFORCEMENT=admins_required` or `all_required`.

## 2. Proxy and HTTPS

Terminate TLS at the maintained reverse proxy; redirect HTTP to HTTPS. Do not expose port 8000 publicly. Set the proxy's Host header and **overwrite** `X-Forwarded-For` with the actual connecting peer; for one Nginx edge proxy:

```nginx
location / {
    proxy_pass http://legal-copilot:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $remote_addr;
}
```

Set `COPILOT_TRUSTED_PROXIES` to that proxy's exact container IP or smallest controlled CIDR; leave it empty for direct connections. Never enable Uvicorn `--proxy-headers`. Enforce upload size/time limits at the proxy too.

## 3. Secrets, email and public links

Generate independent keys: `python manage.py genkey` for `BACKUP_KEY`, and `python manage.py gen-mfa-key` for `MFA_ENCRYPTION_KEY`. Never reuse or commit either key; preserve both securely for recovery. Set `COPILOT_PUBLIC_BASE_URL` to the clean public HTTPS base URL used in invitation/recovery links.

For identity email set `COPILOT_EMAIL_SMTP_HOST`, `COPILOT_EMAIL_SMTP_PORT` (default 587), `COPILOT_EMAIL_SMTP_SECURITY` (`starttls` or `ssl`), `COPILOT_EMAIL_FROM`, and the username/password together when authentication is required. For reminders set `REMINDER_SMTP_HOST`, `REMINDER_SMTP_PORT` (default 587), `REMINDER_SMTP_SECURITY` (`starttls` or `ssl`), `REMINDER_SMTP_SENDER`, `REMINDER_SMTP_USERNAME`, and `REMINDER_SMTP_PASSWORD`. Use encrypted transport; production identity email forbids plaintext. SMTP configuration checks do not prove delivery: test with an operator-controlled mailbox.

Production matter-file storage uses S3/KMS: configure `COPILOT_OBJECT_STORAGE_BACKEND=s3`, `COPILOT_S3_BUCKET`, `COPILOT_S3_REGION`, and `COPILOT_S3_KMS_KEY_ID`; use workload identity rather than static AWS keys. Configure the separate recovery archive bucket/region/KMS key when using the archive workflow.

## 4. First firm owner and start

Before starting the app, provision/accept the three profile databases and create the first firm owner through the reviewed bootstrap command (fresh, empty installation only):

```sh
python manage.py init-tenancy --firm-name "Firm name" --owner-name "Owner name" --owner-email "owner@example.com"
```

It prompts for the owner's password. It creates a firm administrator, **not** a platform administrator. Do not use this command to replace existing identities. Install the real acceptance manifest at the configured path; never fabricate one to pass startup.

Start the reviewed immutable image using the [container deployment template](container_deployment.md), then run `python tools/deployment_preflight.py --strict` and the aggregate release gate against the exact release commit/configuration. Keep the app quiesced during the backup snapshot window; create an encrypted bundle with `python manage.py backup-tenancy /protected/backup-dir --quiesced`, verify it with `python manage.py verify-tenancy-backup /path/to/bundle`, and perform a witnessed restore drill before production. Keep backups encrypted, versioned, off-host, access-restricted, and regularly restore-tested.

## 5. Is it healthy? (setup-health screen)

- [ ] **Invitation/recovery SMTP:** host, sender, port, security and paired credentials are configured; controlled-mailbox delivery has been tested.
- [ ] **Reminder SMTP:** all required reminder SMTP values validate; controlled-mailbox delivery has been tested.
- [ ] **Public HTTPS origin:** `COPILOT_PUBLIC_ORIGIN` is a bare HTTPS origin and matches the public host.
- [ ] **MFA key:** `MFA_ENCRYPTION_KEY` is valid Fernet material and differs from `BACKUP_KEY`.
- [ ] All three profile database paths are distinct, persistent and accessible to the service account.
- [ ] `COPILOT_DB` is unset; allowed hosts and trusted-proxy entries are correct.
- [ ] The accepted database-operations manifest exists at `COPILOT_DATABASE_ACCEPTANCE_FILE`.
- [ ] S3/KMS object storage is configured and original-file access is tested.
- [ ] Encrypted backup verification and a witnessed restore/rollback drill have passed.
- [ ] Strict deployment preflight and the exact-commit production release gate pass.

The first four items correspond to the setup-health screen. Its SMTP checks validate configuration only; they do not establish mailbox delivery. A green liveness probe is not operational or legal readiness.
