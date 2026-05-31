package authconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	userservice "github.com/anthropics/agentsmesh/backend/internal/service/user"
	authv1 "github.com/anthropics/agentsmesh/proto/gen/go/auth/v1"
)

// VerifyEmail mirrors REST POST /api/v1/auth/verify-email. After verification
// fresh tokens are minted so the SPA can transition to authenticated state
// without a separate Login round-trip.
func (s *Server) VerifyEmail(
	ctx context.Context, req *connect.Request[authv1.VerifyEmailRequest],
) (*connect.Response[authv1.VerifyEmailResponse], error) {
	if req.Msg.GetToken() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("token is required"))
	}
	verifiedUser, err := s.userSvc.VerifyEmail(ctx, req.Msg.GetToken())
	if err != nil {
		switch {
		case errors.Is(err, userservice.ErrInvalidVerificationToken):
			return nil, connect.NewError(connect.CodeInvalidArgument,
				errors.New("invalid or expired verification token"))
		case errors.Is(err, userservice.ErrEmailAlreadyVerified):
			return nil, connect.NewError(connect.CodeAlreadyExists,
				errors.New("email already verified"))
		default:
			return nil, connect.NewError(connect.CodeInternal, err)
		}
	}

	result, err := s.authSvc.GenerateTokens(ctx, verifiedUser)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	// Force is_email_verified=true on response — REST hard-codes the same
	// because the verifiedUser snapshot may not have been re-read post-update.
	verified := true
	pUser := toProtoUser(verifiedUser)
	if pUser != nil {
		pUser.IsEmailVerified = &verified
	}

	return connect.NewResponse(&authv1.VerifyEmailResponse{
		Token:        result.Token,
		RefreshToken: result.RefreshToken,
		ExpiresIn:    result.ExpiresIn,
		User:         pUser,
		Message:      "Email verified successfully",
	}), nil
}

// ResendVerification mirrors REST POST /api/v1/auth/resend-verification.
// Mirrors the security posture: never reveal whether an email exists in the
// database. The response message is constant regardless of lookup outcome.
func (s *Server) ResendVerification(
	ctx context.Context, req *connect.Request[authv1.ResendVerificationRequest],
) (*connect.Response[authv1.ResendVerificationResponse], error) {
	if req.Msg.GetEmail() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("email is required"))
	}

	const successMsg = "If the email exists, a verification link will be sent"

	u, err := s.userSvc.GetByEmail(ctx, req.Msg.GetEmail())
	if err != nil {
		return connect.NewResponse(&authv1.ResendVerificationResponse{
			Message: successMsg,
		}), nil
	}

	if u.IsEmailVerified {
		return nil, connect.NewError(connect.CodeAlreadyExists,
			errors.New("email already verified"))
	}

	token, err := s.userSvc.SetEmailVerificationToken(ctx, u.ID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal,
			errors.New("failed to generate verification token"))
	}
	if err := s.emailSvc.SendVerificationEmail(ctx, u.Email, token); err != nil {
		return nil, connect.NewError(connect.CodeInternal,
			errors.New("failed to send verification email"))
	}

	return connect.NewResponse(&authv1.ResendVerificationResponse{
		Message: "Verification email sent",
	}), nil
}

// ForgotPassword mirrors REST POST /api/v1/auth/forgot-password. Constant
// response regardless of email existence (don't reveal account discovery).
// Mail-send failure DOES return an error here — REST surfaces it the same way.
func (s *Server) ForgotPassword(
	ctx context.Context, req *connect.Request[authv1.ForgotPasswordRequest],
) (*connect.Response[authv1.ForgotPasswordResponse], error) {
	if req.Msg.GetEmail() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("email is required"))
	}

	const successMsg = "If the email exists, a password reset link will be sent"

	token, u, err := s.userSvc.SetPasswordResetToken(ctx, req.Msg.GetEmail())
	if err != nil {
		// Don't reveal email existence — return success message anyway.
		return connect.NewResponse(&authv1.ForgotPasswordResponse{
			Message: successMsg,
		}), nil
	}

	if err := s.emailSvc.SendPasswordResetEmail(ctx, u.Email, token); err != nil {
		return nil, connect.NewError(connect.CodeInternal,
			errors.New("failed to send password reset email"))
	}

	return connect.NewResponse(&authv1.ForgotPasswordResponse{
		Message: successMsg,
	}), nil
}

// ResetPassword mirrors REST POST /api/v1/auth/reset-password.
func (s *Server) ResetPassword(
	ctx context.Context, req *connect.Request[authv1.ResetPasswordRequest],
) (*connect.Response[authv1.ResetPasswordResponse], error) {
	if req.Msg.GetToken() == "" || req.Msg.GetNewPassword() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("token and new_password are required"))
	}
	if len(req.Msg.GetNewPassword()) < 8 {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("password must be at least 8 characters"))
	}

	if _, err := s.userSvc.ResetPassword(ctx, req.Msg.GetToken(), req.Msg.GetNewPassword()); err != nil {
		if errors.Is(err, userservice.ErrInvalidResetToken) {
			return nil, connect.NewError(connect.CodeInvalidArgument,
				errors.New("invalid or expired reset token"))
		}
		return nil, connect.NewError(connect.CodeInternal,
			errors.New("failed to reset password"))
	}

	return connect.NewResponse(&authv1.ResetPasswordResponse{
		Message: "Password reset successfully",
	}), nil
}
