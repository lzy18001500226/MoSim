-- Remove the ticket type column.
-- The type field (task/bug/feature/etc.) is no longer used; all tickets are
-- treated uniformly regardless of former type.
ALTER TABLE tickets DROP COLUMN IF EXISTS type;
