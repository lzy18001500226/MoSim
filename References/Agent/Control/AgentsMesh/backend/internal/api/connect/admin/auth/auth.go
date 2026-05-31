// Package adminauthconnect hosts Connect-RPC handlers for the
// admin-console login flow + authenticated-session lookup.
//
// AdminAuthService.Login is PUBLIC (no auth interceptor) — the caller
// does not yet hold a bearer; the handler enforces is_system_admin +
// is_active server-side.
//
// AdminAuthSessionService.GetMe is auth-required — it lives behind the
// admin-auth interceptor pipeline (JWT + is_system_admin).
package adminauthconnect

import (
	"context"
	"errors"
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/config"
	"github.com/anthropics/agentsmesh/backend/internal/domain/user"
	"github.com/anthropics/agentsmesh/backend/internal/infra/database"
	authsvc "github.com/anthropics/agentsmesh/backend/internal/service/auth"
	"github.com/anthropics/agentsmesh/backend/pkg/protoconv"
	adminv1 "github.com/anthropics/agentsmesh/proto/gen/go/admin/v1"
)

const (
	LoginServiceName        = "proto.admin.v1.AdminAuthService"
	LoginProcedure          = "/" + LoginServiceName + "/Login"
	SessionServiceName      = "proto.admin.v1.AdminAuthSessionService"
	GetMeProcedure          = "/" + SessionServiceName + "/GetMe"
)

// authServiceInterface mirrors v1/admin/auth.go to keep the public Login
// path mockable. Same signature, same semantics.
type authServiceInterface interface {
	Login(ctx context.Context, email, password string) (*authsvc.LoginResult, error)
}

// LoginServer hosts the public Login RPC.
type LoginServer struct {
	authSvc authServiceInterface
	cfg     *config.Config
}

func NewLoginServer(authSvc *authsvc.Service, cfg *config.Config) *LoginServer {
	return &LoginServer{authSvc: authSvc, cfg: cfg}
}

// MountLogin wires AdminAuthService.Login. The caller is responsible for
// applying the PUBLIC handler options (no auth interceptor) so the
// pre-token login path can land.
func MountLogin(mux *http.ServeMux, srv *LoginServer, opts ...connect.HandlerOption) {
	mux.Handle(LoginProcedure, connect.NewUnaryHandler(LoginProcedure, srv.Login, opts...))
}

func (s *LoginServer) Login(
	ctx context.Context, req *connect.Request[adminv1.AdminLoginRequest],
) (*connect.Response[adminv1.AdminLoginResponse], error) {
	if req.Msg.GetEmail() == "" || req.Msg.GetPassword() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("email and password are required"))
	}
	result, err := s.authSvc.Login(ctx, req.Msg.GetEmail(), req.Msg.GetPassword())
	if err != nil {
		return nil, connect.NewError(connect.CodeUnauthenticated,
			errors.New("invalid email or password"))
	}
	if !result.User.IsSystemAdmin {
		return nil, connect.NewError(connect.CodePermissionDenied,
			errors.New("system administrator privileges required"))
	}
	if !result.User.IsActive {
		return nil, connect.NewError(connect.CodePermissionDenied,
			errors.New("account disabled"))
	}
	return connect.NewResponse(&adminv1.AdminLoginResponse{
		Token:        result.Token,
		RefreshToken: result.RefreshToken,
		User:         toProtoAdminUser(result.User),
	}), nil
}

// SessionServer hosts the auth-required GetMe RPC. The handler invokes
// ResolveSystemAdmin (same admin gate every other Connect admin handler
// uses) to load the admin user — keeps the auth model uniform across
// admin RPCs and removes the need for a parallel ctx-key.
type SessionServer struct {
	db database.DB
}

func NewSessionServer(db database.DB) *SessionServer { return &SessionServer{db: db} }

// MountSession wires AdminAuthSessionService.GetMe behind the auth
// interceptor (opts). ResolveSystemAdmin enforces is_system_admin +
// is_active on top of the JWT check.
func MountSession(mux *http.ServeMux, srv *SessionServer, opts ...connect.HandlerOption) {
	mux.Handle(GetMeProcedure, connect.NewUnaryHandler(GetMeProcedure, srv.GetMe, opts...))
}

func (s *SessionServer) GetMe(
	ctx context.Context, _ *connect.Request[adminv1.GetMeRequest],
) (*connect.Response[adminv1.AdminUser], error) {
	_, u, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}
	return connect.NewResponse(toProtoAdminUser(u)), nil
}

func toProtoAdminUser(u *user.User) *adminv1.AdminUser {
	if u == nil {
		return nil
	}
	out := &adminv1.AdminUser{
		Id:              u.ID,
		Email:           u.Email,
		Username:        u.Username,
		IsActive:        u.IsActive,
		IsSystemAdmin:   u.IsSystemAdmin,
		IsEmailVerified: u.IsEmailVerified,
		CreatedAt:       protoconv.RFC3339(u.CreatedAt),
		UpdatedAt:       protoconv.RFC3339(u.UpdatedAt),
	}
	if u.Name != nil {
		v := *u.Name
		out.Name = &v
	}
	if u.AvatarURL != nil {
		v := *u.AvatarURL
		out.AvatarUrl = &v
	}
	if u.LastLoginAt != nil {
		out.LastLoginAt = protoconv.RFC3339Ptr(u.LastLoginAt)
	}
	return out
}
