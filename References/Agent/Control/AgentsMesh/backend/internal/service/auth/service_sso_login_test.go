package auth

import (
	"context"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/backend/internal/infra"
	userService "github.com/anthropics/agentsmesh/backend/internal/service/user"
)

func TestSSOLoginWithUserService(t *testing.T) {
	db := setupTestDB(t)
	userSvc := userService.NewService(infra.NewUserRepository(db))
	ctx := context.Background()

	cfg := &Config{
		JWTSecret:         "test-secret-key-at-least-32-bytes",
		JWTExpiration:     time.Hour,
		RefreshExpiration: time.Hour * 24 * 7,
		Issuer:            "test-issuer",
	}
	svc := NewService(cfg, userSvc)

	t.Run("creates new user via SSO", func(t *testing.T) {
		req := &SSOLoginRequest{
			ProviderName: "sso_oidc_42",
			ExternalID:   "ext_001",
			Email:        "ssouser@example.com",
			Username:     "ssouser",
			Name:         "SSO User",
			AvatarURL:    "https://idp.example.com/avatar.png",
		}

		u, tokens, err := svc.SSOLogin(ctx, req)
		if err != nil {
			t.Fatalf("SSOLogin failed: %v", err)
		}
		if u == nil {
			t.Fatal("User should not be nil")
		}
		if u.Email != "ssouser@example.com" {
			t.Errorf("Email = %s, want ssouser@example.com", u.Email)
		}
		if tokens.AccessToken == "" {
			t.Error("AccessToken should not be empty")
		}
		if tokens.RefreshToken == "" {
			t.Error("RefreshToken should not be empty")
		}
	})

	t.Run("returns existing user via SSO", func(t *testing.T) {
		req := &SSOLoginRequest{
			ProviderName: "sso_ldap_10",
			ExternalID:   "ext_exist",
			Email:        "existing-sso@example.com",
			Username:     "existingsso",
			Name:         "Existing SSO",
		}
		u1, _, _ := svc.SSOLogin(ctx, req)

		// Second SSO login returns same user
		u2, _, err := svc.SSOLogin(ctx, req)
		if err != nil {
			t.Fatalf("Second SSOLogin failed: %v", err)
		}
		if u2.ID != u1.ID {
			t.Errorf("User ID mismatch: %d != %d", u2.ID, u1.ID)
		}
	})

	t.Run("rejects disabled user", func(t *testing.T) {
		req := &SSOLoginRequest{
			ProviderName: "sso_saml_5",
			ExternalID:   "ext_disabled",
			Email:        "disabled-sso@example.com",
			Username:     "disabledsso",
			Name:         "Disabled SSO",
		}
		// Create user first
		svc.SSOLogin(ctx, req)

		// Disable the user
		db.Exec("UPDATE users SET is_active = 0 WHERE email = ?", "disabled-sso@example.com")

		_, _, err := svc.SSOLogin(ctx, req)
		if err == nil {
			t.Fatal("expected error for disabled user")
		}
		if err != ErrUserDisabled {
			t.Errorf("expected ErrUserDisabled, got %v", err)
		}
	})

	t.Run("updates last_login_at on SSO login", func(t *testing.T) {
		req := &SSOLoginRequest{
			ProviderName: "sso_oidc_99",
			ExternalID:   "ext_login_time",
			Email:        "ssologintime@example.com",
			Username:     "ssologintime",
			Name:         "SSO Login Time",
		}

		before := time.Now()
		u, _, err := svc.SSOLogin(ctx, req)
		if err != nil {
			t.Fatalf("SSOLogin failed: %v", err)
		}

		// Re-fetch from DB
		fetched, err := userSvc.GetByID(ctx, u.ID)
		if err != nil {
			t.Fatalf("GetByID failed: %v", err)
		}
		if fetched.LastLoginAt == nil {
			t.Fatal("expected LastLoginAt to be set after SSO login")
		}
		if fetched.LastLoginAt.Before(before) {
			t.Error("expected LastLoginAt to be >= time before SSO login")
		}
	})
}
