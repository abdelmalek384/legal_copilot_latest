-- Firm-local EGP fee invoices. This is not an Egyptian tax-invoice/e-receipt schema.
-- Each firm has its own database, so invoice numbering is naturally firm-scoped.
CREATE TABLE invoice_sequences (
    issue_year INTEGER PRIMARY KEY CHECK(issue_year BETWEEN 2000 AND 2200),
    next_sequence INTEGER NOT NULL CHECK(next_sequence > 0)
);

CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE RESTRICT,
    invoice_number TEXT UNIQUE,
    status TEXT NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','issued','void')),
    currency TEXT NOT NULL DEFAULT 'EGP' CHECK(currency = 'EGP'),
    client_name_snapshot TEXT NOT NULL DEFAULT '',
    case_title_snapshot TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    subtotal_piasters INTEGER NOT NULL DEFAULT 0 CHECK(subtotal_piasters >= 0),
    total_piasters INTEGER NOT NULL DEFAULT 0 CHECK(total_piasters >= 0),
    issue_date TEXT,
    due_date TEXT,
    created_by INTEGER NOT NULL CHECK(created_by > 0),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    issued_at TEXT,
    void_reason TEXT,
    voided_by INTEGER,
    voided_at TEXT,
    CHECK((status = 'draft' AND invoice_number IS NULL AND issued_at IS NULL)
       OR (status IN ('issued','void') AND invoice_number IS NOT NULL AND issued_at IS NOT NULL))
);

CREATE TABLE invoice_lines (
    id INTEGER PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE RESTRICT,
    position INTEGER NOT NULL CHECK(position > 0),
    description TEXT NOT NULL CHECK(length(trim(description)) BETWEEN 1 AND 500),
    quantity_milli INTEGER NOT NULL CHECK(quantity_milli BETWEEN 1 AND 1000000),
    unit_price_piasters INTEGER NOT NULL CHECK(unit_price_piasters BETWEEN 0 AND 1000000000000),
    line_total_piasters INTEGER NOT NULL CHECK(line_total_piasters BETWEEN 0 AND 1000000000000),
    UNIQUE(invoice_id, position)
);

CREATE TABLE invoice_payments (
    id INTEGER PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE RESTRICT,
    amount_piasters INTEGER NOT NULL CHECK(amount_piasters > 0),
    paid_on TEXT NOT NULL,
    method TEXT NOT NULL CHECK(method IN ('cash','bank_transfer','instapay','other')),
    reference TEXT NOT NULL DEFAULT '' CHECK(length(reference) <= 200),
    note TEXT NOT NULL DEFAULT '' CHECK(length(note) <= 1000),
    idempotency_key TEXT NOT NULL CHECK(length(idempotency_key) BETWEEN 8 AND 100),
    recorded_by INTEGER NOT NULL CHECK(recorded_by > 0),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(invoice_id, idempotency_key)
);

CREATE TABLE invoice_events (
    id INTEGER PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE RESTRICT,
    actor_user_id INTEGER NOT NULL CHECK(actor_user_id > 0),
    event_type TEXT NOT NULL CHECK(event_type IN ('created','issued','payment_recorded','voided')),
    details_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_invoices_case_status ON invoices(case_id,status,created_at DESC);
CREATE INDEX idx_invoices_number ON invoices(invoice_number);
CREATE INDEX idx_invoice_lines_invoice ON invoice_lines(invoice_id,position);
CREATE INDEX idx_invoice_payments_invoice ON invoice_payments(invoice_id,paid_on,id);
CREATE INDEX idx_invoice_events_invoice ON invoice_events(invoice_id,id);

CREATE TRIGGER invoice_lines_insert_only_draft
BEFORE INSERT ON invoice_lines
WHEN (SELECT status FROM invoices WHERE id=NEW.invoice_id) != 'draft'
BEGIN SELECT RAISE(ABORT, 'issued invoice lines are immutable'); END;
CREATE TRIGGER invoice_lines_update_only_draft
BEFORE UPDATE ON invoice_lines
WHEN (SELECT status FROM invoices WHERE id=OLD.invoice_id) != 'draft'
BEGIN SELECT RAISE(ABORT, 'issued invoice lines are immutable'); END;
CREATE TRIGGER invoice_lines_delete_only_draft
BEFORE DELETE ON invoice_lines
WHEN (SELECT status FROM invoices WHERE id=OLD.invoice_id) != 'draft'
BEGIN SELECT RAISE(ABORT, 'issued invoice lines are immutable'); END;

CREATE TRIGGER invoice_issued_content_immutable
BEFORE UPDATE OF case_id,invoice_number,currency,client_name_snapshot,case_title_snapshot,
    description,subtotal_piasters,total_piasters,issue_date,due_date,created_by,created_at,issued_at
ON invoices
WHEN OLD.status IN ('issued','void')
BEGIN SELECT RAISE(ABORT, 'issued invoice content is immutable'); END;

CREATE TRIGGER invoice_payments_no_update
BEFORE UPDATE ON invoice_payments
BEGIN SELECT RAISE(ABORT, 'invoice payments are append-only'); END;
CREATE TRIGGER invoice_payments_no_delete
BEFORE DELETE ON invoice_payments
BEGIN SELECT RAISE(ABORT, 'invoice payments are append-only'); END;

CREATE TRIGGER invoice_events_no_update
BEFORE UPDATE ON invoice_events
BEGIN SELECT RAISE(ABORT, 'invoice events are append-only'); END;
CREATE TRIGGER invoice_events_no_delete
BEFORE DELETE ON invoice_events
BEGIN SELECT RAISE(ABORT, 'invoice events are append-only'); END;
