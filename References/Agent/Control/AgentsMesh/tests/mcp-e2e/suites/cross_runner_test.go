package suites

import (
	"context"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// Cross-runner pod_interaction. dev-runner-2 (added in docker-compose for
// e2e) hosts a second pod. Pod_A on dev-runner asks for pod_B's snapshot
// via MCP. runner-1's LocalPodProvider misses (pod_B is on runner-2),
// falls back to backend, backend dispatches to runner-2 via gRPC, and the
// snapshot round-trips back. Without this spec, the entire fallback path
// in http_tools_pod_interaction.go:50 has zero coverage in dev.
func TestCrossRunner_PodInteractionRoutesThroughBackend(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	r1 := fixture.DiscoverRunnerByNode(t, env, rest, "dev-runner")
	r2 := fixture.DiscoverRunnerByNode(t, env, rest, "dev-runner-2")
	if r1.ID == r2.ID {
		t.Fatalf("expected two distinct runners, got the same: %+v", r1)
	}

	podA := fixture.NewEchoPod(t, env, rest, r1.ID)
	podB := fixture.NewEchoPod(t, env, rest, r2.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	// Bind so podA has read+write rights on podB. In dev, same-user bindings
	// auto-activate so we don't need accept_binding from podB.
	if _, err := podA.MCP.CallToolText(ctx, "bind_pod", map[string]any{
		"target_pod": podB.Pod.PodKey,
		"scopes":     []string{"pod:read", "pod:write"},
	}); err != nil {
		t.Fatalf("bind_pod cross-runner: %v", err)
	}
	t.Cleanup(func() {
		ctx2, cancel2 := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel2()
		_, _ = podA.MCP.CallToolText(ctx2, "unbind_pod", map[string]any{
			"target_pod": podB.Pod.PodKey,
		})
	})

	// Feed podB an input via the cross-runner path. podA's runner (r1) does
	// NOT have podB locally, so this MUST go through the backend gRPC route
	// to r2. If that path is broken, send_pod_input either errors or
	// silently drops — both fail the assertion below.
	if _, err := podA.MCP.CallToolText(ctx, "send_pod_input", map[string]any{
		"pod_key": podB.Pod.PodKey,
		"text":    "cross-runner-hello\n",
	}); err != nil {
		t.Fatalf("send_pod_input across runners: %v", err)
	}

	deadline := time.Now().Add(8 * time.Second)
	for time.Now().Before(deadline) {
		snap, err := podA.MCP.CallToolText(ctx, "get_pod_snapshot", map[string]any{
			"pod_key": podB.Pod.PodKey,
			"lines":   200,
		})
		if err == nil && strings.Contains(snap, "got: cross-runner-hello") {
			return // success: full round-trip across runners
		}
		time.Sleep(300 * time.Millisecond)
	}
	t.Fatalf("expected 'got: cross-runner-hello' in cross-runner snapshot within 8s")
}

func TestCrossRunner_BothRunnersListed(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	r1 := fixture.DiscoverRunnerByNode(t, env, rest, "dev-runner")
	pod := fixture.NewEchoPod(t, env, rest, r1.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	out, err := pod.MCP.CallToolText(ctx, "list_runners", nil)
	if err != nil {
		t.Fatalf("list_runners: %v", err)
	}
	for _, want := range []string{"dev-runner", "dev-runner-2"} {
		if !strings.Contains(out, want) {
			t.Errorf("expected runner %q in list_runners (cross-runner stack should expose both):\n%s", want, out)
		}
	}
}
