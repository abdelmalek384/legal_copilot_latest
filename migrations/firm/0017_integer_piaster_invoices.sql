-- Per-firm invoice ledger. All monetary values are integer EGP piasters.
CREATE TABLE invoice_number_sequences (
    document_kind TEXT NOT NULL CHECK(document_kind IN ('invoice','receipt')),
    calendar_year INTEGER NOT NULL CHECK(calendar_year BETWEEN 2000 AND 9999),
    last_sequence INTEGER NOT NULL DEFAULT 0 CHECK(last_sequence >= 0),
    PRIMARY KEY(document_kind, calendar_year)
);

CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    invoice_number TEXT NOT NULL UNIQUE CHECK(length(invoice_number) BETWEEN 14 AND 24),
    issue_date TEXT NOT NULL CHECK(length(issue_date) = 10),
    due_date TEXT CHECK(due_date IS NULL OR length(due_date) = 10),
    currency TEXT NOT NULL DEFAULT 'EGP' CHECK(currency = 'EGP'),
    total_piasters INTEGER NOT NULL CHECK(total_piasters > 0),
    status TEXT NOT NULL DEFAULT 'unpaid' CHECK(status IN ('unpaid','partially_paid','paid','void')),
    notes TEXT NOT NULL DEFAULT '' CHECK(length(notes) <= 2000),
    created_by INTEGER NOT NULL CHECK(created_by > 0),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX invoices_case_issue ON invoices(case_id, issue_date DESC, id DESC);
CREATE INDEX invoices_status_due ON invoices(status, due_date);

CREATE TABLE invoice_lines (
    id INTEGER PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE RESTRICT,
    line_number INTEGER NOT NULL CHECK(line_number > 0),
    description TEXT NOT NULL CHECK(length(trim(description)) BETWEEN 1 AND 500),
    quantity INTEGER NOT NULL CHECK(quantity BETWEEN 1 AND 1000000),
    unit_amount_piasters INTEGER NOT NULL CHECK(unit_amount_piasters BETWEEN 0 AND 9000000000000000),
    line_total_piasters INTEGER NOT NULL CHECK(line_total_piasters BETWEEN 0 AND 9000000000000000),
    UNIQUE(invoice_id, line_number)
);

CREATE TABLE invoice_payments (
    id INTEGER PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE RESTRICT,
    amount_piasters INTEGER NOT NULL CHECK(amount_piasters > 0),
    paid_at TEXT NOT NULL CHECK(length(paid_at) = 10),
    method TEXT NOT NULL CHECK(method IN ('cash','bank_transfer','instapay','other')),
    reference TEXT NOT NULL DEFAULT '' CHECK(length(reference) <= 160),
    received_by INTEGER NOT NULL CHECK(received_by > 0),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX invoice_payments_invoice ON invoice_payments(invoice_id, paid_at, id);

CREATE TABLE invoice_receipts (
    id INTEGER PRIMARY KEY,
    payment_id INTEGER NOT NULL UNIQUE REFERENCES invoice_payments(id) ON DELETE RESTRICT,
    receipt_number TEXT NOT NULL UNIQUE CHECK(length(receipt_number) BETWEEN 14 AND 24),
    issued_at TEXT NOT NULL DEFAULT (datetime('now')),
    issued_by INTEGER NOT NULL CHECK(issued_by > 0)
);

CREATE TRIGGER invoice_lines_no_update_after_payment
BEFORE UPDATE ON invoice_lines
WHEN EXISTS (SELECT 1 FROM invoice_payments p WHERE p.invoice_id=OLD.invoice_id)
BEGIN SELECT RAISE(ABORT, 'invoice lines cannot change after a payment'); END;

CREATE TRIGGER invoice_lines_no_delete_after_payment
BEFORE DELETE ON invoice_lines
WHEN EXISTS (SELECT 1 FROM invoice_payments p WHERE p.invoice_id=OLD.invoice_id)
BEGIN SELECT RAISE(ABORT, 'invoice lines cannot be deleted after a payment'); END;

CREATE TRIGGER invoice_payments_no_update
BEFORE UPDATE ON invoice_payments
BEGIN SELECT RAISE(ABORT, 'invoice payments are append-only'); END;

CREATE TRIGGER invoice_payments_no_delete
BEFORE DELETE ON invoice_payments
BEGIN SELECT RAISE(ABORT, 'invoice payments are append-only'); END;

CREATE TRIGGER invoice_receipts_no_update
BEFORE UPDATE ON invoice_receipts
BEGIN SELECT RAISE(ABORT, 'invoice receipts are append-only'); END;

CREATE TRIGGER invoice_receipts_no_delete
BEFORE DELETE ON invoice_receipts
BEGIN SELECT RAISE(ABORT, 'invoice receipts are append-only'); END;
