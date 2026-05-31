-- Restore think_level to Claude Code agent configuration

-- Step 1: Add back think_level field to config_schema fields array
UPDATE agent_types SET
    config_schema = jsonb_set(
        config_schema,
        '{fields}',
        (config_schema->'fields') || '[{
            "name": "think_level",
            "type": "select",
            "default": "",
            "options": [
                {"value": ""},
                {"value": "think"},
                {"value": "ultrathink"}
            ]
        }]'::jsonb
    )
WHERE slug = 'claude-code'
  AND config_schema->'fields' IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM jsonb_array_elements(config_schema->'fields') AS field
      WHERE field->>'name' = 'think_level'
  );

-- Step 2: Add back think_level arg to command_template args array
-- Insert before the mcp_enabled arg (second to last) to maintain original ordering
-- The think_level arg uses a template to pass --think or --ultrathink based on the config value
UPDATE agent_types SET
    command_template = jsonb_set(
        command_template,
        '{args}',
        (command_template->'args') || '[{
            "condition": {"field": "think_level", "operator": "not_empty"},
            "args": ["--{{.config.think_level}}"]
        }]'::jsonb
    )
WHERE slug = 'claude-code'
  AND command_template->'args' IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM jsonb_array_elements(command_template->'args') AS arg
      WHERE arg->'condition'->>'field' = 'think_level'
  );

-- Note: user_agent_configs values are not restored since those are user data
-- and the original values are lost after the up migration removes them.
