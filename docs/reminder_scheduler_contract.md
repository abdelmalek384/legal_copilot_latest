# Deadline reminder scheduler contract (non-database foundation)

## Status and boundary

This is a non-database planning contract, not a working notification service. The pure helper in tools/reminder_schedule.py accepts normalized records from a caller that has already authenticated the recipient and filtered events to that recipient's permitted matters. It does not query SQLite, send email/SMS/WhatsApp, persist sent records, retry failures, or claim delivery.

## Normalized input

Each event has only:
- kind: task, deadline, or session;
- event_id: stable record identifier;
- due_date: canonical local calendar date in YYYY-MM-DD form;
- is_complete: explicit boolean.

The caller supplies a firm/scope identifier, recipient identifier, an aware current timestamp, the IANA timezone for the recipient/firm policy, and previously sent idempotency keys. Scope is included in the idempotency key so a user who belongs to multiple firms cannot accidentally suppress an otherwise identical event in another firm. Date-only deadlines remain date-only; this helper does not calculate legal deadlines or infer a due date from a judgment or event.

## Planning rules

- Convert the current timestamp to the configured IANA timezone before comparing calendar dates.
- Produce a plan for items due in the configured lead window (default one day), due today, or overdue.
- Skip completed events and suppress keys supplied in the sent-key set.
- Generate a stable SHA-256 idempotency key from the firm/scope, recipient, event kind/ID, due date, and reminder window. The overdue window is stable across repeated daily runs; changing a due date creates a new key.
- Do not include client names, matter titles, case facts, or legal strategy in the planned payload.
- Sort the plan deterministically to make dry-run output diffable.

## Integration requirements before real delivery

1. The authenticated request/scheduler layer must prove recipient authorization and filter firm-scoped events before calling this helper.
2. A durable persistence layer must atomically claim an idempotency key before sending and record queued/sent/failed states. The database-focused workstream must approve any schema or transaction changes.
3. Add an explicit provider adapter (email first) with timeouts, bounded retries/backoff, sanitized errors, provider message IDs, and permanent-failure handling. Never treat a planned item or a timeout as delivered.
4. Notification content should be generic by default and link back to the authenticated application. Do not put client names, matter facts, or legal strategy in email subject/body.
5. Add monitoring for failed delivery, retry exhaustion, scheduler lag, and stale unsent records. Operators need a manual retry/reconciliation runbook.
6. Test two-firm recipient isolation and concurrent scheduler runs against the actual persistence adapter before claiming deduplication is production-safe.

## Operator check

Run the unit tests with the command:

    PYTHONPATH=. python tests/test_reminder_schedule.py

The helper is safe to use for dry-run planning only. It does not complete issue #474 or make deadline reminders production-ready.
