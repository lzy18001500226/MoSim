package blockstoreservice

import (
	"context"
	"testing"

	"github.com/anthropics/agentsmesh/backend/internal/domain/blockstore"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestIndicatorLifecycle covers the Tier 1 happy path end-to-end at the
// service layer:
//   1. Agent "defines" an indicator by writing a block_type_def with columns
//   2. Type resolver picks up the new type immediately (via ListTypeDefs)
//   3. Creating a record with correct columns succeeds
//   4. Creating a record missing a required column fails
//   5. Creating a record with an out-of-enum select value fails
func TestIndicatorLifecycle(t *testing.T) {
	svc, actor, wsID, rootID := setup(t)
	ctx := context.Background()

	// Step 1 — Define an "okr" indicator.
	_, err := svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"type": blockstore.BlockTypeTypeDef,
				"data": map[string]any{
					"type_key":        "okr",
					"revision":        1,
					"label":           "OKR",
					"description":     "Quarterly objective",
					"default_view":    "kanban",
					"supported_views": []string{"kanban", "table"},
					"columns": []map[string]any{
						{"key": "title", "type": "text", "required": true},
						{"key": "quarter", "type": "select", "required": true, "options": []map[string]any{
							{"value": "Q1"}, {"value": "Q2"}, {"value": "Q3"}, {"value": "Q4"},
						}},
						{"key": "progress", "type": "number", "default": 0.0},
					},
				},
			}},
		},
	})
	require.NoError(t, err)

	// Step 2/3 — Create a record with the new type; resolver sees it and
	// validates columns.
	okrID := uuid.New()
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id":   okrID.String(),
				"type": "okr",
				"data": map[string]any{"title": "Ship v1", "quarter": "Q4", "progress": 0.5},
			}},
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": rootID.String(), "to": okrID.String(),
				"rel": blockstore.RelNest, "order_key": "a0",
			}},
		},
	})
	require.NoError(t, err, "valid okr record should apply")

	// Step 4 — Missing required column rejected.
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"type": "okr",
				"data": map[string]any{"title": "Missing quarter"},
			}},
		},
	})
	require.Error(t, err)
	assert.ErrorIs(t, err, blockstore.ErrMissingRequiredKey)

	// Step 5 — Invalid select value rejected.
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"type": "okr",
				"data": map[string]any{"title": "Bad quarter", "quarter": "Q5"},
			}},
		},
	})
	require.Error(t, err)
	assert.ErrorIs(t, err, blockstore.ErrColumnValueInvalid)
}
