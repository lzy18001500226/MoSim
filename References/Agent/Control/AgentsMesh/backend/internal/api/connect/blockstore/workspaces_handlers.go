package blockstoreconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"
	"github.com/google/uuid"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	blockstorev1 "github.com/anthropics/agentsmesh/proto/gen/go/blockstore/v1"
)

func (s *Server) ListWorkspaces(
	ctx context.Context, req *connect.Request[blockstorev1.ListWorkspacesRequest],
) (*connect.Response[blockstorev1.ListWorkspacesResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	actor := actorFromCtx(ctx, req)
	list, err := s.svc.ListWorkspaces(ctx, actor)
	if err != nil {
		return nil, translateErr(err)
	}
	items := make([]*blockstorev1.Workspace, 0, len(list))
	for _, w := range list {
		items = append(items, toProtoWorkspaceView(w))
	}
	return connect.NewResponse(&blockstorev1.ListWorkspacesResponse{
		Items: items,
		Total: int64(len(items)),
		Limit: 0,
		Offset: 0,
	}), nil
}

func (s *Server) EnsureDefaultWorkspace(
	ctx context.Context, req *connect.Request[blockstorev1.EnsureDefaultWorkspaceRequest],
) (*connect.Response[blockstorev1.Workspace], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	actor := actorFromCtx(ctx, req)
	ws, err := s.svc.EnsureDefaultWorkspace(ctx, actor)
	if err != nil {
		return nil, translateErr(err)
	}
	return connect.NewResponse(toProtoWorkspaceView(ws)), nil
}

func (s *Server) CreateWorkspace(
	ctx context.Context, req *connect.Request[blockstorev1.CreateWorkspaceRequest],
) (*connect.Response[blockstorev1.Workspace], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if req.Msg.GetSlug() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("slug is required"))
	}
	actor := actorFromCtx(ctx, req)
	name := req.Msg.GetName()
	ws, err := s.svc.CreateWorkspace(ctx, actor, req.Msg.GetSlug(), name)
	if err != nil {
		return nil, translateErr(err)
	}
	return connect.NewResponse(toProtoWorkspaceView(ws)), nil
}

func (s *Server) DeleteWorkspace(
	ctx context.Context, req *connect.Request[blockstorev1.DeleteWorkspaceRequest],
) (*connect.Response[blockstorev1.DeleteWorkspaceResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	wsID, err := uuid.Parse(req.Msg.GetWorkspaceId())
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid workspace id"))
	}
	actor := actorFromCtx(ctx, req)
	if err := s.svc.DeleteWorkspace(ctx, actor, wsID); err != nil {
		return nil, translateErr(err)
	}
	return connect.NewResponse(&blockstorev1.DeleteWorkspaceResponse{}), nil
}
