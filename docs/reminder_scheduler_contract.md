# Deadline reminder scheduler contract (non-database foundation)

## Status and boundary

The planner in tools/reminder_schedule.py and SMTP adapter in tools/reminder_email.py are non-database components. They do not query SQLite, authorize users, persist sent records, or guarantee deduplication. The email adapter is disabled by default. Neither a planned reminder nor SMTP acceptance means the user received or read an email.

## Normalized input

Each event has only:
- kind: task, deadline, or session;
- event_id: stable record identifier;
- due_date: canonical local calendar date in YYYY-MM-DD form;
- is_complete: explicit boolean.

The caller supplies a firm/scope identifier, recipient identifier, aware current timestamp, IANA timezone, and previously sent idempotency keys. Scope is included in the idempotency key. Date-only deadlines remain date-only; this helper does not calculate legal deadlines or infer due dates from judgments.

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

## Integration requirements before real delivery

1. The authenticated request/scheduler must prove recipient authorization and filter firm-scoped events before planning or sending.
2. The database-focused workstream must provide an atomic idempotency claim and durable queued/sent/failed states before production scheduling. Do not add schema or migration changes in this non-database workstream.
3. Connect the adapter only after the durable claim, then persist attempts, SMTP acceptance, timestamps, provider identifiers if available, and sanitized failures.
4. Notification content should remain generic and link back to the authenticated application.
5. Monitor failed delivery, retry exhaustion, scheduler lag, and stale unsent records; reconcile ambiguous timeouts before manual retries.
6. Test two-firm isolation and concurrent scheduler runs against the actual persistence adapter before claiming deduplication is production-safe.

## Operator checks

    PYTHONPATH=. python tests/test_reminder_schedule.py
    PYTHONPATH=. python tests/test_reminder_email.py

These tests use local/fake inputs and do not send live email. The reminder system is not production-ready until authorization, persistence, monitoring, real-provider staging tests, and concurrent deduplication tests are complete.
