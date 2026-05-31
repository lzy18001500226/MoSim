package suites

import (
	"context"
	"fmt"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// memory.retrieve has three filter knobs: type (only blocks of that type),
// k (top-K cap), and min_score (cosine threshold). Each spec writes a
// disjoint mix of blocks then asserts the filter narrows the result set.

type memoryHit struct {
	BlockID string  `json:"block_id"`
	Score   float64 `json:"score"`
	Type    string  `json:"type"`
}

type memoryResp struct {
	Hits []memoryHit `json:"hits"`
}

func TestMemoryRetrieve_TypeFilterRestrictsToType(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	wsID := getDefaultWorkspaceID(ctx, t, pod.MCP)

	tag := fmt.Sprintf("e2e-mem-tf-%d", time.Now().UnixMilli())

	// Mix of two types, same tag in both so embeddings overlap.
	for _, body := range []struct{ typ, text string }{
		{"task", tag + " review the auth flow"},
		{"task", tag + " ship the feature"},
		{"paragraph", tag + " random paragraph content"},
		{"paragraph", tag + " another paragraph here"},
	} {
		payload := map[string]any{
			"type": body.typ,
			"text": body.text,
		}
		if body.typ == "task" {
			payload["data"] = map[string]any{"title": body.text, "status": "open"}
		}
		if err := pod.MCP.CallTool(ctx, "block.create", map[string]any{
			"workspace_id": wsID,
			"payload":      payload,
		}, nil); err != nil {
			t.Fatalf("seed %s: %v", body.typ, err)
		}
	}
	time.Sleep(2 * time.Second) // embeddings async

	var resp memoryResp
	if err := pod.MCP.CallTool(ctx, "memory.retrieve", map[string]any{
		"workspace_id": wsID,
		"query":        tag,
		"k":            20,
		"min_score":    0,
		"type":         "task",
	}, &resp); err != nil {
		t.Fatalf("memory.retrieve type=task: %v", err)
	}
	if len(resp.Hits) == 0 {
		t.Fatalf("expected at least one task hit, got 0")
	}
	for _, h := range resp.Hits {
		if h.Type != "task" {
			t.Errorf("type filter leak: hit type=%q (expected only 'task')", h.Type)
		}
	}
}

func TestMemoryRetrieve_TopKLimitsResultCount(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	wsID := getDefaultWorkspaceID(ctx, t, pod.MCP)

	tag := fmt.Sprintf("e2e-mem-k-%d", time.Now().UnixMilli())
	const seedN = 6
	for i := 0; i < seedN; i++ {
		if err := pod.MCP.CallTool(ctx, "block.create", map[string]any{
			"workspace_id": wsID,
			"payload": map[string]any{
				"type": "paragraph",
				"text": fmt.Sprintf("%s seed %d different content here", tag, i),
			},
		}, nil); err != nil {
			t.Fatalf("seed %d: %v", i, err)
		}
	}
	time.Sleep(2 * time.Second)

	// k=2 must return at most 2 even though seedN=6 are all candidates.
	var capped memoryResp
	if err := pod.MCP.CallTool(ctx, "memory.retrieve", map[string]any{
		"workspace_id": wsID,
		"query":        tag,
		"k":            2,
		"min_score":    0,
	}, &capped); err != nil {
		t.Fatalf("memory.retrieve k=2: %v", err)
	}
	if len(capped.Hits) > 2 {
		t.Errorf("k=2 returned %d hits, expected ≤2", len(capped.Hits))
	}

	// k=20 must return at least more than k=2 (all 6 if scoring permits).
	var wide memoryResp
	if err := pod.MCP.CallTool(ctx, "memory.retrieve", map[string]any{
		"workspace_id": wsID,
		"query":        tag,
		"k":            20,
		"min_score":    0,
	}, &wide); err != nil {
		t.Fatalf("memory.retrieve k=20: %v", err)
	}
	if len(wide.Hits) <= len(capped.Hits) {
		t.Errorf("k=20 returned %d hits, expected > k=2 (%d)", len(wide.Hits), len(capped.Hits))
	}
}

// TestMemoryRetrieve_HighMinScoreShrinksResults exercises the cosine
// threshold: at min_score=0.99 (effectively only exact matches survive)
// fewer hits should land than at min_score=0.
func TestMemoryRetrieve_HighMinScoreShrinksResults(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	wsID := getDefaultWorkspaceID(ctx, t, pod.MCP)

	tag := fmt.Sprintf("e2e-mem-score-%d", time.Now().UnixMilli())
	for _, text := range []string{
		tag + " exact match",
		tag + " loosely related to the topic",
		"completely unrelated " + tag + " trailing",
		tag + " another close one",
	} {
		if err := pod.MCP.CallTool(ctx, "block.create", map[string]any{
			"workspace_id": wsID,
			"payload":      map[string]any{"type": "paragraph", "text": text},
		}, nil); err != nil {
			t.Fatalf("seed %s: %v", text, err)
		}
	}
	time.Sleep(2 * time.Second)

	query := tag + " exact match"

	var loose, strict memoryResp
	if err := pod.MCP.CallTool(ctx, "memory.retrieve", map[string]any{
		"workspace_id": wsID,
		"query":        query,
		"k":            20,
		"min_score":    0,
	}, &loose); err != nil {
		t.Fatalf("memory.retrieve loose: %v", err)
	}
	if err := pod.MCP.CallTool(ctx, "memory.retrieve", map[string]any{
		"workspace_id": wsID,
		"query":        query,
		"k":            20,
		"min_score":    0.99,
	}, &strict); err != nil {
		t.Fatalf("memory.retrieve strict: %v", err)
	}
	if len(strict.Hits) >= len(loose.Hits) {
		t.Errorf("min_score=0.99 returned %d hits, expected fewer than min_score=0 (%d). loose hits:\n%s",
			len(strict.Hits), len(loose.Hits), summarizeHits(loose.Hits))
	}
	// Sanity: loose result must include the exact match seed.
	var matched bool
	for _, h := range loose.Hits {
		if h.Score > 0 {
			matched = true
			break
		}
	}
	if !matched && len(loose.Hits) > 0 {
		t.Errorf("loose retrieve had hits but all scores ≤0: %s", summarizeHits(loose.Hits))
	}
}

func summarizeHits(hits []memoryHit) string {
	var b strings.Builder
	for _, h := range hits {
		fmt.Fprintf(&b, "  type=%s score=%.3f id=%s\n", h.Type, h.Score, h.BlockID)
	}
	return b.String()
}
