package suites

import (
	"context"
	"fmt"
	"sync"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/client"
	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// Concurrency invariants. Idempotency keys must serialise duplicate writes
// across goroutines (no "first wins, second errors" race window), and stale
// updates must lose deterministically when two writers race.

func TestConcurrent_IdempotencyKeyDedupesAcrossGoroutines(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	wsID := getDefaultWorkspaceID(ctx, t, pod.MCP)
	ts := time.Now().UnixNano()
	key := fmt.Sprintf("e2e-concurrent-idem-%d", ts)
	uniqueTitle := fmt.Sprintf("concurrent-target-%d", ts)

	// Fire N concurrent block.create calls with the same idempotency_key.
	// Backend must respond with the same op_id chain to all of them; only
	// one row should land in the database.
	const N = 8
	results := make([]applyOpsResult, N)
	errs := make([]error, N)
	var wg sync.WaitGroup
	for i := 0; i < N; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			errs[i] = pod.MCP.CallTool(ctx, "block.create", map[string]any{
				"workspace_id":    wsID,
				"idempotency_key": key,
				"payload": map[string]any{
					"type": "task",
					"data": map[string]any{"title": uniqueTitle, "status": "open"},
				},
			}, &results[i])
		}(i)
	}
	wg.Wait()

	for i, e := range errs {
		if e != nil {
			t.Fatalf("call %d errored: %v", i, e)
		}
	}

	// All op_id chains must match the winner. We don't predict which goroutine
	// wins — the contract is "same op_id observed by every caller".
	winner := results[0].OpIDs
	if len(winner) == 0 {
		t.Fatalf("first result had no op_ids: %+v", results[0])
	}
	replayCount := 0
	for i := 0; i < N; i++ {
		if len(results[i].OpIDs) != len(winner) || results[i].OpIDs[0] != winner[0] {
			t.Errorf("call %d op_ids drifted: winner=%v this=%v", i, winner, results[i].OpIDs)
		}
		if results[i].WasReplay {
			replayCount++
		}
	}
	// At minimum, N-1 calls must be tagged replay (the actual winner sees
	// was_replay=false, every other call sees true). Race timing can cause
	// the first batch of arrivers to all see `was_replay=true` if they
	// queue behind a leader, so we don't pin the exact split.
	if replayCount < N-1 {
		t.Errorf("expected at least %d replay markers across %d concurrent calls, got %d",
			N-1, N, replayCount)
	}

	// Fact assertion: only ONE block of this title in the workspace.
	db, err := client.OpenDB(env.PostgresDSN)
	if err != nil {
		t.Fatalf("open db: %v", err)
	}
	t.Cleanup(func() { _ = db.Close() })

	// Use a direct SQL count to avoid trusting the deduped count from the
	// idempotency layer itself.
	var count int
	if err := db.QueryRow(ctx,
		`SELECT count(*) FROM blocks
		   WHERE workspace_id = $1
		     AND data->>'title' = $2
		     AND deleted_at IS NULL`,
		wsID, uniqueTitle,
	).Scan(&count); err != nil {
		t.Fatalf("db count: %v", err)
	}
	if count != 1 {
		t.Errorf("idempotency violated: %d rows of %q in workspace, expected 1", count, uniqueTitle)
	}
}

func TestConcurrent_OptimisticLockOneWriterWins(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	wsID := getDefaultWorkspaceID(ctx, t, pod.MCP)

	// Create the target row.
	var create applyOpsResult
	if err := pod.MCP.CallTool(ctx, "block.create", map[string]any{
		"workspace_id": wsID,
		"payload": map[string]any{
			"type": "task",
			"data": map[string]any{"title": "lock-target", "status": "open"},
		},
	}, &create); err != nil {
		t.Fatalf("create target: %v", err)
	}
	id := mostRecentBlockID(ctx, t, pod.MCP, wsID)

	// Read its current updated_at via DB so both writers can submit the same
	// expected_updated_at — the second commit must lose.
	db, err := client.OpenDB(env.PostgresDSN)
	if err != nil {
		t.Fatalf("open db: %v", err)
	}
	t.Cleanup(func() { _ = db.Close() })

	var ts time.Time
	if err := db.QueryRow(ctx,
		`SELECT updated_at FROM blocks WHERE id = $1`, id,
	).Scan(&ts); err != nil {
		t.Fatalf("read updated_at: %v", err)
	}
	expected := ts.UTC().Format(time.RFC3339Nano)

	// Two writers race using the same expected_updated_at.
	const N = 2
	errs := make([]error, N)
	var wg sync.WaitGroup
	for i := 0; i < N; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			errs[i] = pod.MCP.CallTool(ctx, "block.update", map[string]any{
				"workspace_id": wsID,
				"payload": map[string]any{
					"id":                  id,
					"data":                map[string]any{"title": fmt.Sprintf("renamed-%d", i), "status": "open"},
					"expected_updated_at": expected,
				},
			}, nil)
		}(i)
	}
	wg.Wait()

	successes := 0
	staleErrors := 0
	for _, e := range errs {
		if e == nil {
			successes++
		} else {
			staleErrors++
		}
	}
	// Exactly one must succeed, the other must fail with a stale-update
	// error. Both succeeding means the lock is broken.
	if successes != 1 {
		t.Errorf("expected exactly 1 successful update, got %d successes / %d errors: %v",
			successes, staleErrors, errs)
	}
}
