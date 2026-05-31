package eval

import (
	"testing"

	"github.com/anthropics/agentsmesh/agentfile/parser"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestEval_BuiltinJSON(t *testing.T) {
	prog, errs := parser.Parse(`
AGENT test
x = json({ key: "value", num: 42 })
file "/out.json" x
`)
	require.Empty(t, errs)
	ctx := NewContext(nil)
	require.NoError(t, Eval(prog, ctx))

	require.Len(t, ctx.Result.FilesToCreate, 1)
	assert.Contains(t, ctx.Result.FilesToCreate[0].Content, `"key":"value"`)
}

func TestEval_BuiltinJSONMerge(t *testing.T) {
	prog, errs := parser.Parse(`
AGENT test
merged = json_merge(a, b)
file "/out.json" json({ mcpServers: merged })
`)
	require.Empty(t, errs)

	ctx := NewContext(map[string]interface{}{
		"a": map[string]interface{}{"server1": map[string]interface{}{"url": "http://a"}},
		"b": map[string]interface{}{"server2": map[string]interface{}{"url": "http://b"}},
	})
	require.NoError(t, Eval(prog, ctx))

	require.Len(t, ctx.Result.FilesToCreate, 1)
	content := ctx.Result.FilesToCreate[0].Content
	assert.Contains(t, content, "server1")
	assert.Contains(t, content, "server2")
}

func TestEval_BuiltinMCPTransform_Gemini(t *testing.T) {
	prog, errs := parser.Parse(`
AGENT test
transformed = mcp_transform(servers, "gemini")
`)
	require.Empty(t, errs)

	ctx := NewContext(map[string]interface{}{
		"servers": map[string]interface{}{
			"agentsmesh": map[string]interface{}{
				"type": "http",
				"url":  "http://localhost:19000/mcp",
			},
		},
	})
	require.NoError(t, Eval(prog, ctx))

	result, _ := ctx.Get("transformed")
	m := result.(map[string]interface{})
	srv := m["agentsmesh"].(map[string]interface{})
	assert.Equal(t, "http://localhost:19000/mcp", srv["httpUrl"])
	_, hasURL := srv["url"]
	assert.False(t, hasURL, "url should be removed for gemini format")
	_, hasType := srv["type"]
	assert.False(t, hasType, "type should be removed for gemini format")
}

func TestEval_BuiltinStrReplace(t *testing.T) {
	prog, errs := parser.Parse(`
AGENT test
x = str_replace("hello world", "world", "agentfile")
arg x
`)
	require.Empty(t, errs)
	ctx := NewContext(nil)
	require.NoError(t, Eval(prog, ctx))
	assert.Equal(t, []string{"hello agentfile"}, ctx.Result.LaunchArgs)
}

func TestEval_BuiltinStrContains(t *testing.T) {
	prog, errs := parser.Parse(`
AGENT test
CONFIG model STRING = "claude-opus"
arg "--found" when str_contains(config.model, "opus")
`)
	require.Empty(t, errs)

	ctx := NewContext(map[string]interface{}{
		"config": make(map[string]interface{}),
	})
	require.NoError(t, Eval(prog, ctx))
	assert.Equal(t, []string{"--found"}, ctx.Result.LaunchArgs)
}

func TestEval_AllDeclarationsInBuildResult(t *testing.T) {
	prog, errs := parser.Parse(`
AGENT gemini
EXECUTABLE gemini
REPO "https://github.com/org/repo"
BRANCH "main"
GIT_CREDENTIAL oauth
MCP ON
SKILLS am-delegate, am-channel
SETUP timeout=120 <<EOF
npm install
EOF

PROMPT_POSITION append
`)
	require.Empty(t, errs)

	ctx := NewContext(nil)
	require.NoError(t, Eval(prog, ctx))

	r := ctx.Result
	assert.Equal(t, "gemini", r.LaunchCommand)
	assert.Equal(t, "gemini", r.Executable)
	assert.Equal(t, "append", r.PromptPosition)
	assert.True(t, r.MCPEnabled)
	assert.Equal(t, []string{"am-delegate", "am-channel"}, r.Skills)

	assert.Equal(t, "https://github.com/org/repo", r.Sandbox.RepoURL)
	assert.Equal(t, "main", r.Sandbox.Branch)
	assert.Equal(t, "oauth", r.Sandbox.CredentialType)

	assert.Equal(t, 120, r.Setup.Timeout)
	assert.Contains(t, r.Setup.Script, "npm install")
}

const fullClaudeCodeAgentFile = `
AGENT claude
EXECUTABLE claude

MODE pty
MODE acp "-p" "--verbose" "--input-format" "stream-json" "--output-format" "stream-json"

CONFIG model SELECT("", "sonnet", "opus") = ""
CONFIG permission_mode SELECT("default", "plan", "acceptEdits", "dontAsk", "bypassPermissions") = "bypassPermissions"
CONFIG mcp_enabled BOOL = true

ENV ANTHROPIC_API_KEY SECRET OPTIONAL
MCP ON
SKILLS am-delegate, am-channel

PROMPT_POSITION prepend

arg "--model" config.model when config.model != ""

if config.permission_mode == "plan" and mode == "acp" {
  arg "--permission-mode" "default"
}
if config.permission_mode == "plan" and mode != "acp" {
  arg "--permission-mode" "plan"
}
if config.permission_mode != "default" and config.permission_mode != "plan" and config.permission_mode != "" {
  arg "--permission-mode" config.permission_mode
}

if mcp.enabled {
  mcp_cfg = json_merge(mcp.builtin, mcp.installed)
  plugin_dir = sandbox.root + "/agentsmesh-plugin"

  mkdir plugin_dir
  mkdir plugin_dir + "/.claude-plugin"

  file plugin_dir + "/.claude-plugin/plugin.json" json({
    name: "agentsmesh",
    description: "AgentsMesh collaboration plugin",
    version: "1.0.0"
  })

  file plugin_dir + "/.mcp.json" json({ mcpServers: mcp_cfg })

  arg "--plugin-dir" plugin_dir
}
`

func TestEval_FullClaudeCode(t *testing.T) {
	// Simulate post-resolve state: CONFIG defaults contain final resolved values.
	overridden := replaceConfigDefault(fullClaudeCodeAgentFile, "model", `"opus"`)
	overridden = replaceConfigDefault(overridden, "permission_mode", `"plan"`)
	prog, errs := parser.Parse(overridden)
	require.Empty(t, errs)

	ctx := newMCPContext()
	require.NoError(t, Eval(prog, ctx))
	ApplyModeArgs(ctx.Result)

	r := ctx.Result
	assert.Equal(t, "claude", r.LaunchCommand)
	assert.Equal(t, "prepend", r.PromptPosition)
	assert.True(t, r.MCPEnabled)
	assert.Equal(t, []string{"am-delegate", "am-channel"}, r.Skills)

	// PTY mode (default): plan stays as --permission-mode plan
	assert.Contains(t, r.LaunchArgs, "--model")
	assert.Contains(t, r.LaunchArgs, "opus")
	assert.Contains(t, r.LaunchArgs, "--permission-mode")
	assert.Contains(t, r.LaunchArgs, "plan")
	assert.Contains(t, r.LaunchArgs, "--plugin-dir")
}
