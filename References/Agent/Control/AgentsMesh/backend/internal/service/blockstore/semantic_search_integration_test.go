package blockstoreservice

import (
	"context"
	"testing"

	"github.com/anthropics/agentsmesh/backend/internal/domain/blockstore"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestSemanticSearch_RanksByTextSimilarity(t *testing.T) {
	svc, actor, wsID, rootID := setup(t)
	ctx := context.Background()

	seed := func(title, summary string) {
		_, err := svc.ApplyOps(ctx, actor, ApplyOpsInput{
			WorkspaceID: wsID.String(),
			Ops: []OpEnvelope{
				{Op: blockstore.OpCreateBlock, Payload: map[string]any{
					"type": blockstore.BlockTypeParagraph,
					"data": map[string]any{"text": summary},
					"text": summary,
				}},
			},
		})
		require.NoError(t, err, "seed %q", title)
	}

	seed("api", "build a REST API with Go and gin framework")
	seed("ui", "design the mobile landing page in Figma")
	seed("deploy", "ship the Go REST server to Kubernetes with Helm")
	_ = rootID
	svc.FlushEmbeddings()

	hits, err := svc.SemanticSearch(ctx, actor, SearchInput{
		WorkspaceID: wsID,
		Query:       "go rest api server",
		TopK:        3,
	})
	require.NoError(t, err)
	require.NotEmpty(t, hits, "expected semantic hits")

	// Both Go-related blocks should outrank the Figma one on a query about
	// Go/REST. This is the minimum contract of a bag-of-words embedder.
	assert.NotContains(t, hits[0].Snippet, "Figma",
		"top hit should be topically close to query, got %q", hits[0].Snippet)
}

func TestSemanticSearch_HonorsTypeFilter(t *testing.T) {
	svc, actor, wsID, _ := setup(t)
	ctx := context.Background()

	_, err := svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"type": blockstore.BlockTypeParagraph,
				"text": "kubernetes helm chart release pipeline",
			}},
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"type": blockstore.BlockTypeTask,
				"data": map[string]any{"title": "helm release", "status": "todo"},
				"text": "kubernetes helm chart release pipeline",
			}},
		},
	})
	require.NoError(t, err)
	svc.FlushEmbeddings()

	hits, err := svc.SemanticSearch(ctx, actor, SearchInput{
		WorkspaceID: wsID,
		Query:       "kubernetes helm",
		TopK:        10,
		TypeFilter:  blockstore.BlockTypeTask,
	})
	require.NoError(t, err)
	for _, h := range hits {
		assert.Equal(t, blockstore.BlockTypeTask, h.Type,
			"type filter violated: %+v", h)
	}
}

func TestSemanticSearch_SkipsEmptyText(t *testing.T) {
	svc, actor, wsID, _ := setup(t)
	ctx := context.Background()

	// Block with no text — should not appear in results regardless of query.
	_, err := svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"type": blockstore.BlockTypeList,
				"data": map[string]any{"title": "bullet list"},
			}},
		},
	})
	require.NoError(t, err)
	svc.FlushEmbeddings()

	hits, err := svc.SemanticSearch(ctx, actor, SearchInput{
		WorkspaceID: wsID,
		Query:       "bullet list",
	})
	require.NoError(t, err)
	assert.Empty(t, hits, "empty-text block leaked into results")
}

func TestHashEmbedder_Deterministic(t *testing.T) {
	e := NewHashEmbedder(128)
	a, err := e.Embed(context.Background(), "shared vocabulary matters here")
	require.NoError(t, err)
	b, err := e.Embed(context.Background(), "shared vocabulary matters here")
	require.NoError(t, err)
	require.Equal(t, len(a), len(b))
	for i := range a {
		assert.InDelta(t, a[i], b[i], 1e-6,
			"same input produced different vectors at %d", i)
	}
}

// TestSemanticSearch_UpdateRefreshesEmbedding is the guard rail for B3: when
// an Agent rewrites a block's text via updateBlock, subsequent memory queries
// should rank the new text — not the old. This is the contract Agent memory
// relies on to "forget" stale notes once they're superseded.
func TestSemanticSearch_UpdateRefreshesEmbedding(t *testing.T) {
	svc, actor, wsID, _ := setup(t)
	ctx := context.Background()

	createRes, err := svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpCreateBlock, Payload: map[string]any{
				"type": blockstore.BlockTypeParagraph,
				"text": "initial note about rust compilers",
			}},
		},
	})
	require.NoError(t, err)
	require.NotEmpty(t, createRes.OpIDs)
	svc.FlushEmbeddings()

	// Find the new block id via a matching search.
	hits, err := svc.SemanticSearch(ctx, actor, SearchInput{
		WorkspaceID: wsID, Query: "rust compilers", TopK: 1,
	})
	require.NoError(t, err)
	require.Len(t, hits, 1)
	blockID := hits[0].BlockID

	// Rewrite the text to something topically different.
	_, err = svc.ApplyOps(ctx, actor, ApplyOpsInput{
		WorkspaceID: wsID.String(),
		Ops: []OpEnvelope{
			{Op: blockstore.OpUpdateBlock, Payload: map[string]any{
				"id":   blockID.String(),
				"text": "baking sourdough bread recipe",
			}},
		},
	})
	require.NoError(t, err)
	svc.FlushEmbeddings()

	// The old query should no longer top-rank this block strongly, and the new
	// query should.
	newHits, err := svc.SemanticSearch(ctx, actor, SearchInput{
		WorkspaceID: wsID, Query: "sourdough recipe", TopK: 1,
	})
	require.NoError(t, err)
	require.Len(t, newHits, 1)
	assert.Equal(t, blockID, newHits[0].BlockID,
		"updated block should match the new text query")
}
