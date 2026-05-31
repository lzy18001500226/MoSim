package auth

import (
	"testing"
	"time"
)

func TestGetOAuthURL(t *testing.T) {
	cfg := &Config{
		JWTSecret:     "test-secret",
		JWTExpiration: time.Hour,
		Issuer:        "test-issuer",
		OAuthProviders: map[string]OAuthConfig{
			"github": {
				ClientID:     "github-client-id",
				ClientSecret: "github-secret",
				RedirectURL:  "https://example.com/callback/github",
				Scopes:       []string{"user:email"},
			},
			"google": {
				ClientID:     "google-client-id",
				ClientSecret: "google-secret",
				RedirectURL:  "https://example.com/callback/google",
				Scopes:       []string{"email", "profile"},
			},
			"gitlab": {
				ClientID:     "gitlab-client-id",
				ClientSecret: "gitlab-secret",
				RedirectURL:  "https://example.com/callback/gitlab",
				Scopes:       []string{"read_user"},
			},
			"gitee": {
				ClientID:     "gitee-client-id",
				ClientSecret: "gitee-secret",
				RedirectURL:  "https://example.com/callback/gitee",
				Scopes:       []string{"user_info"},
			},
		},
	}
	svc := NewService(cfg, nil)

	tests := []struct {
		provider    string
		expectError bool
		contains    string
	}{
		{"github", false, "github.com/login/oauth/authorize"},
		{"google", false, "accounts.google.com/o/oauth2/v2/auth"},
		{"gitlab", false, "gitlab.com/oauth/authorize"},
		{"gitee", false, "gitee.com/oauth/authorize"},
		{"unsupported", true, ""},
	}

	for _, tt := range tests {
		t.Run(tt.provider, func(t *testing.T) {
			url, err := svc.GetOAuthURL(tt.provider, "test-state")
			if tt.expectError {
				if err == nil {
					t.Error("Expected error for unsupported provider")
				}
			} else {
				if err != nil {
					t.Fatalf("GetOAuthURL failed: %v", err)
				}
				if url == "" {
					t.Error("URL is empty")
				}
				if tt.contains != "" && !contains(url, tt.contains) {
					t.Errorf("URL does not contain %s: %s", tt.contains, url)
				}
			}
		})
	}
}

func TestOAuthURLHelpers(t *testing.T) {
	cfg := OAuthConfig{
		ClientID:     "test-client-id",
		ClientSecret: "test-secret",
		RedirectURL:  "https://example.com/callback",
		Scopes:       []string{"user:email"},
	}

	tests := []struct {
		name     string
		fn       func(OAuthConfig, string) string
		contains string
	}{
		{"GitHub", getGitHubAuthURL, "github.com"},
		{"Google", getGoogleAuthURL, "accounts.google.com"},
		{"GitLab", getGitLabAuthURL, "gitlab.com"},
		{"Gitee", getGiteeAuthURL, "gitee.com"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			url := tt.fn(cfg, "test-state")
			if !contains(url, tt.contains) {
				t.Errorf("URL does not contain %s: %s", tt.contains, url)
			}
			if !contains(url, "client_id=test-client-id") {
				t.Errorf("URL does not contain client_id: %s", url)
			}
			if !contains(url, "state=test-state") {
				t.Errorf("URL does not contain state: %s", url)
			}
		})
	}
}

func TestGetOAuthURLDefault(t *testing.T) {
	cfg := &Config{
		JWTSecret:     "test-secret",
		JWTExpiration: time.Hour,
		Issuer:        "test-issuer",
		OAuthProviders: map[string]OAuthConfig{
			"customauth": {
				ClientID: "custom-id",
			},
		},
	}
	svc := NewService(cfg, nil)

	// Test default case in GetOAuthURL
	t.Run("default switch case", func(t *testing.T) {
		_, err := svc.GetOAuthURL("customauth", "state")
		if err == nil {
			t.Error("Expected error for unsupported provider in switch")
		}
	})
}
