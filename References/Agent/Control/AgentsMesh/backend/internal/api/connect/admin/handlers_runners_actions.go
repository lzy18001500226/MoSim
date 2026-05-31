package adminconnect

import (
	"context"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/domain/admin"
	adminv1 "github.com/anthropics/agentsmesh/proto/gen/go/admin/v1"
)

func (s *Server) DisableRunner(
	ctx context.Context, req *connect.Request[adminv1.DisableRunnerRequest],
) (*connect.Response[adminv1.AdminRunner], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	runnerID := req.Msg.GetRunnerId()
	oldRunner, _ := s.svc.GetRunner(ctx, runnerID)

	r, err := s.svc.DisableRunner(ctx, runnerID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.svc, adminUser.ID,
		admin.AuditActionRunnerDisable, admin.TargetTypeRunner, runnerID,
		oldRunner, r, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(toProtoAdminRunner(r, nil)), nil
}

func (s *Server) EnableRunner(
	ctx context.Context, req *connect.Request[adminv1.EnableRunnerRequest],
) (*connect.Response[adminv1.AdminRunner], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	runnerID := req.Msg.GetRunnerId()
	oldRunner, _ := s.svc.GetRunner(ctx, runnerID)

	r, err := s.svc.EnableRunner(ctx, runnerID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.svc, adminUser.ID,
		admin.AuditActionRunnerEnable, admin.TargetTypeRunner, runnerID,
		oldRunner, r, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(toProtoAdminRunner(r, nil)), nil
}

func (s *Server) DeleteRunner(
	ctx context.Context, req *connect.Request[adminv1.DeleteRunnerRequest],
) (*connect.Response[adminv1.DeleteRunnerResponse], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	runnerID := req.Msg.GetRunnerId()
	deleted, err := s.svc.DeleteRunner(ctx, runnerID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.svc, adminUser.ID,
		admin.AuditActionRunnerDelete, admin.TargetTypeRunner, runnerID,
		deleted, nil, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(&adminv1.DeleteRunnerResponse{
		Message: "Runner deleted successfully",
	}), nil
}
