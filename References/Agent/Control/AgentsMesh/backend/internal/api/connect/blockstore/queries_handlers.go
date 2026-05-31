package blockstoreconnect

import (
	"context"
	"encoding/json"
	"errors"

	"connectrpc.com/connect"
	"github.com/google/uuid"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/domain/blockstore"
	blockstorev1 "github.com/anthropics/agentsmesh/proto/gen/go/blockstore/v1"
)

func (s *Server) GetSubtree(
	ctx context.Context, req *connect.Request[blockstorev1.GetSubtreeRequest],
) (*connect.Response[blockstorev1.ChildrenResult], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	wsID, err := uuid.Parse(req.Msg.GetWorkspaceId())
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid workspace id"))
	}
	rootID, err := uuid.Parse(req.Msg.GetRootId())
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid root id"))
	}
	maxDepth := 64
	if v := req.Msg.GetMaxDepth(); v > 0 {
		maxDepth = int(v)
	}
	actor := actorFromCtx(ctx, req)
	res, err := s.svc.ListSubtree(ctx, actor, wsID, rootID, maxDepth)
	if err != nil {
		return nil, translateErr(err)
	}
	return connect.NewResponse(childrenResultToProto(res.Blocks, res.Refs)), nil
}

func childrenResultToProto(blocks []*blockstore.Block, refs []*blockstore.BlockRef) *blockstorev1.ChildrenResult {
	out := &blockstorev1.ChildrenResult{
		Blocks: make([]*blockstorev1.Block, 0, len(blocks)),
		Refs:   make([]*blockstorev1.BlockRef, 0, len(refs)),
	}
	for _, b := range blocks {
		out.Blocks = append(out.Blocks, toProtoBlock(b))
	}
	for _, r := range refs {
		out.Refs = append(out.Refs, toProtoRef(r))
	}
	return out
}

func (s *Server) StreamOps(
	ctx context.Context, req *connect.Request[blockstorev1.StreamOpsRequest],
) (*connect.Response[blockstorev1.StreamOpsResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	wsID, err := uuid.Parse(req.Msg.GetWorkspaceId())
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid workspace id"))
	}
	after := req.Msg.GetAfter()
	limit := 200
	if v := req.Msg.GetLimit(); v > 0 {
		limit = int(v)
	}
	actor := actorFromCtx(ctx, req)
	ops, err := s.svc.StreamOps(ctx, actor, wsID, after, limit)
	if err != nil {
		return nil, translateErr(err)
	}
	items := make([]*blockstorev1.BlockOp, 0, len(ops))
	for _, op := range ops {
		items = append(items, toProtoOp(op))
	}
	return connect.NewResponse(&blockstorev1.StreamOpsResponse{
		Items:  items,
		Total:  int64(len(items)),
		Limit:  int32(limit),
		Offset: 0,
	}), nil
}

func (s *Server) ExportWorkspace(
	ctx context.Context, req *connect.Request[blockstorev1.ExportWorkspaceRequest],
) (*connect.Response[blockstorev1.ExportWorkspaceResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	wsID, err := uuid.Parse(req.Msg.GetWorkspaceId())
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid workspace id"))
	}
	actor := actorFromCtx(ctx, req)
	out, err := s.svc.ExportWorkspace(ctx, actor, wsID)
	if err != nil {
		return nil, translateErr(err)
	}
	b, err := json.Marshal(out)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(&blockstorev1.ExportWorkspaceResponse{
		ExportJson: string(b),
	}), nil
}

func (s *Server) ListTypeDefs(
	ctx context.Context, req *connect.Request[blockstorev1.ListTypeDefsRequest],
) (*connect.Response[blockstorev1.ListTypeDefsResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	wsID, err := uuid.Parse(req.Msg.GetWorkspaceId())
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid workspace id"))
	}
	actor := actorFromCtx(ctx, req)
	blocks, err := s.svc.ListTypeDefBlocks(ctx, actor, wsID)
	if err != nil {
		return nil, translateErr(err)
	}
	items := make([]*blockstorev1.Block, 0, len(blocks))
	for _, b := range blocks {
		items = append(items, toProtoBlock(b))
	}
	return connect.NewResponse(&blockstorev1.ListTypeDefsResponse{
		Items:  items,
		Total:  int64(len(items)),
		Limit:  0,
		Offset: 0,
	}), nil
}

func (s *Server) GetBlockAt(
	ctx context.Context, req *connect.Request[blockstorev1.GetBlockAtRequest],
) (*connect.Response[blockstorev1.Block], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	id, err := uuid.Parse(req.Msg.GetId())
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid block id"))
	}
	opID := req.Msg.GetOpId()
	actor := actorFromCtx(ctx, req)
	snap, err := s.svc.GetBlockAt(ctx, actor, id, opID)
	if err != nil {
		return nil, translateErr(err)
	}
	// BlockSnapshot is a time-travel projection — repacks into the proto Block
	// shape so clients have one decoder for both "live" and "snapshot" reads.
	// CreatedAt / UpdatedAt aren't tracked on the snapshot row (the op log
	// rebuilds the value-bag, not the timestamps), so we leave them blank;
	// callers reading historical snapshots use the at_op_id field of the
	// snapshot, not block timestamps.
	out := &blockstorev1.Block{
		Id:          snap.ID.String(),
		WorkspaceId: "",
		Type:        snap.Type,
		DataJson:    jsonMapToString(snap.Data),
		MetaJson:    jsonMapToString(snap.Meta),
	}
	if snap.Text != nil {
		s := *snap.Text
		out.Text = &s
	}
	if snap.Deleted {
		s := "deleted"
		out.DeletedAt = &s
	}
	return connect.NewResponse(out), nil
}
