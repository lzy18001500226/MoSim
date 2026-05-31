-- Add capabilities column to runners table
ALTER TABLE runners ADD COLUMN IF NOT EXISTS capabilities JSONB;

-- Create index for capabilities queries (useful for filtering by supported agents)
CREATE INDEX IF NOT EXISTS idx_runners_capabilities ON runners USING GIN (capabilities);

COMMENT ON COLUMN runners.capabilities IS 'JSON array of plugin capabilities reported by runner';
