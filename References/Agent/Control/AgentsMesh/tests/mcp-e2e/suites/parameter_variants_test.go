package suites

import (
	"context"
	"fmt"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// TestPodInteraction_SpecialKeys feeds keyboard control sequences via the
// `keys` parameter. The echo agent's stdin loop only reacts to plain lines,
// but we can still verify the runner accepts and forwards each keys symbol
// without error — i.e. send_pod_input doesn't reject the symbols defined in
// its tool description (enter, ctrl+c, ctrl+d, etc.).
//
// This complements TestPodInteraction_RoundTrip which already tests the
// `text` payload path.
func TestPodInteraction_SpecialKeys(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// "enter" is the safest standalone key — most others either kill the pod
	// (ctrl+c, ctrl+d) or have no observable effect on a bash echo loop.
	// We just need to prove the keys path is wired end-to-end.
	if _, err := pod.MCP.CallToolText(ctx, "send_pod_input", map[string]any{
		"pod_key": pod.Pod.PodKey,
		"keys":    []string{"enter"},
	}); err != nil {
		t.Fatalf("send_pod_input keys=[enter]: %v", err)
	}

	// Combining text + keys: feed "abc" then enter, expect a "got: abc" line
	// to surface in a snapshot afterwards.
	if _, err := pod.MCP.CallToolText(ctx, "send_pod_input", map[string]any{
		"pod_key": pod.Pod.PodKey,
		"text":    "abc",
		"keys":    []string{"enter"},
	}); err != nil {
		t.Fatalf("send_pod_input text+keys: %v", err)
	}

	deadline := time.Now().Add(3 * time.Second)
	for time.Now().Before(deadline) {
		snap, err := pod.MCP.CallToolText(ctx, "get_pod_snapshot", map[string]any{
			"pod_key": pod.Pod.PodKey,
			"lines":   200,
		})
		if err == nil && strings.Contains(snap, "got: abc") {
			return // success
		}
		time.Sleep(150 * time.Millisecond)
	}
	t.Fatalf("expected 'got: abc' in snapshot after text+enter")
}

func TestPodInteraction_NeitherTextNorKeysRejected(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	err := pod.MCP.CallTool(ctx, "send_pod_input", map[string]any{
		"pod_key": pod.Pod.PodKey,
		// no text, no keys — backend must enforce "at least one"
	}, nil)
	if err == nil {
		t.Fatalf("expected error when neither text nor keys provided")
	}
}

// TestPodInteraction_GetSnapshotOptions exercises the lines / raw flags. The
// content shape varies (raw includes ANSI escapes; default strips them) but
// both must succeed and return a non-empty result for a live pod.
func TestPodInteraction_GetSnapshotOptions(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	// Push a line to ensure there's some PTY history to snapshot.
	if _, err := pod.MCP.CallToolText(ctx, "send_pod_input", map[string]any{
		"pod_key": pod.Pod.PodKey,
		"text":    "snapshot-marker\n",
	}); err != nil {
		t.Fatalf("seed input: %v", err)
	}
	time.Sleep(300 * time.Millisecond)

	for _, label := range []string{"raw=false", "raw=true"} {
		raw := strings.HasSuffix(label, "true")
		out, err := pod.MCP.CallToolText(ctx, "get_pod_snapshot", map[string]any{
			"pod_key": pod.Pod.PodKey,
			"lines":   50,
			"raw":     raw,
		})
		if err != nil {
			t.Fatalf("snapshot %s: %v", label, err)
		}
		if out == "" {
			t.Errorf("snapshot %s returned empty output", label)
		}
	}
}

// TestSearchTickets_PaginationLimit caps results: comparing limit=1 vs
// limit=10 row counts. Done with self-created ticket pairs to avoid
// depending on cross-test state.
func TestSearchTickets_PaginationLimit(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Create 3 tickets so limit=1 vs limit=10 give measurably different rows.
	ts := time.Now().UnixMilli()
	tag := fmt.Sprintf("e2e-page-%d", ts)
	var slugs []string
	for i := 0; i < 3; i++ {
		out, err := pod.MCP.CallToolText(ctx, "create_ticket", map[string]any{
			"title": fmt.Sprintf("%s-%d", tag, i),
		})
		if err != nil {
			t.Fatalf("seed ticket %d: %v", i, err)
		}
		slugs = append(slugs, ticketSlugRE.FindStringSubmatch(out)[1])
	}
	t.Cleanup(func() {
		ctx2, cancel2 := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel2()
		for _, s := range slugs {
			_, _ = pod.MCP.CallToolText(ctx2, "delete_ticket", map[string]any{"ticket_slug": s})
		}
	})

	one, err := pod.MCP.CallToolText(ctx, "search_tickets", map[string]any{
		"query": tag,
		"limit": 1,
	})
	if err != nil {
		t.Fatalf("search_tickets limit=1: %v", err)
	}
	all, err := pod.MCP.CallToolText(ctx, "search_tickets", map[string]any{
		"query": tag,
		"limit": 10,
	})
	if err != nil {
		t.Fatalf("search_tickets limit=10: %v", err)
	}

	// Count tag occurrences as a row proxy. Header rows of the markdown table
	// don't contain the tag, so this is unambiguous.
	oneCount := strings.Count(one, tag)
	allCount := strings.Count(all, tag)
	if oneCount >= allCount {
		t.Errorf("expected limit=1 (%d rows) < limit=10 (%d rows)\nlimit=1:\n%s\nlimit=10:\n%s",
			oneCount, allCount, one, all)
	}
	if allCount < 3 {
		t.Errorf("expected to see all 3 seeded tickets at limit=10, got %d:\n%s", allCount, all)
	}
}

// TestSearchTickets_StatusFilter narrows by status; dev seed has both
// tickets in status=backlog, so a filter to "in_progress" must return zero.
func TestSearchTickets_StatusFilter(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Create one ticket at status=backlog (default), then filter for
	// in_progress and assert it's NOT in the result. We don't compare against
	// dev seed because other tests churn ticket state.
	title := fmt.Sprintf("e2e-status-%d", time.Now().UnixMilli())
	out, err := pod.MCP.CallToolText(ctx, "create_ticket", map[string]any{
		"title": title,
	})
	if err != nil {
		t.Fatalf("create_ticket: %v", err)
	}
	slug := ticketSlugRE.FindStringSubmatch(out)[1]
	t.Cleanup(func() {
		ctx2, cancel2 := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel2()
		_, _ = pod.MCP.CallToolText(ctx2, "delete_ticket", map[string]any{"ticket_slug": slug})
	})

	search, err := pod.MCP.CallToolText(ctx, "search_tickets", map[string]any{
		"status": "in_progress",
		"limit":  100,
	})
	if err != nil {
		t.Fatalf("search_tickets status=in_progress: %v", err)
	}
	if strings.Contains(search, slug) {
		t.Errorf("backlog ticket %q surfaced in status=in_progress filter:\n%s", slug, search)
	}
}
