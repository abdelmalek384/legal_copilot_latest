# Safe legacy bulk law imports

The legacy `POST /law/import` endpoint accepts bulk article passages that are not necessarily linked to a reviewed legal-document version. Such rows are therefore imported with `verified=0` and `in_force=0`, regardless of caller-supplied values for those flags. The response explicitly reports `review_required: true` and `search_eligible: false`.

This protects the legal-research search filter from treating a bulk-uploaded passage as verified law merely because an import payload asserted it. It is a compatibility/safety path, not a replacement for the legal-source registry.

## Intended workflow

1. Record the authoritative source, title, legal version, publication evidence, and provenance in the legal-source registry.
2. Preserve original text and a stable content hash when registering/importing a version.
3. Record review evidence for authenticity, extraction quality, legal status, amendment history, and relevant permissions.
4. Only use the registry's controlled review workflow to determine search eligibility; do not treat the legacy import response as a legal approval.

The legacy endpoint does not create registry links or determine that a law is current. Existing unlinked rows already in the database are not retroactively altered by this change and should be audited separately.
