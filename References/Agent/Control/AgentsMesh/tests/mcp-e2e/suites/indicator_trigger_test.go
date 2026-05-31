package suites

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// TestIndicatorDefine_AppearsInListTypes registers a custom indicator type
// and confirms block.list_types returns it on the next call. This is the
// canonical proof that schema registration is workspace-scoped and visible
// to the same agent.
func TestIndicatorDefine_AppearsInListTypes(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()

	wsID := getDefaultWorkspaceID(ctx, t, pod.MCP)
	typeKey := fmt.Sprintf("e2e_indicator_%d", time.Now().UnixMilli())

	if err := pod.MCP.CallTool(ctx, "indicator.define", map[string]any{
		"workspace_id": wsID,
		"arguments": map[string]any{
			"type_key":    typeKey,
			"label":       "E2E Indicator",
			"description": "Defined by mcp-e2e for assertion",
			"columns": []map[string]any{
				{"key": "value", "type": "number", "required": true},
			},
		},
	}, nil); err != nil {
		t.Fatalf("indicator.define: %v", err)
	}

	var resp struct {
		Types []struct {
			Type string `json:"type"`
		} `json:"types"`
	}
	if err := pod.MCP.CallTool(ctx, "block.list_types", map[string]any{
		"workspace_id": wsID,
	}, &resp); err != nil {
		t.Fatalf("block.list_types: %v", err)
	}
	var seen bool
	for _, ty := range resp.Types {
		if ty.Type == typeKey {
			seen = true
			break
		}
	}
	if !seen {
		t.Errorf("indicator %q not in list_types after define", typeKey)
	}
}

// TestTriggerDefine_RegistersOk only asserts a trigger.define call succeeds
// without error. End-to-end firing semantics need a webhook target, which is
// out of scope for the local dev stack; that path is covered by backend
// integration tests in service/blockstore/trigger_engine_*.
func TestTriggerDefine_RegistersOk(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	wsID := getDefaultWorkspaceID(ctx, t, pod.MCP)
	name := fmt.Sprintf("e2e-trigger-%d", time.Now().UnixMilli())

	if err := pod.MCP.CallTool(ctx, "trigger.define", map[string]any{
		"workspace_id": wsID,
		"arguments": map[string]any{
			"name":        name,
			"target_type": "task",
			"on":          "create",
			"action": map[string]any{
				"kind": "noop",
			},
		},
	}, nil); err != nil {
		t.Fatalf("trigger.define: %v", err)
	}
}
