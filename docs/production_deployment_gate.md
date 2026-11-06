# Production deployment gate

Production mode is deliberately stricter than local development. Do not deploy the shared `COPILOT_DB` compatibility configuration for a multi-firm legal product.

## Required configuration

Set `COPILOT_ENV=production` and configure all three separate database locations:

- `COPILOT_CONTROL_DB`: global identities, memberships, sessions, and platform audit.
- `COPILOT_TENANT_DB_ROOT`: per-firm database files.
- `COPILOT_CORPUS_DB`: shared legal corpus.

Do not set `COPILOT_DB` in production. The application refuses to start if production is configured with the legacy shared database or any required separate path is missing.

The release preflight also requires:

- `ADMIN_TOKEN` with sufficient entropy.
- `COPILOT_ALLOWED_HOSTS` containing explicit trusted hostnames.
- `COPILOT_SECURE_COOKIES=1` when the public endpoint is HTTPS.
- `COPILOT_PUBLIC_ORIGIN` set to the public HTTPS origin.
- `BACKUP_KEY` containing a valid Fernet key. Never print or commit the secret.

Run before deployment:

```bash
COPILOT_ENV=production python tools/deployment_preflight.py --require-separate --strict
```

This is a configuration gate, not proof that a deployment is secure. Before handling client data, complete an independent security review, witnessed backup/restore and rollback drill, monitoring/alerting setup, and access-control acceptance tests. Do not treat a passing preflight as a substitute for those checks.
