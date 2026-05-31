-- Add resume support to agent command_templates
-- Resume is triggered by setting resume_enabled=true and optionally resume_session=<session_id>
-- in config_overrides when creating a Pod

-- Claude Code: Add --session-id for new sessions, --resume <id> for resuming
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
            },
            {
                "condition": {"field": "session_id", "operator": "not_empty"},
                "args": ["--session-id", "{{.config.session_id}}"]
            },
            {
                "condition": {"field": "resume_enabled", "operator": "eq", "value": true},
                "args": ["--resume", "{{.config.resume_session}}"]
            }
        ]
    }'::jsonb
WHERE slug = 'claude-code';

-- Gemini CLI: Add --resume latest for resuming
UPDATE agent_types SET
    command_template = '{
        "args": [
            {
                "condition": {"field": "sandbox_mode", "operator": "eq", "value": true},
                "args": ["--sandbox"]
            },
            {
                "condition": {"field": "resume_enabled", "operator": "eq", "value": true},
                "args": ["--resume", "latest"]
            }
        ]
    }'::jsonb
WHERE slug = 'gemini-cli';

-- Aider: Add --restore-chat-history for resuming
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
            },
            {
                "condition": {"field": "resume_enabled", "operator": "eq", "value": true},
                "args": ["--restore-chat-history"]
            }
        ]
    }'::jsonb
WHERE slug = 'aider';

-- Codex CLI: For resume, need to use "codex resume --last" command
-- This requires changing the executable or command, which is more complex
-- For now, add a resume_enabled check that will use --approval-mode to continue
-- Note: Codex's resume is automatic based on directory context
UPDATE agent_types SET
    command_template = '{
        "args": [
            {
                "condition": {"field": "approval_mode", "operator": "not_empty"},
                "args": ["--approval-mode", "{{.config.approval_mode}}"]
            }
        ]
    }'::jsonb
WHERE slug = 'codex-cli';
-- Note: Codex CLI sessions are automatically tracked by directory
-- No special resume parameter needed - just restarting in the same directory resumes
