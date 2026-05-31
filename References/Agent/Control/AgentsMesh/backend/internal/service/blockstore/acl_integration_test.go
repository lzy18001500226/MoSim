package blockstoreservice

import (
	"context"
	"testing"

	"github.com/anthropics/agentsmesh/backend/internal/domain/blockstore"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestBlockACL_PrivateVisibility covers Phase 3.3:
//   - visibility=private blocks are readable only by creator + allowed_users
//   - updateBlock + deleteBlock fail with ErrBlockForbidden for outsiders
//   - granting access via allowed_users unlocks the block mid-flight
func TestBlockACL_PrivateVisibility(t *testing.T) {
	svc, creator, wsID, rootID := setup(t)
	ctx := context.Background()

	// userB is another member of the same org.
	other := creator
	other.UserID = 200
	other.ActorID = 200

	// Creator writes a private block.
	secret := uuid.New()
	_, err := svc.ApplyOps(ctx, creator, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "mk-secret",
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id":   secret.String(),
				"type": blockstore.BlockTypeParagraph,
				"data": map[string]any{"text": "shh"},
				"meta": map[string]any{
					"acl": map[string]any{
						"visibility":    "private",
						"allowed_users": []int64{},
					},
				},
			}},
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": rootID.String(), "to": secret.String(),
				"rel": blockstore.RelNest, "order_key": "a0",
			}},
		},
	})
	require.NoError(t, err)

	// Outsider cannot read.
	_, err = svc.GetBlock(ctx, other, secret)
	assert.ErrorIs(t, err, blockstore.ErrBlockForbidden)

	// Outsider cannot update or delete.
	_, err = svc.ApplyOps(ctx, other, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "other-tries-update",
		Ops: []OpEnvelope{
			{Op: blockstore.OpUpdateBlock, Payload: map[string]any{
				"id":   secret.String(),
				"data": map[string]any{"text": "leaked"},
			}},
		},
	})
	assert.ErrorIs(t, err, blockstore.ErrBlockForbidden)

	_, err = svc.ApplyOps(ctx, other, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "other-tries-delete",
		Ops: []OpEnvelope{
			{Op: blockstore.OpDeleteBlock, Payload: map[string]any{
				"id": secret.String(),
			}},
		},
	})
	assert.ErrorIs(t, err, blockstore.ErrBlockForbidden)

	// Creator can still read + update.
	got, err := svc.GetBlock(ctx, creator, secret)
	require.NoError(t, err)
	assert.Equal(t, "shh", got.Data["text"])

	// Creator grants access to userB.
	_, err = svc.ApplyOps(ctx, creator, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "grant-other",
		Ops: []OpEnvelope{
			{Op: blockstore.OpUpdateBlock, Payload: map[string]any{
				"id": secret.String(),
				"meta": map[string]any{
					"acl": map[string]any{
						"visibility":    "private",
						"allowed_users": []int64{other.UserID},
					},
				},
			}},
		},
	})
	require.NoError(t, err)

	// userB can now read.
	got, err = svc.GetBlock(ctx, other, secret)
	require.NoError(t, err)
	assert.Equal(t, "shh", got.Data["text"])
}

// TestBlockACL_ListFiltersPrivate verifies ListChildren / ListSubtree hide
// private blocks the caller can't see, and that orphaned refs to hidden
// blocks are dropped so the UI doesn't render gaps.
func TestBlockACL_ListFiltersPrivate(t *testing.T) {
	svc, creator, wsID, rootID := setup(t)
	ctx := context.Background()

	other := creator
	other.UserID = 200
	other.ActorID = 200

	publicID := uuid.New()
	privateID := uuid.New()
	_, err := svc.ApplyOps(ctx, creator, ApplyOpsInput{
		WorkspaceID: wsID.String(), IdempotencyKey: "mk-both",
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id": publicID.String(), "type": blockstore.BlockTypeParagraph,
				"data": map[string]any{"text": "public"},
			}},
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": rootID.String(), "to": publicID.String(),
				"rel": blockstore.RelNest, "order_key": "a0",
			}},
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id": privateID.String(), "type": blockstore.BlockTypeParagraph,
				"data": map[string]any{"text": "secret"},
				"meta": map[string]any{
					"acl": map[string]any{"visibility": "private"},
				},
			}},
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": rootID.String(), "to": privateID.String(),
				"rel": blockstore.RelNest, "order_key": "a1",
			}},
		},
	})
	require.NoError(t, err)

	// Creator sees both children.
	mine, err := svc.ListChildren(ctx, creator, rootID, blockstore.RelNest)
	require.NoError(t, err)
	assert.Len(t, mine.Blocks, 2, "creator sees all siblings")

	// Outsider sees only the public one.
	theirs, err := svc.ListChildren(ctx, other, rootID, blockstore.RelNest)
	require.NoError(t, err)
	require.Len(t, theirs.Blocks, 1, "outsider must only see public block")
	assert.Equal(t, publicID, theirs.Blocks[0].ID)
	// The dangling ref to the private block must be dropped too.
	for _, r := range theirs.Refs {
		assert.NotEqual(t, privateID, r.ToID, "ref to private block must be filtered out")
	}
}
