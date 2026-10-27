# Manual legal-source capture record

## Purpose and safety boundary

Use this sidecar to preserve provenance for an original file obtained through a **permitted** manual route. It does not download anything, access a database, extract text, or mark a law authentic/current/approved. A matching SHA-256 proves that the file matches the recorded hash; it does not prove that the file is an official or complete law.

**Do not use manual capture to bypass login, paywalls, access restrictions, or source terms.** Public visibility and an unanswered permission request do not establish collection or commercial reuse permission. If the planned use is not clearly allowed, retain only whatever metadata and notes are permitted and keep the text out of production retrieval.

## Workflow

1. Review the specific source's access terms and the planned actions: saving, storing, extracting, indexing, retrieval, displaying, and commercial use. Record the terms URL and date checked.
2. Save the original bytes unchanged only if the method is permitted. Keep the file and its JSON sidecar together in a controlled local directory.
3. Calculate a SHA-256 digest:
   - macOS/Linux: `shasum -a 256 original.pdf`
   - Windows PowerShell: `Get-FileHash .\original.pdf -Algorithm SHA256`
4. Create a JSON sidecar using the field names below. Do not fill in publication/effective dates, Gazette issue/pages, permission states, or legal status by guessing.
5. Run the local validator:
   ```bash
   python tools/validate_manual_capture_record.py --record path/to/capture.json
   ```
6. Preserve the JSON output with the review package. Fix every error. Warnings about rights mean the file is not ready for the planned use.
7. Submit the source, original file, extracted text (if separately and lawfully produced), comparison report, and metadata for qualified Egyptian-lawyer review. Use the separate source-to-release gate before any production indexing.

## Required fields

- `document_id`, `official_title`, `source_authority`
- `source_url`, `retrieved_at` (ISO-8601 with explicit timezone; future timestamps are rejected), `acquisition_method`
- `original_file` (relative path inside the sidecar directory), `original_sha256`
- `collection_permission`: `unknown`, `permission_pending`, `allowed`, `allowed_limited`, `not_allowed`, `prohibited`, or `not_allowed_without_explicit_exception_or_license`
- `commercial_reuse_permission`: `unknown`, `allowed`, `allowed_limited`, `restricted`, `prohibited`, `not_allowed_without_explicit_exception_or_license`, or `prior_written_permission_required_per_published_terms`

Optional evidence fields:
- `terms_url`, `terms_checked_on` (must not be future-dated)
- `collection_permission_evidence_url`, `commercial_reuse_evidence_url`
- `publication_date`, `effective_date`, `repeal_date`, `gazette_issue`, `gazette_pages`
- `legal_status`: `unknown`, `under_review`, `not_yet_in_force`, `in_force`, `partially_repealed`, `repealed`, or `historical`
- `review_status`: `pending_source_review`, `pending_lawyer_review`, `verified`, or `rejected`
- `notes`

Use distinct evidence URLs for collection permission and commercial reuse permission when they have different scopes. Do not reuse an unrelated URL merely to make a gate pass. Limited, prohibited, or permission-required states are recorded but never treated as unrestricted permission by this validator.

## Example sidecar

This is a schema example only, not a real source or permission decision. Replace every placeholder with observed facts before validation.

```json
{
  "document_id": "EG-LABOUR-14-2025",
  "official_title": "قانون العمل رقم 14 لسنة 2025",
  "source_authority": "Record the actual issuing/publishing authority",
  "source_url": "https://example.gov/source-page",
  "retrieved_at": "2026-10-27T12:00:00Z",
  "acquisition_method": "manual",
  "original_file": "original.pdf",
  "original_sha256": "REPLACE_WITH_64_HEX_CHARACTERS_FROM_FILE_HASH",
  "collection_permission": "unknown",
  "commercial_reuse_permission": "unknown",
  "terms_url": null,
  "terms_checked_on": null,
  "collection_permission_evidence_url": null,
  "commercial_reuse_evidence_url": null,
  "publication_date": null,
  "effective_date": null,
  "repeal_date": null,
  "gazette_issue": null,
  "gazette_pages": null,
  "legal_status": "unknown",
  "review_status": "pending_source_review",
  "notes": "Record only facts supported by evidence."
}
```

The example intentionally starts with unknown permissions and legal status. Even if a sidecar claims `review_status: verified`, the validator treats that as an unverified assertion and always reports `retrieval_eligible: false`; it is a provenance check, not the legal release gate.
