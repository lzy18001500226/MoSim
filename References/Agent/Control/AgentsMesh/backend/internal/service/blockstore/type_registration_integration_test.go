package blockstoreservice

import (
	"context"
	"testing"

	"github.com/anthropics/agentsmesh/backend/internal/domain/blockstore"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestDynamicTypeRegistration_Revisions exercises the Phase 3.1/3.2 story:
// new block types can be defined at runtime by writing a block_type_def block,
// a later revision overrides the earlier, and ApplyOps validates new writes
// against the highest revision.
func TestDynamicTypeRegistration_Revisions(t *testing.T) {
	svc, actor, wsID, rootID := setup(t)
	ctx := context.Background()

	// Step 1 — Register a custom type "note" requiring data.title.
	defV1 := uuid.New()
	_, err := svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "define-note-v1",
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id":   defV1.String(),
				"type": blockstore.BlockTypeTypeDef,
				"data": map[string]any{
					"type_key":          "note",
					"revision":          1,
					"default_view":      "list",
					"required_data_key": []string{"title"},
					"allowed_children":  []string{"paragraph"},
				},
			}},
		},
	})
	require.NoError(t, err, "registering a new type must succeed")

	// Step 2 — Good create: title present.
	noteA := uuid.New()
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "note-a",
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id":   noteA.String(),
				"type": "note",
				"data": map[string]any{"title": "first note"},
			}},
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": rootID.String(), "to": noteA.String(),
				"rel": blockstore.RelNest, "order_key": "a0",
			}},
		},
	})
	require.NoError(t, err)

	// Step 3 — Bad create: title missing; must hit ErrMissingRequiredKey.
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "note-bad",
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"type": "note",
				"data": map[string]any{},
			}},
		},
	})
	assert.ErrorIs(t, err, blockstore.ErrMissingRequiredKey)

	// Step 4 — Revision 2 changes the requirement from "title" to "content".
	defV2 := uuid.New()
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "define-note-v2",
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id":   defV2.String(),
				"type": blockstore.BlockTypeTypeDef,
				"data": map[string]any{
					"type_key":          "note",
					"revision":          2,
					"required_data_key": []string{"content"},
				},
			}},
		},
	})
	require.NoError(t, err)

	// Step 5 — Old shape (title only) now fails: v2 requires "content".
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "note-c-old-shape",
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"type": "note",
				"data": map[string]any{"title": "stale"},
			}},
		},
	})
	assert.ErrorIs(t, err, blockstore.ErrMissingRequiredKey)

	// Step 6 — New shape succeeds.
	noteC := uuid.New()
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "note-c-new-shape",
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id":   noteC.String(),
				"type": "note",
				"data": map[string]any{"content": "hello"},
			}},
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": rootID.String(), "to": noteC.String(),
				"rel": blockstore.RelNest, "order_key": "a1",
			}},
		},
	})
	require.NoError(t, err)

	// Step 7 — Old "note" block (noteA, from before the revision bump) is
	// still in the DB untouched. Backwards compatibility is "best-effort"
	// by design: we do not retro-validate old rows.
	existing, err := svc.GetBlock(ctx, actor, noteA)
	require.NoError(t, err)
	assert.Equal(t, "first note", existing.Data["title"])

	// Step 8 — ListRegisteredTypes exposes the new type with its latest spec.
	types, err := svc.ListRegisteredTypes(ctx, actor, wsID)
	require.NoError(t, err)
	var noteSpec *blockstore.BlockTypeSpec
	for i := range types {
		if types[i].Type == "note" {
			noteSpec = &types[i]
			break
		}
	}
	require.NotNil(t, noteSpec, "note type must appear in the workspace type list")
	assert.Equal(t, 2, noteSpec.Revision)
	assert.Equal(t, []string{"content"}, noteSpec.RequiredDataKey)
}
