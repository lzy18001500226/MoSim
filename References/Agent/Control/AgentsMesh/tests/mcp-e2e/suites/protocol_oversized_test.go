package suites

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"net/http"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// TestProtocol_OversizedPayloadRejected pins the MCP HTTP server's 1 MB
// MaxBytesReader (http_server_handlers.go: maxMCPRequestSize). A payload
// larger than that must be rejected before reaching tool dispatch — silently
// truncating would let a misbehaving agent flood the runner with arbitrary
// memory pressure.
func TestProtocol_OversizedPayloadRejected(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()

	// Build a 1.5 MB JSON-RPC request: legal envelope + a giant string in
	// `params.arguments.text` so the payload would route to a real tool if
	// it weren't capped.
	const padBytes = 1_500_000
	pad := strings.Repeat("x", padBytes)
	body := fmt.Sprintf(
		`{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_runners","arguments":{"text":%q}}}`,
		pad,
	)

	req, _ := http.NewRequestWithContext(ctx,
		http.MethodPost, env.MCPBaseURL, bytes.NewReader([]byte(body)))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Pod-Key", pod.Pod.PodKey)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		// Connection-level abort is also acceptable — server may close on
		// MaxBytesReader exhaustion before the response writes back.
		return
	}
	defer resp.Body.Close()
	raw, _ := io.ReadAll(resp.Body)
	// We accept any of:
	//   * HTTP 4xx (413 / 400)
	//   * HTTP 200 with JSON-RPC error envelope
	// The non-acceptable outcome is "200 OK with successful tool result" —
	// that means the cap was bypassed and the runner truly processed 1.5 MB.
	if resp.StatusCode/100 != 2 {
		return // server rejected at HTTP layer
	}
	if strings.Contains(string(raw), `"error"`) {
		return // server rejected at JSON-RPC layer
	}
	if strings.Contains(string(raw), `"isError":true`) {
		return // tool result with isError flag
	}
	t.Errorf("oversized payload (1.5 MB) was accepted and processed; status=%d body=%.300s",
		resp.StatusCode, string(raw))
}
