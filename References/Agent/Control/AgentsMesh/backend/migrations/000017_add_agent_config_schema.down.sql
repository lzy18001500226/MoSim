-- Remove the new columns from agent_types
ALTER TABLE agent_types
    DROP COLUMN IF EXISTS executable,
    DROP COLUMN IF EXISTS config_schema,
    DROP COLUMN IF EXISTS command_template,
    DROP COLUMN IF EXISTS files_template;

-- Drop the index
DROP INDEX IF EXISTS idx_agent_types_slug_active;
