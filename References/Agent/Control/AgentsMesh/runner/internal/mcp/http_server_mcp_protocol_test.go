package mcp

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestHTTPServerMCPInitialize(t *testing.T) {
	server := NewHTTPServer(nil, 9090)
	server.RegisterPod("test-pod", "test-org", nil, nil, "claude")

	body := bytes.NewBufferString(`{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}`)
	req := httptest.NewRequest(http.MethodPost, "/mcp", body)
	req.Header.Set("X-Pod-Key", "test-pod")
	rec := httptest.NewRecorder()

	server.handleMCP(rec, req)

	var resp MCPResponse
	if err := json.NewDecoder(rec.Body).Decode(&resp); err != nil {
		t.Fatalf("failed to decode response: %v", err)
	}

	if resp.Error != nil {
		t.Errorf("unexpected error: %v", resp.Error.Message)
	}

	if resp.Result == nil {
		t.Error("result should not be nil")
	}

	result, ok := resp.Result.(map[string]interface{})
	if !ok {
		t.Fatal("result should be a map")
	}

	if result["protocolVersion"] != "2024-11-05" {
		t.Errorf("protocolVersion: got %v, want 2024-11-05", result["protocolVersion"])
	}
}

func TestHTTPServerMCPToolsList(t *testing.T) {
	server := NewHTTPServer(nil, 9090)
	server.RegisterPod("test-pod", "test-org", nil, nil, "claude")

	body := bytes.NewBufferString(`{"jsonrpc":"2.0","id":1,"method":"tools/list"}`)
	req := httptest.NewRequest(http.MethodPost, "/mcp", body)
	req.Header.Set("X-Pod-Key", "test-pod")
	rec := httptest.NewRecorder()

	server.handleMCP(rec, req)

	var resp MCPResponse
	if err := json.NewDecoder(rec.Body).Decode(&resp); err != nil {
		t.Fatalf("failed to decode response: %v", err)
	}

	if resp.Error != nil {
		t.Errorf("unexpected error: %v", resp.Error.Message)
	}

	result, ok := resp.Result.(map[string]interface{})
	if !ok {
		t.Fatal("result should be a map")
	}

	tools, ok := result["tools"].([]interface{})
	if !ok {
		t.Fatal("tools should be an array")
	}

	// Should have 21 tools (all collaboration tools)
	if len(tools) < 20 {
		t.Errorf("tools count: got %v, want at least 20", len(tools))
	}
}

func TestHTTPServerMCPNotificationsInitialized(t *testing.T) {
	server := NewHTTPServer(nil, 9090)
	server.RegisterPod("test-pod", "test-org", nil, nil, "claude")

	body := bytes.NewBufferString(`{
		"jsonrpc": "2.0",
		"method": "notifications/initialized"
	}`)

	req := httptest.NewRequest(http.MethodPost, "/mcp", body)
	req.Header.Set("X-Pod-Key", "test-pod")
	rec := httptest.NewRecorder()

	server.handleMCP(rec, req)

	// Per Streamable HTTP spec, notifications MUST receive 202 Accepted with no body
	if rec.Code != http.StatusAccepted {
		t.Errorf("expected status 202 Accepted for notification, got %d", rec.Code)
	}
	if rec.Body.Len() != 0 {
		t.Errorf("expected empty body for notification, got %q", rec.Body.String())
	}
}

func TestHTTPServerMCPNotificationsCancelled(t *testing.T) {
	server := NewHTTPServer(nil, 9090)
	server.RegisterPod("test-pod", "test-org", nil, nil, "codex")

	body := bytes.NewBufferString(`{
		"jsonrpc": "2.0",
		"method": "notifications/cancelled",
		"params": {"requestId": 1}
	}`)

	req := httptest.NewRequest(http.MethodPost, "/mcp", body)
	req.Header.Set("X-Pod-Key", "test-pod")
	rec := httptest.NewRecorder()

	server.handleMCP(rec, req)

	if rec.Code != http.StatusAccepted {
		t.Errorf("expected status 202 for notifications/cancelled, got %d", rec.Code)
	}
}
