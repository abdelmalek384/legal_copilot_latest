# Proposal: a separate source-matched, unreviewed legal-text tier

**Decision requested:** whether to authorize a non-authoritative, separately gated `source_matched_unreviewed` tier for a future controlled pilot. **No release gate is changed by this proposal.**

## Conflict with the current release rules

The current [Legal Release Readiness Gate](legal_release_readiness_gate.md) requires real source/reuse evidence, original-file and extracted-text hashes, reviewed expected article identifiers, and passing source, extraction, amendment, licensing, and lawyer-review records. A passing lawyer-approval event must carry the configured qualified-counsel attestation marker. The [Verified Egyptian Legal Knowledge Roadmap](verified_egyptian_legal_knowledge_roadmap.md) explicitly says that agreement between two copies or a successful extraction comparison does not make text lawyer-approved.

A record expressly labelled **not lawyer-reviewed** cannot satisfy the existing lawyer-approval requirement. Serving it through today's legal retrieval path would therefore require changing a hard gate. This proposal does not make that change.

## Proposed additive model

If the maintainer and qualified Egyptian counsel approve a policy amendment, introduce a distinct status and API field:

- `trust_tier: "source_matched_unreviewed"` on both answer and source records.
- Visible label: **"Source-matched — not lawyer-reviewed"**. Never use "verified", "lawyer-approved", or equivalent wording.
- Separate candidate eligibility decision; never translate it into the existing `verified` state or satisfy `lawyer_approval`.
- Feature flag disabled by default in production. Enabling it requires a separate, explicit deployment decision and a documented pilot boundary.
- If the flag is off, or any evidence is incomplete, return sources only / abstain under current behavior.

## Minimum evidence for the proposed tier

1. Original manual capture saved unchanged, SHA-256 recorded, and provenance metadata validated.
2. Article-row audit passes with no missing, duplicate, malformed, or unexpected article identifiers.
3. Independent second copy is separately sourced and hashed; article-by-article comparison is complete.
4. Every numeric/date/percentage/period/exception/negation difference is resolved against the primary Gazette text and recorded; unresolved critical differences block the tier.
5. Publication and effective dates are kept separate; effective-date and transitional provisions are extracted from the text, not inferred from file metadata.
6. Rights/reuse status is separately evidenced. A matching hash or public URL does not grant reuse rights.
7. The UI/API clearly distinguishes this tier from lawyer-reviewed content; no answer may imply that a lawyer has checked its interpretation.

## Required safeguards and acceptance

- Keep the existing verified-corpus query and release gate unchanged.
- Implement a separate, opt-in candidate retrieval path only after written approval of the policy and its pilot scope.
- Keep the tier off in production by default; require tests proving the flag-off path is identical to current fail-closed behavior.
- Add tests proving source-matched content cannot be returned as `verified_operative_text` and cannot satisfy lawyer approval.
- Have qualified Egyptian counsel review the proposed disclosure wording and pilot boundary before enabling the feature.

## Recommendation

**Do not implement or enable production serving yet.** First obtain an explicit decision from the project maintainer and qualified Egyptian counsel on whether a separately gated, non-authoritative pilot tier is acceptable. Until then, keep the existing gate intact and treat hash/audit/comparison success as technical evidence only.
