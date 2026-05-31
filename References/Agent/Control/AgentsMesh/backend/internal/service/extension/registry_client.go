package extension

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"net/url"
	"time"

	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
)

type McpRegistryClient struct {
	httpClient *http.Client
	baseURL    string
}

func NewMcpRegistryClient(baseURL string) *McpRegistryClient {
	return &McpRegistryClient{
		httpClient: &http.Client{
			Timeout:   30 * time.Second,
			Transport: otelhttp.NewTransport(http.DefaultTransport),
		},
		baseURL: baseURL,
	}
}

const maxRegistryPages = 500

func (c *McpRegistryClient) FetchAll(ctx context.Context) ([]RegistryServerEntry, error) {
	var all []RegistryServerEntry
	cursor := ""
	pageNum := 0

	for {
		if ctx.Err() != nil {
			return nil, ctx.Err()
		}

		page, err := c.FetchPage(ctx, cursor, 100)
		if err != nil {
			return nil, fmt.Errorf("fetch page %d: %w", pageNum, err)
		}
		pageNum++

		for _, entry := range page.Servers {
			if !c.isLatestActive(entry.Meta) {
				continue
			}
			all = append(all, entry)
		}

		slog.DebugContext(ctx, "MCP Registry: fetched page",
			"page", pageNum, "count", len(page.Servers), "total_kept", len(all))

		if page.Metadata.NextCursor == "" || len(page.Servers) == 0 {
			break
		}
		cursor = page.Metadata.NextCursor

		if pageNum >= maxRegistryPages {
			slog.WarnContext(ctx, "MCP Registry: reached max page limit, stopping pagination",
				"maxPages", maxRegistryPages, "total_kept", len(all))
			break
		}
	}

	return all, nil
}

func (c *McpRegistryClient) FetchPage(ctx context.Context, cursor string, limit int) (*RegistryResponse, error) {
	u, err := url.Parse(c.baseURL + "/v0/servers")
	if err != nil {
		return nil, fmt.Errorf("parse URL: %w", err)
	}

	q := u.Query()
	q.Set("limit", fmt.Sprintf("%d", limit))
	if cursor != "" {
		q.Set("cursor", cursor)
	}
	u.RawQuery = q.Encode()

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, u.String(), nil)
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	req.Header.Set("User-Agent", "AgentsMesh-Backend/1.0")
	req.Header.Set("Accept", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("HTTP request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(io.LimitReader(resp.Body, 1024))
		return nil, fmt.Errorf("registry returned %d: %s", resp.StatusCode, string(body))
	}

	var result RegistryResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}
	return &result, nil
}

func (c *McpRegistryClient) isLatestActive(meta json.RawMessage) bool {
	if len(meta) == 0 {
		return true
	}
	var metaMap map[string]json.RawMessage
	if err := json.Unmarshal(meta, &metaMap); err != nil {
		return true
	}
	officialRaw, ok := metaMap["io.modelcontextprotocol.registry/official"]
	if !ok {
		return true
	}
	var official RegistryOfficialMeta
	if err := json.Unmarshal(officialRaw, &official); err != nil {
		return true
	}
	return official.IsLatest && official.Status == "active"
}
