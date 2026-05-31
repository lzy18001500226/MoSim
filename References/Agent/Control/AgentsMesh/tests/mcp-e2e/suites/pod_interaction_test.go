package suites

import (
	"context"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// TestPodInteraction_RoundTrip exercises the 3 pod-interaction tools on an
// echo-agent pod: status → snapshot → input → snapshot. The agent prints
// "got: <line>" for every line it receives on stdin, so a successful
// round-trip means the second snapshot contains "got: hello".
//
// We don't assert on the startup banner ("ready") because PTY snapshots are
// rolling and "ready" can scroll out before the test reads it; the input/
// echo round-trip is the more reliable signal.
func TestPodInteraction_RoundTrip(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Wait briefly so the echo agent has finished its initial read setup
	// before we feed it input.
	time.Sleep(500 * time.Millisecond)

	// 1) get_pod_status — must include the pod key.
	status, err := pod.MCP.CallToolText(ctx, "get_pod_status", map[string]any{
		"pod_key": pod.Pod.PodKey,
	})
	if err != nil {
		t.Fatalf("get_pod_status: %v", err)
	}
	if !strings.Contains(status, pod.Pod.PodKey) {
		t.Errorf("get_pod_status missing pod key: %q", status)
	}

	// 2) send_pod_input — feed a line + trailing enter.
	if _, err := pod.MCP.CallToolText(ctx, "send_pod_input", map[string]any{
		"pod_key": pod.Pod.PodKey,
		"text":    "hello\n",
	}); err != nil {
		t.Fatalf("send_pod_input: %v", err)
	}

	// 3) Poll snapshot for the echoed line. PTY echo plus the agent's
	//    "got: " response can take a few hundred ms.
	deadline := time.Now().Add(5 * time.Second)
	for time.Now().Before(deadline) {
		snap, err := pod.MCP.CallToolText(ctx, "get_pod_snapshot", map[string]any{
			"pod_key": pod.Pod.PodKey,
			"lines":   200,
		})
		if err == nil && strings.Contains(snap, "got: hello") {
			return // success
		}
		time.Sleep(200 * time.Millisecond)
	}
	t.Fatalf("expected 'got: hello' in snapshot within 5s")
}
