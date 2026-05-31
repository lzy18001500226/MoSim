package adminconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/domain/admin"
	domainUser "github.com/anthropics/agentsmesh/backend/internal/domain/user"
	adminservice "github.com/anthropics/agentsmesh/backend/internal/service/admin"
	adminv1 "github.com/anthropics/agentsmesh/proto/gen/go/admin/v1"
)

func (s *Server) ListUsers(
	ctx context.Context, req *connect.Request[adminv1.ListUsersRequest],
) (*connect.Response[adminv1.ListUsersResponse], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	query := &adminservice.UserListQuery{
		Search:   req.Msg.GetSearch(),
		Page:     int(req.Msg.GetPage()),
		PageSize: int(req.Msg.GetPageSize()),
	}
	if req.Msg.IsActive != nil {
		v := req.Msg.GetIsActive()
		query.IsActive = &v
	}
	if req.Msg.IsAdmin != nil {
		v := req.Msg.GetIsAdmin()
		query.IsAdmin = &v
	}

	result, err := s.svc.ListUsers(ctx, query)
	if err != nil {
		return nil, mapServiceError(err)
	}

	items := make([]*adminv1.AdminUser, 0, len(result.Data))
	for i := range result.Data {
		items = append(items, ToProtoAdminUser(&result.Data[i]))
	}
	return connect.NewResponse(&adminv1.ListUsersResponse{
		Items:      items,
		Total:      result.Total,
		Page:       int32(result.Page),
		PageSize:   int32(result.PageSize),
		TotalPages: int32(result.TotalPages),
	}), nil
}

func (s *Server) GetUser(
	ctx context.Context, req *connect.Request[adminv1.GetUserRequest],
) (*connect.Response[adminv1.AdminUser], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	userID := req.Msg.GetUserId()
	u, err := s.svc.GetUser(ctx, userID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.svc, adminUser.ID,
		admin.AuditActionUserView, admin.TargetTypeUser, userID,
		nil, nil, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(ToProtoAdminUser(u)), nil
}

func (s *Server) UpdateUser(
	ctx context.Context, req *connect.Request[adminv1.UpdateUserRequest],
) (*connect.Response[adminv1.AdminUser], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	userID := req.Msg.GetUserId()

	updates := make(map[string]interface{})
	if req.Msg.Name != nil {
		updates["name"] = req.Msg.GetName()
	}
	if req.Msg.Username != nil {
		username := req.Msg.GetUsername()
		if err := domainUser.ValidateUsername(username); err != nil {
			return nil, connect.NewError(connect.CodeInvalidArgument, err)
		}
		updates["username"] = username
	}
	if req.Msg.Email != nil {
		updates["email"] = req.Msg.GetEmail()
	}

	if len(updates) == 0 {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("no updates provided"))
	}

	oldUser, _ := s.svc.GetUser(ctx, userID)

	u, err := s.svc.UpdateUser(ctx, userID, updates)
	if err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.svc, adminUser.ID,
		admin.AuditActionUserUpdate, admin.TargetTypeUser, userID,
		oldUser, u, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(ToProtoAdminUser(u)), nil
}
