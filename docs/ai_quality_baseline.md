# AI quality baseline — fictional retrieval measurement

**Snapshot:** 2026-11-05  
**Scope:** 200 known-answer queries against an 80-article fictional Arabic corpus. This measures retrieval and refusal only, not Egyptian legal correctness.

## Benchmark design

- 80 fictional articles across employment, tenancy, family, procedure, cheques, tax, social insurance, and data protection (32 target articles plus 48 distractors).
- 192 answerable queries: 32 each for direct, paraphrase, Egyptian colloquial, synonym, word-form, and date-sensitive styles.
- 8 must-abstain queries, including out-of-corpus questions and requests to predict a case outcome.
- Date-sensitive retrieval uses the explicit `as_of` parameter. Future-effective and expired versions are excluded from the 2024-06-01 result set.
- The benchmark runs through the production `app.search()` retrieval path with synthetic registry fixtures. No Egyptian legislation or legal answers are included.

## Results — latest actual CI run

| Style | Queries | Top-1 | Top-3 | Wrong top-ranked article | Refusal correctness |
|---|---:|---:|---:|---:|---:|
| Direct | 32 | 31/32 (96.9%) | 32/32 (100%) | 1 | 32/32 (100%) |
| Paraphrase | 32 | 6/32 (18.8%) | 11/32 (34.4%) | 25 | 31/32 (96.9%) |
| Egyptian colloquial | 32 | 9/32 (28.1%) | 12/32 (37.5%) | 15 | 24/32 (75%) |
| Synonym | 32 | 14/32 (43.8%) | 19/32 (59.4%) | 16 | 30/32 (93.8%) |
| Word-form | 32 | 22/32 (68.8%) | 30/32 (93.8%) | 10 | 32/32 (100%) |
| Date-sensitive | 32 | 31/32 (96.9%) | 32/32 (100%) | 1 | 32/32 (100%) |
| Must-abstain | 8 | — | — | 0 | 8/8 (100%) |
| **Total** | **200** | **113/192 (58.9%)** | **136/192 (70.8%)** | **68** | **189/200 (94.5%)** |

**Task 2 safety condition is not met:** wrong top-ranked articles must be zero. Keep this benchmark PR open while Task 3 addresses the measured gaps.

## Metric definitions and limits

- Top-1/top-3 count whether the intended article appears at rank 1 / within the first three results for answerable queries.
- A wrong-article answer is a top-ranked retrieved article different from the intended article. The required count is zero.
- Refusal correctness means answerable queries return at least one result and must-abstain queries return none. It does not grade generated legal answers.
- These are controlled fictional-text results. They must not be generalized to real Egyptian laws, source currentness, or lawyer-reviewed legal correctness.
- This measurement does not establish legal accuracy, completeness, authority, licensing, or lawyer approval.
