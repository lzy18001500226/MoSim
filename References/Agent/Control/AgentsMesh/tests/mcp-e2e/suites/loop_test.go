package suites

import (
	"context"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// list_loops returns either a markdown table or a "No loops found" sentinel
// — both are valid happy-path outputs in dev (seed has no loops). We only
// assert the call succeeds.
func TestLoop_ListDecodes(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if _, err := pod.MCP.CallToolText(ctx, "list_loops", map[string]any{
		"limit": 10,
	}); err != nil {
		t.Fatalf("list_loops: %v", err)
	}
}

// trigger_loop with a bogus slug must return an MCP error (isError=true).
// CallToolText surfaces that as a non-nil error containing the message.
func TestLoop_TriggerUnknownErrors(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	_, err := pod.MCP.CallToolText(ctx, "trigger_loop", map[string]any{
		"loop_slug": "definitely-not-a-real-loop-e2e",
	})
	if err == nil {
		t.Fatalf("expected error for unknown loop_slug, got nil")
	}
	// Optional sanity: error message should mention the slug or "not found".
	msg := err.Error()
	if !strings.Contains(msg, "not") && !strings.Contains(msg, "loop") {
		t.Errorf("unexpected error shape: %v", err)
	}
}
