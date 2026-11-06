# Paid Pilot Readiness and Revenue Gates

**Status:** Planning and acceptance criteria only. This document does not mean the product is ready to sell, that a payment provider is integrated, or that legal answers have passed lawyer review.

## Product hypothesis

Start with a small, invitation-only pilot for Egyptian labour-law practitioners. The initial value proposition should be limited to:
1. Source-linked research that abstains when the available evidence is insufficient.
2. Case-file search and optional local Arabic OCR, with human correction and explicit unverified status.
3. Structured drafting assistance that uses lawyer-supplied facts and reviewed sources, with visible placeholders for missing facts and citations.
4. Matter workflow features already present in the product, including tasks, hearings, legal deadlines, notes, and fee tracking.

Do not market broad Egyptian-law coverage, guaranteed legal accuracy, automatic limitation-period calculations, or access to licensed court rulings until each is independently supported.

## Gate 0 — lawful and trustworthy legal content

Required before marketing research as current-law advice:
- Obtain and record the source and item-level rights required for collection, OCR, storage, indexing, display, and commercial reuse.
- Authenticate the exact source text and publication evidence; record Gazette issue/pages where applicable.
- Review commencement, effective date, amendments, repeal, and transitional rules for the requested date.
- Have a qualified Egyptian lawyer review the exact text and status; preserve reviewer, date, outcome, and evidence.
- Keep unknown, metadata-only, user-supplied, secondary, and unverified records visibly distinct.
- Test answers against the approved benchmark and keep critical legal defects as explicit release blockers.

A public URL or an “allowed” source-level permission record does not by itself license an individual instrument or establish current legal force.

## Gate 1 — confidential-data handling

Required before real client files are used:
- Finish and independently review firm isolation across API routes, database queries, background work, exports, audit logs, and UI.
- Resolve the current shared-SQLite limitation; do not onboard unrelated firms to a shared database as if it were tenant-isolated.
- Document the external model provider, endpoint, processing location, retention/logging, access, subprocessors, and contractual terms before enabling transmission.
- Keep `LLM_DATA_PROCESSING_APPROVED` unset until the deployment's data-processing decision is documented. The flag is an operator attestation, not technical proof of consent or redaction.
- Define access controls, session revocation, backup encryption, restore tests, incident handling, and retention/deletion rules.
- Use synthetic or specifically approved data for initial evaluation.

## Gate 2 — OCR and document workflow

- Evaluate page-level Arabic OCR using permission-cleared scans and manually corrected reference text. Follow [the OCR evaluation protocol](arabic_ocr_evaluation.md).
- Include low-quality, skewed, stamped, multi-column, and mixed Arabic/English pages.
- Inspect article numbers, dates, negations, monetary values, provisos, and amendment language separately; aggregate CER/WER alone cannot establish safety.
- Let a lawyer compare recognized text with the original page and preserve corrections and review history.
- Do not claim the original upload is retained if the current workflow only stores extracted text. Decide separately whether secure original-page retention is needed for correction review and implement access/retention safeguards before promising it.

## Gate 3 — paid workflow features

### Drafting

Begin with a small, lawyer-reviewed template set rather than unrestricted “generate any pleading”:
- Memorandum / مذكرة دفاع.
- Statement of claim / صحيفة دعوى.
- Client facts, parties, requested relief, procedural posture, dates, and missing-information checklist.
- Source-linked propositions that cite only retrieved material; no invented cases, article numbers, or authorities.
- Clearly marked placeholders when a required fact, verified rule, or citation is missing.
- Editable export, version history, and a final lawyer-review step.

Acceptance requires a lawyer-reviewed set of representative scenarios, regression tests for unsupported citations, and a clear disclaimer that the lawyer remains responsible for the filed document.

### Deadlines

Keep legal deadlines distinct from court sessions. Do not turn a judgment date into a definitive deadline until a qualified reviewer has specified the applicable procedure, triggering event, counting rules, holidays, exceptions, and transitional provisions. Show the rule, inputs, calculation, source, and uncertainty; ask for confirmation when facts or rules are incomplete.

### Client communications

WhatsApp notifications should follow, not precede, consent and privacy design. Require explicit client opt-in, verify recipient identity, minimize message contents, avoid exposing privileged details in lock-screen previews, log delivery outcomes, and provide a way to revoke consent. Confirm applicable provider and legal requirements before launch.

## Gate 4 — billing and trial

No billing integration is represented as implemented by this checklist.

Before choosing a payment flow:
- Confirm the business/merchant eligibility, onboarding requirements, fees, settlement timing, refunds, dispute handling, and technical integration options for the selected Egyptian provider.
- Evaluate Fawry and an appropriate InstaPay-based merchant/collection workflow against those requirements; do not assume a personal transfer method provides subscription APIs, automated reconciliation, or recurring payments.
- Decide whether the first pilot is paid manually/invoiced or uses integrated checkout. Prefer the simplest compliant flow that can be reconciled and supported.
- Define plan limits, trial duration, cancellation, refunds, account suspension, invoices/receipts, and who can access a firm's subscription information.
- Do not let payment status grant access to another firm's data. Entitlements must be checked server-side.
- Test successful, pending, failed, duplicated, reversed/refunded, and mismatched-payment states before charging customers.

Do not set final pricing based only on competitor claims. Interview lawyers about frequency of use, time saved, acceptable error risk, document volume, and willingness to pay; test a small number of clearly defined offers during the pilot.

## Pilot acceptance checklist

A pilot owner should mark each item only after reviewing evidence:

- [ ] Written source/item permission and provenance record for every corpus item offered commercially.
- [ ] Qualified lawyer has approved the exact current legal text and relevant date/history.
- [ ] Benchmark has been run and lawyer-reviewed; critical defects are zero for the approved release scope.
- [ ] Tenant isolation and confidential-data handling have passed independent review.
- [ ] LLM endpoint and data-processing terms have been explicitly approved or external transmission remains disabled.
- [ ] OCR has been evaluated on an authorized, representative scan set; human correction is available.
- [ ] Drafting outputs have been reviewed on a defined scenario set and unsupported authorities are blocked or clearly surfaced.
- [ ] Deadline functionality is bounded to reviewed rules and clearly separates estimates from confirmed deadlines.
- [ ] Arabic RTL and English LTR usability has been checked on phone, tablet, and desktop.
- [ ] Billing, refund, cancellation, receipt, reconciliation, and access-entitlement cases have been tested if charging in-product.
- [ ] Monitoring, backups, restore, incident response, rollback, support ownership, and data-retention/deletion are documented.
- [ ] Pilot lawyers have accepted the scope, limitations, support channel, and feedback process.

Until these gates are evidenced, treat the application as a controlled development/pilot candidate, not a production-ready multi-firm legal service.
