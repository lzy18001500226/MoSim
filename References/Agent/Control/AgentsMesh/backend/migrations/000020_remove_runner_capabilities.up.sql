-- Remove deprecated capabilities column from runners table
-- Capabilities are no longer needed as agent configuration is now managed by Backend ConfigSchema

DROP INDEX IF EXISTS idx_runners_capabilities;
ALTER TABLE runners DROP COLUMN IF EXISTS capabilities;
