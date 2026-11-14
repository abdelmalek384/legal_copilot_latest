# Lawyer answer-rating and benchmark export contract

**Status (2026-11-14):** firm-local schema, submit/update/read handlers, admin listing, CSV export, and bilingual Legal Research rating controls are implemented on `main`. Focused route tests have been added. They have not been executed in this environment because GitHub Actions billing blocks hosted runners and no local checkout is available. Treat the feature as implemented but not runtime-verified.

## Purpose and boundaries

Collect firm-private lawyer assessments of generated answers. Ratings are quality feedback, not legal-source verification, counsel approval of statutory text, model-training consent, or permission to reuse firm data outside that firm. Do not feed notes or answer content into training automatically.

## Firm database model

Migration: `migrations/firm/0021_answer_ratings.sql`.

### `answer_ratings`

| Field | Type / constraint | Meaning |
|---|---|---|
| `id` | integer PK | Rating record |
| `answer_message_id` | integer FK → `research_messages.id`, RESTRICT | Exact assistant message being assessed |
| `answer_id` | text, 8–128 chars | Opaque answer ID already returned by the research message API |
| `rating` | enum: `correct`, `partially_correct`, `wrong` | Overall lawyer assessment |
| `cited_article_accuracy` | enum: `right`, `wrong`, `not_applicable` | Whether the cited article(s) support the answer |
| `expected_article_ids_json` | JSON array, default `[]` | Lawyer-selected correct article IDs; required for a benchmark label |
| `answerable` | nullable boolean | Lawyer's answerability label; null until reviewed |
| `notes` | text, max 2,000 chars | Optional reviewer explanation |
| `rated_by` | integer | Authenticated firm user ID, taken from server context |
| `created_at`, `updated_at` | timestamps | Audit timestamps |

One reviewer may have one current rating per assistant message. A subsequent submission updates that review rather than creating duplicate active labels. The unique key is `(answer_message_id, rated_by)`.

### `answer_rating_events`

Append-only event history records `created` and `updated` actions, actor ID, timestamp, and a compact JSON detail. Database triggers reject event updates/deletes. Do not put answer text, question text, client names, or free-form notes into event details.

## API contract for UI implementation

All routes are authenticated and scoped to the active firm. The server must resolve the conversation and assistant message through the trusted firm database; never accept a firm ID, reviewer ID, role, or database path from the client.

### Submit or update a rating

`PUT /research/answers/{answer_id}/rating`

Request JSON:

```json
{
  "rating": "partially_correct",
  "cited_article_accuracy": "wrong",
  "expected_article_ids": ["LABOUR-SOURCE::law:قانون العمل::article:12"],
  "answerable": true,
  "notes": "The answer cites the wrong provision; use Article 12."
}
```

Rules:
- `rating` and `cited_article_accuracy` are required enum values.
- `expected_article_ids` is an array of stable article IDs; default empty. A benchmark-ready label needs at least one expected article for answerable questions.
- `answerable` is nullable; null means not labelled.
- `notes` is optional and limited to 2,000 characters.
- `answer_id` must resolve to exactly one assistant message inside a conversation owned by the active firm. Reject user messages, unknown IDs, cross-firm IDs, and malformed stored metadata.
- Derive `rated_by` from the authenticated principal. Derive authorization from the active membership/role on the server; do not trust a submitted role.
- Return the saved rating and whether it is benchmark-ready. Do not claim the rating is approved for training.

Suggested response:

```json
{
  "rating_id": 42,
  "answer_id": "ans_opaque",
  "rating": "partially_correct",
  "cited_article_accuracy": "wrong",
  "expected_article_ids": ["LABOUR-SOURCE::law:قانون العمل::article:12"],
  "answerable": true,
  "notes": "The answer cites the wrong provision; use Article 12.",
  "benchmark_ready": true
}
```

### Export firm ratings

`GET /research/answer-ratings/export.csv`

- Admin/authorized reviewer only; enforce the active firm's trusted database context.
- UTF-8 CSV with BOM for spreadsheet compatibility; use Python's `csv` module and correct quoting.
- Export one row per current rating, joined to its exact assistant message and parent conversation.
- Required columns, in order: `rating_id, answer_id, conversation_id, answer_message_id, question, answer, rating, cited_article_accuracy, cited_article_ids, expected_article_ids, answerable, notes, rated_by, created_at, updated_at, trust_tier`.
- Resolve the immediately preceding user question in the same conversation; if no unambiguous preceding user message exists, export an empty question and set `benchmark_ready=false`.
- Derive cited article IDs from the saved assistant result metadata; do not infer article IDs from free-form citation text.
- Include `trust_tier` as a message-time snapshot: preserve explicit `source_matched`; emit `verified` only when every saved source is marked `verified=true` and `source_status=verified_operative_text`; otherwise emit `unverified`. Ignore a stored `verified` label if its source evidence is incomplete. Add `benchmark_ready` as the final column. It is true only when the question and answer are linked, the answerability label is present, and the expected article IDs are non-empty for answerable questions (or the answer is explicitly labelled unanswerable).
- Do not export other firms' data. Do not write export contents to logs. Record a count-only security audit event.

## Benchmark interpretation

- `correct` / `partially_correct` / `wrong` measure answer quality; they are not interchangeable with retrieval hit rate.
- `cited_article_accuracy=wrong` is a direct wrong-citation signal. The expected article IDs provide the answer key needed for top-3 and wrong-article scoring.
- `answerable` is required to measure abstention compliance.
- Keep all labels provisional until the designated Egyptian lawyer/reviewer role approves them under the project's benchmark review policy. Export must preserve reviewer identity and timestamps for traceability.
- The 110 curated candidate questions remain excluded from scoring. Ratings on real firm-test questions must have the required privacy/consent basis before any cross-firm aggregation or external reuse.

## Implementation notes\n\n- `PUT /research/answers/{answer_id}/rating` derives the reviewer from the authenticated principal, resolves the opaque answer ID only inside the active firm's database, and updates the reviewer's existing rating for that exact assistant message.\n- `GET /research/answers/{answer_id}/rating` returns only the current reviewer's saved rating.\n- `GET /research/answer-ratings` and `GET /research/answer-ratings/export.csv` are firm-admin-only. The CSV is UTF-8 with BOM, uses spreadsheet-formula neutralization, records count-only audit metadata, and does not log row contents.\n- The Legal Research answer panel supports save/update in Arabic and English. Firm administrators can list saved ratings and download the CSV. Trust-tier badges remain displayed by the existing answer renderer. The CSV now includes a conservative message-time `trust_tier` column compatible with the canonical AI-1 adapter.\n- `tests/test_answer_rating_routes.py` covers create/update uniqueness, append-only events, cross-firm denial, listing, CSV quoting/formula safety, and export isolation.\n\n## Acceptance and verification gates

The focused tests now exist in `tests/test_answer_rating_migration.py`, `tests/test_answer_rating_routes.py`, and `tests/test_frontend_ux_contract.py`. The route tests include fail-closed trust-tier mapping for verified, source-matched, malformed and insufficient source metadata. They have **not been executed** because the hosted runner is billing-blocked and no local checkout is available in this work session. Run the following under the supported Python 3.12 environment before treating this feature as runtime-verified:

1. Fresh firm migration and upgrade migration include tables, indexes, checks and immutable event triggers (`tests/test_answer_rating_migration.py`).
2. Create/update rating; enforce one rating per reviewer per answer; verify event append-only behavior (`tests/test_answer_rating_routes.py`).
3. Deny unknown and cross-firm answer IDs; verify authenticated reviewer identity and admin-only listing.
4. Verify export CSV quoting, UTF-8 BOM, exact columns, answer/question pairing, benchmark-ready flags, and no cross-firm leakage.
5. Verify audit logs contain counts/metadata only and never answer text or notes.
6. Run browser acceptance in Arabic and English at desktop and phone widths; physical-device acceptance remains a separate human gate.
