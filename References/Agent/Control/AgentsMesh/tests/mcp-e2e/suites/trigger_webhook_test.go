package suites

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net"
	"net/http"
	"sync/atomic"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// TestTrigger_WebhookFiresOnCreate completes the trigger fire matrix begun
// in trigger_fire_test.go: registering a webhook-action trigger, performing
// the target write, and verifying the spec's local HTTP listener actually
// received the POST. The dev backend's BLOCKSTORE_WEBHOOK_ALLOW_HOSTS
// (host_services.sh:106) whitelists `localhost` so webhooks pointing at the
// test process pass the SSRF guard.
func TestTrigger_WebhookFiresOnCreate(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	wsID := getDefaultWorkspaceID(ctx, t, pod.MCP)

	// Bind a port on loopback. Backend (host process) reaches us via
	// localhost:<port> directly — same network namespace.
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatalf("listen: %v", err)
	}
	port := listener.Addr().(*net.TCPAddr).Port

	var hits atomic.Int64
	type capturedReq struct {
		Trigger string         `json:"trigger"`
		Event   string         `json:"event"`
		OpKind  string         `json:"op_kind"`
		Target  map[string]any `json:"target"`
	}
	captured := make(chan capturedReq, 4)
	srv := &http.Server{
		Handler: http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			body, _ := io.ReadAll(r.Body)
			var req capturedReq
			_ = json.Unmarshal(body, &req)
			hits.Add(1)
			select {
			case captured <- req:
			default:
			}
			w.WriteHeader(http.StatusOK)
		}),
	}
	go func() { _ = srv.Serve(listener) }()
	t.Cleanup(func() {
		shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 2*time.Second)
		defer shutdownCancel()
		_ = srv.Shutdown(shutdownCtx)
	})

	webhookURL := fmt.Sprintf("http://localhost:%d/hook", port)
	triggerName := fmt.Sprintf("e2e-wh-%d", time.Now().UnixMilli())
	if err := pod.MCP.CallTool(ctx, "trigger.define", map[string]any{
		"workspace_id": wsID,
		"arguments": map[string]any{
			"name":        triggerName,
			"target_type": "task",
			"on":          "create",
			"action": map[string]any{
				"kind": "webhook",
				"url":  webhookURL,
			},
		},
	}, nil); err != nil {
		t.Fatalf("trigger.define webhook: %v", err)
	}

	// Trigger the target write.
	if err := pod.MCP.CallTool(ctx, "block.create", map[string]any{
		"workspace_id": wsID,
		"payload": map[string]any{
			"type": "task",
			"data": map[string]any{"title": "wh-fire-target", "status": "open"},
		},
	}, nil); err != nil {
		t.Fatalf("block.create: %v", err)
	}

	// Webhook fire is async; poll for receipt.
	deadline := time.Now().Add(5 * time.Second)
	for time.Now().Before(deadline) {
		if hits.Load() > 0 {
			break
		}
		time.Sleep(200 * time.Millisecond)
	}
	if hits.Load() == 0 {
		t.Fatalf("webhook listener received no POST within 5s")
	}

	// Confirm payload shape: trigger name + event + target.type round-trip.
	select {
	case req := <-captured:
		if req.Trigger != triggerName {
			t.Errorf("expected webhook trigger=%q, got %q", triggerName, req.Trigger)
		}
		if req.Event != "create" {
			t.Errorf("expected event=create, got %q", req.Event)
		}
		if req.OpKind == "" {
			t.Errorf("expected non-empty op_kind in webhook payload")
		}
	case <-time.After(2 * time.Second):
		t.Errorf("captured channel empty even though hits > 0")
	}
}
