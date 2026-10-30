# Reminder outbox monitoring and operator reconciliation

## Purpose and safety

`tools/reminder_healthcheck.py` is a read-only health probe for the tenant-local reminder outbox. It is intended for an external scheduler or monitoring agent. It reads active firm IDs from the control-plane catalog and only counts outbox states and evaluates timestamps in each mapped firm database.

It does not initialize databases, apply migrations, enqueue reminders, send email, retry rows, or change any state. It does not read message bodies, client names, matter titles, or recipient email addresses. It opens SQLite files in read-only mode and enables `query_only`.

The health result is an operational signal, not proof of delivery. `accepted_by_smtp` means only that the SMTP server accepted a submission; it does not establish inbox delivery.

## Run

Configure the three separate database paths in the process environment, then run:

```bash
PYTHONPATH=. python tools/reminder_healthcheck.py
```

Optional controls:

```bash
PYTHONPATH=. python tools/reminder_healthcheck.py --stale-queued-minutes 30
PYTHONPATH=. python tools/reminder_healthcheck.py --now 2026-10-30T14:00:00+00:00
PYTHONPATH=. python tools/reminder_healthcheck.py --out /var/lib/legal-copilot/reports/reminder-health.json
```

The report contains only firm IDs, status counts, stale queue counts, expired/missing sender lease counts, and sanitized finding codes. Do not place the report under database storage.

## Exit codes and alert policy

- `0`: no detected outbox health issue for scanned active firms.
- `1`: operator attention is required.
- `2`: the check could not safely complete (configuration, catalog, storage, or database access problem).

The default stale-queue threshold is 30 minutes. Tune it to the actual scheduler cadence and retry policy; a threshold shorter than the scheduler interval causes false alarms.

The following findings make the check unhealthy:

| Finding | Severity | Operator action |
|---|---|---|
| `tenant_outbox_unavailable` | Critical | Verify the firm's catalog state, tenant database availability, and applied outbox migration. Do not recreate or rebind the database automatically. |
| `ambiguous_reminders_require_reconciliation` | Critical | Check the SMTP provider's message trace using the attempt timestamp/provider metadata available to authorized operators. Determine whether submission was accepted before any retry. |
| `expired_or_missing_sender_lease` | Critical | Inspect scheduler process/host health and the individual outbox attempt. Expired sends are ambiguous by design; do not blindly requeue. |
| `stale_queued_reminders` | Warning | Check scheduler cadence, last successful run, provider configuration, and queue eligibility. |
| `failed_reminders_present` | Warning | Review sanitized error codes and provider status. Retry only a confirmed retryable failed row using the approved operator procedure. |

## Operator reconciliation

1. Run `python tools/reminder_service.py --status` to get the existing per-firm state counts. The command is read-only.
2. Use the health report to identify the firm and condition; it intentionally does not reveal recipient or matter information.
3. For ambiguous rows, reconcile with the SMTP provider's logs and preserve the outcome. If acceptance cannot be established, escalate rather than assume failure.
4. For an expired `sending` lease, determine whether the sender process died before or after contacting SMTP. Never treat lease expiry as proof that no email was sent.
5. Failed rows may be explicitly retried only after confirming the cause is transient and recipient authorization is still valid. The scheduler rechecks authorization at send time.
6. Record operator, time, firm, finding code, evidence reference, decision, and any approved action in the firm's operational incident log. Do not copy client data or secrets into monitoring tickets.
7. Escalate repeated failures, unexplained tenant-unavailable findings, unexpected recipients, or any evidence of cross-firm leakage. Disable sending while investigating suspected authorization or content disclosure.

## External scheduling

Run the health probe at a cadence aligned with the reminder scheduler (for example, every 5–10 minutes if the scheduler is expected to run every 5 minutes). Alert on exit code 1 or 2. Send probe output to a restricted monitoring destination with a short retention period; it contains firm identifiers and should not be public.

This repository does not configure the host's cron/systemd/monitoring provider or send alert notifications. The operator must provision the service account, environment, cadence, alert routing, and on-call ownership in staging before production.

## Release gate still outstanding

This tooling does not complete live SMTP staging, two-firm concurrent scheduler testing, monitoring-provider integration, operator on-call assignment, or witnessed incident/recovery exercises. Those require the deployment environment and its responsible operator. Keep reminder delivery disabled until those gates pass.
