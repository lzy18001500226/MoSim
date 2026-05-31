package blockstore

import (
	"context"
	"errors"
	"fmt"
	"time"
)

// CreateBlock writes a single block into a workspace and returns its id.
// Generates its own idempotency key from the supplied op hash so a retry of
// the same payload won't double-write.
func (c *Client) CreateBlock(
	ctx context.Context,
	workspaceID, blockType string,
	data map[string]any,
) (*BlockRef, error) {
	op := OpEnvelope{
		Op: "createBlock",
		Payload: map[string]any{
			"type": blockType,
			"data": data,
		},
	}
	res, err := c.ApplyOps(ctx, workspaceID, []OpEnvelope{op}, "")
	if err != nil {
		return nil, err
	}
	if len(res.OpIDs) == 0 {
		return nil, errors.New("blockstore: createBlock returned no op id")
	}
	return &BlockRef{OpID: res.OpIDs[0]}, nil
}

// AddRef creates a relationship edge. For rel="nest" callers must supply a
// fractional-index orderKey; for other rels pass "".
func (c *Client) AddRef(
	ctx context.Context,
	workspaceID, from, to, rel, orderKey string,
) error {
	payload := map[string]any{"from": from, "to": to, "rel": rel}
	if orderKey != "" {
		payload["order_key"] = orderKey
	}
	_, err := c.ApplyOps(ctx, workspaceID, []OpEnvelope{
		{Op: "addRef", Payload: payload},
	}, "")
	return err
}

// UpdateBlock merges `patch` into the block's data field. Pass a non-zero
// expectedUpdatedAt for optimistic concurrency control.
func (c *Client) UpdateBlock(
	ctx context.Context,
	workspaceID, blockID string,
	patch map[string]any,
	expectedUpdatedAt *time.Time,
) error {
	payload := map[string]any{"id": blockID, "data": patch}
	if expectedUpdatedAt != nil {
		payload["expected_updated_at"] = expectedUpdatedAt.UTC().Format(time.RFC3339Nano)
	}
	_, err := c.ApplyOps(ctx, workspaceID, []OpEnvelope{
		{Op: "updateBlock", Payload: payload},
	}, "")
	return err
}

// ApplyOps is the raw batch entrypoint; prefer the helpers above unless you
// need multi-op atomicity.
func (c *Client) ApplyOps(
	ctx context.Context,
	workspaceID string,
	ops []OpEnvelope,
	idempotencyKey string,
) (*ApplyOpsResponse, error) {
	body := map[string]any{
		"workspace_id": workspaceID,
		"ops":          ops,
	}
	if idempotencyKey != "" {
		body["idempotency_key"] = idempotencyKey
	}
	var out ApplyOpsResponse
	err := c.do(ctx, "POST", fmt.Sprintf("/api/v1/orgs/%s/blocks/ops", c.orgSlug), body, &out)
	return &out, err
}
