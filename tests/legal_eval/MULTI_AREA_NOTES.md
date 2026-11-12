# Multi-area legal benchmark draft

This benchmark contains 100 unreviewed questions across ten practice areas. It is a review queue, not an answer key and not a legal accuracy score set. Expected answers, expected sources, pin citations, and answerability remain blank pending review by qualified Egyptian counsel. All 100 now set `must_abstain_if_unverified=true`; the seven explicitly out-of-scope questions are a separate abstention cohort, not the only questions that must abstain when sources are unverified.

- All rows use `review_status=needs_lawyer_review` and `answerable=null`.
- Seven questions are explicitly marked as requiring abstention because they ask for unknowable case outcomes, exact personal predictions, current case assignments, or other out-of-scope judgments.
- Questions include Modern Standard Arabic, Egyptian colloquial phrasing, paraphrases, simplified terminology, and date-sensitive issues.
- Dates are draft prompts only; counsel must confirm the legally relevant date and applicable law before approval.
- Do not use this dataset for accuracy claims until reviewed.

Counts by area:
- rent_and_tenancy: 15
- personal_status: 15
- civil_procedure: 13
- criminal_procedure: 10
- commercial_law: 9
- civil_law: 13
- tax_law: 8
- social_insurance: 6
- data_protection: 5
- real_estate: 6


## Release-gate inventory size

- Six additional draft prompts were added so this separate ten-practice-area release-gate review queue reaches the configured minimum of 100 questions.
- The six additions cover rent and tenancy, personal status, civil procedure, civil law, criminal procedure and commercial law. They remain unreviewed with empty expected answers, sources and pin citations.
- This only removes the structural shortfall in draft question count. It does not satisfy the release gate: all 100 still require qualified counsel approval, answerability labels, source/pin-cite evidence and a valid reviewer registry.
