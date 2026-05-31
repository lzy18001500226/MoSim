package suites

import (
	"context"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/client"
	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// Block CRUD error paths — pinning the contracts that catch the most expensive
// regressions. Each call expects a non-nil error and the message to mention
// the relevant invariant, so a backend change that silently accepts an
// invalid input fails here loud.

func TestBlockCreate_UnknownTypeReturns400(t *testing.T) {
	ctx, mcp, wsID := setupBlockSpec(t)
	err := mcp.CallTool(ctx, "block.create", map[string]any{
		"workspace_id": wsID,
		"payload": map[string]any{
			"type": "totally-not-a-real-type",
			"data": map[string]any{},
		},
	}, nil)
	requireMCPError(t, err, "unknown")
}

func TestBlockCreate_MissingRequiredKeyReturns400(t *testing.T) {
	ctx, mcp, wsID := setupBlockSpec(t)
	// `task` requires `data.title` (entity_block.go bootstrap spec). Submitting
	// without it must surface ErrMissingRequiredKey, not a 500.
	err := mcp.CallTool(ctx, "block.create", map[string]any{
		"workspace_id": wsID,
		"payload": map[string]any{
			"type": "task",
			"data": map[string]any{},
		},
	}, nil)
	requireMCPError(t, err, "title")
}

func TestBlockUpdate_StaleExpectedUpdatedAtReturns409(t *testing.T) {
	ctx, mcp, wsID := setupBlockSpec(t)

	// Create a task we can race against ourselves.
	var res applyOpsResult
	if err := mcp.CallTool(ctx, "block.create", map[string]any{
		"workspace_id": wsID,
		"payload": map[string]any{
			"type": "task",
			"data": map[string]any{"title": "stale-target", "status": "open"},
		},
	}, &res); err != nil {
		t.Fatalf("create target: %v", err)
	}
	id := mostRecentBlockID(ctx, t, mcp, wsID)

	// Submit an update with a deliberately old expected_updated_at — backend
	// compares this against the row's updated_at column and must reject when
	// the caller's view is stale.
	stale := time.Now().Add(-1 * time.Hour).UTC().Format(time.RFC3339Nano)
	err := mcp.CallTool(ctx, "block.update", map[string]any{
		"workspace_id": wsID,
		"payload": map[string]any{
			"id":                  id,
			"data":                map[string]any{"title": "renamed", "status": "open"},
			"expected_updated_at": stale,
		},
	}, nil)
	requireMCPError(t, err, "stale")
}

func TestBlockAddRef_CrossWorkspaceForbidden(t *testing.T) {
	// Default workspace id from one MCP call, plus an obviously-foreign uuid
	// for the `to` block. Backend must reject before even loading the target.
	ctx, mcp, wsID := setupBlockSpec(t)

	// Create a real `from` block so the only invalid thing is `to`'s workspace.
	var res applyOpsResult
	if err := mcp.CallTool(ctx, "block.create", map[string]any{
		"workspace_id": wsID,
		"payload": map[string]any{
			"type": "task",
			"data": map[string]any{"title": "ref-source", "status": "open"},
		},
	}, &res); err != nil {
		t.Fatalf("create source: %v", err)
	}
	from := mostRecentBlockID(ctx, t, mcp, wsID)

	// A uuid that doesn't exist anywhere — we only need it to pass uuid parsing.
	const ghostBlock = "00000000-0000-0000-0000-000000000001"

	err := mcp.CallTool(ctx, "block.add_ref", map[string]any{
		"workspace_id": wsID,
		"payload": map[string]any{
			"from":      from,
			"to":        ghostBlock,
			"rel":       "nest",
			"order_key": "a0",
		},
	}, nil)
	// Either ErrCrossWorkspaceRef or ErrBlockNotFound is acceptable — both
	// are "not allowed" outcomes. Failing silently is not.
	if err == nil {
		t.Fatalf("expected error for ref to non-existent / cross-workspace block, got nil")
	}
}

func TestBlockCreate_IdempotencyReplay(t *testing.T) {
	ctx, mcp, wsID := setupBlockSpec(t)
	key := "e2e-idem-" + time.Now().Format("150405.000000")

	// First call must succeed and produce an op_id.
	var first applyOpsResult
	if err := mcp.CallTool(ctx, "block.create", map[string]any{
		"workspace_id":    wsID,
		"idempotency_key": key,
		"payload": map[string]any{
			"type": "task",
			"data": map[string]any{"title": "idem-test", "status": "open"},
		},
	}, &first); err != nil {
		t.Fatalf("first call: %v", err)
	}
	if len(first.OpIDs) == 0 {
		t.Fatalf("first call returned no op_ids: %+v", first)
	}

	// Second call with the same key must return was_replay=true and the
	// SAME op_id, not a fresh insert.
	var replay applyOpsResult
	if err := mcp.CallTool(ctx, "block.create", map[string]any{
		"workspace_id":    wsID,
		"idempotency_key": key,
		"payload": map[string]any{
			"type": "task",
			"data": map[string]any{"title": "idem-test", "status": "open"},
		},
	}, &replay); err != nil {
		t.Fatalf("replay call: %v", err)
	}
	if !replay.WasReplay {
		t.Errorf("expected was_replay=true on retry, got %+v", replay)
	}
	if len(replay.OpIDs) != len(first.OpIDs) || replay.OpIDs[0] != first.OpIDs[0] {
		t.Errorf("replay op_ids drifted: first=%v replay=%v", first.OpIDs, replay.OpIDs)
	}
}

// setupBlockSpec is the shared per-test bootstrap for block error specs:
// fresh pod, default workspace id, and an MCP client.
func setupBlockSpec(t *testing.T) (context.Context, *client.MCPClient, string) {
	t.Helper()
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	t.Cleanup(cancel)

	wsID := getDefaultWorkspaceID(ctx, t, pod.MCP)
	return ctx, pod.MCP, wsID
}

func requireMCPError(t *testing.T, err error, expectedSubstring string) {
	t.Helper()
	if err == nil {
		t.Fatalf("expected error matching %q, got nil", expectedSubstring)
	}
	if !strings.Contains(strings.ToLower(err.Error()), strings.ToLower(expectedSubstring)) {
		t.Errorf("error %q does not contain expected %q", err.Error(), expectedSubstring)
	}
}
