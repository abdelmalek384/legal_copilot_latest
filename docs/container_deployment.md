# Container deployment (production template)

**Status:** deployment packaging and secure defaults only. This is not a production deployment, database acceptance, S3/KMS acceptance, or legal/security certification.

## Architecture and security boundary

- Build from the checked-in Python 3.12 hash-locked dependency set. The image build fails if hashes or dependency constraints do not validate.
- Run as UID/GID 10001, with a read-only container root filesystem, dropped Linux capabilities, no-new-privileges, bounded temporary storage, process/memory/CPU limits, and bounded local logs.
- Publish no host port. The service is exposed only on the pre-created legal-copilot-proxy Docker network; attach the separately managed TLS reverse proxy to that network.
- Keep the three SQLite profiles on one persistent host and run **one application replica**. Do not scale this Compose service horizontally or share local SQLite files across hosts.
- Mount application data separately from the image. The database acceptance manifest is mounted read-only. No database is created, migrated, restored, or reset by the image entrypoint.
- Original matter binaries must use the approved S3/KMS storage backend. The local filesystem adapter is not approved for production.
- Uvicorn proxy-header processing is disabled. Do not enable forwarded-header trust without a separate trusted-proxy allowlist and security review.

## Prepare a host

Use a supported Linux host with Docker Engine and the Docker Compose plugin. Create the persistent directories on the same host that will hold the SQLite profiles:

    sudo install -d -o 10001 -g 10001 -m 0700 runtime-data runtime-data/control runtime-data/tenants runtime-data/corpus
    sudo install -d -o root -g root -m 0700 secrets
    cp .env.production.example .env.production
    chmod 0600 .env.production

Edit .env.production using a secret manager or a protected operator session. Replace every placeholder. Generate the backup and MFA keys independently with the documented commands; keep them separate and backed up securely. Prefer an instance/task role for AWS access instead of static access keys. The application process must be able to read the mounted acceptance manifest as UID 10001.

Install the approved database-acceptance manifest as a regular file owned by UID/GID 10001 with mode 0400, for example: sudo install -o 10001 -g 10001 -m 0400 /protected/path/database-acceptance.json secrets/database-acceptance.json. Do not create an empty or fabricated manifest to bypass a release gate; the production release gate must validate the actual completed evidence.

Create the external proxy network and attach the TLS reverse proxy to it:

    docker network create legal-copilot-proxy

Provision the three database profiles and first firm owner using the approved maintenance/bootstrap process **before** starting the service. Do not rely on container startup to initialize a database. Complete the database acceptance manifest and place it at secrets/database-acceptance.json; it must be current, protected, and accepted by the runtime gate. The app will fail closed if the required profile databases, S3/KMS configuration, MFA policy, or acceptance evidence are missing.

## Build and start

Use an immutable image tag and keep the previous image available for rollback:

    docker compose --env-file .env.production -f compose.production.yaml config --quiet
    docker compose --env-file .env.production -f compose.production.yaml build --pull
    docker compose --env-file .env.production -f compose.production.yaml up -d
    docker compose --env-file .env.production -f compose.production.yaml ps
    docker compose --env-file .env.production -f compose.production.yaml logs --tail=100 legal-copilot

The Compose service does not publish port 8000 to the host. Configure the external reverse proxy to route HTTPS traffic to legal-copilot:8000 on the shared proxy network. Enforce TLS, request-size limits, upload timeouts, and the explicit public Host allowlist at the proxy and application layers.

## Operational gates before client data

1. Run docker compose --env-file .env.production -f compose.production.yaml exec legal-copilot python tools/deployment_preflight.py --strict --require-separate in the exact deployment environment and retain the sanitized output.
2. Run docker compose --env-file .env.production -f compose.production.yaml exec legal-copilot python tools/production_release_gate.py --database-acceptance /run/secrets/database-acceptance.json and verify every legal, benchmark, and database/storage acceptance gate against the exact image and configuration.
3. Verify the S3 bucket policy, KMS key policy, workload identity, versioning, retention and deletion controls using the approved non-destructive acceptance procedure.
4. Complete a witnessed encrypted backup, restore, rollback, staged-upload recovery and original-file recovery drill on a protected staging copy.
5. Test two-firm isolation, session revocation, upload/download authorization, background jobs, reminder monitoring and SMTP behavior against staging.
6. Complete independent security review and the required Egyptian-counsel app acceptance before legal client use.

The Docker health check requests the public application shell and reports **liveness only**. It does not prove that a firm database is healthy, S3/KMS is reachable, reminders are scheduled, backups are recoverable, or the application is legally approved. Use the separate deployment preflight, database acceptance manifest, monitoring probes and witnessed release gates for readiness.

## Updates and rollback

- Review Dependabot updates for Python packages, Docker base image and GitHub Actions. Rebuild from the lockfile and retain the build logs/SBOM according to the release policy.
- Deploy only an immutable tag whose full tests, dependency audit, CodeQL/Bandit and container build have passed on the exact commit.
- Keep the previous image tag and database/storage backup bundle available. Roll back the application image only after checking schema/profile compatibility with the database owner; never roll back or restore databases automatically as part of container restart.
- Do not run multiple Compose replicas against the same SQLite paths. A multi-host deployment requires a separately designed shared database/rate-limit architecture and fresh acceptance.

## Configuration and secrets

The .env.production.example file lists the required configuration shape, not valid credentials. Store the real .env.production with restrictive permissions and outside source control. Docker administrators can inspect container environment values; protect access to the Docker socket and host. Do not put AWS access keys, SMTP credentials, model keys, backup keys, MFA keys or client data into the image, Compose file, command line, tickets or logs.
