# AI quality baseline — fictional retrieval measurement

**Snapshot:** 2026-11-05  
**Scope:** 200 known-answer queries against an 80-article fictional Arabic corpus. This measures retrieval and refusal only, not Egyptian legal correctness.

## Benchmark design

- 80 fictional articles across employment, tenancy, family, procedure, cheques, tax, social insurance, and data protection (32 target articles plus 48 distractors).
- 192 answerable queries: 32 each for direct, paraphrase, Egyptian colloquial, synonym, word-form, and date-sensitive styles.
- 8 must-abstain queries, including out-of-corpus questions and requests to predict a case outcome.
- Date-sensitive retrieval uses the explicit `as_of` parameter. Future-effective and expired versions are excluded from the 2024-06-01 result set.
- The benchmark runs through the production `app.search()` retrieval path with synthetic registry fixtures. No Egyptian legislation or legal answers are included.

## Results

| Style | Queries | Top-1 | Top-3 | Wrong-article answers | Refusal correctness |
|---|---:|---:|---:|---:|---:|
| Direct | 32 | 32/32 (100%) | 32/32 (100%) | 0 | 32/32 (100%) |
| Paraphrase | 32 | 32/32 (100%) | 32/32 (100%) | 0 | 32/32 (100%) |
| Egyptian colloquial | 32 | 32/32 (100%) | 32/32 (100%) | 0 | 32/32 (100%) |
| Synonym | 32 | 32/32 (100%) | 32/32 (100%) | 0 | 32/32 (100%) |
| Word-form | 32 | 32/32 (100%) | 32/32 (100%) | 0 | 32/32 (100%) |
| Date-sensitive | 32 | 32/32 (100%) | 32/32 (100%) | 0 | 32/32 (100%) |
| Must-abstain | 8 | — | — | 0 | 8/8 (100%) |
| **Total** | **200** | **192/192 (100%)** | **192/192 (100%)** | **0** | **200/200 (100%)** |

## Metric definitions and limits

- Top-1/top-3 count whether the intended article appears at rank 1 / within the first three results for answerable queries.
- A wrong-article answer is a top-ranked retrieved article different from the intended article. The required count is zero.
- Refusal correctness means answerable queries return at least one result and must-abstain queries return none. It does not grade generated legal answers.
- These perfect scores reflect a controlled corpus whose query/article relationships are known by construction. They must not be generalized to real Egyptian laws, unfamiliar wording, source currentness, or lawyer-reviewed legal correctness.
- This is a retrieval/refusal engineering measurement only. It does not establish legal accuracy, completeness, authority, licensing, or lawyer approval.
