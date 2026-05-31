package authconnect

import (
	"context"
	"errors"
	"log/slog"
	"strings"

	"connectrpc.com/connect"

	domainUser "github.com/anthropics/agentsmesh/backend/internal/domain/user"
	authservice "github.com/anthropics/agentsmesh/backend/internal/service/auth"
	authv1 "github.com/anthropics/agentsmesh/proto/gen/go/auth/v1"
)

// Login mirrors REST POST /api/v1/auth/login. Public RPC — no bearer token
// required (the caller is authenticating to obtain one).
func (s *Server) Login(
	ctx context.Context, req *connect.Request[authv1.LoginRequest],
) (*connect.Response[authv1.LoginResponse], error) {
	if req.Msg.GetEmail() == "" || req.Msg.GetPassword() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("email and password are required"))
	}
	result, err := s.authSvc.Login(ctx, req.Msg.GetEmail(), req.Msg.GetPassword())
	if err != nil {
		switch {
		case errors.Is(err, authservice.ErrInvalidCredentials):
			return nil, connect.NewError(connect.CodeUnauthenticated,
				errors.New("invalid email or password"))
		case errors.Is(err, authservice.ErrUserDisabled):
			return nil, connect.NewError(connect.CodePermissionDenied,
				errors.New("user is disabled"))
		case errors.Is(err, authservice.ErrSSOEnforced):
			return nil, connect.NewError(connect.CodePermissionDenied,
				errors.New("SSO login is required for this domain"))
		default:
			return nil, connect.NewError(connect.CodeInternal, err)
		}
	}
	return connect.NewResponse(&authv1.LoginResponse{
		Token:        result.Token,
		RefreshToken: result.RefreshToken,
		ExpiresIn:    result.ExpiresIn,
		User:         toProtoUser(result.User),
	}), nil
}

// Register mirrors REST POST /api/v1/auth/register. Public RPC — emits a
// verification email after creating the user; mailer failure is non-fatal
// (REST keeps the same contract — user receives "Please verify" but can
// retry via ResendVerification).
func (s *Server) Register(
	ctx context.Context, req *connect.Request[authv1.RegisterRequest],
) (*connect.Response[authv1.RegisterResponse], error) {
	email := req.Msg.GetEmail()
	username := req.Msg.GetUsername()
	password := req.Msg.GetPassword()
	if email == "" || username == "" || password == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("email, username, and password are required"))
	}
	if len(password) < 8 {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("password must be at least 8 characters"))
	}
	if err := domainUser.ValidateUsername(username); err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, err)
	}

	result, err := s.authSvc.Register(ctx, &authservice.RegisterRequest{
		Email:    email,
		Username: username,
		Password: password,
		Name:     req.Msg.GetName(),
	})
	if err != nil {
		switch {
		case errors.Is(err, authservice.ErrEmailExists):
			return nil, connect.NewError(connect.CodeAlreadyExists,
				errors.New("email already registered"))
		case errors.Is(err, authservice.ErrUsernameExists):
			return nil, connect.NewError(connect.CodeAlreadyExists,
				errors.New("username already taken"))
		default:
			return nil, connect.NewError(connect.CodeInternal, err)
		}
	}

	resp := &authv1.RegisterResponse{
		Token:        result.Token,
		RefreshToken: result.RefreshToken,
		ExpiresIn:    result.ExpiresIn,
		User:         toProtoUser(result.User),
	}

	verificationToken, vErr := s.userSvc.SetEmailVerificationToken(ctx, result.User.ID)
	if vErr != nil {
		// Mirror REST: registration succeeds without verification token.
		msg := "Registration successful. Please verify your email."
		resp.Message = &msg
		return connect.NewResponse(resp), nil
	}
	if mailErr := s.emailSvc.SendVerificationEmail(ctx, result.User.Email, verificationToken); mailErr != nil {
		// 邮件失败不阻塞注册 — 用户走 ResendVerification 重发，
		// 但必须落日志保持与 REST 行为一致。
		slog.ErrorContext(ctx, "failed to send verification email after registration",
			"user_id", result.User.ID, "email", result.User.Email, "error", mailErr)
	}
	msg := "Registration successful. Please check your email to verify your account."
	resp.Message = &msg
	return connect.NewResponse(resp), nil
}

// RefreshToken mirrors REST POST /api/v1/auth/refresh.
func (s *Server) RefreshToken(
	ctx context.Context, req *connect.Request[authv1.RefreshTokenRequest],
) (*connect.Response[authv1.RefreshTokenResponse], error) {
	if req.Msg.GetRefreshToken() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("refresh_token is required"))
	}
	result, err := s.authSvc.RefreshToken(ctx, req.Msg.GetRefreshToken())
	if err != nil {
		if errors.Is(err, authservice.ErrInvalidToken) ||
			errors.Is(err, authservice.ErrInvalidRefreshToken) {
			return nil, connect.NewError(connect.CodeUnauthenticated,
				errors.New("invalid refresh token"))
		}
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(&authv1.RefreshTokenResponse{
		Token:        result.Token,
		RefreshToken: result.RefreshToken,
		ExpiresIn:    result.ExpiresIn,
	}), nil
}

// Logout mirrors REST POST /api/v1/auth/logout. The Authorization header
// is mandatory (interceptor enforces it); the raw bearer token is then
// blacklisted in Redis so subsequent requests with that token fail.
func (s *SessionServer) Logout(
	ctx context.Context, req *connect.Request[authv1.LogoutRequest],
) (*connect.Response[authv1.LogoutResponse], error) {
	header := req.Header().Get("Authorization")
	parts := strings.SplitN(header, " ", 2)
	if len(parts) == 2 && parts[0] == "Bearer" && parts[1] != "" {
		// Errors from Redis are non-fatal — REST swallowed them too. The
		// JWT still expires on its own.
		_ = s.authSvc.RevokeToken(ctx, parts[1])
	}
	return connect.NewResponse(&authv1.LogoutResponse{
		Message: "Logged out successfully",
	}), nil
}
