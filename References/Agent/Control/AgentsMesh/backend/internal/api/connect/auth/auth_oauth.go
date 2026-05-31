package authconnect

import (
	"context"
	"errors"
	"net/url"
	"strings"

	"connectrpc.com/connect"

	authservice "github.com/anthropics/agentsmesh/backend/internal/service/auth"
	"github.com/anthropics/agentsmesh/backend/pkg/auth/oauth"
	authv1 "github.com/anthropics/agentsmesh/proto/gen/go/auth/v1"
)

// OAuthRedirect mirrors REST GET /api/v1/auth/oauth/:provider. The REST
// handler issues an HTTP 307; Connect cannot redirect, so the response
// carries the provider's authorization URL and the SPA navigates client-side.
func (s *Server) OAuthRedirect(
	ctx context.Context, req *connect.Request[authv1.OAuthRedirectRequest],
) (*connect.Response[authv1.OAuthRedirectResponse], error) {
	provider := req.Msg.GetProvider()
	if provider == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("provider is required"))
	}

	redirectTo := req.Msg.GetRedirect()
	if redirectTo == "" {
		redirectTo = s.config.OAuth.DefaultRedirectURL
	}
	if !s.isAllowedRedirect(redirectTo) {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("invalid redirect URL"))
	}

	oauthCfg := s.getOAuthConfig(provider)
	if oauthCfg == nil {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("OAuth provider not configured"))
	}

	state, err := s.authSvc.GenerateOAuthState(ctx, provider, redirectTo)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	return connect.NewResponse(&authv1.OAuthRedirectResponse{
		AuthUrl: oauthCfg.AuthURL(state),
	}), nil
}

// OAuthCallback mirrors REST GET /api/v1/auth/oauth/:provider/callback.
// REST redirects; Connect returns the tokens + redirect path so the SPA
// finishes the navigation client-side.
func (s *Server) OAuthCallback(
	ctx context.Context, req *connect.Request[authv1.OAuthCallbackRequest],
) (*connect.Response[authv1.OAuthCallbackResponse], error) {
	provider := req.Msg.GetProvider()
	code := req.Msg.GetCode()
	state := req.Msg.GetState()
	if provider == "" || code == "" || state == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("provider, code, and state are required"))
	}

	redirectTo, err := s.authSvc.ValidateOAuthState(ctx, state)
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("invalid or expired state"))
	}

	oauthCfg := s.getOAuthConfig(provider)
	if oauthCfg == nil {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("OAuth provider not configured"))
	}

	token, err := oauthCfg.Exchange(ctx, code)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal,
			errors.New("failed to exchange OAuth code"))
	}

	userInfo, err := oauthCfg.GetUserInfo(ctx, token.AccessToken)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal,
			errors.New("failed to get user info"))
	}

	result, err := s.authSvc.OAuthLogin(ctx, &authservice.OAuthLoginRequest{
		Provider:       provider,
		ProviderUserID: userInfo.ID,
		Email:          userInfo.Email,
		Username:       userInfo.Username,
		Name:           userInfo.Name,
		AvatarURL:      userInfo.AvatarURL,
		AccessToken:    token.AccessToken,
		RefreshToken:   token.RefreshToken,
		ExpiresAt:      &token.ExpiresAt,
	})
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal,
			errors.New("OAuth authentication failed"))
	}

	return connect.NewResponse(&authv1.OAuthCallbackResponse{
		Token:        result.Token,
		RefreshToken: result.RefreshToken,
		ExpiresIn:    result.ExpiresIn,
		User:         toProtoUser(result.User),
		Redirect:     redirectTo,
	}), nil
}

// getOAuthConfig mirrors auth.go:67 — picks the OAuth provider config from
// app config. Returns nil when the provider has no client_id (unsupported
// or unconfigured).
func (s *Server) getOAuthConfig(provider string) *oauth.Config {
	switch provider {
	case "github":
		if s.config.OAuth.GitHub.ClientID == "" {
			return nil
		}
		return oauth.NewGitHubConfig(
			s.config.OAuth.GitHub.ClientID,
			s.config.OAuth.GitHub.ClientSecret,
			s.config.GitHubRedirectURL(),
		)
	case "google":
		if s.config.OAuth.Google.ClientID == "" {
			return nil
		}
		return oauth.NewGoogleConfig(
			s.config.OAuth.Google.ClientID,
			s.config.OAuth.Google.ClientSecret,
			s.config.GoogleRedirectURL(),
		)
	case "gitlab":
		if s.config.OAuth.GitLab.ClientID == "" {
			return nil
		}
		return oauth.NewGitLabConfig(
			s.config.OAuth.GitLab.ClientID,
			s.config.OAuth.GitLab.ClientSecret,
			s.config.GitLabRedirectURL(),
			s.config.OAuth.GitLab.BaseURL,
		)
	case "gitee":
		if s.config.OAuth.Gitee.ClientID == "" {
			return nil
		}
		return oauth.NewGiteeConfig(
			s.config.OAuth.Gitee.ClientID,
			s.config.OAuth.Gitee.ClientSecret,
			s.config.GiteeRedirectURL(),
		)
	}
	return nil
}

// isAllowedRedirect mirrors auth_oauth.go:49. Open-redirect prevention —
// accept relative paths, the desktop deep-link, or URLs matching the
// PrimaryDomain hostname. Port is intentionally ignored.
func (s *Server) isAllowedRedirect(redirectTo string) bool {
	if strings.HasPrefix(redirectTo, "/") && !strings.HasPrefix(redirectTo, "//") {
		return true
	}
	parsed, err := url.Parse(redirectTo)
	if err != nil {
		return false
	}
	if parsed.Scheme == "agentsmesh" {
		return parsed.Host == "oauth" && parsed.Path == "/callback"
	}
	allowedHost, _, _ := strings.Cut(s.config.PrimaryDomain, ":")
	return parsed.Hostname() == allowedHost
}
