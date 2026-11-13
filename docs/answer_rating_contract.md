# Answer rating contract

**Status:** ready for AI-2 integration  
**Version:** 1.0  
**Purpose:** a stable, minimal interchange contract for human review of Legal Copilot answers. This contract records reviewer judgments; it does not itself approve legal content or promote a source's trust tier.

## Required fields

Every rated answer is one CSV record with these columns, in this exact order:

| Column | Type / allowed values | Meaning |
|---|---|---|
| `answer_id` | non-empty string | Stable unique identifier for the answer being rated. Preserve the ID across exports and corrections. |
| `answer_rating` | `correct`, `partial`, `wrong` | Overall assessment of the answer against the cited source material and question. |
| `cited_article_rating` | `right`, `wrong` | Whether the cited article(s) are the correct legal provision(s) for the answer. Use `wrong` if a material citation is incorrect or irrelevant. |
| `notes` | string; may be empty | Short explanation, correction, missing qualification, or reason for the rating. Do not put personal/sensitive client information here. |
| `rater` | non-empty reviewer identifier | Stable reviewer ID or approved reviewer handle. Do not use a display name as an authentication mechanism. |
| `timestamp` | ISO 8601 timestamp with timezone | Time the rating was submitted, e.g. `2026-11-13T20:00:00Z`. |
| `trust_tier` | `verified`, `source_matched`, `unverified` | Trust tier attached to the answer's underlying legal source at rating time. This is a recorded snapshot, not a reviewer action that changes source status. |

### CSV header

```csv
answer_id,answer_rating,cited_article_rating,notes,rater,timestamp,trust_tier
```

## Export format

- Export as **CSV, UTF-8**. For spreadsheet compatibility, UTF-8 with BOM is recommended; the file remains a CSV.
- Use the exact header and column order above. Include one record per answer rating.
- Follow RFC 4180-style CSV escaping: quote fields containing commas, quotes, or line breaks; represent an embedded quote as two quotes.
- Use ISO 8601 timestamps with an explicit timezone. Store UTC with `Z` where possible.
- Empty `notes` is allowed. All other fields are required.
- Do not silently coerce unknown enum values. Reject the row and report the invalid field.
- Do not merge multiple answers into one record. If an answer is re-rated, preserve the prior record and add a new rating event or use the product's explicit revision mechanism.

## Validation helper

The repository includes `tools/validate_answer_ratings.py` for validating an exported file before AI-2 imports or stores it:

```bash
python tools/validate_answer_ratings.py path/to/answer-ratings.csv
```

It accepts UTF-8 with or without BOM, requires the exact header/order, validates required fields and enum values, and rejects timestamps without an explicit timezone. It does not authenticate raters, authorize a trust-tier change, or verify legal correctness. Its regression tests are in `tests/test_validate_answer_ratings.py` (not yet executed).

## Rating guidance

- **correct:** materially answers the question accurately, with the necessary qualifications and support.
- **partial:** contains useful correct material but omits a material issue, qualification, or part of the requested answer.
- **wrong:** materially incorrect, misleading, unsupported, or answers a different question.
- **cited article right:** the cited article is relevant and supports the proposition for which it is cited.
- **cited article wrong:** at least one material cited article is incorrect, irrelevant, or does not support the proposition. Explain which citation in `notes`.

## Trust and legal-review safeguards

- The trust tier must be copied from the answer/source metadata; a rater must not upgrade it by selecting a value in the rating UI.
- `source_matched` means machine/source matching only; it does **not** mean lawyer-reviewed or legally verified.
- Do not label any Egyptian-law source `verified` without the project's required qualified Egyptian-lawyer sign-off and recorded evidence.
- A rating is an evaluation record, not legal advice, a source verification, or permission to use restricted material.
- Evaluation datasets marked `machine-proposed, unapproved` or `unreviewed` must not be treated as approved labels or used to claim benchmark performance.

## Example record

```csv
ans-000123,partial,right,"Correct article but omits the exception in the final paragraph",reviewer-07,2026-11-13T20:00:00Z,source_matched
```
