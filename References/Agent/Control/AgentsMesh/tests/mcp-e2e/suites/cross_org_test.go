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

// Cross-org isolation: every MCP call's tenant context (TenantContext.OrganizationID)
// is sourced from the pod's owning org (authenticatePod in
// runner_adapter_mcp_auth.go). A pod in org A must not be able to read
// resources from org B even if the human who created it owns both orgs —
// resource scope is "org of the pod", not "user's reachable orgs".
//
// We construct the foreign org with the same human (dev) who creates the
// pod in dev-org, so any leak would be a tenant-isolation failure rather
// than an authentication failure.

func TestCrossOrg_TicketLookupIsolated(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// 1) Create a foreign org owned by the same human (dev). Slug must be
	//    unique per run so re-runs don't collide.
	foreignSlug := fmt.Sprintf("e2e-foreign-%d", time.Now().UnixMilli())
	foreignOrg, err := rest.CreateOrg(ctx, "E2E Foreign Org", foreignSlug)
	if err != nil {
		t.Fatalf("create foreign org: %v", err)
	}
	t.Cleanup(func() {
		ctx2, cancel2 := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel2()
		_ = rest.DeleteOrg(ctx2, foreignOrg.Slug)
	})

	// 2) Seed a ticket in the foreign org with a unique title that we can
	//    pattern-match — TICKET-N slugs collide across orgs by design (each
	//    org has its own TICKET-1), so we can't use slug presence alone as
	//    the leak signal. Title content is the unambiguous signal.
	uniqueTitle := fmt.Sprintf("foreign-secret-%d", time.Now().UnixNano())
	foreignTicket, err := rest.CreateTicket(ctx, foreignOrg.Slug, client.CreateTicketRequest{
		Title:    uniqueTitle,
		Priority: "medium",
	})
	if err != nil {
		t.Fatalf("create foreign ticket: %v", err)
	}

	// 3) Spawn a pod in dev-org. Its tenant scope is dev-org, NOT
	//    foreign-org, even though the same human created both.
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	// 4) Try to read the foreign ticket via MCP. Either:
	//    (a) dev-org has no ticket with that slug → MCP returns an error
	//        (the expected, fail-closed path), OR
	//    (b) dev-org happens to also have a ticket at that slug because
	//        TICKET-N counters are per-org → MCP returns dev-org's ticket,
	//        whose title MUST NOT be the foreign one.
	out, err := pod.MCP.CallToolText(ctx, "get_ticket", map[string]any{
		"ticket_slug": foreignTicket.Slug,
	})
	if err == nil && strings.Contains(out, uniqueTitle) {
		t.Errorf("CROSS-ORG LEAK: foreign-org ticket title %q surfaced through dev-org pod's get_ticket:\n%s",
			uniqueTitle, out)
	}
}

// TestCrossOrg_PodCannotSearchForeignTickets verifies search_tickets is
// scoped to pod.OrgID, not "any org the human is in". A foreign-org ticket
// must NOT surface in dev-org pod's search even with broad query terms.
func TestCrossOrg_PodCannotSearchForeignTickets(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	foreignSlug := fmt.Sprintf("e2e-foreign-search-%d", time.Now().UnixMilli())
	foreignOrg, err := rest.CreateOrg(ctx, "E2E Foreign Search", foreignSlug)
	if err != nil {
		t.Fatalf("create foreign org: %v", err)
	}
	t.Cleanup(func() {
		ctx2, cancel2 := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel2()
		_ = rest.DeleteOrg(ctx2, foreignOrg.Slug)
	})

	tag := fmt.Sprintf("xorg-tag-%d", time.Now().UnixMilli())
	if _, err := rest.CreateTicket(ctx, foreignOrg.Slug, client.CreateTicketRequest{
		Title: tag + " in foreign org",
	}); err != nil {
		t.Fatalf("create foreign ticket: %v", err)
	}

	pod := fixture.NewEchoPod(t, env, rest, runner.ID)
	out, err := pod.MCP.CallToolText(ctx, "search_tickets", map[string]any{
		"query": tag,
		"limit": 50,
	})
	if err != nil {
		t.Fatalf("search_tickets: %v", err)
	}
	if strings.Contains(out, tag) {
		t.Errorf("search_tickets in dev-org leaked foreign-org ticket containing %q:\n%s", tag, out)
	}
}
