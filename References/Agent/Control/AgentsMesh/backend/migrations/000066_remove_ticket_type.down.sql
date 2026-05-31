-- Restore the ticket type column with its original default.
ALTER TABLE tickets ADD COLUMN type VARCHAR(50) NOT NULL DEFAULT 'task';
