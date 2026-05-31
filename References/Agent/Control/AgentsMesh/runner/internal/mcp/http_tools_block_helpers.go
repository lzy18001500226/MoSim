package mcp

import (
	"context"

	"github.com/anthropics/agentsmesh/runner/internal/mcp/tools"
)

// blockstoreHandler is a small adapter that unwraps map[string]interface{}
// returns from the BlockStoreClient and hands them back as the generic
// interface{} expected by MCPToolHandler.
func blockstoreHandler(
	fn func(context.Context, tools.CollaborationClient, map[string]interface{}) (interface{}, error),
) MCPToolHandler {
	return func(ctx context.Context, client tools.CollaborationClient, args map[string]interface{}) (interface{}, error) {
		return fn(ctx, client, args)
	}
}

func blockstoreStringProp(desc string) map[string]interface{} {
	return map[string]interface{}{"type": "string", "description": desc}
}

func blockstoreObjectProp(desc string) map[string]interface{} {
	return map[string]interface{}{"type": "object", "description": desc}
}
