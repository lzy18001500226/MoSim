package blockstoreconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"
	"github.com/google/uuid"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	blockstoreservice "github.com/anthropics/agentsmesh/backend/internal/service/blockstore"
	blockstorev1 "github.com/anthropics/agentsmesh/proto/gen/go/blockstore/v1"
)

func (s *Server) SemanticSearch(
	ctx context.Context, req *connect.Request[blockstorev1.SemanticSearchRequest],
) (*connect.Response[blockstorev1.SemanticSearchResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	wsID, err := uuid.Parse(req.Msg.GetWorkspaceId())
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid workspace id"))
	}
	actor := actorFromCtx(ctx, req)

	in := blockstoreservice.SearchInput{
		WorkspaceID: wsID,
		Query:       req.Msg.GetQuery(),
		TopK:        int(req.Msg.GetTopK()),
		MinScore:    req.Msg.GetMinScore(),
		TypeFilter:  req.Msg.GetType(),
	}
	hits, err := s.svc.SemanticSearch(ctx, actor, in)
	if err != nil {
		return nil, translateErr(err)
	}
	return connect.NewResponse(&blockstorev1.SemanticSearchResponse{
		Hits: searchHitsToProto(hits),
	}), nil
}

func (s *Server) MemoryRetrieve(
	ctx context.Context, req *connect.Request[blockstorev1.MemoryRetrieveRequest],
) (*connect.Response[blockstorev1.MemoryRetrieveResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	wsID, err := uuid.Parse(req.Msg.GetWorkspaceId())
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid workspace id"))
	}
	k := int(req.Msg.GetK())
	if k <= 0 {
		k = 5
	}
	actor := actorFromCtx(ctx, req)
	in := blockstoreservice.SearchInput{
		WorkspaceID: wsID,
		Query:       req.Msg.GetQuery(),
		TopK:        k,
	}
	hits, err := s.svc.SemanticSearch(ctx, actor, in)
	if err != nil {
		return nil, translateErr(err)
	}
	return connect.NewResponse(&blockstorev1.MemoryRetrieveResponse{
		Memories: searchHitsToProto(hits),
	}), nil
}

func searchHitsToProto(hits []blockstoreservice.SearchHit) []*blockstorev1.SearchHit {
	out := make([]*blockstorev1.SearchHit, 0, len(hits))
	for _, h := range hits {
		out = append(out, &blockstorev1.SearchHit{
			BlockId: h.BlockID.String(),
			Type:    h.Type,
			Snippet: h.Snippet,
			Score:   h.Score,
		})
	}
	return out
}
