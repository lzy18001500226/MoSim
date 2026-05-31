package blockstoreservice

import (
	"context"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/backend/internal/domain/blockstore"
	blockstoreinfra "github.com/anthropics/agentsmesh/backend/internal/infra/blockstore"
	"github.com/anthropics/agentsmesh/backend/internal/testkit"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// setup wires a Service over an in-memory SQLite DB and returns a ready
// workspace + root page block for each test.
func setup(t *testing.T) (*Service, ActorContext, uuid.UUID, uuid.UUID) {
	t.Helper()
	db := testkit.SetupTestDB(t)
	repo := blockstoreinfra.NewRepository(db)
	svc := NewService(repo, nil)

	actor := ActorContext{
		UserID:    100,
		OrgID:     1,
		ActorType: blockstore.ActorUser,
		ActorID:   100,
	}
	ws, err := svc.EnsureDefaultWorkspace(context.Background(), actor)
	require.NoError(t, err)
	require.NotNil(t, ws.RootBlockID)
	return svc, actor, ws.ID, *ws.RootBlockID
}

func TestApplyOps_Idempotency(t *testing.T) {
	svc, actor, wsID, rootID := setup(t)
	ctx := context.Background()

	taskID := uuid.New()
	in := ApplyOpsInput{
		WorkspaceID:    wsID.String(),
		IdempotencyKey: "idem-key-1",
		Ops: []OpEnvelope{
			{
				Op: blockstore.OpCreateBlock,
				Payload: map[string]any{
					"id":   taskID.String(),
					"type": blockstore.BlockTypeTask,
					"data": map[string]any{"title": "hello", "status": "todo"},
				},
			},
			{
				Op: blockstore.OpAddRef,
				Payload: map[string]any{
					"from": rootID.String(), "to": taskID.String(),
					"rel": blockstore.RelNest, "order_key": "a0",
				},
			},
		},
	}

	first, err := svc.ApplyOps(ctx, actor, in)
	require.NoError(t, err)
	require.False(t, first.WasReplay)
	require.Len(t, first.OpIDs, 2)

	// Second call with the same idempotency key is short-circuited and
	// returns the FULL original batch (both op_ids), not just the first.
	// This lets the client verify every op was persisted without an
	// additional /ops?parent= lookup.
	second, err := svc.ApplyOps(ctx, actor, in)
	require.NoError(t, err)
	assert.True(t, second.WasReplay, "replay flag must flip for a repeat call")
	assert.Equal(t, first.OpIDs, second.OpIDs,
		"replay must return the full op_id list, not just the first")

	// And the block should exist exactly once.
	blocks, _, err := svc.repo.ListBlocks(ctx, blockstore.BlockFilter{
		WorkspaceID: wsID,
		Type:        strPtr(blockstore.BlockTypeTask),
	})
	require.NoError(t, err)
	assert.Len(t, blocks, 1, "idempotent replay must not double-insert the block")
}

func TestApplyOps_SingleNestParent(t *testing.T) {
	svc, actor, wsID, rootID := setup(t)
	ctx := context.Background()

	// Create two potential parents and a child; nest the child under the first parent.
	parentA := uuid.New()
	parentB := uuid.New()
	child := uuid.New()
	_, err := svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "seed",
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id": parentA.String(), "type": blockstore.BlockTypePage,
				"data": map[string]any{"title": "A"},
			}},
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id": parentB.String(), "type": blockstore.BlockTypePage,
				"data": map[string]any{"title": "B"},
			}},
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id": child.String(), "type": blockstore.BlockTypeTask,
				"data": map[string]any{"title": "t"},
			}},
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": rootID.String(), "to": parentA.String(),
				"rel": blockstore.RelNest, "order_key": "a0",
			}},
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": rootID.String(), "to": parentB.String(),
				"rel": blockstore.RelNest, "order_key": "a1",
			}},
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": parentA.String(), "to": child.String(),
				"rel": blockstore.RelNest, "order_key": "a0",
			}},
		},
	})
	require.NoError(t, err)

	// Now a second nest parent (parentB) for the same child must fail.
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "second-parent",
		Ops: []OpEnvelope{
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": parentB.String(), "to": child.String(),
				"rel": blockstore.RelNest, "order_key": "a0",
			}},
		},
	})
	assert.ErrorIs(t, err, blockstore.ErrSingleNestParent)
}

func TestApplyOps_NestCycleDetection(t *testing.T) {
	svc, actor, wsID, _ := setup(t)
	ctx := context.Background()

	// Build A nest B (A has no parent; B's only parent is A). Then attempt
	// B nest A — single-parent check passes (A is free) so the cycle check
	// must fire because A is an ancestor of B via the existing A→B edge.
	a := uuid.New()
	b := uuid.New()
	_, err := svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "seed",
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id": a.String(), "type": blockstore.BlockTypePage,
				"data": map[string]any{"title": "A"},
			}},
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id": b.String(), "type": blockstore.BlockTypePage,
				"data": map[string]any{"title": "B"},
			}},
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": a.String(), "to": b.String(),
				"rel": blockstore.RelNest, "order_key": "a0",
			}},
		},
	})
	require.NoError(t, err)

	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "cycle",
		Ops: []OpEnvelope{
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": b.String(), "to": a.String(),
				"rel": blockstore.RelNest, "order_key": "a0",
			}},
		},
	})
	assert.ErrorIs(t, err, blockstore.ErrNestCycle)
}

func TestApplyOps_StaleUpdateOptimisticLock(t *testing.T) {
	svc, actor, wsID, rootID := setup(t)
	ctx := context.Background()

	target := uuid.New()
	_, err := svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "seed",
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id": target.String(), "type": blockstore.BlockTypeTask,
				"data": map[string]any{"title": "t", "status": "todo"},
			}},
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": rootID.String(), "to": target.String(),
				"rel": blockstore.RelNest, "order_key": "a0",
			}},
		},
	})
	require.NoError(t, err)

	// First successful update advances updated_at.
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "update-1",
		Ops: []OpEnvelope{
			{Op: blockstore.OpUpdateBlock, Payload: map[string]any{
				"id":   target.String(),
				"data": map[string]any{"title": "v2"},
			}},
		},
	})
	require.NoError(t, err)

	// Now pretend a stale client tries again with the original created_at timestamp.
	stale := time.Now().Add(-1 * time.Hour).UTC()
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "update-stale",
		Ops: []OpEnvelope{
			{Op: blockstore.OpUpdateBlock, Payload: map[string]any{
				"id":                  target.String(),
				"data":                map[string]any{"title": "should-not-stick"},
				"expected_updated_at": stale.Format(time.RFC3339Nano),
			}},
		},
	})
	assert.ErrorIs(t, err, blockstore.ErrStaleUpdate)

	// Confirm the stale write did NOT land.
	b, err := svc.GetBlock(ctx, actor, target)
	require.NoError(t, err)
	assert.Equal(t, "v2", b.Data["title"])
}

func strPtr(s string) *string { return &s }
