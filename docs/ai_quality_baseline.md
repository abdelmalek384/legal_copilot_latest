# AI quality baseline — fictional retrieval measurement

**Snapshot:** 2026-11-05  
**Scope:** 200 known-answer queries against an 80-article fictional Arabic corpus. This measures retrieval and refusal only, not Egyptian legal correctness.

## Benchmark design

- 80 fictional articles across employment, tenancy, family, procedure, cheques, tax, social insurance, and data protection (32 target articles plus 48 distractors).
- 192 answerable queries: 32 each for direct, paraphrase, Egyptian colloquial, synonym, word-form, and date-sensitive styles.
- 8 must-abstain queries, including out-of-corpus questions and requests to predict a case outcome.
- Query variants are distinct from canonical article wording; fictional articles contain concise topic context. Expected articles are known by construction.
- The benchmark runs through the production `app.search()` retrieval path with synthetic registry fixtures and a test-only counsel allowlist.
- Date-sensitive retrieval uses the explicit `as_of` parameter. Future-effective and expired versions are excluded from the 2024-06-01 result set.

## Results

| Style | Queries | Top-1 | Top-3 | Wrong-article answers | Refusal correctness |
|---|---:|---:|---:|---:|---:|
| Direct | 32 | 32/32 (100%) | 32/32 (100%) | 0 | 32/32 (100%) |
| Paraphrase | 32 | 32/32 (100%) | 32/32 (100%) | 0 | 32/32 (100%) |
| Egyptian colloquial | 32 | 31/32 (96.9%) | 31/32 (96.9%) | 0 | 31/32 (96.9%) |
| Synonym | 32 | 31/32 (96.9%) | 31/32 (96.9%) | 0 | 31/32 (96.9%) |
| Word-form | 32 | 32/32 (100%) | 32/32 (100%) | 0 | 32/32 (100%) |
| Date-sensitive | 32 | 32/32 (100%) | 32/32 (100%) | 0 | 32/32 (100%) |
| Must-abstain | 8 | — | — | 0 | 8/8 (100%) |
| **Total** | **200** | **190/192 (99.0%)** | **190/192 (99.0%)** | **0** | **198/200 (99.0%)** |

## Metric definitions and limits

- Top-1/top-3 count whether the intended article appears at rank 1 / within the first three results for answerable queries.
- A wrong-article answer is a top-ranked retrieved article different from the intended article. The required count is zero.
- Refusal correctness means answerable queries return at least one result and must-abstain queries return none. Two answerable queries were refused; neither produced a wrong-article result.
- These scores reflect a controlled fictional corpus whose query/article relationships are known by construction. They must not be generalized to real Egyptian laws, unfamiliar wording, source currentness, or lawyer-reviewed legal correctness.
- This is a retrieval/refusal engineering measurement only. It does not establish legal accuracy, completeness, authority, licensing, or lawyer approval.


## Fictional claim-support measurement

**Snapshot:** 2026-11-05  
**Scope:** 60 fictional answer sentences paired with fictional evidence. This measures the optional lexical claim-support screen only; it is not semantic entailment, Egyptian legal correctness, or lawyer review.

| Claim class | Cases | Misclassified |
|---|---:|---:|
| Supported | 12 | 0 false blocks |
| Unsupported number / amount / period | 12 | 0 false passes |
| Unsupported qualitative / absolute claim | 12 | 0 false passes |
| Reversed meaning / polarity | 12 | 0 false passes |
| Over-generalization | 12 | 0 false passes |
| **Total unsupported** | **48** | **0 false passes (0%)** |

- False-block rate on supported fictional claims: **0/12 (0%)**.
- False-pass rate on unsupported fictional claims: **0/48 (0%)**.
- The measured gaps were addressed with conservative number/unit comparison, unsupported qualifier detection, and reversal-polarity checks.
- The screen remains optional and disabled unless `LEGAL_CLAIM_SUPPORT_CHECK=1` is explicitly configured. A zero false-pass rate on this small constructed set does not establish broad accuracy.
