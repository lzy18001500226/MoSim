package suites

import (
	"context"
	"fmt"
	"regexp"
	"strconv"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// bindingIDRE captures the numeric id out of either "Binding: #8" or
// "Binding #8" or any "ID: 8" header. The character class [^\d]* lets us
// skip over colons / spaces / # without enumerating them.
var bindingIDRE = regexp.MustCompile(`Binding[^\d]*(\d+)`)

// TestBinding_LifecycleHappyPath creates two echo pods and exercises the
// binding lifecycle. Note: in the dev environment both pods are created by
// the same user, so the binding is auto-activated on bind_pod (Status: active
// in the response, not "pending"). We therefore skip the accept_binding step
// — calling it on an already-active binding returns "binding is not pending".
// The state visibility (get_bindings / get_bound_pods) and unbinding are the
// parts of the lifecycle this spec actually verifies.
func TestBinding_LifecycleHappyPath(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	podA := fixture.NewEchoPod(t, env, rest, runner.ID)
	podB := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	bindOut, err := podA.MCP.CallToolText(ctx, "bind_pod", map[string]any{
		"target_pod": podB.Pod.PodKey,
		"scopes":     []string{"pod:read", "pod:write"},
	})
	if err != nil {
		t.Fatalf("bind_pod: %v", err)
	}
	if _, err := extractBindingID(bindOut); err != nil {
		t.Fatalf("could not parse binding id:\n%s", bindOut)
	}
	if !strings.Contains(bindOut, "active") {
		t.Errorf("expected auto-activated binding (status=active) in same-user dev env, got:\n%s", bindOut)
	}

	bindings, err := podA.MCP.CallToolText(ctx, "get_bindings", nil)
	if err != nil {
		t.Fatalf("get_bindings: %v", err)
	}
	if !strings.Contains(bindings, podB.Pod.PodKey) {
		t.Errorf("podB key %q not in get_bindings output:\n%s", podB.Pod.PodKey, bindings)
	}

	bound, err := podA.MCP.CallToolText(ctx, "get_bound_pods", nil)
	if err != nil {
		t.Fatalf("get_bound_pods: %v", err)
	}
	if !strings.Contains(bound, podB.Pod.PodKey) {
		t.Errorf("podB key %q not in get_bound_pods output:\n%s", podB.Pod.PodKey, bound)
	}

	if _, err := podA.MCP.CallToolText(ctx, "unbind_pod", map[string]any{
		"target_pod": podB.Pod.PodKey,
	}); err != nil {
		t.Fatalf("unbind_pod: %v", err)
	}

	time.Sleep(300 * time.Millisecond)
	after, err := podA.MCP.CallToolText(ctx, "get_bound_pods", nil)
	if err != nil {
		t.Fatalf("get_bound_pods (after): %v", err)
	}
	if strings.Contains(after, podB.Pod.PodKey) {
		t.Errorf("podB still present after unbind:\n%s", after)
	}
}

// TestBinding_AcceptRejectRequiresPending pins the contract that accept and
// reject are pending-only operations. In a same-user dev env bindings auto-
// activate, so calling accept/reject on them must return "binding is not
// pending". Cross-user pending flows belong to a future spec that owns
// multiple users.
func TestBinding_AcceptRejectRequiresPending(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	podA := fixture.NewEchoPod(t, env, rest, runner.ID)
	podB := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	bindOut, err := podA.MCP.CallToolText(ctx, "bind_pod", map[string]any{
		"target_pod": podB.Pod.PodKey,
		"scopes":     []string{"pod:read"},
	})
	if err != nil {
		t.Fatalf("bind_pod: %v", err)
	}
	bindingID, err := extractBindingID(bindOut)
	if err != nil {
		t.Fatalf("parse binding id:\n%s", bindOut)
	}

	if _, err := podB.MCP.CallToolText(ctx, "accept_binding", map[string]any{
		"binding_id": bindingID,
	}); err == nil {
		t.Errorf("expected accept_binding to fail on auto-activated binding, got success")
	}
	if _, err := podB.MCP.CallToolText(ctx, "reject_binding", map[string]any{
		"binding_id": bindingID,
		"reason":     "e2e",
	}); err == nil {
		t.Errorf("expected reject_binding to fail on auto-activated binding, got success")
	}

	// Cleanup so the pair doesn't bleed into other tests.
	_, _ = podA.MCP.CallToolText(ctx, "unbind_pod", map[string]any{
		"target_pod": podB.Pod.PodKey,
	})
}

func extractBindingID(text string) (int, error) {
	m := bindingIDRE.FindStringSubmatch(text)
	if len(m) != 2 {
		return 0, fmt.Errorf("no binding id matched")
	}
	return strconv.Atoi(m[1])
}
