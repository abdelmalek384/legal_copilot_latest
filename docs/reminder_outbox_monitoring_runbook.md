# Reminder outbox monitoring and operator runbook

This runbook operationalizes the read-only `tools/reminder_healthcheck.py` probe. The probe does not send mail, change delivery state, release leases, retry ambiguous sends, or read reminder bodies. It reports firm IDs, status counts, and timestamp-health findings only.

## Health probe contract

Run from the application release directory, using the same Python environment and database paths as the deployed application:

```bash
python tools/reminder_healthcheck.py
```

Exit codes:

| Code | Meaning | Required action |
|---:|---|---|
| 0 | Every active firm's outbox is readable and no monitored issue was found | Continue normal monitoring |
| 1 | One or more firms need operator attention | Alert and reconcile the reported firm IDs/findings |
| 2 | The probe could not complete because configuration, database access, or runtime validation failed | Treat as monitoring failure; alert immediately |

Optional controls:

```bash
python tools/reminder_healthcheck.py --stale-queued-minutes 30
python tools/reminder_healthcheck.py --out /var/lib/legal-copilot-monitor/reminder-health.json
```

The default stale-queued threshold is 30 minutes. The allowed threshold is 1–10,080 minutes. Use `--now` only for deterministic tests; production monitoring must use the system clock. If `--out` is used, keep the report outside all database paths and tenant storage. Restrict report permissions and retention. Standard output is suitable for a service manager or monitoring agent to capture.

## Recommended cadence and alert policy

- Run every **5 minutes**. This is an operational recommendation, not an application-enforced schedule.
- Alert on exit code **1** and **2**. Exit code 2 must not be treated as a healthy/empty result.
- Escalate critical findings immediately:
  - `tenant_outbox_unavailable`
  - `ambiguous_reminders_require_reconciliation`
  - `expired_or_missing_sender_lease`
- Escalate warning findings to the reminder operator:
  - `failed_reminders_present`
  - `stale_queued_reminders`
- Retain sanitized probe output according to the firm's operational log-retention policy. Do not add recipient addresses, reminder text, case names, legal matter data, SMTP credentials, session tokens, or provider secrets to monitoring output.
- Alert delivery itself must be monitored by the organization's external monitoring system. A failed health probe must not silently disappear because its notifier is unavailable.

## Linux systemd example

Adapt paths, account names, and the alert integration to the approved host. Do not copy example paths unchanged. The service account should have read access to the control-plane and tenant database files but no write access to database directories.

Create `/etc/legal-copilot/reminder-healthcheck.env` with only the three database path settings:

```ini
COPILOT_CONTROL_DB=/var/lib/legal-copilot/control_plane.sqlite3
COPILOT_TENANT_DB_ROOT=/var/lib/legal-copilot/tenants
COPILOT_CORPUS_DB=/var/lib/legal-copilot/legal_corpus.sqlite3
```

Restrict the file to root and the dedicated application/monitoring group (for example, mode `0640`). Do not place passwords, SMTP keys, or model credentials in this file.

Create `/etc/systemd/system/legal-copilot-reminder-health.service`:

```ini
[Unit]
Description=Read-only Legal Copilot reminder outbox health probe

[Service]
Type=oneshot
User=legal-copilot
Group=legal-copilot
WorkingDirectory=/opt/legal-copilot/current
EnvironmentFile=/etc/legal-copilot/reminder-healthcheck.env
ExecStart=/opt/legal-copilot/venv/bin/python tools/reminder_healthcheck.py --stale-queued-minutes 30
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ProtectSystem=strict
ReadOnlyPaths=/var/lib/legal-copilot
RestrictSUIDSGID=true
LockPersonality=true
```

Create `/etc/systemd/system/legal-copilot-reminder-health.timer`:

```ini
[Unit]
Description=Run Legal Copilot reminder health probe every five minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
AccuracySec=30s
Persistent=true
Unit=legal-copilot-reminder-health.service

[Install]
WantedBy=timers.target
```

Enable and verify:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now legal-copilot-reminder-health.timer
systemctl list-timers legal-copilot-reminder-health.timer
systemctl status legal-copilot-reminder-health.service
journalctl -u legal-copilot-reminder-health.service --since "1 hour ago"
```

The service exits nonzero when attention is required. Configure the host's monitoring agent to watch the service result and alert on failed executions; the example intentionally does not invent a notification provider or send email itself. Verify the alert path by staging one synthetic stale queued row and one synthetic expired sender lease, then remove the test rows using the approved staging reset procedure.

The service must run under a dedicated read-only OS identity. If the deployment's SQLite directory permissions prevent read-only access, correct the least-privilege group/ACL configuration; do not grant the monitor write access to make it work.

## Operator response procedure

1. Capture the report, exact deployed commit, check timestamp, and finding codes. Do not capture message bodies or recipient addresses.
2. Identify the affected firm through the protected control-plane operator interface; do not use the firm ID as a substitute for an authorization check.
3. For `tenant_outbox_unavailable`, check database file presence, permissions, migration status, storage health, and control-plane tenant mapping. Do not initialize, migrate, replace, or restore a tenant database as an automatic monitoring response.
4. For `ambiguous_reminders_require_reconciliation`, inspect the provider's delivery evidence through the approved restricted operator procedure. Do not retry until it is established whether the provider accepted the message.
5. For `expired_or_missing_sender_lease`, inspect the sender process, worker logs, and lease history. Reconcile whether an SMTP attempt may have occurred before changing delivery state.
6. For `stale_queued_reminders`, inspect scheduler ownership, scheduler last-run time, due-date windows, retry backoff, and worker availability. Do not bypass retry limits.
7. For `failed_reminders_present`, classify permanent vs transient provider failures and follow the retry/reconciliation policy. Do not expose SMTP diagnostics or secrets in general application logs.
8. Record operator, time, evidence reference, action, and outcome in the restricted operations log.

## Important limitations and release gates

- `accepted_by_smtp` means the provider accepted the message; it does not prove inbox delivery or that the recipient read it.
- The probe is a snapshot. It does not prove scheduler liveness, SMTP connectivity, correct recipient authorization, or eventual delivery.
- A successful probe does not replace a controlled staging rehearsal of concurrent scheduler runs, worker crash, provider timeout, credential rotation, and manual reconciliation.
- Do not enable `--send` in production until the reminder policy, sender identity, recipients, retention, operator ownership, and alert route have been approved.
- The probe is read-only by design. Never extend it to auto-retry, clear leases, mark failures successful, or mutate tenant state.
