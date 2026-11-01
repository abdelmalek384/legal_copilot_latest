# Arabic Retrieval & Citation Evaluation (RSH-02)

## Purpose

Provide a reproducible measurement harness for Arabic legal retrieval and citation behavior. This is a measurement tool, not a legal verifier. It must not invent expected answers, sources, pin-cites, or current-law conclusions.

## Current state

- `tests/legal_eval/practice_questions.seed.jsonl` contains discovery/evaluation-question seeds, not approved ground truth.
- Seed questions are marked `needs_lawyer_review`, have no expected answer, and have no expected source IDs. The evaluator excludes them from scoring.
- Retrieval uses Arabic normalization, conservative light stemming, curated Arabic/English legal synonym groups, and selected Egyptian colloquial phrase hints. These hints affect retrieval only and do not rewrite source passages or establish legal equivalence.
- Current phrase coverage includes labour, wages, dismissal, rent/eviction, family support, cheques, police reports, arrest/pretrial detention, administrative grievances, inheritance, insurance and repayment wording. New phrase mappings have regression tests in `tests/test_arabic_matching.py`.
- Ten Egyptian colloquial legal-question seeds were added to `tests/legal_eval/practice_questions.seed.jsonl` across labour, criminal procedure, administrative law, family, inheritance, tenancy, cheques and debt recovery. They remain `needs_lawyer_review`, have no expected source labels, and are intentionally excluded from metrics until counsel reviews exact sources and pin-cites.
- Answer generation remains fail-closed on missing/invalid inline citations, unsupported numeric claims, weak lexical citation anchors, and unverified corpus sources. These automated checks are safety heuristics, not semantic entailment or proof of legal correctness.
- `tests/legal_eval/runs.example.jsonl` is intentionally empty apart from an explanatory comment. No real run results or lawyer-approved labels are claimed.
- Add reviewed labels only after a qualified Egyptian-law reviewer records their name/date and identifies exact expected source IDs. Pin-cite labels are optional but should be exact and evidence-backed.

## Current measurement limitation

No lawyer-reviewed Egyptian colloquial question set or measured model-run output is currently available. Phrase-expansion unit tests prove that selected colloquial expressions map to retrieval hints; they do not prove that the correct article is retrieved or that an answer is legally correct. Do not report retrieval recall, citation precision, or answer accuracy until a qualified Egyptian reviewer approves exact expected source IDs and pin-cites and a real run is scored.

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

## Configurable retrieval release gate

The evaluator can optionally fail a command with exit code 1 when reviewed-data coverage or quality thresholds are not met. These are engineering gates over lawyer-supplied labels, not legal-correctness certification.

Example (thresholds are illustrative and must be approved for the actual benchmark before use):

```bash
python tools/evaluate_retrieval_quality.py \
  --questions reviewed_questions.jsonl --runs model_runs.jsonl \
  --min-reviewed-cases 100 --min-practice-areas 3 --min-cases-per-practice-area 20 \
  --min-answerable-cases 60 --min-unanswerable-cases 20 --min-expected-pin-cites 50 \
  --min-recall-at-5 0.90 --min-mrr-at-5 0.80 \
  --min-citation-precision 0.95 --min-citation-coverage 0.90 \
  --min-expected-pin-cite-recall 0.90 --min-abstention-compliance 0.98 \
  --max-excluded-cases 0 --max-invalid-records 0 \
  --max-unsafe-unverified-source-uses 0 \
  --output retrieval-release-report.json
```

Quality thresholds require explicit total sample-size and practice-area coverage gates. Citation coverage requires a minimum answerable cohort; abstention compliance requires a minimum unanswerable cohort; expected pin-cite recall requires a minimum count of expected pin-cites. The gate also supports maximum excluded-case and unsafe-unverified-source-use counts. Missing metric denominators fail a configured threshold rather than being treated as a pass. The report always retains excluded records and data-quality findings. `--max-invalid-records` independently gates malformed question/run records and duplicate IDs; `--max-excluded-cases` gates reviewed questions that could not be scored.

The example thresholds above are placeholders, not a recommendation or current product policy. Set them only after qualified Egyptian counsel approves the benchmark composition, risk tolerance and threshold policy. An empty or unreviewed seed set cannot pass a meaningful quality gate.

## Synthetic end-to-end retrieval regression

Run:

```bash
PYTHONPATH=. python tests/test_synthetic_retrieval.py
```

This test exercises the production `app.search` path against an in-memory SQLite/FTS5 corpus containing only explicitly fictional passages. In addition to the focused examples above, it now runs 51 curated Egyptian-colloquial query fixtures across labour, tenancy, family support, inheritance, criminal procedure, administrative grievances, cheques, electronic fraud, debt recovery, and other areas. For each query, the intended fictional passage must appear in the top three; the test prints both top-three and top-one fixture counts. Ten unrelated out-of-corpus questions must return no passages. It also checks that unverified, permission-blocked, future-effective and expired versions are filtered; empty retrieval abstains; and unrelated/uncited answer claims fail the existing citation guards.

The fixture marks its synthetic records as verified solely to exercise the positive branch of the retrieval gate. It patches the provenance display helpers and uses reserved `example.test` evidence URLs. None of these records is Egyptian law, a legal authority, a lawyer-reviewed label, or a benchmark of legal-answer accuracy. The reported top-three/top-one counts are synthetic regression coverage only; they are not real-corpus Recall@k, model performance, or a legal-correctness score. The test proves behavior of the code paths under controlled fixtures only. It does not measure recall or precision on the real corpus, prove semantic entailment, validate the production databases, or replace a lawyer-reviewed end-to-end model run.

## Release gates

Do not claim legal-answer accuracy from retrieval metrics alone. Before a release decision, review:

1. Sample size and practice-area balance.
2. Relevant-source completeness and false-positive retrieval.
3. Exact pin-cite correctness against the source version and effective date.
4. Behavior when the corpus is empty, stale, incomplete, or permissions block access.
5. Abstention when no reviewed operative source supports an answer.
6. Separate human legal correctness review; no automated metric replaces it.
