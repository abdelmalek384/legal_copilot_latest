-- Support the measured firm-wide invoice list ordering without changing invoice semantics.
CREATE INDEX idx_invoices_created_id_case
ON invoices(created_at DESC, id DESC, case_id);
