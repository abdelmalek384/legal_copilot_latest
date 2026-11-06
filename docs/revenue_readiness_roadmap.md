# Revenue Readiness Roadmap

**Status:** Product/engineering proposal; not a launch or legal-readiness claim.  
**Updated:** 2026-10-24  
**Purpose:** Prioritize work that can turn Legal Copilot into a trustworthy paid product for Egyptian lawyers, while keeping licensing, confidentiality, and legal correctness as release gates.

## Executive decision

Do not launch as a broad “AI lawyer” over an unverified corpus. Start with a narrow, demonstrably useful workflow for Egyptian lawyers, validate willingness to pay with a small pilot, then expand only when quality and operational controls are evidenced.

**Recommended first paid workflow:** labour-law research with source-linked answers, Arabic scanned-document ingestion/OCR review, and exportable first drafts that clearly distinguish source-backed propositions from lawyer-entered facts and unverified suggestions.

This is a product hypothesis to test with Egyptian lawyers, not a claim that labour law has already been fully collected, verified, or approved for production.

## Revenue blockers and readiness gates

| Workstream | Customer value / revenue hypothesis | Minimum release gate | Priority |
|---|---|---|---|
| Paid plans, trial, entitlements | Converts a pilot into recurring revenue; enables packaging and usage limits | Server-side entitlement checks on protected APIs; trial expiry; plan change/cancellation; payment-state reconciliation; failed-payment/grace policy; auditable admin override; no client-side-only paywall | P0 |
| Egypt-compatible payment | Reduces friction for local customers | Select a provider and business/merchant account; verify current merchant eligibility, fees, settlement, refunds, webhook signature verification, idempotency and sandbox-to-live process. Evaluate Fawry and InstaPay-based options directly with providers; do not assume a consumer transfer rail provides a subscription API | P0, after provider access |
| Cited legal answers | Core differentiator and trust proposition | Verified, permitted primary sources for a defined labour-law scope; each material proposition linked to exact source passage and version; status/effective-date uncertainty visible; abstain if evidence is missing; regression evaluation reviewed by an Egyptian lawyer | P0 |
| Arabic OCR and scanned-file review | Reduces manual retyping of common court and client documents | Test on a representative, permissioned Arabic scan set; measure character/word error and critical-field accuracy; preserve page references; flag low confidence; reviewer can compare extracted text with the original page | P0 |
| Document drafting | Saves time on common work such as مذكرة دفاع and صحيفة دعوى | Approved templates; structured fact intake; citations tied to verified sources; missing facts marked as placeholders; no invented authorities, article numbers, court rulings or case facts; lawyer review required before export/finalization | P1 |
| Legal deadline calculator | High-value risk reduction | Rule registry reviewed by counsel, jurisdiction/procedure/trigger inputs explicit, calendar/holiday assumptions documented, boundary tests and worked examples; show calculation and source; require confirmation and warn when facts/rules are ambiguous | P1 |
| Case-file Q&A | Differentiates from generic legal search | Tenant isolation and authorization verified across retrieval, exports, background jobs, logs, and backups; confidential data handling and retention policy approved; no cross-firm retrieval; deployment/security review | Blocked by SEC-01 |
| Customer-facing verification record | Makes trust work visible | Display reviewer identity/role, review date, evidence links, source version and “in force as of” date only when that status was actually checked; unknown must remain visible; never show an unearned verified badge | P1 |
| Mobile-friendly web app | Improves use in court, office and on the move | Responsive RTL/LTR workflows tested on real phones; accessible forms, upload, search, deadlines and document export; poor-network/error states handled | P1 |
| Power-of-attorney tracking and WhatsApp updates | Workflow retention and client service | Define reminder/expiry rules with counsel; customer-controlled recipients and consent; message templates, delivery failure handling, opt-out and audit trail; verify WhatsApp Business Platform eligibility and pricing before promising delivery | P2 |
| Cassation rulings | Potentially valuable specialist corpus | Written licence/permission or a verified lawful reuse route for the specific content and intended commercial use; record item-level provenance and restrictions; do not scrape or sell restricted content absent authorization | Blocked by rights |
 
## Proposed packaging (hypotheses to test)

Start with a small paid pilot rather than inventing a price from assumptions:

- **Pilot / evaluation:** limited seats and usage, fixed duration, explicit data-handling terms, onboarding and feedback sessions. Avoid calling it a free trial until its limits and expiry are implemented.
- **Solo:** one lawyer, limited monthly research and OCR/drafting usage, export and saved matters.
- **Firm:** multiple authorized users, shared matters, administration, usage visibility and support. Do not sell multi-firm isolation as ready until SEC-01 has passed its acceptance gates.
- **Later add-ons:** higher OCR volume, drafting packs, deadline workflows or licensed specialist content, only after costs, rights and support burden are measured.

Pricing should be decided after interviews and a pilot. Track conversion, activation, repeat weekly use, cost per successful workflow, gross margin, churn intent and support load. Do not use raw query volume as the only value metric.

## Implementation sequence

### Phase A — Prove the narrow value proposition

1. Pick a specific labour-law scope and list the authoritative instruments and versions needed for the pilot.
2. Obtain permitted source copies and lawyer review; publish no completeness claim beyond the reviewed scope.
3. Build a reviewed evaluation set of realistic lawyer questions, expected source passages and mandatory abstentions.
4. Evaluate Arabic OCR using representative, permissioned scans; record text quality and critical-field errors.
5. Interview 3–5 Egyptian lawyers and run supervised workflow tests. Record task completion, correction time, citation trust and willingness-to-pay evidence.

**Exit gate:** a lawyer-reviewed evaluation report, known limitations, and observed evidence that the workflow saves time without hiding uncertainty.

### Phase B — Paid pilot foundation

1. Define plans, quotas, trial state, cancellation, grace period, refunds and support ownership.
2. Choose a payment provider only after confirming merchant eligibility, API capabilities, fees and settlement terms.
3. Implement server-side subscription/entitlement state and verified payment webhooks with idempotency and reconciliation.
4. Provide terms, privacy/data-processing notices, retention/deletion process and a support/contact path.
5. Keep confidential case-file features gated until tenant isolation and data handling are accepted.

**Exit gate:** successful sandbox and end-to-end lifecycle tests, including duplicate/out-of-order webhook events, failed payment, cancellation, expiry, refund and entitlement revocation.

### Phase C — Expand retention and drafting

1. Create source-grounded memo/pleading templates with placeholders and explicit provenance.
2. Add deadline calculation only after rules and edge cases are approved by counsel.
3. Expose source verification metadata to users with conservative, evidence-backed labels.
4. Improve mobile UX and add client reminders only after consent, privacy and delivery controls are designed.

## Non-negotiable safety and commercial rules

- Never fabricate a citation, article number, ruling, effective date, reviewer, licence, or “in force” status.
- “Source discovered,” “text extracted,” “lawyer reviewed,” “status checked,” and “commercial reuse permitted” are different states.
- A source-check badge must be backed by recorded evidence and a named accountable reviewer.
- No customer matter content may be used to train or improve shared systems by default without an explicit, lawful basis and clear agreement.
- No cross-firm case-file Q&A launch until authorization and isolation have been tested across routes, search indexes, files, background jobs, logs and restore paths.
- No Cassation corpus commercialization without written rights evidence for the intended use.
- Payment integration must not store raw payment credentials; use provider-hosted/tokenized flows and verify callbacks.
- All legal drafts and deadline outputs require clear limits and lawyer confirmation; the product is decision support, not a guarantee of legal outcome.

## Decisions needed from the product owner

1. Confirm the first target customer: solo practitioners, small firms, or in-house teams.
2. Approve labour law as the first practice-area scope and name the lawyer responsible for legal validation.
3. Confirm intended trial length, usage caps, cancellation/refund policy and customer support owner.
4. Authorize commercial outreach to Fawry and potential InstaPay-compatible payment providers, then select based on verified merchant/API terms.
5. Approve data hosting, retention, original-file retention and deletion requirements before private case-file analysis is marketed.
6. Confirm whether WhatsApp messaging is in the first release or deferred.
7. Assign a legal owner to verify template wording and deadline rules.

## Current implementation reality

This document is a prioritization and acceptance plan. It does **not** mean subscriptions, payments, legal template drafting, deadline calculation, source verification badges, or WhatsApp delivery are implemented or production-ready. Existing OCR paths and source-review tooling require real Arabic-scan evaluation and human verification. The tenant preflight tool is read-only and does not establish isolation. Current Cassation permission status must be established item by item; no permission is assumed.
