package blockstoreservice

import (
	"context"
	"testing"

	"github.com/anthropics/agentsmesh/backend/internal/domain/blockstore"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestCascadeDelete_ListChildrenFiltersDeleted guards the read-path
// guarantee that a soft-deleted child block never surfaces in nest listings.
// Phase 1 keeps ref rows intact on block delete so time-travel works; the
// filter lives at query time.
func TestCascadeDelete_ListChildrenFiltersDeleted(t *testing.T) {
	svc, actor, wsID, rootID := setup(t)
	ctx := context.Background()

	child := uuid.New()
	_, err := svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id": child.String(), "type": blockstore.BlockTypeTask,
				"data": map[string]any{"title": "x", "status": "todo"},
			}},
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": rootID.String(), "to": child.String(),
				"rel": blockstore.RelNest, "order_key": "a0",
			}},
		},
	})
	require.NoError(t, err)

	// Before delete: child is visible.
	res, err := svc.ListChildren(ctx, actor, rootID, blockstore.RelNest)
	require.NoError(t, err)
	assert.Len(t, res.Blocks, 1)

	// Soft-delete the child.
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpDeleteBlock, Payload: map[string]any{"id": child.String()}},
		},
	})
	require.NoError(t, err)

	// After delete: child is invisible even though the ref row still exists.
	res, err = svc.ListChildren(ctx, actor, rootID, blockstore.RelNest)
	require.NoError(t, err)
	assert.Empty(t, res.Blocks, "deleted child must not appear in nest listing")
}

// TestCascadeDelete_BacklinksFiltersTombstonedOrigin mirrors the above for
// the ListBacklinks read path: an incoming ref from a soft-deleted block
// must not surface in the target's backlink list.
func TestCascadeDelete_BacklinksFiltersTombstonedOrigin(t *testing.T) {
	svc, actor, wsID, rootID := setup(t)
	ctx := context.Background()

	speaker := uuid.New()
	target := uuid.New()
	_, err := svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id": speaker.String(), "type": blockstore.BlockTypeParagraph,
				"text": "mentions target",
			}},
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id": target.String(), "type": blockstore.BlockTypeParagraph,
				"text": "being mentioned",
			}},
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": rootID.String(), "to": speaker.String(),
				"rel": blockstore.RelNest, "order_key": "a0",
			}},
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": rootID.String(), "to": target.String(),
				"rel": blockstore.RelNest, "order_key": "a1",
			}},
			{Op: blockstore.OpAddRef, Payload: map[string]any{
				"from": speaker.String(), "to": target.String(),
				"rel": blockstore.RelMention,
			}},
		},
	})
	require.NoError(t, err)

	// Before delete: mention surfaces.
	refs, err := svc.ListBacklinks(ctx, actor, target)
	require.NoError(t, err)
	assert.NotEmpty(t, refs, "backlinks should include the mention")

	// Soft-delete the speaker.
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpDeleteBlock, Payload: map[string]any{"id": speaker.String()}},
		},
	})
	require.NoError(t, err)

	// After delete: mention is filtered out.
	refs, err = svc.ListBacklinks(ctx, actor, target)
	require.NoError(t, err)
	for _, r := range refs {
		assert.NotEqual(t, speaker, r.FromID,
			"mention from deleted speaker must not surface in backlinks")
	}
}

// TestTimeTravel_ACLPreventsLeakingPastPublicState guards the subtle ACL +
// time-travel interaction: flipping a block to private must NOT let
// other-users time-travel back to its previous public revision.
//
// This is the "revisions snapshot ACL from the LIVE meta" invariant — any
// change that reads ACL from the reconstructed snapshot would be wrong.
func TestTimeTravel_ACLPreventsLeakingPastPublicState(t *testing.T) {
	owner := ActorContext{UserID: 100, OrgID: 1, ActorType: blockstore.ActorUser, ActorID: 100}
	otherUser := ActorContext{UserID: 101, OrgID: 1, ActorType: blockstore.ActorUser, ActorID: 101}

	svc, _, wsID, _ := setup(t)
	ctx := context.Background()

	blockID := uuid.New()
	createRes, err := svc.ApplyOps(ctx, owner, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"id": blockID.String(), "type": blockstore.BlockTypeParagraph,
				"text": "originally public",
				"meta": map[string]any{"acl": map[string]any{"visibility": "workspace"}},
			}},
		},
	})
	require.NoError(t, err)
	publicOpID := createRes.OpIDs[0]

	// While public, the other user can time-travel back to op = publicOpID.
	snap, err := svc.GetBlockAt(ctx, otherUser, blockID, publicOpID)
	require.NoError(t, err)
	assert.Equal(t, "originally public", *snap.Text)

	// Owner flips visibility to private.
	_, err = svc.ApplyOps(ctx, owner, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpUpdateBlock, Payload: map[string]any{
				"id":   blockID.String(),
				"meta": map[string]any{"acl": map[string]any{"visibility": "private"}},
			}},
		},
	})
	require.NoError(t, err)

	// Other user's time-travel to the previously-public revision must now
	// fail with a forbidden error — the live meta's ACL gates history.
	_, err = svc.GetBlockAt(ctx, otherUser, blockID, publicOpID)
	require.ErrorIs(t, err, blockstore.ErrBlockForbidden,
		"time-travel to past public state leaked after private flip")

	// Owner still reaches history.
	snap, err = svc.GetBlockAt(ctx, owner, blockID, publicOpID)
	require.NoError(t, err)
	assert.Equal(t, "originally public", *snap.Text)
}
