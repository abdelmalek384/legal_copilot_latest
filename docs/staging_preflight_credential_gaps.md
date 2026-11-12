# Staging preflight: credential gaps versus deployment configuration

**Purpose:** explain the failures expected when running the strict deployment preflight on a clean staging host with placeholder configuration. This is a planning aid, not a successful preflight, a deployment approval, or evidence that provider credentials work.

Run the check only after loading the staging environment on the target host:

```bash
python tools/deployment_preflight.py --strict
```

The preflight never prints secret values. It validates selected values and filesystem conditions; it does not authenticate to SMTP, S3/KMS, a model provider, DNS, or the public reverse proxy.

## Values that are credentials or cryptographic secrets

| Variable | Strict production requirement | Notes |
|---|---|---|
| `ADMIN_TOKEN` | Non-placeholder secret of at least 32 characters | Generate/store it through the approved secret manager. Do not commit it or use an example value. |
| `BACKUP_KEY` | Valid Fernet key | Protect separately; needed to encrypt/decrypt tenancy bundles. |
| `MFA_ENCRYPTION_KEY` | Valid Fernet key, distinct from `BACKUP_KEY` | Required in production. Do not reuse the backup key. |
| `COPILOT_EMAIL_SMTP_USERNAME` / `COPILOT_EMAIL_SMTP_PASSWORD` | Optional authentication pair | Both may be empty if the SMTP relay does not require authentication; if one is set, both must be set. Store any values in the secret manager. |
| `LLM_KEY` | Not required by preflight | Supply only if the selected endpoint requires it. Model processing remains disabled unless the separate approval flags are explicitly set to `1`. |

Static AWS access keys are not individually checked by this preflight. Prefer the staging host's approved IAM role/provider credential chain; never invent or commit AWS credentials. Bucket/KMS identifiers below are configuration, not proof of authorization.

## Required non-secret deployment configuration (not credential-only failures)

| Variable / condition | Required setting | Why it can fail on a placeholder host |
|---|---|---|
| `COPILOT_ALLOWED_HOSTS` | Explicit comma-separated hostnames/IPs; no wildcard-all | Host-header allowlisting must be enabled in production. |
| `COPILOT_SECURE_COOKIES` | `1` when the public endpoint is HTTPS | Enables secure cookies/HSTS for TLS deployment. |
| `COPILOT_PUBLIC_ORIGIN` | Exact public HTTPS origin, no path/query/fragment | Required for production origin checks. |
| `COPILOT_EMAIL_SMTP_HOST`, `COPILOT_EMAIL_FROM`, `COPILOT_EMAIL_SMTP_PORT`, `COPILOT_EMAIL_SMTP_SECURITY` | Valid relay hostname, sender address, port 1–65535, and `starttls` or `ssl` | These are endpoint/sender/transport settings, not secret values. A complete configuration still does not prove live delivery. |
| `COPILOT_OBJECT_STORAGE_BACKEND` | `s3` | Local filesystem storage is not approved for production matter binaries. |
| Original and recovery S3/KMS settings | Distinct original/recovery buckets and KMS key IDs, plus regions | Preflight requires `COPILOT_S3_BUCKET`, `COPILOT_S3_REGION`, `COPILOT_S3_KMS_KEY_ID`, `COPILOT_S3_RECOVERY_BUCKET`, `COPILOT_S3_RECOVERY_REGION`, and `COPILOT_S3_RECOVERY_KMS_KEY_ID`. Live provider acceptance is separate. |
| `MFA_ENFORCEMENT` | `admins_required` or `all_required` | Production cannot use `optional`. |
| Three database paths | Absolute, separate `COPILOT_CONTROL_DB`, `COPILOT_TENANT_DB_ROOT`, `COPILOT_CORPUS_DB` paths | Parents/directories must exist with restrictive permissions and be accessible to the service user. The check does not create them. |
| `COPILOT_DB` | Unset | The retired shared-database setting is rejected. |
| `ALLOW_UNLINKED_LEGACY_LAW_SEARCH` | Unset or not `1` | Enabling the legacy retrieval override is rejected. |

## Expected credential-related failures on an empty template

With secrets intentionally absent, expect failures for `ADMIN_TOKEN`, `BACKUP_KEY`, and `MFA_ENCRYPTION_KEY`. SMTP username/password do **not** fail when both are blank; the SMTP host/sender/transport configuration still must be complete. Any model API key is optional unless the chosen provider requires it, and the model approval flags must remain unset until the data-processing review is complete.

Other failures from an untouched template are configuration or host-readiness failures, not missing credentials. Do not classify missing S3 bucket names, regions, KMS key IDs, public origin, allowed hosts, database paths, secure-cookie policy, or MFA policy as credentials.

## Clean-machine staging acceptance

1. Create the three database parent paths and tenant root with owner-only permissions for the service identity.
2. Populate non-secret host/origin/SMTP/S3/MFA configuration from the staging operator; do not fabricate values.
3. Inject `ADMIN_TOKEN`, `BACKUP_KEY`, and a distinct `MFA_ENCRYPTION_KEY` from the protected secret manager.
4. Keep `LLM_URL`, `LLM_KEY`, `LLM_DATA_PROCESSING_APPROVED`, and `LLM_FIRM_DATA_PROCESSING_APPROVED` unset unless and until the provider and data-processing terms are approved.
5. Run strict preflight and preserve its sanitized output. Resolve every FAIL and WARN; a preflight PASS validates configuration shape only.
6. Separately verify Docker/Compose startup, reverse-proxy header overwrite, SMTP delivery, S3/KMS write/read/version recovery, MFA enrollment, backup restore, browser acceptance, and real-device acceptance.

No credentials are supplied by this document. Do not weaken strict preflight or replace missing production values with placeholders to obtain a green result.