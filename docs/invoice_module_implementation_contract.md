# Invoice module — implementation contract (proposal)

**Status:** engineering proposal for database-owner review; not an implemented feature, migration, tax invoice certification, or authorization to change tenant boundaries.

## 1. Product boundary

The invoice module must create a durable invoice record linked to one client and one case, support multiple billable line items, record partial and full payments, expose invoice history, and render a printable/exportable invoice.

The existing fees table and FeeIn request model are a recorded-fee summary only. They do not provide invoice identity, line items, a payment ledger, issue/void lifecycle, or immutable issued-document history. Do not represent an invoice by overloading fees.note, creating one fee row per line, or treating the existing paid amount as a payment ledger.

This proposal covers ordinary law-firm fee invoices in EGP. It does not claim compliance with Egyptian tax-invoice/e-receipt requirements. Tax registration, VAT treatment, electronic invoicing integration, mandatory fields and retention must be separately confirmed by the firm's accountant/tax counsel before any document is labelled a tax invoice.

## 2. Core records proposed for approval

The database owner must select the actual migration location, tenant key strategy, constraints, naming and backfill approach. The following is a logical model, not executable SQL.

### Invoice
- Stable primary key.
- Firm scope using the database owner's approved tenant model.
- Required case foreign key; case/client snapshot fields sufficient to preserve the billed-to identity if the case's client label later changes.
- Human-readable invoice number, unique within the approved firm scope; sequence allocation must be concurrency-safe.
- Currency fixed to EGP for the initial release.
- Issue date, due date, optional service period, description/terms, and created-by/created-at metadata.
- Lifecycle: draft, issued, void. Payment state is derived separately.
- Issued invoice content is immutable. Corrections after issue require a void/replacement or an explicitly approved credit-note workflow; never silently rewrite a sent invoice.

### Invoice line item
- Invoice foreign key with cascade behavior decided by the DB owner.
- Stable display order, description, quantity, unit price and line total.
- Monetary values stored as integer piastres (or another database-owner-approved exact decimal representation); do not use binary floating point for financial arithmetic.
- Validate quantity and amounts as non-negative, bounded values; calculate line totals and invoice totals server-side.

### Payment
- Invoice foreign key, amount in piastres, payment date, method, external reference/receipt reference, note, actor and creation timestamp.
- Payments are append-only ledger entries. A correction is a reversal/refund entry linked to the original payment, not destructive editing.
- Sum of effective payments cannot exceed the amount due unless an explicit credit/overpayment policy is approved.
- Payment records must be firm- and case-authorized through the same approved access boundary as the invoice.

### Audit/history
- Record issue, void, payment, reversal/refund and permitted metadata changes with actor and timestamp.
- Preserve the issued invoice snapshot and a stable printable representation or deterministic rendering inputs.
- Do not expose audit notes or payment references to users without case access.

## 3. Derived payment states

Payment status must not be stored as a user-editable field. Derive it from invoice lifecycle, total, effective payments and due date:

| Condition | Display state |
|---|---|
| Draft invoice | Draft |
| Issued and effective payments = 0 | Unpaid |
| Issued and 0 < effective payments < total | Partially paid |
| Issued and effective payments = total | Paid |
| Issued, balance > 0, and due date is before the business-local current date | Overdue |
| Voided invoice | Void |

The API must return the exact balance and a consistent as-of date/time basis. A draft is not overdue. A fully paid invoice is not overdue even if its due date has passed.

## 4. Proposed API contract

Route names are illustrative and must be aligned with the existing API conventions after review.

- POST /cases/{case_id}/invoices — create a draft with one or more validated line items.
- GET /invoices — list invoices visible to the signed-in user, with filters for case, client, issue/due range and derived payment state.
- GET /invoices/{invoice_id} — retrieve invoice, line items, payments, totals, balance, state and history.
- PATCH /invoices/{invoice_id} — edit draft only; reject edits after issue.
- POST /invoices/{invoice_id}/issue — atomically allocate invoice number, freeze invoice snapshot and transition draft to issued.
- POST /invoices/{invoice_id}/payments — append a payment with idempotency protection against duplicate submissions.
- POST /invoices/{invoice_id}/payments/{payment_id}/reverse — append a reversal/refund with reason and actor.
- POST /invoices/{invoice_id}/void — void an issued invoice with mandatory reason and audit event, subject to approved accounting policy.
- GET /invoices/{invoice_id}/print — render a print-ready view/PDF from the immutable issued snapshot.

All writes must use the existing transaction/rollback pattern. Every route must enforce firm scope and case membership using the established authorization helper; guessed IDs must not disclose cross-firm or non-member invoice existence. Never rely on frontend filtering for authorization.

## 5. UI acceptance criteria

- Create invoice from a case and show the linked client/case clearly.
- Add, remove and reorder multiple line items while in draft.
- Show server-calculated subtotal, any approved adjustment/tax fields, total, paid amount and balance in EGP.
- Require confirmation before issue and void.
- Show invoice number, issue/due dates and derived payment state.
- Record partial payments and show a chronological payment ledger.
- Provide searchable/filterable invoice history and a print/export action.
- Handle empty states, validation errors, duplicate payment submission and concurrent issue attempts.
- Display Arabic RTL and Latin invoice numbers/amounts without bidi corruption; provide a usable print layout.

## 6. Required regression tests

1. Firm A cannot list, read, print, pay, void or mutate Firm B invoices by guessed IDs.
2. A same-firm user without case membership cannot access invoice data or mutate it.
3. Invoice creation rejects missing/foreign case references and malformed dates/amounts.
4. Line totals and invoice totals are calculated server-side with exact arithmetic.
5. Invoice number allocation remains unique under concurrent issue requests.
6. Issued invoices cannot be silently edited; void/replacement preserves history.
7. Partial, full, overdue, unpaid, draft and void states are derived correctly at date boundaries.
8. Duplicate payment requests are idempotent; overpayment and invalid reversal are rejected.
9. Payment reversal restores the correct balance without deleting the original payment.
10. Print/export uses the issued snapshot and does not leak another firm's data.
11. Existing fee overview and fee records remain backward-compatible during any approved migration.
12. Separate-database runtime tests exercise the same schema and authorization behavior as production.

## 7. Database-owner decisions required before implementation

- Approve the logical model and the actual migration target.
- Confirm tenant isolation strategy and whether firm identity is implicit in per-firm databases or explicit in row keys.
- Confirm invoice-number format, sequencing and reset policy.
- Confirm whether invoices may be issued only by firm admins/partners or by another role.
- Confirm client snapshot/identity fields and what happens when a case's client changes.
- Confirm tax/VAT, withholding, discounts, credit notes, refunds and overpayment policy.
- Confirm retention, export, legal hold and deletion behavior for issued invoices and payment records.
- Confirm whether the first release is a fee invoice only or must satisfy Egyptian tax-invoice/e-receipt requirements.

**Implementation gate:** do not add invoice tables, migrations, tenant filters or schema changes until the database owner approves the decisions above. After approval, implement the migration and tests first, then API, then UI. Do not migrate legacy fees rows into invoices unless a reviewed mapping and reconciliation policy is approved.