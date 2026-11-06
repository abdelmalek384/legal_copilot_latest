# Firm data export contract

The firm-admin ZIP export is available only in the separate-database runtime. It binds to the authenticated user's active firm; it does not accept a caller-supplied firm ID. Demo firms are excluded. The route is limited to two requests per hour and returns a no-store ZIP stream. A successful build writes a tenant-local security audit event.

## Included data

- Firm record and profile; active memberships; invitation metadata and identity lifecycle events (never raw invitation tokens).
- Subscription plan/state, payment-submission metadata, subscription audit events, firm usage aggregates/events and setup-test metadata.
- Cases, clients as recorded on matters, case membership, tasks, notes, events, deadlines, hearings/sessions, fees, invoices, invoice lines/payments/events, and case-deletion audit snapshots.
- Documents, extraction review history, matter chunks, research conversations/messages, answer-correction records, product feedback, security audit events, reminder deliveries/attempts/preferences, and original-file hold/deletion history.
- original_file_objects.csv records object metadata and lifecycle state. original_files_manifest.csv records whether each original binary was included.

## Original documents and attachments

Ready original-file objects are included as original_files/<document-id>-<safe-name> only after storage integrity verification and a second SHA-256/byte-size check on the exact bytes written to the archive. Legal holds do not prevent export. Staged or quarantined objects are not included as bytes; the manifest records their state and exclusion reason. If ready originals exceed the 250,000,000-byte aggregate limit, the export fails closed with HTTP 413 rather than returning a partial archive. If integrity verification fails, the export fails closed with HTTP 503.

The current payment-submission schema stores transfer references and review metadata, not uploaded payment-proof attachments. There are therefore no payment-proof binaries in the current export contract.

## Deliberate exclusions

- Password hashes, MFA/TOTP secrets, recovery-token hashes, invitation-token hashes, session tokens/cookies, and platform operator credentials.
- Shared legal-corpus records and source material; these are not firm-owned tenant data.
- Raw external mailbox contents or provider-side delivery logs; the application exports only the reminder metadata it stores.
- Original binaries that are staged or quarantined, as described above; their metadata and manifest status remain included.

CSV cells are neutralized against spreadsheet formula injection. The archive is streamed from a spooled temporary file so a firm export does not require the complete ZIP to remain in process memory. No production acceptance or independent penetration test is implied by automated CI.