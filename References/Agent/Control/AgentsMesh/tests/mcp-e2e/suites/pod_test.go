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

// create_pod returns text like "Pod: <key> ..." — extract the key with a
// regex and use it to clean up via REST.
var nestedPodKeyRE = regexp.MustCompile(`(\d+-standalone-[a-f0-9]+)`)

func TestCreatePod_NestedSpawn(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	alias := fmt.Sprintf("e2e-nested-%d", time.Now().UnixMilli())
	out, err := pod.MCP.CallToolText(ctx, "create_pod", map[string]any{
		"agent_slug": "e2e-echo",
		"runner_id":  runner.ID,
		"alias":      alias,
		"cols":       80,
		"rows":       24,
	})
	if err != nil {
		t.Fatalf("create_pod: %v", err)
	}
	// The exact label varies (Pod / pod_key / etc.) — we only need the key
	// itself, and pod keys follow a stable pattern <n>-standalone-<hex>.
	m := nestedPodKeyRE.FindStringSubmatch(out)
	if len(m) != 2 {
		t.Fatalf("could not parse spawned pod key from output:\n%s", out)
	}
	spawnedKey := m[1]
	if !strings.Contains(out, spawnedKey) {
		t.Errorf("expected pod key in output:\n%s", out)
	}

	t.Cleanup(func() {
		ctx2, cancel2 := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel2()
		_ = rest.TerminatePod(ctx2, env.DevOrgSlug, spawnedKey)
	})
}
