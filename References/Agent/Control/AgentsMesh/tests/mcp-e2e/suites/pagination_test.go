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

// search_tickets supports `page` (1-based) + `limit`. With limit=2 across
// 5 seeded tickets, page 1 and page 3 must show disjoint slugs (page 1 is
// rows 1-2, page 3 is row 5). Combined with the existing limit-only spec,
// this nails the offset semantic without depending on global ticket
// ordering across other tests.
func TestSearchTickets_PaginationPageSkipsRows(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	tag := fmt.Sprintf("e2e-page-skip-%d", time.Now().UnixMilli())
	const seedN = 5
	var slugs []string
	for i := 0; i < seedN; i++ {
		out, err := pod.MCP.CallToolText(ctx, "create_ticket", map[string]any{
			"title": fmt.Sprintf("%s #%d", tag, i),
		})
		if err != nil {
			t.Fatalf("seed %d: %v", i, err)
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

	page1, err := pod.MCP.CallToolText(ctx, "search_tickets", map[string]any{
		"query": tag,
		"limit": 2,
		"page":  1,
	})
	if err != nil {
		t.Fatalf("search_tickets page=1: %v", err)
	}
	page3, err := pod.MCP.CallToolText(ctx, "search_tickets", map[string]any{
		"query": tag,
		"limit": 2,
		"page":  3,
	})
	if err != nil {
		t.Fatalf("search_tickets page=3: %v", err)
	}

	page1Slugs := slugsContained(page1, slugs)
	page3Slugs := slugsContained(page3, slugs)

	if len(page1Slugs) == 0 {
		t.Errorf("page=1 returned no seeded slugs:\n%s", page1)
	}
	if len(page3Slugs) == 0 {
		t.Errorf("page=3 returned no seeded slugs (offset broken?):\n%s", page3)
	}
	overlap := intersect(page1Slugs, page3Slugs)
	if len(overlap) > 0 {
		t.Errorf("page=1 and page=3 results overlapped on %v — pagination not advancing", overlap)
	}
}

// TestListLoops_OffsetSkipsRows mirrors the ticket pagination spec for the
// loop list: offset=0 vs offset=N must surface different rows when more
// loops exist than the page can hold.
func TestListLoops_OffsetSkipsRows(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	tag := fmt.Sprintf("e2e-loop-off-%d", time.Now().UnixMilli())
	const seedN = 4
	for i := 0; i < seedN; i++ {
		runnerID := runner.ID
		if _, err := rest.CreateLoop(ctx, env.DevOrgSlug, client.CreateLoopRequest{
			Name:           fmt.Sprintf("%s-%d", tag, i),
			AgentSlug:      "e2e-echo",
			PromptTemplate: "do",
			RunnerID:       &runnerID,
		}); err != nil {
			t.Fatalf("seed loop %d: %v", i, err)
		}
	}

	page1, err := pod.MCP.CallToolText(ctx, "list_loops", map[string]any{
		"query":  tag,
		"limit":  2,
		"offset": 0,
	})
	if err != nil {
		t.Fatalf("list_loops offset=0: %v", err)
	}
	page2, err := pod.MCP.CallToolText(ctx, "list_loops", map[string]any{
		"query":  tag,
		"limit":  2,
		"offset": 2,
	})
	if err != nil {
		t.Fatalf("list_loops offset=2: %v", err)
	}
	// At minimum offset must change something — full equality means broken.
	if page1 == page2 {
		t.Errorf("list_loops offset=0 and offset=2 returned identical output:\n%s", page1)
	}
}

func slugsContained(text string, candidates []string) []string {
	var out []string
	for _, s := range candidates {
		if strings.Contains(text, s) {
			out = append(out, s)
		}
	}
	return out
}

func intersect(a, b []string) []string {
	bset := map[string]bool{}
	for _, x := range b {
		bset[x] = true
	}
	var out []string
	for _, x := range a {
		if bset[x] {
			out = append(out, x)
		}
	}
	return out
}
