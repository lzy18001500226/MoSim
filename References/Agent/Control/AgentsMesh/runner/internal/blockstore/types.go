package blockstore

import "time"

// OpEnvelope mirrors the server's JSON shape (see backend/internal/service/blockstore).
type OpEnvelope struct {
	Op      string         `json:"op"`
	Payload map[string]any `json:"payload"`
}

// ApplyOpsResponse is the wire shape returned by POST /blocks/ops.
type ApplyOpsResponse struct {
	OpIDs      []int64 `json:"op_ids"`
	WasReplay  bool    `json:"was_replay"`
	ParentOpID *int64  `json:"parent_op_id,omitempty"`
}

// BlockRef is a thin handle returned by convenience constructors. The server
// does not echo the full block on ApplyOps — callers that need the row fetch
// via GET /blocks/:id with OpID as the correlation hint.
type BlockRef struct {
	OpID int64
}

// Workspace matches the JSON produced by EnsureDefaultWorkspace.
type Workspace struct {
	ID             string     `json:"id"`
	OrganizationID int64      `json:"organization_id"`
	Slug           string     `json:"slug"`
	Name           string     `json:"name"`
	RootBlockID    *string    `json:"root_block_id,omitempty"`
	CreatedAt      time.Time  `json:"created_at"`
}

// MemoryHit is one ranked result from RetrieveMemory. Agents use Snippet to
// build a textual memory context; BlockID is the pointer to fetch the full
// row when they need data beyond the snippet.
type MemoryHit struct {
	BlockID string  `json:"block_id"`
	Type    string  `json:"type"`
	Snippet string  `json:"snippet"`
	Score   float32 `json:"score"`
}

// MemoryResponse matches POST /blocks/workspaces/:ws_id/memory/retrieve.
type MemoryResponse struct {
	Memories []MemoryHit `json:"memories"`
}
