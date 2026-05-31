// Package blockstore provides a thin HTTP client so Runner-side Agents can
// push structured outputs into the AgentsMesh Block Store from within the
// sandbox process. Every Agent action (plan, file edit, build result, ticket
// insight) can be recorded as a block with a stable ID and replayable op log.
//
// Usage:
//
//	c := blockstore.NewClient(cfg.BackendURL, cfg.AgentJWT)
//	task, err := c.CreateBlock(ctx, cfg.WorkspaceID, "task", map[string]any{
//	    "title":  "Implement feature X",
//	    "status": "in_progress",
//	})
//	_ = c.AddRef(ctx, cfg.WorkspaceID, rootBlock, task.ID, "nest", "a0")
package blockstore

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

const defaultTimeout = 30 * time.Second

// Client is the Runner → Block Store HTTP client. Safe for concurrent use.
type Client struct {
	baseURL string
	token   string
	orgSlug string
	hc      *http.Client
}

// Config is the minimal set of fields a Runner needs to talk to the Block
// Store. AgentsMesh bootstrap populates these from the registered agent pod.
type Config struct {
	BaseURL        string       // e.g. "https://api.agentsmesh.com"
	OrgSlug        string       // e.g. "acme"
	Token          string       // bearer JWT minted for the agent
	HTTPClient     *http.Client // optional
	RequestTimeout time.Duration
}

func NewClient(cfg Config) *Client {
	hc := cfg.HTTPClient
	if hc == nil {
		timeout := cfg.RequestTimeout
		if timeout == 0 {
			timeout = defaultTimeout
		}
		hc = &http.Client{Timeout: timeout}
	}
	return &Client{
		baseURL: cfg.BaseURL,
		token:   cfg.Token,
		orgSlug: cfg.OrgSlug,
		hc:      hc,
	}
}

// do is the shared HTTP transport for every call. JSON-marshals the body,
// attaches the bearer token, decodes the response (with UseNumber so the
// caller can distinguish ints from floats), and wraps non-2xx as an error
// that includes the raw response body for diagnostic grep-ability.
func (c *Client) do(ctx context.Context, method, path string, body, out any) error {
	var rdr io.Reader
	if body != nil {
		buf, err := json.Marshal(body)
		if err != nil {
			return err
		}
		rdr = bytes.NewReader(buf)
	}
	req, err := http.NewRequestWithContext(ctx, method, c.baseURL+path, rdr)
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+c.token)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	resp, err := c.hc.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		raw, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("blockstore: %s %s → %d: %s",
			method, path, resp.StatusCode, string(raw))
	}
	if out == nil {
		return nil
	}
	dec := json.NewDecoder(resp.Body)
	dec.UseNumber()
	if err := dec.Decode(out); err != nil {
		return fmt.Errorf("blockstore: decode %s %s: %w", method, path, err)
	}
	return nil
}
