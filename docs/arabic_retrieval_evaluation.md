# Arabic Retrieval & Citation Evaluation (RSH-02)

## Purpose

Provide a reproducible measurement harness for Arabic legal retrieval and citation behavior. This is a measurement tool, not a legal verifier. It must not invent expected answers, sources, pin-cites, or current-law conclusions.

## Current state

- `tests/legal_eval/practice_questions.seed.jsonl` contains discovery/evaluation-question seeds, not approved ground truth.
- Seed questions are marked `needs_lawyer_review`, have no expected answer, and have no expected source IDs. The evaluator excludes them from scoring.
- `tests/legal_eval/runs.example.jsonl` is intentionally empty apart from an explanatory comment. No real run results or lawyer-approved labels are claimed.
- Add reviewed labels only after a qualified Egyptian-law reviewer records their name/date and identifies exact expected source IDs. Pin-cite labels are optional but should be exact and evidence-backed.

## Reviewed question record

The evaluator requires:

- `id`, `practice_area`, and `question_ar`
- `review_status` equal to `lawyer_reviewed` or `approved_for_evaluation`
- `reviewer_name` and `review_date`
- non-empty `expected_source_ids`
- explicit boolean `answerable`
- `must_abstain_if_unverified: true`
- optional `expected_pin_cites`, as a list of objects with non-empty string `source_id` and `pin_cite` values

Do not mark a question reviewed merely to make it count. Keep the seed file unlabelled until the review occurs.

## Run record

One JSON object per question in `runs.example.jsonl`:

```json
{
  "question_id": "Q-ID-FROM-REVIEWED-SET",
  "retrieved_source_ids": ["SOURCE-ID-1", "SOURCE-ID-2"],
  "citations": [
    {"source_id": "SOURCE-ID-1", "pin_cite": "Article 12"}
  ],
  "abstained": false,
  "used_unverified_source": false
}
```

The API runner now emits this scoring schema directly (`question_id`, `retrieved_source_ids`, `citations`, `abstained`, and `used_unverified_source`) while retaining its diagnostic fields (`answer`, `source_summary`, `invalid_citation_indices`, and `requested_as_of`). A visible citation whose source has no stable ID is listed as invalid. Missing or non-verified source status is treated conservatively as unverified. The example is not a real result; do not copy placeholder IDs into the measured dataset. If the optional `invalid_citation_indices` field is supplied, it must be a list of unique positive integers; those markers count against citation precision and are reported separately.

## Metrics

- **Recall@k:** mean fraction of reviewer-labelled relevant source IDs found in the top k unique retrieved sources.
- **MRR@k:** mean reciprocal rank of the first relevant source, with zero if no relevant source appears in the first k.
- **Citation precision:** fraction of emitted citation records and invalid visible citation indices that are supported. A source citation is correct only if its ID is both in the reviewed expected-source set and in the retrieved source set; invalid indices count as incorrect. This is a source-match metric, not proof the proposition is legally correct. If no citation markers are emitted, precision is `null` rather than zero.
- **Citation coverage:** fraction of answerable reviewed cases that emit at least one citation to an expected source. This prevents a run with no citations from looking healthy simply because its remaining citations are all correct.
- **Pin-cite accuracy (precision):** fraction of emitted citation records that match a reviewer-labelled source ID and exact pin-cite, scored only for questions with expected pin-cites.
- **Expected pin-cite recall:** fraction of distinct reviewer-expected source-ID/pin-cite pairs that were emitted exactly. A missing citation counts against recall.
- **Abstention compliance:** among reviewed unanswerable cases, fraction where the system abstained and did not use an unverified source.
- **Unsafe unverified-source uses:** count of runs marked as using an unverified source without abstaining.
- **Source-status evidence:** when `source_summary` is supplied, cited source IDs must appear there and a non-verified status cannot be paired with `used_unverified_source: false`. For records with citations but no status summary, the evaluator fails closed for safety scoring and reports `source_status_evidence_missing_count`.

Metrics are `null` when there is no eligible denominator (for example, no answerable reviewed cases for citation coverage, or no expected pin-cite pairs for pin-cite recall). The report lists excluded questions and reasons, malformed question/run records, duplicate question IDs, and duplicate run question IDs. Duplicate IDs are excluded from scoring instead of choosing an arbitrary record. Resolve these data-quality errors before relying on a score.

## Run locally

```bash
python tools/evaluate_retrieval_quality.py
python tests/test_retrieval_evaluation.py
```

For a reviewed dataset and a real run file:

```bash
python tools/evaluate_retrieval_quality.py --questions path/to/reviewed_questions.jsonl --runs path/to/runner_output.jsonl --output evaluation-report.json
```

## Synthetic end-to-end retrieval regression

Run:

```bash
PYTHONPATH=. python tests/test_synthetic_retrieval.py
```

This test exercises the production `app.search` path against an in-memory SQLite/FTS5 corpus containing only explicitly fictional passages. It checks that a colloquial Egyptian query (for example, `شغال من غير عقد`) can retrieve its intended synthetic passage; unrelated questions do not acquire irrelevant passages; unverified, permission-blocked, future-effective and expired versions are filtered; empty retrieval abstains; and unrelated/uncited answer claims fail the existing citation guards.

The fixture marks its synthetic records as verified solely to exercise the positive branch of the retrieval gate. It patches the provenance display helpers and uses reserved `example.test` evidence URLs. None of these records is Egyptian law, a legal authority, a lawyer-reviewed label, or a benchmark of legal-answer accuracy. The test proves behavior of the code paths under controlled fixtures only. It does not measure recall or precision on the real corpus, prove semantic entailment, validate the production databases, or replace a lawyer-reviewed end-to-end model run.

## Release gates

Do not claim legal-answer accuracy from retrieval metrics alone. Before a release decision, review:

1. Sample size and practice-area balance.
2. Relevant-source completeness and false-positive retrieval.
3. Exact pin-cite correctness against the source version and effective date.
4. Behavior when the corpus is empty, stale, incomplete, or permissions block access.
5. Abstention when no reviewed operative source supports an answer.
6. Separate human legal correctness review; no automated metric replaces it.
