-- Remove think_level from Claude Code agent configuration
-- This field is no longer needed as the Claude CLI no longer supports --think/--ultrathink flags

-- Step 1: Remove think_level field from config_schema fields array
-- Rebuild the fields array excluding any element where name='think_level'
UPDATE agent_types SET
    config_schema = jsonb_set(
        config_schema,
        '{fields}',
        (
            SELECT COALESCE(jsonb_agg(field), '[]'::jsonb)
            FROM jsonb_array_elements(config_schema->'fields') AS field
            WHERE field->>'name' != 'think_level'
        )
    )
WHERE slug = 'claude-code'
  AND config_schema->'fields' IS NOT NULL;

-- Step 2: Remove think_level arg from command_template args array
-- Rebuild the args array excluding any element where condition.field='think_level'
UPDATE agent_types SET
    command_template = jsonb_set(
        command_template,
        '{args}',
        (
            SELECT COALESCE(jsonb_agg(arg), '[]'::jsonb)
            FROM jsonb_array_elements(command_template->'args') AS arg
            WHERE arg->'condition'->>'field' != 'think_level'
        )
    )
WHERE slug = 'claude-code'
  AND command_template->'args' IS NOT NULL;

-- Step 3: Clean existing user_agent_configs to remove think_level from config_values
UPDATE user_agent_configs
SET config_values = config_values - 'think_level',
    updated_at = NOW()
WHERE agent_type_id = (SELECT id FROM agent_types WHERE slug = 'claude-code')
  AND config_values ? 'think_level';
