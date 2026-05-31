package suites

import (
	"context"
	"fmt"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/client"
	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// Loops are agent-driven repeatable tasks. The dev seed doesn't include any,
// so these specs seed via REST then exercise the agent surface (list_loops,
// trigger_loop) and verify a real loop_run row materialises in the DB.

func TestLoop_ListShowsSeededLoop(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	loopName := fmt.Sprintf("e2e-loop-list-%d", time.Now().UnixMilli())
	loop, err := rest.CreateLoop(ctx, env.DevOrgSlug, client.CreateLoopRequest{
		Name:           loopName,
		AgentSlug:      "e2e-echo",
		PromptTemplate: "do something",
		RunnerID:       &runner.ID,
	})
	if err != nil {
		t.Fatalf("create loop via REST: %v", err)
	}

	out, err := pod.MCP.CallToolText(ctx, "list_loops", map[string]any{
		"query": loopName,
		"limit": 10,
	})
	if err != nil {
		t.Fatalf("list_loops: %v", err)
	}
	if !strings.Contains(out, loopName) && !strings.Contains(out, loop.Slug) {
		t.Errorf("seeded loop %q (slug=%s) not surfaced by list_loops:\n%s",
			loopName, loop.Slug, out)
	}
}

func TestLoop_TriggerCreatesRun(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	loopName := fmt.Sprintf("e2e-loop-trigger-%d", time.Now().UnixMilli())
	loop, err := rest.CreateLoop(ctx, env.DevOrgSlug, client.CreateLoopRequest{
		Name:           loopName,
		AgentSlug:      "e2e-echo",
		PromptTemplate: "{{.task}}",
		RunnerID:       &runner.ID,
	})
	if err != nil {
		t.Fatalf("create loop: %v", err)
	}
	if err := rest.EnableLoop(ctx, env.DevOrgSlug, loop.Slug); err != nil {
		t.Fatalf("enable loop %s: %v", loop.Slug, err)
	}

	db, err := client.OpenDB(env.PostgresDSN)
	if err != nil {
		t.Fatalf("open db: %v", err)
	}
	t.Cleanup(func() { _ = db.Close() })

	var beforeRuns int
	if err := db.QueryRow(ctx,
		`SELECT count(*) FROM loop_runs WHERE loop_id = $1`, loop.ID,
	).Scan(&beforeRuns); err != nil {
		t.Fatalf("count loop_runs before: %v", err)
	}

	if _, err := pod.MCP.CallToolText(ctx, "trigger_loop", map[string]any{
		"loop_slug": loop.Slug,
		"variables": map[string]any{"task": "ping"},
	}); err != nil {
		t.Fatalf("trigger_loop %s: %v", loop.Slug, err)
	}

	// Trigger creates a row in loop_runs synchronously, but the actual pod
	// spawn is async. We only need the run row to land.
	deadline := time.Now().Add(5 * time.Second)
	for time.Now().Before(deadline) {
		var after int
		if err := db.QueryRow(ctx,
			`SELECT count(*) FROM loop_runs WHERE loop_id = $1`, loop.ID,
		).Scan(&after); err != nil {
			t.Fatalf("count loop_runs after: %v", err)
		}
		if after > beforeRuns {
			return // success
		}
		time.Sleep(200 * time.Millisecond)
	}
	var final int
	_ = db.QueryRow(ctx, `SELECT count(*) FROM loop_runs WHERE loop_id = $1`, loop.ID).Scan(&final)
	t.Fatalf("trigger_loop did not produce a loop_run row within 5s (before=%d final=%d)", beforeRuns, final)
}
