# AI quality baseline — measurement availability

**Snapshot:** 2026-11-04  
**Scope:** 155 draft questions in `tests/legal_eval/`; retrieval/refusal measurement only, not legal correctness.

## Benchmark composition

| Category | Draft questions | Run records | Top-1 | Top-3 | Wrong-article answers | Abstention correctness | Claim-support block rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Direct | 64 | 0 | N/A | N/A | 0 observed (n=0) | N/A | N/A |
| Paraphrase | 24 | 0 | N/A | N/A | 0 observed (n=0) | N/A | N/A |
| Colloquial | 24 | 0 | N/A | N/A | 0 observed (n=0) | N/A | N/A |
| Synonym / simplified terms | 17 | 0 | N/A | N/A | 0 observed (n=0) | N/A | N/A |
| Date-sensitive | 14 | 0 | N/A | N/A | 0 observed (n=0) | N/A | N/A |
| Must-abstain / out of scope | 12 | 0 | N/A | N/A | 0 observed (n=0) | N/A | N/A |
| **Total** | **155** | **0** | **N/A** | **N/A** | **0 observed (n=0)** | **N/A** | **N/A** |

## What is actually measured

- The two draft benchmark files contain 61 labour questions and 94 multi-area questions. Category mapping uses the explicit multi-area `question_type` and the labour question-ID suffixes (D/P/C/S/T/X).
- All 155 rows are `needs_lawyer_review`; all require abstention when sources are unverified. None has lawyer-approved expected sources or answerability labels.
- `tests/legal_eval/runs.example.jsonl` contains zero run records.
- The repository status says there are zero verified Egyptian laws available to the product.
- Therefore the only numeric quality observations are sample availability: 155 draft questions, 0 reviewed labels, 0 run records, and 0 observed wrong-article answers in an empty run set. **Zero observed wrong-article answers at n=0 is not a passing safety result.**

## Why the requested rates are N/A

- `tools/evaluate_retrieval_quality.py` scores lawyer-reviewed labels and excludes unreviewed draft seeds; there are no reviewed expected-source labels from which to calculate top-1/top-3.
- `tools/evaluate_legal_answers.py` requires lawyer-approved question records, answerability labels, expected sources/pin-cites, and corresponding result records.
- `tools/run_legal_eval.py` collects actual API runs but does not create expected-source ground truth. No authenticated local API run or run output is present in this snapshot.
- The existing run/result schema does not provide an observed claim-support-block outcome for these 155 questions. Claim-support block rate cannot be inferred from the feature being enabled or from unit tests.

## Interpretation and next measurement

This is a **data-availability baseline, not a retrieval-performance score**. It does not measure legal correctness. Draft questions have no lawyer-approved answers, so any future score on them must be explicitly limited to retrieval behaviour and safe refusal, not substantive legal correctness.

To produce actual rates, run the 155 questions against a controlled local test corpus/API, preserve the raw run output, and add reviewed retrieval relevance labels where appropriate. Measure refusal against the explicit unverified-source requirement without presenting draft provisional answers as approved ground truth. Keep wrong-article answers at zero; do not weaken abstention to improve recall.
