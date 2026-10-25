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

Both boolean fields are required explicitly; malformed source-ID lists, citation objects, booleans, or dates are reported and excluded rather than interpreted as zero-quality results. This is a schema example, not a real result. Do not copy placeholder IDs into the measured dataset.

## Metrics

- **Recall@k:** mean fraction of reviewer-labelled relevant source IDs found in the top k unique retrieved sources.
- **MRR@k:** mean reciprocal rank of the first relevant source, with zero if no relevant source appears in the first k.
- **Citation precision:** fraction of emitted citations whose source ID is in the reviewed expected-source set. This is a source-match metric, not proof the proposition is legally correct.
- **Pin-cite accuracy:** fraction of citation records that match a reviewer-labelled source ID and exact pin-cite, scored only for questions with expected pin-cites.
- **Abstention compliance:** among reviewed unanswerable cases, fraction where the system abstained and did not use an unverified source.
- **Unsafe unverified-source uses:** count of runs marked as using an unverified source without abstaining.

Metrics are `null` when there is no eligible denominator. The report lists excluded questions and reasons, malformed question/run records, duplicate question IDs, and duplicate run question IDs. Duplicate IDs are excluded from scoring instead of choosing an arbitrary record. Resolve these data-quality errors before relying on a score.

## Run locally

```bash
python tools/evaluate_retrieval_quality.py
python tests/test_retrieval_evaluation.py
```

For a reviewed dataset and a real run file:

```bash
python tools/evaluate_retrieval_quality.py --questions path/to/reviewed_questions.jsonl --runs path/to/real_runs.jsonl --output evaluation-report.json
```

## Release gates

Do not claim legal-answer accuracy from retrieval metrics alone. Before a release decision, review:

1. Sample size and practice-area balance.
2. Relevant-source completeness and false-positive retrieval.
3. Exact pin-cite correctness against the source version and effective date.
4. Behavior when the corpus is empty, stale, incomplete, or permissions block access.
5. Abstention when no reviewed operative source supports an answer.
6. Separate human legal correctness review; no automated metric replaces it.
