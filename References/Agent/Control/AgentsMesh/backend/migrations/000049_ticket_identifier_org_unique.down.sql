-- Revert: restore global unique constraint on tickets.identifier

-- Drop the composite unique index
DROP INDEX IF EXISTS idx_tickets_org_identifier;

-- Restore the global unique constraint
ALTER TABLE tickets ADD CONSTRAINT tickets_identifier_key UNIQUE (identifier);

-- Restore the plain index
CREATE INDEX idx_tickets_identifier ON tickets(identifier);
