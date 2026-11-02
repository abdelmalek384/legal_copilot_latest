-- Firm-local invoice and receipt ledger. All monetary values are integer EGP piasters.
CREATE TABLE invoice_sequences (
    year INTEGER PRIMARY KEY CHECK(year BETWEEN 2000 AND 2200),
    next_number INTEGER NOT NULL CHECK(next_number > 0)
);
CREATE TABLE receipt_sequences (
    year INTEGER PRIMARY KEY CHECK(year BETWEEN 2000 AND 2200),
    next_number INTEGER NOT NULL CHECK(next_number > 0)
);
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    invoice_number TEXT NOT NULL UNIQUE,
    client_name TEXT NOT NULL,
    issue_date TEXT NOT NULL CHECK(length(issue_date)=10),
    due_date TEXT CHECK(due_date IS NULL OR length(due_date)=10),
    currency TEXT NOT NULL DEFAULT 'EGP' CHECK(currency='EGP'),
    status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','issued','void')),
    subtotal_piasters INTEGER NOT NULL CHECK(subtotal_piasters >= 0),
    total_piasters INTEGER NOT NULL CHECK(total_piasters >= 0),
    note TEXT NOT NULL DEFAULT '',
    snapshot_json TEXT,
    void_reason TEXT,
    created_by INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    issued_at TEXT,
    voided_at TEXT
);
CREATE INDEX idx_invoices_case_date ON invoices(case_id,issue_date DESC,id DESC);
CREATE INDEX idx_invoices_status_due ON invoices(status,due_date);
CREATE TABLE invoice_lines (
    id INTEGER PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE RESTRICT,
    line_number INTEGER NOT NULL CHECK(line_number > 0),
    description TEXT NOT NULL CHECK(length(trim(description)) > 0),
    quantity INTEGER NOT NULL CHECK(quantity BETWEEN 1 AND 10000),
    unit_price_piasters INTEGER NOT NULL CHECK(unit_price_piasters >= 0),
    line_total_piasters INTEGER NOT NULL CHECK(line_total_piasters >= 0),
    UNIQUE(invoice_id,line_number)
);
CREATE INDEX idx_invoice_lines_invoice ON invoice_lines(invoice_id,line_number);
CREATE TABLE invoice_payments (
    id INTEGER PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE RESTRICT,
    receipt_number TEXT NOT NULL UNIQUE,
    amount_piasters INTEGER NOT NULL CHECK(amount_piasters > 0),
    method TEXT NOT NULL CHECK(method IN ('cash','bank_transfer','instapay','cheque','other')),
    reference TEXT NOT NULL DEFAULT '',
    paid_on TEXT NOT NULL CHECK(length(paid_on)=10),
    recorded_by INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_invoice_payments_invoice ON invoice_payments(invoice_id,paid_on,id);
CREATE TRIGGER invoice_lines_insert_draft_only
BEFORE INSERT ON invoice_lines
WHEN (SELECT status FROM invoices WHERE id=NEW.invoice_id) <> 'draft'
BEGIN SELECT RAISE(ABORT, 'issued invoice lines are immutable'); END;
CREATE TRIGGER invoice_lines_update_draft_only
BEFORE UPDATE ON invoice_lines
WHEN (SELECT status FROM invoices WHERE id=OLD.invoice_id) <> 'draft'
BEGIN SELECT RAISE(ABORT, 'issued invoice lines are immutable'); END;
CREATE TRIGGER invoice_lines_delete_draft_only
BEFORE DELETE ON invoice_lines
WHEN (SELECT status FROM invoices WHERE id=OLD.invoice_id) <> 'draft'
BEGIN SELECT RAISE(ABORT, 'issued invoice lines are immutable'); END;
CREATE TRIGGER invoice_payments_no_update
BEFORE UPDATE ON invoice_payments
BEGIN SELECT RAISE(ABORT, 'invoice payments are append-only'); END;
CREATE TRIGGER invoice_payments_no_delete
BEFORE DELETE ON invoice_payments
BEGIN SELECT RAISE(ABORT, 'invoice payments are append-only'); END;
CREATE TRIGGER invoices_issued_no_delete
BEFORE DELETE ON invoices
WHEN OLD.status IN ('issued','void')
BEGIN SELECT RAISE(ABORT, 'issued invoices cannot be deleted'); END;
