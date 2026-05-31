package blockstoreconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"
	"github.com/google/uuid"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	blockstorev1 "github.com/anthropics/agentsmesh/proto/gen/go/blockstore/v1"
)

func (s *Server) GetBlock(
	ctx context.Context, req *connect.Request[blockstorev1.GetBlockRequest],
) (*connect.Response[blockstorev1.Block], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	id, err := uuid.Parse(req.Msg.GetId())
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid block id"))
	}
	actor := actorFromCtx(ctx, req)
	b, err := s.svc.GetBlock(ctx, actor, id)
	if err != nil {
		return nil, translateErr(err)
	}
	return connect.NewResponse(toProtoBlock(b)), nil
}

func (s *Server) ListChildren(
	ctx context.Context, req *connect.Request[blockstorev1.ListChildrenRequest],
) (*connect.Response[blockstorev1.ChildrenResult], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	id, err := uuid.Parse(req.Msg.GetId())
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid block id"))
	}
	rel := req.Msg.GetRel()
	if rel == "" {
		rel = "nest"
	}
	actor := actorFromCtx(ctx, req)
	res, err := s.svc.ListChildren(ctx, actor, id, rel)
	if err != nil {
		return nil, translateErr(err)
	}
	return connect.NewResponse(childrenResultToProto(res.Blocks, res.Refs)), nil
}

func (s *Server) ListBacklinks(
	ctx context.Context, req *connect.Request[blockstorev1.ListBacklinksRequest],
) (*connect.Response[blockstorev1.ListBacklinksResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	id, err := uuid.Parse(req.Msg.GetId())
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid block id"))
	}
	actor := actorFromCtx(ctx, req)
	refs, err := s.svc.ListBacklinks(ctx, actor, id)
	if err != nil {
		return nil, translateErr(err)
	}
	items := make([]*blockstorev1.BlockRef, 0, len(refs))
	for _, r := range refs {
		items = append(items, toProtoRef(r))
	}
	return connect.NewResponse(&blockstorev1.ListBacklinksResponse{
		Items:  items,
		Total:  int64(len(items)),
		Limit:  0,
		Offset: 0,
	}), nil
}
