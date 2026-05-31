package userconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	userv1 "github.com/anthropics/agentsmesh/proto/gen/go/user/v1"
)

// GetMe — REST analogue: GET /api/v1/users/me.
func (s *Server) GetMe(
	ctx context.Context, _ *connect.Request[userv1.GetMeRequest],
) (*connect.Response[userv1.User], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	u, err := s.userSvc.GetByID(ctx, userID)
	if err != nil {
		return nil, mapUserServiceError(err)
	}
	return connect.NewResponse(ToProtoUser(u)), nil
}

// UpdateMe — REST analogue: PUT /api/v1/users/me.
//
// REST treats empty strings as "no change"; proto3 `optional` lets the
// client explicitly send absent. We build the same `map[string]interface{}`
// REST uses, omitting unset fields so the update is a no-op for those
// columns.
func (s *Server) UpdateMe(
	ctx context.Context, req *connect.Request[userv1.UpdateMeRequest],
) (*connect.Response[userv1.User], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	updates := make(map[string]interface{})
	if req.Msg.Name != nil && *req.Msg.Name != "" {
		updates["name"] = *req.Msg.Name
	}
	if req.Msg.AvatarUrl != nil && *req.Msg.AvatarUrl != "" {
		updates["avatar_url"] = *req.Msg.AvatarUrl
	}
	u, err := s.userSvc.Update(ctx, userID, updates)
	if err != nil {
		return nil, mapUserServiceError(err)
	}
	return connect.NewResponse(ToProtoUser(u)), nil
}

// ChangePassword — REST analogue: POST /api/v1/users/me/password.
//
// Same semantics as REST: verify current password via Authenticate, then
// UpdatePassword. CodeUnauthenticated on bad current_password (mirrors
// REST's apierr.Unauthorized → 401).
func (s *Server) ChangePassword(
	ctx context.Context, req *connect.Request[userv1.ChangePasswordRequest],
) (*connect.Response[userv1.ChangePasswordResponse], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	if req.Msg.GetCurrentPassword() == "" || req.Msg.GetNewPassword() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("current_password and new_password are required"))
	}
	if len(req.Msg.GetNewPassword()) < 8 {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("new_password must be at least 8 characters"))
	}
	u, err := s.userSvc.GetByID(ctx, userID)
	if err != nil {
		return nil, mapUserServiceError(err)
	}
	if _, err := s.userSvc.Authenticate(ctx, u.Email, req.Msg.GetCurrentPassword()); err != nil {
		return nil, connect.NewError(connect.CodeUnauthenticated,
			errors.New("current password is incorrect"))
	}
	if err := s.userSvc.UpdatePassword(ctx, userID, req.Msg.GetNewPassword()); err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(&userv1.ChangePasswordResponse{
		Message: "Password changed successfully",
	}), nil
}
