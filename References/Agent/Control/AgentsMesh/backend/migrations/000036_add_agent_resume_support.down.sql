-- Revert resume support from agent command_templates

-- Claude Code: Remove session_id and resume_enabled args
UPDATE agent_types SET
    command_template = '{
        "args": [
            {
                "condition": {"field": "model", "operator": "not_empty"},
                "args": ["--model", "{{.config.model}}"]
            },
            {
                "condition": {"field": "permission_mode", "operator": "eq", "value": "plan"},
                "args": ["--permission-mode", "plan"]
            },
            {
                "condition": {"field": "dangerously_skip_permissions", "operator": "eq", "value": true},
                "args": ["--dangerously-skip-permissions"]
            },
            {
                "condition": {"field": "think_level", "operator": "not_empty"},
                "args": ["--{{.config.think_level}}"]
            },
            {
                "condition": {"field": "mcp_enabled", "operator": "eq", "value": true},
                "args": ["--mcp-config", "{{.sandbox.root_path}}/mcp-config.json"]
            }
        ]
    }'::jsonb
WHERE slug = 'claude-code';

-- Gemini CLI: Remove resume args
UPDATE agent_types SET
    command_template = '{
        "args": [
            {
                "condition": {"field": "sandbox_mode", "operator": "eq", "value": true},
                "args": ["--sandbox"]
            }
        ]
    }'::jsonb
WHERE slug = 'gemini-cli';

-- Aider: Remove restore-chat-history arg
UPDATE agent_types SET
    command_template = '{
        "args": [
            {
                "condition": {"field": "model", "operator": "not_empty"},
                "args": ["--model", "{{.config.model}}"]
            },
            {
                "condition": {"field": "edit_format", "operator": "not_empty"},
                "args": ["--edit-format", "{{.config.edit_format}}"]
            }
        ]
    }'::jsonb
WHERE slug = 'aider';

-- Codex CLI: No changes needed (resume is automatic based on directory)
