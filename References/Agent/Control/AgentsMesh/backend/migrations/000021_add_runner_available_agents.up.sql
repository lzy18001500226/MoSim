-- Add available_agents column to runners table
-- Stores the list of agent type slugs that are available on the runner
ALTER TABLE runners ADD COLUMN IF NOT EXISTS available_agents JSONB DEFAULT '[]'::jsonb;

-- Add comment for documentation
COMMENT ON COLUMN runners.available_agents IS 'List of agent type slugs available on this runner, populated during initialization handshake';
