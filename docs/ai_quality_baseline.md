# AI quality baseline — fictional retrieval measurement

**Snapshot:** 2026-11-05  
**Scope:** 200 known-answer queries against an 80-article fictional Arabic corpus. This measures retrieval and refusal only, not Egyptian legal correctness.

## Benchmark design

- 80 fictional articles across employment, tenancy, family, procedure, cheques, tax, social insurance, and data protection (32 target articles plus 48 distractors).
- 192 answerable queries: 32 each for direct, paraphrase, Egyptian colloquial, synonym, word-form, and date-sensitive styles.
- 8 must-abstain queries, including out-of-corpus questions and requests to predict a case outcome.
- Date-sensitive retrieval uses the explicit `as_of` parameter. Future-effective and expired versions are excluded from the 2024-06-01 result set.
- The benchmark runs through production `app.search()` with synthetic registry fixtures. No Egyptian legislation or legal answers are included.

## Results — after PR #1424 lexicon changes

| Style | Queries | Top-1 | Top-3 | Wrong top-ranked article | Refusal correctness |
|---|---:|---:|---:|---:|---:|
| Direct | 32 | 32/32 (100%) | 32/32 (100%) | 0 | 32/32 (100%) |
| Paraphrase | 32 | 31/32 (96.9%) | 32/32 (100%) | 1 | 32/32 (100%) |
| Egyptian colloquial | 32 | 28/32 (87.5%) | 31/32 (96.9%) | 3 | 31/32 (96.9%) |
| Synonym | 32 | 31/32 (96.9%) | 31/32 (96.9%) | 0 | 31/32 (96.9%) |
| Word-form | 32 | 31/32 (96.9%) | 32/32 (100%) | 1 | 32/32 (100%) |
| Date-sensitive | 32 | 32/32 (100%) | 32/32 (100%) | 0 | 32/32 (100%) |
| Must-abstain | 8 | — | — | 0 | 8/8 (100%) |
| **Total** | **200** | **185/192 (96.4%)** | **190/192 (99.0%)** | **5** | **198/200 (99.0%)** |

## Remaining failures

- Colloquial: 3 wrong top-ranked articles; examples include a repair/landlord query, cheque endorsement, and unemployment compensation.
- Paraphrase: 1 wrong top-ranked article for a query about dividing an estate.
- Word-form: 1 wrong top-ranked article for a query about taxpayer inspections.
- The colloquial and synonym top-3 results both exceed the 80% Task 3 target. Stop lexicon expansion here; do not chase further gains in this task.
- Task 2's zero-wrong-article requirement remains unmet. Keep the benchmark PR open and do not describe this as a passing safety result.

## Metric definitions and limits

- Top-1/top-3 count whether the intended article appears at rank 1 / within the first three results for answerable queries.
- A wrong-article answer is a top-ranked retrieved article different from the intended article. The required count is zero.
- Refusal correctness means answerable queries return at least one result and must-abstain queries return none. It does not grade generated legal answers.
- These are controlled fictional-text results. They do not establish Egyptian legal accuracy, completeness, authority, licensing, currentness, or lawyer approval.
