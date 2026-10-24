-- Supports ordered operator review of unclassified legacy ownership records.
CREATE INDEX IF NOT EXISTS idx_tenant_quarantine_first_seen
    ON tenant_ownership_quarantine(first_seen);
