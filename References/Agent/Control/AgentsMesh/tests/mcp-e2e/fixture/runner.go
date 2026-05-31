package fixture

import (
	"context"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/client"
)

// DiscoverRunner returns the first online runner attached to the dev org.
// Online means status != "offline"; we accept "online", "ready", or any
// non-offline state to be tolerant of small backend status taxonomy shifts.
//
// The dev seed creates a runner with node_id="dev-runner". When deploy/dev
// is up that runner registers via gRPC and flips its status. This helper
// blocks up to 30s to give the runner enough time to come up after a fresh
// stack restart.
func DiscoverRunner(t *testing.T, env *Env, rest *client.REST) client.Runner {
	t.Helper()
	deadline := time.Now().Add(30 * time.Second)
	for time.Now().Before(deadline) {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		runners, err := rest.ListRunners(ctx, env.DevOrgSlug)
		cancel()
		if err == nil {
			for _, r := range runners {
				if r.NodeID == env.RunnerNode && r.Status != "offline" {
					return r
				}
			}
		}
		time.Sleep(500 * time.Millisecond)
	}
	t.Fatalf("no online runner with node_id=%q in org %s within 30s", env.RunnerNode, env.DevOrgSlug)
	return client.Runner{}
}

// DiscoverRunnerByNode returns a specific runner by node_id, used by the
// cross-runner spec which needs both dev-runner and dev-runner-2 distinctly.
func DiscoverRunnerByNode(t *testing.T, env *Env, rest *client.REST, nodeID string) client.Runner {
	t.Helper()
	deadline := time.Now().Add(30 * time.Second)
	for time.Now().Before(deadline) {
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		runners, err := rest.ListRunners(ctx, env.DevOrgSlug)
		cancel()
		if err == nil {
			for _, r := range runners {
				if r.NodeID == nodeID && r.Status != "offline" {
					return r
				}
			}
		}
		time.Sleep(500 * time.Millisecond)
	}
	t.Fatalf("no online runner with node_id=%q in org %s within 30s", nodeID, env.DevOrgSlug)
	return client.Runner{}
}
