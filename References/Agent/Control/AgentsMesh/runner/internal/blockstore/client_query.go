package blockstore

import (
	"context"
	"fmt"
)

// EnsureDefaultWorkspace creates (or returns) the caller org's default
// workspace. Runner-side Agents should call this once per pod boot.
func (c *Client) EnsureDefaultWorkspace(ctx context.Context) (*Workspace, error) {
	var out Workspace
	err := c.do(ctx, "POST",
		fmt.Sprintf("/api/v1/orgs/%s/blocks/workspaces/default", c.orgSlug),
		nil, &out)
	return &out, err
}

// RetrieveMemory asks the Block Store for the top-K blocks most semantically
// relevant to `query`. Agents typically call this before drafting a response
// to ground output in prior notes, tasks, or comments from the workspace.
// k<=0 defaults to 5.
func (c *Client) RetrieveMemory(
	ctx context.Context,
	workspaceID, query string,
	k int,
) ([]MemoryHit, error) {
	body := map[string]any{"query": query}
	if k > 0 {
		body["k"] = k
	}
	var out MemoryResponse
	err := c.do(ctx, "POST",
		fmt.Sprintf("/api/v1/orgs/%s/blocks/workspaces/%s/memory/retrieve", c.orgSlug, workspaceID),
		body, &out)
	if err != nil {
		return nil, err
	}
	return out.Memories, nil
}
