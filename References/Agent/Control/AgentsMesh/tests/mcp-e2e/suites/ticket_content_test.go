package suites

import (
	"context"
	"fmt"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// Ticket content (`content` field) is server-side parsed as BlockNote AST and
// persisted in Block Store as a `document` block. The ticket row stores only
// the block id; subsequent get_ticket round-trips through the block to render
// plain text. These specs pin that contract.

// minimalBlockNote is the shortest BlockNote AST that round-trips: one
// paragraph block with a single text inline. Backend's parseBlocknote +
// blocknote.ToPlainText must accept this and emit "hello world" as plain.
func minimalBlockNote(text string) string {
	return fmt.Sprintf(
		`[{"id":"b1","type":"paragraph","props":{},"content":[{"type":"text","text":%q,"styles":{}}],"children":[]}]`,
		text,
	)
}

func TestTicket_CreateWithBlockNoteContent(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	title := fmt.Sprintf("e2e-blocknote-%d", time.Now().UnixMilli())
	out, err := pod.MCP.CallToolText(ctx, "create_ticket", map[string]any{
		"title":   title,
		"content": minimalBlockNote("hello world"),
	})
	if err != nil {
		t.Fatalf("create_ticket with BlockNote AST: %v", err)
	}
	m := ticketSlugRE.FindStringSubmatch(out)
	if len(m) != 2 {
		t.Fatalf("could not parse ticket slug from output:\n%s", out)
	}
	slug := m[1]
	t.Cleanup(func() {
		ctx2, cancel2 := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel2()
		_, _ = pod.MCP.CallToolText(ctx2, "delete_ticket", map[string]any{"ticket_slug": slug})
	})

	// get_ticket must surface the rendered plain text (the AST -> plaintext
	// conversion is what makes the field round-trip useful for agents).
	getOut, err := pod.MCP.CallToolText(ctx, "get_ticket", map[string]any{
		"ticket_slug": slug,
	})
	if err != nil {
		t.Fatalf("get_ticket: %v", err)
	}
	if !strings.Contains(getOut, "hello world") {
		t.Errorf("expected plain-text rendering of 'hello world' in get_ticket, got:\n%s", getOut)
	}
}

func TestTicket_UpdateContentReplacesBlock(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	title := fmt.Sprintf("e2e-update-content-%d", time.Now().UnixMilli())
	out, err := pod.MCP.CallToolText(ctx, "create_ticket", map[string]any{
		"title":   title,
		"content": minimalBlockNote("first version"),
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

	// Replace the content; the underlying document block is updated in place.
	if _, err := pod.MCP.CallToolText(ctx, "update_ticket", map[string]any{
		"ticket_slug": slug,
		"content":     minimalBlockNote("second version"),
	}); err != nil {
		t.Fatalf("update_ticket: %v", err)
	}
	getOut, err := pod.MCP.CallToolText(ctx, "get_ticket", map[string]any{
		"ticket_slug": slug,
	})
	if err != nil {
		t.Fatalf("get_ticket: %v", err)
	}
	if !strings.Contains(getOut, "second version") {
		t.Errorf("expected updated content 'second version' in get_ticket, got:\n%s", getOut)
	}
	if strings.Contains(getOut, "first version") {
		t.Errorf("old content 'first version' must be gone, got:\n%s", getOut)
	}
}

func TestTicket_ParentChildSubtask(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	parentTitle := fmt.Sprintf("e2e-parent-%d", time.Now().UnixMilli())
	out, err := pod.MCP.CallToolText(ctx, "create_ticket", map[string]any{
		"title": parentTitle,
	})
	if err != nil {
		t.Fatalf("create parent: %v", err)
	}
	parentSlug := ticketSlugRE.FindStringSubmatch(out)[1]
	t.Cleanup(func() {
		ctx2, cancel2 := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel2()
		_, _ = pod.MCP.CallToolText(ctx2, "delete_ticket", map[string]any{"ticket_slug": parentSlug})
	})

	childTitle := fmt.Sprintf("e2e-child-%d", time.Now().UnixMilli())
	childOut, err := pod.MCP.CallToolText(ctx, "create_ticket", map[string]any{
		"title":              childTitle,
		"parent_ticket_slug": parentSlug,
	})
	if err != nil {
		t.Fatalf("create child: %v", err)
	}
	childSlug := ticketSlugRE.FindStringSubmatch(childOut)[1]
	t.Cleanup(func() {
		ctx2, cancel2 := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel2()
		_, _ = pod.MCP.CallToolText(ctx2, "delete_ticket", map[string]any{"ticket_slug": childSlug})
	})

	// search_tickets with parent_ticket_slug should surface the child.
	search, err := pod.MCP.CallToolText(ctx, "search_tickets", map[string]any{
		"parent_ticket_slug": parentSlug,
		"limit":              10,
	})
	if err != nil {
		t.Fatalf("search_tickets parent_ticket_slug: %v", err)
	}
	if !strings.Contains(search, childSlug) {
		t.Errorf("expected child %q under parent %q in search:\n%s", childSlug, parentSlug, search)
	}
}
