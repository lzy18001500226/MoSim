package suites

import (
	"context"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// TestBlockListTypes returns the bootstrap type catalog. Every workspace gets
// page/paragraph/task/list/view/comment etc. for free, so the response must
// be non-empty even on a fresh workspace, and must include the well-known
// "task" type (which the CRUD spec depends on).
func TestBlockListTypes_HasBootstrapTypes(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	wsID := getDefaultWorkspaceID(ctx, t, pod.MCP)

	var resp struct {
		Types []struct {
			Type        string `json:"type"`
			Label       string `json:"label,omitempty"`
			Description string `json:"description,omitempty"`
		} `json:"types"`
	}
	if err := pod.MCP.CallTool(ctx, "block.list_types", map[string]any{
		"workspace_id": wsID,
	}, &resp); err != nil {
		t.Fatalf("block.list_types: %v", err)
	}
	if len(resp.Types) == 0 {
		t.Fatalf("expected non-empty type catalog, got %+v", resp)
	}
	wantTypes := []string{"task", "page", "paragraph"}
	have := map[string]bool{}
	for _, ty := range resp.Types {
		have[ty.Type] = true
	}
	for _, want := range wantTypes {
		if !have[want] {
			t.Errorf("expected bootstrap type %q in catalog (got: %v)", want, keysOf(have))
		}
	}
}

func keysOf(m map[string]bool) []string {
	out := make([]string, 0, len(m))
	for k := range m {
		out = append(out, k)
	}
	return out
}
