# Pilot usage metric definitions

The platform pilot dashboard reports weekly, firm-scoped usage aggregates.

- **Successful sign-ins** is an event count of successful authentications attributed to the user's default firm. Repeated sign-ins by one person increment the count more than once.
- **Weekly active users (WAU)** is the number of distinct users in a firm who generated at least one successful metered product-workflow event during the UTC Monday-to-Sunday week. Qualifying events are successful research queries, document uploads, OCR processing, and draft generation. Repeated events by one person count once; successful sign-ins alone do not qualify.
- Case, deadline, answer, invoice and correction metrics are event counts for their respective successful workflows.
- Demo firms are excluded from platform pilot aggregates. Firm metrics are visible only to platform operators.
- WAU is derived on demand from the existing append-only `firm_usage_events` ledger using `COUNT(DISTINCT user_id)` grouped by firm and UTC week. The distinct user IDs remain in that access-controlled usage ledger; they are not copied into the pilot aggregate table, API response, dashboard, or CSV export.
- The aggregate pilot table stores counts by firm, week and metric; it does not store user IDs, matter IDs, client names, question text or answer content.

Do not describe successful sign-ins as unique active users in reports, pricing evidence or customer-facing material. When presenting WAU, retain the qualifying-workflow definition above; it is not a count of sign-in events or every authenticated page view.
