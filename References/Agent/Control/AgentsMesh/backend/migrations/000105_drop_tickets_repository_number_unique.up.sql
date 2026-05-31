-- Drop legacy unique constraint on (repository_id, number).
-- Ticket number is scoped by (organization_id, prefix), not by repository.
-- Uniqueness is already enforced by idx_tickets_org_slug on (organization_id, slug).
ALTER TABLE tickets DROP CONSTRAINT IF EXISTS tickets_repository_id_number_key;
