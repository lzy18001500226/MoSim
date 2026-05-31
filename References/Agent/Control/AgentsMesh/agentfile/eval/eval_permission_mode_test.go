package eval

import (
	"testing"

	"github.com/anthropics/agentsmesh/agentfile/parser"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Tests for the permission mode build logic in the Claude Code AgentFile.
// Verifies that each permission_mode CONFIG value produces the correct
// --permission-mode CLI flag, including ACP mode degradation.

func TestEval_PermissionMode_BypassEmitsCorrectFlag(t *testing.T) {
	// bypassPermissions must emit --permission-mode bypassPermissions (NOT --dangerously-skip-permissions)
	src := replaceConfigDefault(fullClaudeCodeAgentFile, "permission_mode", `"bypassPermissions"`)
	prog, errs := parser.Parse(src)
	require.Empty(t, errs)

	ctx := newMCPContext()
	require.NoError(t, Eval(prog, ctx))
	ApplyModeArgs(ctx.Result)

	assert.Contains(t, ctx.Result.LaunchArgs, "--permission-mode")
	assert.Contains(t, ctx.Result.LaunchArgs, "bypassPermissions")
	assert.NotContains(t, ctx.Result.LaunchArgs, "--dangerously-skip-permissions")
}

func TestEval_PermissionMode_PlanACP_DegradesToDefault(t *testing.T) {
	// ACP mode + plan → degrades to --permission-mode default
	src := replaceConfigDefault(fullClaudeCodeAgentFile, "permission_mode", `"plan"`)
	src = replaceModeDecl(src, "acp")
	prog, errs := parser.Parse(src)
	require.Empty(t, errs)

	ctx := newMCPContext()
	require.NoError(t, Eval(prog, ctx))
	ApplyModeArgs(ctx.Result)

	args := ctx.Result.LaunchArgs
	assert.Contains(t, args, "--permission-mode")
	assert.Contains(t, args, "default")
	assert.NotContains(t, args, "plan")
	// ACP mode args should be prepended
	assert.Contains(t, args, "-p")
	assert.Contains(t, args, "--verbose")
}

func TestEval_PermissionMode_PlanPTY_StaysPlan(t *testing.T) {
	src := replaceConfigDefault(fullClaudeCodeAgentFile, "permission_mode", `"plan"`)
	prog, errs := parser.Parse(src)
	require.Empty(t, errs)

	ctx := newMCPContext()
	require.NoError(t, Eval(prog, ctx))
	ApplyModeArgs(ctx.Result)

	assert.Contains(t, ctx.Result.LaunchArgs, "--permission-mode")
	assert.Contains(t, ctx.Result.LaunchArgs, "plan")
}

func TestEval_PermissionMode_AcceptEdits(t *testing.T) {
	src := replaceConfigDefault(fullClaudeCodeAgentFile, "permission_mode", `"acceptEdits"`)
	prog, errs := parser.Parse(src)
	require.Empty(t, errs)

	ctx := newMCPContext()
	require.NoError(t, Eval(prog, ctx))

	assert.Contains(t, ctx.Result.LaunchArgs, "--permission-mode")
	assert.Contains(t, ctx.Result.LaunchArgs, "acceptEdits")
}

func TestEval_PermissionMode_DontAsk(t *testing.T) {
	src := replaceConfigDefault(fullClaudeCodeAgentFile, "permission_mode", `"dontAsk"`)
	prog, errs := parser.Parse(src)
	require.Empty(t, errs)

	ctx := newMCPContext()
	require.NoError(t, Eval(prog, ctx))

	assert.Contains(t, ctx.Result.LaunchArgs, "--permission-mode")
	assert.Contains(t, ctx.Result.LaunchArgs, "dontAsk")
}

func TestEval_PermissionMode_DefaultEmitsNoFlag(t *testing.T) {
	src := replaceConfigDefault(fullClaudeCodeAgentFile, "permission_mode", `"default"`)
	prog, errs := parser.Parse(src)
	require.Empty(t, errs)

	ctx := newMCPContext()
	require.NoError(t, Eval(prog, ctx))

	assert.NotContains(t, ctx.Result.LaunchArgs, "--permission-mode")
}
