-- Fix permission mode system: align with Claude Code Agent SDK --permission-mode flag
--
-- Problems fixed:
-- 1. "bypassPermissions" was mapped to --dangerously-skip-permissions (old flag)
--    instead of --permission-mode bypassPermissions (new flag, hooks still work)
-- 2. "plan" in ACP/pipe mode = read-only (no execution), not plan-then-execute
--    ACP mode now degrades "plan" to "default" (per-tool can_use_tool approval)
-- 3. Only 3 options exposed; Claude Code supports 6 (adding acceptEdits, dontAsk)
-- 4. Default was "default"; changed to "bypassPermissions" for autonomous execution

-- Claude Code: update CONFIG options, default, and build logic
UPDATE agents SET agentfile_source = E'# === Identity ===\nAGENT claude\nEXECUTABLE claude\n\n# === Mode ===\nMODE pty\nMODE acp "-p" "--verbose" "--input-format" "stream-json" "--output-format" "stream-json"\n\n# === Configuration ===\nCONFIG model SELECT("", "sonnet", "opus") = ""\nCONFIG permission_mode SELECT("default", "plan", "acceptEdits", "dontAsk", "bypassPermissions") = "bypassPermissions"\n\n# === Environment ===\nENV ANTHROPIC_API_KEY SECRET OPTIONAL\nENV ANTHROPIC_AUTH_TOKEN SECRET OPTIONAL\nENV ANTHROPIC_BASE_URL TEXT OPTIONAL\n\n# === Prompt ===\nPROMPT_POSITION prepend\n\n# === Capabilities ===\nMCP ON\nSKILLS am-delegate, am-channel\n\n# === Build Logic ===\narg "--model" config.model when config.model != ""\n\nif config.permission_mode == "plan" and mode == "acp" {\n  arg "--permission-mode" "default"\n}\nif config.permission_mode == "plan" and mode != "acp" {\n  arg "--permission-mode" "plan"\n}\nif config.permission_mode != "default" and config.permission_mode != "plan" and config.permission_mode != "" {\n  arg "--permission-mode" config.permission_mode\n}\n\nif mcp.enabled {\n  plugin_dir = sandbox.root + "/agentsmesh-plugin"\n\n  mkdir plugin_dir\n  mkdir plugin_dir + "/.claude-plugin"\n\n  file plugin_dir + "/.claude-plugin/plugin.json" json({\n    name: "agentsmesh",\n    description: "AgentsMesh collaboration plugin for Claude Code",\n    version: "1.0.0"\n  })\n\n  file plugin_dir + "/.mcp.json" json({ mcpServers: mcp.servers })\n\n  arg "--plugin-dir" plugin_dir\n}\n'
WHERE slug = 'claude-code';
