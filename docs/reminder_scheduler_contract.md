# Deadline reminder scheduler contract

## Status and boundary

The project now includes a tenant-local durable outbox (tools/reminder_outbox.py) and an operator-run scheduler (tools/reminder_service.py) in addition to the pure planner and SMTP adapter. Dry-run is the default and performs no outbox writes or email delivery. Sending requires the explicit --send flag and validated SMTP/public-origin configuration.

The scheduler resolves each firm through the trusted control-plane catalog, plans only for active memberships, limits task/deadline reminders to the assigned/creating user (or authorized firm admin) with case access, and limits court-session reminders to explicit case members. It rechecks recipient membership, case access, event state, and due date immediately before sending. Each firm's outbox resides in that firm's database; unique idempotency keys and transactional claims suppress duplicate scheduler claims. Expired in-flight leases become ambiguous rather than being silently resent.

SMTP acceptance is not proof of inbox delivery. A timeout may leave provider acceptance ambiguous; the scheduler records connection-failure outcomes as ambiguous and requires operator reconciliation rather than automatically retrying that outbox row. The SMTP adapter still performs bounded retries for transient errors within a single claimed delivery, so a provider timeout may still be ambiguous. Do not claim exactly-once email delivery.

## Normalized input

Each event has only:
- kind: task, deadline, or session;
- event_id: stable record identifier;
- due_date: canonical local calendar date in YYYY-MM-DD form;
- is_complete: explicit boolean.

The pure planner accepts a firm/scope identifier, recipient identifier, aware current timestamp, IANA timezone, and optional previously sent keys. The integrated scheduler supplies the trusted firm/user scope and persists generated keys in the firm-local outbox. Date-only deadlines remain date-only; the helper does not calculate legal deadlines or infer due dates from judgments.

## Planning rules

- Convert the current timestamp to the configured IANA timezone before comparing dates.
- Plan items due in the configured lead window, due today, or overdue.
- Skip completed events and suppress known sent keys.
- Generate stable SHA-256 keys from scope, recipient, event kind/ID, due date, and reminder window.
- Do not include client names, matter titles, case facts, or legal strategy in the plan or email.
- Sort plans deterministically.

## Local dry-run CLI

Run a plan from a JSON input file without connecting to SQLite or sending any message:

    python tools/reminder_schedule.py --input events.json --recipient-id user-123 --scope-id firm-456 --timezone Africa/Cairo --now 2026-10-26T08:00:00+00:00 --out /tmp/reminder-plan.json

The input root must be an object with an events array and optional already_sent array of idempotency-key strings. Use the exact event fields documented above. The command always returns a dry-run report, refuses to overwrite its input file, and reports delivery_performed=false. The already_sent list is only supplied input, not durable deduplication storage.

## Email adapter

The SMTP adapter in docs/reminder_email_delivery.md supports TLS-protected SMTP with a timeout, generic message content, disabled-by-default delivery, bounded retries for likely transient failures, and sanitized error codes. Status accepted_by_smtp means only that the SMTP server accepted the submission; it is not proof of inbox delivery. A timeout may leave acceptance ambiguous and retries may duplicate a message.

## Operator-run scheduler

Dry-run (no writes and no email):

    python tools/reminder_service.py --timezone Africa/Cairo

The command requires the three explicit database paths and inspects active firms through the trusted catalog. It prints only sanitized counts/warnings, not case titles or recipient email addresses.

Read-only operational status for queued, in-flight, SMTP-accepted, failed, and ambiguous rows:

    python tools/reminder_service.py --status

The status report contains per-firm counts only and does not modify the outbox.

Explicitly send queued reminders after SMTP and public-origin configuration has been approved:

    python tools/reminder_service.py --send --timezone Africa/Cairo --max-send 100

Required SMTP variables are documented in docs/reminder_email_delivery.md. COPILOT_PUBLIC_ORIGIN must be an HTTPS origin without a path, query, fragment, or credentials. Use a restricted service account and external scheduler. The command processes up to --max-send queued reminders per firm. A failed row can be explicitly requeued by idempotency key with --send --retry-failed-key KEY; ambiguous rows are not automatically retried and must be reconciled first.

## Remaining integration/release requirements

1. Configure and validate the real SMTP provider in staging; no live email was sent by automated tests.
2. Test two-firm isolation and concurrent scheduler runs against the persistence adapter before claiming deduplication is production-safe.
3. Add monitoring for failed, ambiguous, expired-lease, and stale queued records; define operator reconciliation and escalation ownership.
4. Schedule the command with a service manager/cron and alert on nonzero exit codes and missed runs.
5. Keep messages generic and links routed back to the authenticated app. Never treat SMTP acceptance as inbox delivery or as legal advice.

## Read-only monitoring and reconciliation

Use `python tools/reminder_healthcheck.py` from the same restricted service environment as the scheduler. It opens the control-plane and tenant databases in SQLite read-only mode, does not initialize or migrate schemas, and never sends or requeues reminders. Exit code 0 means no detected issue; 1 means operator attention is required; 2 means the check could not safely complete. See [reminder outbox monitoring and reconciliation](reminder_outbox_monitoring.md) for thresholds, alert codes, and operator actions.

The monitor flags stale queued rows, expired or missing sender leases, failed/ambiguous outcomes, and unavailable tenant outboxes. Ambiguous outcomes must be reconciled against provider evidence before any retry. Configure the external scheduler and alert routing in staging; this repository does not create host-level schedules or monitoring integrations.

## Operator checks

    PYTHONPATH=. python tools/test_reminder_schedule.py
    PYTHONPATH=. python tests/test_reminder_email.py
    PYTHONPATH=. python tests/test_reminder_outbox.py
    PYTHONPATH=. python tests/test_reminder_service.py

Automated tests use synthetic tenant databases and fake SMTP senders; they do not send live email. The integrated authorization and persistence paths are covered by regression tests, but the service is not production-ready until real-provider staging, scheduler monitoring, operator reconciliation, and independent review are complete.
