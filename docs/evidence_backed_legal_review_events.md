# Evidence-backed legal review events

The authenticated API exposes two platform-legal-reviewer endpoints. Access requires an explicit `platform_reviewer` or `platform_admin` assignment in the control-plane `user_platform_roles` table. A firm-admin role, email match, or deployment allowlist does not grant platform-review authority.

- `GET /legal-review/versions/{version_id}/events` — return the version metadata and chronological review-event history.
- `POST /legal-review/versions/{version_id}/events` — append a review event.

The request body accepts `review_type` (`source_authenticity`, `extraction_quality`, `legal_status`, `amendment_history`, `licensing`, or `lawyer_approval`), `outcome` (`pending`, `pass`, `fail`, or `needs_correction`), optional notes, and an optional HTTPS evidence URL. A `pass` event requires an HTTPS URL without embedded username/password credentials. The URL is stored as evidence supplied by the reviewer; the service does not fetch it or independently establish its authenticity.

## Safety and semantics

- Both endpoints require an authenticated identity with a current platform reviewer/admin role and use the application's normal CSRF protections for writes. Platform roles are separate from firm roles and must be granted and revoked through the controlled platform-role lifecycle.
- A review event is an append-only workflow record. Creating an event never changes `review_status`, `legal_status`, or any verification flag.
- A `pass` outcome means the reviewer recorded that outcome; it is not proof that the underlying legal conclusion is correct.
- This API does not approve an instrument, certify that it is currently in force, change search eligibility, or grant source-collection/commercial-reuse permission.
- Missing evidence must remain unresolved. Reviewers should link to the original official publication or other relevant evidence and describe what was actually examined.
