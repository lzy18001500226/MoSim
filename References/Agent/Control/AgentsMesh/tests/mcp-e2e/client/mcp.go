// Package client provides black-box clients for MCP end-to-end tests.
//
// MCPClient speaks JSON-RPC 2.0 over HTTP to the Runner's MCP server, exactly
// the way an in-pod agent would. Every request carries the X-Pod-Key header
// so the runner can route to the right pod context. Responses are decoded
// twice: once from the JSON-RPC envelope, once from the inner content[0].text
// which is itself a JSON-encoded payload (runner.MCPToolResult shape).
package client

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sync/atomic"
	"time"
)

const defaultMCPTimeout = 30 * time.Second

type MCPClient struct {
	baseURL string
	podKey  string
	hc      *http.Client
	idCtr   atomic.Int64
}

func NewMCP(baseURL, podKey string) *MCPClient {
	return &MCPClient{
		baseURL: baseURL,
		podKey:  podKey,
		hc:      &http.Client{Timeout: defaultMCPTimeout},
	}
}

type mcpRequest struct {
	JSONRPC string         `json:"jsonrpc"`
	ID      int64          `json:"id"`
	Method  string         `json:"method"`
	Params  map[string]any `json:"params,omitempty"`
}

type mcpResponse struct {
	JSONRPC string          `json:"jsonrpc"`
	ID      int64           `json:"id"`
	Result  json.RawMessage `json:"result,omitempty"`
	Error   *MCPError       `json:"error,omitempty"`
}

type MCPError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
	Data    any    `json:"data,omitempty"`
}

func (e *MCPError) Error() string {
	return fmt.Sprintf("mcp error %d: %s", e.Code, e.Message)
}

type toolCallResult struct {
	Content []struct {
		Type string `json:"type"`
		Text string `json:"text"`
	} `json:"content"`
	IsError bool `json:"isError,omitempty"`
}

// CallTool invokes a single MCP tool and decodes the inner JSON payload into
// out (which may be nil to discard). Returns *MCPError when the runner replied
// with isError=true so callers can assert on error codes/messages.
func (c *MCPClient) CallTool(ctx context.Context, name string, args map[string]any, out any) error {
	text, err := c.CallToolText(ctx, name, args)
	if err != nil {
		return err
	}
	if out == nil {
		return nil
	}
	if err := json.Unmarshal([]byte(text), out); err != nil {
		return fmt.Errorf("decode tool inner payload (%s): %w", name, err)
	}
	return nil
}

// CallToolText returns the raw text payload from a tool. Use this for tools
// that return human-readable strings (get_pod_status, send_pod_input) rather
// than JSON, where CallTool would fail to unmarshal.
func (c *MCPClient) CallToolText(ctx context.Context, name string, args map[string]any) (string, error) {
	if args == nil {
		args = map[string]any{}
	}
	req := mcpRequest{
		JSONRPC: "2.0",
		ID:      c.idCtr.Add(1),
		Method:  "tools/call",
		Params:  map[string]any{"name": name, "arguments": args},
	}
	resp, err := c.send(ctx, req)
	if err != nil {
		return "", err
	}
	if resp.Error != nil {
		return "", resp.Error
	}
	var tcr toolCallResult
	if err := json.Unmarshal(resp.Result, &tcr); err != nil {
		return "", fmt.Errorf("decode tool result envelope: %w", err)
	}
	if len(tcr.Content) == 0 {
		return "", fmt.Errorf("tool %s returned empty content", name)
	}
	text := tcr.Content[0].Text
	if tcr.IsError {
		return text, &MCPError{Code: -1, Message: text}
	}
	return text, nil
}

// Initialize performs the MCP handshake. Optional — most servers don't require
// it before tools/call, but exposing it lets tests assert protocol conformance.
func (c *MCPClient) Initialize(ctx context.Context) error {
	req := mcpRequest{
		JSONRPC: "2.0",
		ID:      c.idCtr.Add(1),
		Method:  "initialize",
	}
	resp, err := c.send(ctx, req)
	if err != nil {
		return err
	}
	if resp.Error != nil {
		return resp.Error
	}
	return nil
}

func (c *MCPClient) send(ctx context.Context, req mcpRequest) (*mcpResponse, error) {
	body, err := json.Marshal(req)
	if err != nil {
		return nil, err
	}
	httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, c.baseURL, bytes.NewReader(body))
	if err != nil {
		return nil, err
	}
	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("X-Pod-Key", c.podKey)

	httpResp, err := c.hc.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("mcp http: %w", err)
	}
	defer httpResp.Body.Close()
	raw, err := io.ReadAll(httpResp.Body)
	if err != nil {
		return nil, err
	}
	if httpResp.StatusCode/100 != 2 {
		return nil, fmt.Errorf("mcp http %d: %s", httpResp.StatusCode, string(raw))
	}
	var resp mcpResponse
	if err := json.Unmarshal(raw, &resp); err != nil {
		return nil, fmt.Errorf("decode jsonrpc: %w (body=%s)", err, string(raw))
	}
	return &resp, nil
}
