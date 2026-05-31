package suites

import (
	"context"
	"fmt"
	"regexp"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// Tickets are addressed by slug (e.g. TICKET-3). create_ticket emits
// "Ticket: SLUG - TITLE\n..." in plain text, so we regex the slug out and
// chain it through search → get → update → comment → delete.

var ticketSlugRE = regexp.MustCompile(`Ticket:\s*([A-Z0-9_-]+)`)

func TestTicket_FullLifecycle(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	title := fmt.Sprintf("e2e-ticket-%d", time.Now().UnixMilli())

	// `content` is treated as BlockNote AST JSON server-side
	// (service/ticket/content_block.go:writeContentBlock). Plain strings fail
	// `parseBlocknote` and surface as opaque "failed to create ticket". For
	// the lifecycle spec we leave content empty — coverage of rich content
	// belongs in a dedicated blocknote spec, not this CRUD chain.
	out, err := pod.MCP.CallToolText(ctx, "create_ticket", map[string]any{
		"title": title,
	})
	if err != nil {
		t.Fatalf("create_ticket: %v", err)
	}
	m := ticketSlugRE.FindStringSubmatch(out)
	if len(m) != 2 {
		t.Fatalf("could not parse ticket slug from output:\n%s", out)
	}
	slug := m[1]

	// Defensive cleanup: even on intermediate failure, leave no row behind.
	t.Cleanup(func() {
		ctx2, cancel2 := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel2()
		_, _ = pod.MCP.CallToolText(ctx2, "delete_ticket", map[string]any{"ticket_slug": slug})
	})

	searchOut, err := pod.MCP.CallToolText(ctx, "search_tickets", map[string]any{
		"query": title,
		"limit": 5,
	})
	if err != nil {
		t.Fatalf("search_tickets: %v", err)
	}
	if !strings.Contains(searchOut, slug) {
		t.Errorf("ticket %q not found by search_tickets query=%q:\n%s", slug, title, searchOut)
	}

	getOut, err := pod.MCP.CallToolText(ctx, "get_ticket", map[string]any{
		"ticket_slug": slug,
	})
	if err != nil {
		t.Fatalf("get_ticket: %v", err)
	}
	if !strings.Contains(getOut, title) {
		t.Errorf("get_ticket output missing title %q:\n%s", title, getOut)
	}

	if _, err := pod.MCP.CallToolText(ctx, "update_ticket", map[string]any{
		"ticket_slug": slug,
		"status":      "in_progress",
	}); err != nil {
		t.Fatalf("update_ticket: %v", err)
	}

	if _, err := pod.MCP.CallToolText(ctx, "post_comment", map[string]any{
		"ticket_slug": slug,
		"content":     "first comment from e2e",
	}); err != nil {
		t.Fatalf("post_comment: %v", err)
	}

	if _, err := pod.MCP.CallToolText(ctx, "delete_ticket", map[string]any{
		"ticket_slug": slug,
	}); err != nil {
		t.Fatalf("delete_ticket: %v", err)
	}
}
