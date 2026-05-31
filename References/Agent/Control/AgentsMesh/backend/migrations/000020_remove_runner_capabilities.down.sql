-- Re-add capabilities column to runners table (rollback)
ALTER TABLE runners ADD COLUMN IF NOT EXISTS capabilities JSONB;
CREATE INDEX IF NOT EXISTS idx_runners_capabilities ON runners USING GIN (capabilities);
COMMENT ON COLUMN runners.capabilities IS 'JSON array of plugin capabilities reported by runner';
