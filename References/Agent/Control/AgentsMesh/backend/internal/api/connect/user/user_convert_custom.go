package userconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	domainuser "github.com/anthropics/agentsmesh/backend/internal/domain/user"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	userservice "github.com/anthropics/agentsmesh/backend/internal/service/user"
	"github.com/anthropics/agentsmesh/backend/pkg/protoconv"
	userv1 "github.com/anthropics/agentsmesh/proto/gen/go/user/v1"
)

// requireUserID is the user-scoped equivalent of interceptors.ResolveOrgScope.
// Returns CodeUnauthenticated if the auth interceptor didn't populate UserID
// — mirrors what AuthMiddleware does for REST and matches conventions §3.5.
func requireUserID(ctx context.Context) (int64, error) {
	tenant := middleware.GetTenant(ctx)
	if tenant == nil || tenant.UserID == 0 {
		return 0, connect.NewError(connect.CodeUnauthenticated, errors.New("authentication required"))
	}
	return tenant.UserID, nil
}

// toProtoUserSummary stays handwritten — UserSummary is a wire-only summary
// type with no domain counterpart (synthesised from User), so the codegen
// pipeline (which requires a go_domain annotation) skips it by design.
func toProtoUserSummary(u *domainuser.User) *userv1.UserSummary {
	if u == nil {
		return nil
	}
	return &userv1.UserSummary{
		Id:        u.ID,
		Email:     u.Email,
		Username:  u.Username,
		Name:      protoconv.StringPtr(u.Name),
		AvatarUrl: protoconv.StringPtr(u.AvatarURL),
	}
}

// mapUserServiceError translates user-service sentinels to Connect codes
// per conventions §10.
func mapUserServiceError(err error) error {
	switch {
	case errors.Is(err, userservice.ErrUserNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	case errors.Is(err, userservice.ErrEmailAlreadyExists),
		errors.Is(err, userservice.ErrUsernameExists):
		return connect.NewError(connect.CodeAlreadyExists, err)
	case errors.Is(err, userservice.ErrInvalidCredentials):
		return connect.NewError(connect.CodeUnauthenticated, err)
	case errors.Is(err, userservice.ErrUserInactive):
		return connect.NewError(connect.CodePermissionDenied, err)
	default:
		return connect.NewError(connect.CodeInternal, err)
	}
}
