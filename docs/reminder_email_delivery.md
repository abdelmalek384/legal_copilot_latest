# Privacy-safe reminder email adapter

## Status

The adapter in tools/reminder_email.py is a non-database delivery component. It is disabled by default, has no scheduler or durable queue, and does not claim exactly-once delivery. Do not enable it for production until the database workstream provides an atomic idempotency claim, audit persistence, authorization checks, and operator monitoring.

## Configuration

Set these in the deployment secret manager, never in source control:

- REMINDER_SMTP_HOST: approved SMTP host.
- REMINDER_SMTP_PORT: port (default 587).
- REMINDER_SMTP_SENDER: approved sender address.
- REMINDER_SMTP_USERNAME and REMINDER_SMTP_PASSWORD: provider credentials.
- REMINDER_SMTP_SECURITY: starttls (default) or ssl.
- REMINDER_SMTP_TIMEOUT: seconds, 1–60 (default 10).

Use a dedicated least-privilege sender account. Verify provider terms, outbound firewall policy, sender-domain SPF/DKIM/DMARC, secret rotation, and rate limits before enabling delivery.

## Use and semantics

Call send_reminder_email(..., enabled=True) only after the caller has authenticated and authorized the recipient and atomically claimed the reminder idempotency key. The default is enabled=False, which performs no delivery.

The adapter accepts only a reminder type, date, and supported reminder window. It does not include client names, matter titles, case facts, or strategy. The application URL must be HTTPS and contain no credentials, query, or fragment. SMTP connection security uses certificate verification.

Return statuses are deliberately precise:

- disabled: no attempt was made.
- accepted_by_smtp: the SMTP server accepted the message submission; this does not prove inbox delivery.
- failed: retries ended or a permanent error occurred. Only a sanitized error code is returned; provider response text and credentials are not returned.

Retries are bounded to 1–5 attempts with exponential backoff for likely transient connection or SMTP 4xx failures. Authentication failures and SMTP 5xx failures are not retried. A timeout can occur after a provider accepted a message, so retries can still duplicate an email. Durable idempotency and reconciliation are mandatory before scheduled production use.

## Tests

Run:

    PYTHONPATH=. python tests/test_reminder_email.py
    PYTHONPATH=. python tests/test_reminder_schedule.py

These tests use a fake sender. They do not send email or prove a real provider configuration works.

## Operator runbook before production

1. Confirm the authenticated scheduler supplies only events visible to the recipient in the correct firm scope.
2. Confirm the database workstream implements an atomic idempotency claim and durable queued/sent/failed states; test concurrent runs.
3. Configure credentials in the secret manager and verify TLS, sender-domain policy, quotas, and allowed recipients in a staging environment.
4. Keep delivery disabled until a controlled test is approved. Use a dedicated test mailbox and non-client test records.
5. Monitor counts for attempted, SMTP-accepted, failed, exhausted-retry, and ambiguous-timeout outcomes without logging message bodies or secrets.
6. For a failure, inspect the sanitized status and provider dashboard. Reconcile ambiguous timeouts before retrying manually.
7. Rotate credentials after suspected exposure and disable delivery immediately if unexpected recipients or sensitive content are observed.

This adapter is not a production reminder service by itself. It does not query matters, authorize recipients, persist delivery history, or guarantee deduplication.
