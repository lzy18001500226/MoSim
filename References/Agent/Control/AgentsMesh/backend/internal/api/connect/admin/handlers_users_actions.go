package adminconnect

import (
	"context"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/domain/admin"
	adminservice "github.com/anthropics/agentsmesh/backend/internal/service/admin"
	adminv1 "github.com/anthropics/agentsmesh/proto/gen/go/admin/v1"
)

func (s *Server) DisableUser(
	ctx context.Context, req *connect.Request[adminv1.DisableUserRequest],
) (*connect.Response[adminv1.AdminUser], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	userID := req.Msg.GetUserId()
	if userID == adminUser.ID {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			adminservice.ErrCannotDisableSelf)
	}

	oldUser, _ := s.svc.GetUser(ctx, userID)

	u, err := s.svc.DisableUser(ctx, userID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.svc, adminUser.ID,
		admin.AuditActionUserDisable, admin.TargetTypeUser, userID,
		oldUser, u, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(ToProtoAdminUser(u)), nil
}

func (s *Server) EnableUser(
	ctx context.Context, req *connect.Request[adminv1.EnableUserRequest],
) (*connect.Response[adminv1.AdminUser], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	userID := req.Msg.GetUserId()
	oldUser, _ := s.svc.GetUser(ctx, userID)

	u, err := s.svc.EnableUser(ctx, userID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.svc, adminUser.ID,
		admin.AuditActionUserEnable, admin.TargetTypeUser, userID,
		oldUser, u, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(ToProtoAdminUser(u)), nil
}

func (s *Server) GrantAdmin(
	ctx context.Context, req *connect.Request[adminv1.GrantAdminRequest],
) (*connect.Response[adminv1.AdminUser], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	userID := req.Msg.GetUserId()
	oldUser, _ := s.svc.GetUser(ctx, userID)

	u, err := s.svc.GrantAdmin(ctx, userID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.svc, adminUser.ID,
		admin.AuditActionUserGrantAdmin, admin.TargetTypeUser, userID,
		oldUser, u, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(ToProtoAdminUser(u)), nil
}

func (s *Server) RevokeAdmin(
	ctx context.Context, req *connect.Request[adminv1.RevokeAdminRequest],
) (*connect.Response[adminv1.AdminUser], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	userID := req.Msg.GetUserId()
	oldUser, _ := s.svc.GetUser(ctx, userID)

	u, err := s.svc.RevokeAdmin(ctx, userID, adminUser.ID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.svc, adminUser.ID,
		admin.AuditActionUserRevokeAdmin, admin.TargetTypeUser, userID,
		oldUser, u, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(ToProtoAdminUser(u)), nil
}

func (s *Server) VerifyUserEmail(
	ctx context.Context, req *connect.Request[adminv1.VerifyUserEmailRequest],
) (*connect.Response[adminv1.AdminUser], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	userID := req.Msg.GetUserId()
	oldUser, _ := s.svc.GetUser(ctx, userID)

	u, err := s.svc.VerifyUserEmail(ctx, userID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.svc, adminUser.ID,
		admin.AuditActionUserVerifyEmail, admin.TargetTypeUser, userID,
		oldUser, u, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(ToProtoAdminUser(u)), nil
}

func (s *Server) UnverifyUserEmail(
	ctx context.Context, req *connect.Request[adminv1.UnverifyUserEmailRequest],
) (*connect.Response[adminv1.AdminUser], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	userID := req.Msg.GetUserId()
	oldUser, _ := s.svc.GetUser(ctx, userID)

	u, err := s.svc.UnverifyUserEmail(ctx, userID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.svc, adminUser.ID,
		admin.AuditActionUserUnverifyEmail, admin.TargetTypeUser, userID,
		oldUser, u, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(ToProtoAdminUser(u)), nil
}
