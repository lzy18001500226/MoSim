-- Remove capabilities column from runners table
DROP INDEX IF EXISTS idx_runners_capabilities;
ALTER TABLE runners DROP COLUMN IF EXISTS capabilities;
