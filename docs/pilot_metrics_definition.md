# Pilot usage metric definitions

The platform pilot dashboard reports weekly, firm-scoped usage aggregates.

- **Successful sign-ins** is an event count of successful authentications attributed to the user's default firm. Repeated sign-ins by one person increment the count more than once.
- **Weekly active users (WAU)** is not currently measured. The platform does not infer distinct people from sign-in event counts.
- Case, deadline, answer, invoice and correction metrics are event counts for their respective successful workflows.
- Demo firms are excluded from platform pilot aggregates. Firm metrics are visible only to platform operators.
- The aggregate table stores counts by firm, week and metric; it does not store user IDs, matter IDs, client names, question text or answer content.

Do not describe successful sign-ins as unique active users in reports, pricing evidence or customer-facing material.
