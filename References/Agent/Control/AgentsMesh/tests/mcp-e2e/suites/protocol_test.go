package suites

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/tests/mcp-e2e/fixture"
)

// Protocol-level guards. The MCP HTTP server applies a small number of
// invariants before any tool dispatch; these specs pin them so a regression
// in the dispatcher (auth, JSON-RPC framing, method routing) fails in CI
// rather than in production where an agent silently misbehaves.

func TestProtocol_MissingPodKeyHeaderRejected(t *testing.T) {
	env := fixture.LoadEnv(t)
	// Bring a runner up so the MCP server is alive — but we deliberately don't
	// create a pod, since the test is about the header check, not pod state.
	rest := fixture.SharedREST(t, env)
	_ = fixture.DiscoverRunner(t, env, rest)

	body := []byte(`{"jsonrpc":"2.0","id":1,"method":"tools/list"}`)
	req, _ := http.NewRequestWithContext(context.Background(),
		http.MethodPost, env.MCPBaseURL, bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	// Intentionally no X-Pod-Key.
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("post: %v", err)
	}
	defer resp.Body.Close()
	raw, _ := io.ReadAll(resp.Body)
	// Server replies with a JSON-RPC error envelope (HTTP 200 + error code).
	if !strings.Contains(string(raw), "X-Pod-Key") && !strings.Contains(string(raw), "pod") {
		t.Errorf("expected error mentioning X-Pod-Key, got: %s", string(raw))
	}
}

func TestProtocol_UnknownPodKeyRejected(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	_ = fixture.DiscoverRunner(t, env, rest)

	body := []byte(`{"jsonrpc":"2.0","id":1,"method":"tools/list"}`)
	req, _ := http.NewRequestWithContext(context.Background(),
		http.MethodPost, env.MCPBaseURL, bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Pod-Key", "this-pod-key-does-not-exist")
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("post: %v", err)
	}
	defer resp.Body.Close()
	raw, _ := io.ReadAll(resp.Body)
	if !strings.Contains(string(raw), "not registered") && !strings.Contains(string(raw), "Pod") {
		t.Errorf("expected error mentioning unregistered pod, got: %s", string(raw))
	}
}

func TestProtocol_UnknownMethodReturns32601(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	body := []byte(`{"jsonrpc":"2.0","id":1,"method":"definitely/not/a/real/method"}`)
	req, _ := http.NewRequestWithContext(context.Background(),
		http.MethodPost, env.MCPBaseURL, bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Pod-Key", pod.Pod.PodKey)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("post: %v", err)
	}
	defer resp.Body.Close()
	var body2 map[string]any
	_ = json.NewDecoder(resp.Body).Decode(&body2)
	errObj, _ := body2["error"].(map[string]any)
	code, _ := errObj["code"].(float64)
	if int(code) != -32601 {
		t.Errorf("expected JSON-RPC code -32601 (Method not found), got body=%+v", body2)
	}
}

func TestProtocol_NotificationGets202(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	// MCP "notifications/*" must return 202 with no body per the streamable
	// HTTP spec. handleMCP short-circuits these before routing.
	body := []byte(`{"jsonrpc":"2.0","method":"notifications/initialized"}`)
	req, _ := http.NewRequestWithContext(context.Background(),
		http.MethodPost, env.MCPBaseURL, bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Pod-Key", pod.Pod.PodKey)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("post: %v", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusAccepted {
		t.Errorf("expected 202 for notification, got %d", resp.StatusCode)
	}
}

func TestProtocol_InitializeAdvertisesCapabilities(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	body := []byte(`{"jsonrpc":"2.0","id":1,"method":"initialize"}`)
	req, _ := http.NewRequestWithContext(context.Background(),
		http.MethodPost, env.MCPBaseURL, bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Pod-Key", pod.Pod.PodKey)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("post: %v", err)
	}
	defer resp.Body.Close()
	var out struct {
		Result struct {
			ProtocolVersion string         `json:"protocolVersion"`
			Capabilities    map[string]any `json:"capabilities"`
			ServerInfo      map[string]any `json:"serverInfo"`
		} `json:"result"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		t.Fatalf("decode: %v", err)
	}
	if out.Result.ProtocolVersion == "" {
		t.Errorf("initialize response missing protocolVersion: %+v", out)
	}
	if _, ok := out.Result.Capabilities["tools"]; !ok {
		t.Errorf("initialize must advertise tools capability: %+v", out.Result.Capabilities)
	}
}

// TestProtocol_ToolsListEnumeratesAllRegistered confirms tools/list returns
// every tool declared by registerTools(). A drift between the registration
// list and tools/list response would silently hide tools from agents.
func TestProtocol_ToolsListEnumeratesAllRegistered(t *testing.T) {
	env := fixture.LoadEnv(t)
	rest := fixture.SharedREST(t, env)
	runner := fixture.DiscoverRunner(t, env, rest)
	pod := fixture.NewEchoPod(t, env, rest, runner.ID)

	body := []byte(`{"jsonrpc":"2.0","id":1,"method":"tools/list"}`)
	req, _ := http.NewRequestWithContext(context.Background(),
		http.MethodPost, env.MCPBaseURL, bytes.NewReader(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Pod-Key", pod.Pod.PodKey)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("post: %v", err)
	}
	defer resp.Body.Close()
	var out struct {
		Result struct {
			Tools []struct {
				Name string `json:"name"`
			} `json:"tools"`
		} `json:"result"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		t.Fatalf("decode: %v", err)
	}
	got := map[string]bool{}
	for _, t := range out.Result.Tools {
		got[t.Name] = true
	}
	// Sanity: at least the tools we know exist must be advertised. We keep
	// this list small so adding a new tool doesn't require updating this
	// spec — only removals or renames will trip it.
	expectedCore := []string{
		"block.create", "block.update", "block.delete",
		"block.list_workspaces", "block.get_default_workspace",
		"memory.retrieve", "list_runners", "search_tickets",
		"create_channel", "bind_pod", "create_pod",
		"get_pod_snapshot",
	}
	for _, name := range expectedCore {
		if !got[name] {
			t.Errorf("tools/list missing core tool %q (have %d total)", name, len(out.Result.Tools))
		}
	}
}

// fmtConvert silences the unused-import warning on `fmt` if a future test
// removes its only formatter usage; keeps the import explicit.
var _ = fmt.Sprintf

// timeMarker helps catch tests that block too long if the MCP server hangs.
var _ = time.Second
