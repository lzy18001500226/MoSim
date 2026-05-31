-- Change tickets.identifier unique constraint from global to per-organization.
-- Bug: different organizations using the same ticket_prefix (e.g., "TICKET-")
-- would conflict on the global unique constraint when generating identifiers.

-- Drop the global unique constraint (auto-created by UNIQUE keyword in 000001)
ALTER TABLE tickets DROP CONSTRAINT IF EXISTS tickets_identifier_key;

-- Drop the redundant plain index (also created in 000001)
DROP INDEX IF EXISTS idx_tickets_identifier;

-- Create composite unique index scoped to organization
CREATE UNIQUE INDEX idx_tickets_org_identifier ON tickets(organization_id, identifier);
