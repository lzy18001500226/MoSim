package suites

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// TestMemoryRetrieve_FindsRecentlyCreated writes three blocks via block.create
// and verifies memory.retrieve surfaces at least one of them. This is the
// only spec that meaningfully exercises the pgvector path: SQLite-backed
// integration tests can't run vector search, so this is the canonical
// regression test for the embedding pipeline.
//
// We cap min_score at 0 so the harness doesn't get flaky on small embedding
// model variations between dev and CI machines. Any positive cosine match
// is enough to prove the pipeline (write embedding row → vector index →
// query → return hits) is end-to-end alive.
func TestMemoryRetrieve_FindsRecentlyCreated(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	wsID := getDefaultWorkspaceID(ctx, t, pod.MCP)

	// Distinct seed token so we know the hit comes from this run, not from
	// any previous pollution in dev-org.
	tag := fmt.Sprintf("e2e-mem-%d", time.Now().UnixMilli())

	for i, body := range []string{
		"the brown fox jumps over the lazy dog " + tag,
		"a quick test of vector retrieval " + tag,
		"unrelated text about hot air balloons " + tag,
	} {
		var res applyOpsResult
		if err := pod.MCP.CallTool(ctx, "block.create", map[string]any{
			"workspace_id": wsID,
			"payload": map[string]any{
				"type": "paragraph",
				"text": body,
			},
		}, &res); err != nil {
			t.Fatalf("seed block %d: %v", i, err)
		}
	}

	// Allow embeddings to land. The blockstore service refreshes them async
	// so a quick search right after create can miss them.
	time.Sleep(2 * time.Second)

	var resp struct {
		Hits []struct {
			BlockID string  `json:"block_id"`
			Score   float64 `json:"score"`
			Type    string  `json:"type"`
		} `json:"hits"`
	}
	if err := pod.MCP.CallTool(ctx, "memory.retrieve", map[string]any{
		"workspace_id": wsID,
		"query":        "fox " + tag,
		"k":            10,
		"min_score":    0,
	}, &resp); err != nil {
		t.Fatalf("memory.retrieve: %v", err)
	}
	if len(resp.Hits) == 0 {
		t.Fatalf("expected at least one hit for query containing %q, got 0", tag)
	}
}
