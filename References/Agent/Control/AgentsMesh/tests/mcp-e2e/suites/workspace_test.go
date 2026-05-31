// Package suites houses the MCP end-to-end test specs. Each file targets one
// MCP tool family so a failure points cleanly at the surface that broke.
//
// Phase 1 only covers block.get_default_workspace as the smoke test: it
// exercises auth → REST pod creation → runner pod registration → MCP HTTP
// dispatch → backend gRPC handler → blockstore service → Postgres in a
// single call. Once this is green, all subsequent specs are additive.
package suites

import (
	"context"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/client"
	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

func TestBlockGetDefaultWorkspace_Smoke(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	var ws struct {
		ID   string `json:"id"`
		Slug string `json:"slug"`
		Name string `json:"name"`
	}
	if err := pod.MCP.CallTool(ctx, "block.get_default_workspace", nil, &ws); err != nil {
		t.Fatalf("block.get_default_workspace: %v", err)
	}
	if ws.ID == "" {
		t.Fatalf("expected non-empty workspace id, got %+v", ws)
	}
	if ws.Slug != "default" {
		t.Errorf("expected slug 'default', got %q", ws.Slug)
	}

	db, err := client.OpenDB(env.PostgresDSN)
	if err != nil {
		t.Fatalf("open postgres for fact assertion: %v", err)
	}
	t.Cleanup(func() { _ = db.Close() })

	dbID, err := db.GetWorkspaceIDBySlug(ctx, env.DevOrgSlug, "default")
	if err != nil {
		t.Fatalf("lookup default workspace by slug: %v", err)
	}
	if dbID != ws.ID {
		t.Errorf("MCP returned workspace id %q but DB has %q for org %s", ws.ID, dbID, env.DevOrgSlug)
	}
}

func TestBlockListWorkspaces_IncludesDefault(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Touch get_default_workspace first so the org has at least one row even
	// in a fresh DB; list_workspaces must contain it.
	var def struct {
		ID   string `json:"id"`
		Slug string `json:"slug"`
	}
	if err := pod.MCP.CallTool(ctx, "block.get_default_workspace", nil, &def); err != nil {
		t.Fatalf("get_default_workspace prerequisite: %v", err)
	}

	var listing struct {
		Workspaces []struct {
			ID             string `json:"id"`
			Slug           string `json:"slug"`
			Name           string `json:"name"`
			OrganizationID int64  `json:"organization_id"`
		} `json:"workspaces"`
	}
	if err := pod.MCP.CallTool(ctx, "block.list_workspaces", nil, &listing); err != nil {
		t.Fatalf("block.list_workspaces: %v", err)
	}

	var found bool
	for _, w := range listing.Workspaces {
		if w.ID == def.ID && w.Slug == "default" {
			found = true
			break
		}
	}
	if !found {
		t.Errorf("default workspace %s not present in list_workspaces=%+v", def.ID, listing.Workspaces)
	}
}
