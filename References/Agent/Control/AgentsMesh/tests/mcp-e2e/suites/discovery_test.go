package suites

import (
	"context"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// Discovery tools return human-readable text (markdown tables / labeled
// fields) optimised for LLM consumption. We assert via substring matches
// rather than parsing structure — testing the "agent will see this content"
// contract rather than internal formatting choices.

func TestDiscovery_ListRunners_HasDevRunner(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	out, err := pod.MCP.CallToolText(ctx, "list_runners", nil)
	if err != nil {
		t.Fatalf("list_runners: %v", err)
	}
	if !strings.Contains(out, env.RunnerNode) {
		t.Errorf("dev runner node %q not in list_runners output:\n%s", env.RunnerNode, out)
	}
	if !strings.Contains(out, "online") {
		t.Errorf("expected runner status 'online' in list_runners output:\n%s", out)
	}
}

func TestDiscovery_ListRepositories_HasDemoRepos(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	out, err := pod.MCP.CallToolText(ctx, "list_repositories", nil)
	if err != nil {
		t.Fatalf("list_repositories: %v", err)
	}
	for _, want := range []string{"demo-webapp", "demo-api"} {
		if !strings.Contains(out, want) {
			t.Errorf("expected repo %q in list_repositories output:\n%s", want, out)
		}
	}
}

func TestDiscovery_ListAvailablePods_DecodesShape(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Result text may be empty (no other pods to bind), an empty markdown
	// table, or a populated listing — all valid. Just ensure the call
	// succeeds; cardinality is verified in binding_test.go where the test
	// owns both ends of the binding.
	if _, err := pod.MCP.CallToolText(ctx, "list_available_pods", nil); err != nil {
		t.Fatalf("list_available_pods: %v", err)
	}
}
