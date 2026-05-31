package git

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGitHubDoRequestErrors(t *testing.T) {
	ctx := context.Background()

	t.Run("http client error", func(t *testing.T) {
		// Use invalid URL to trigger HTTP client error
		provider, _ := NewGitHubProvider("http://invalid-host-that-does-not-exist:99999", "test-token")
		_, err := provider.GetCurrentUser(ctx)
		if err == nil {
			t.Error("expected error for invalid host")
		}
	})
}

func TestGitHubErrorHandling(t *testing.T) {
	ctx := context.Background()

	t.Run("get current user HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusInternalServerError)
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.GetCurrentUser(ctx)
		if err == nil {
			t.Error("expected error for HTTP 500")
		}
	})

	t.Run("get current user invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("invalid json"))
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.GetCurrentUser(ctx)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("get project HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusNotFound)
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.GetProject(ctx, "owner/repo")
		if err == nil {
			t.Error("expected error for HTTP 404")
		}
	})

	t.Run("get project invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.GetProject(ctx, "owner/repo")
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("list projects invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("not an array"))
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.ListProjects(ctx, 1, 20)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("search projects invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.SearchProjects(ctx, "test", 1, 20)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("list branches invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("not an array"))
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.ListBranches(ctx, "owner/repo")
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("get branch invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.GetBranch(ctx, "owner/repo", "main")
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("create branch HTTP error on ref GET", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusNotFound)
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.CreateBranch(ctx, "owner/repo", "feature", "main")
		if err == nil {
			t.Error("expected error for HTTP 404")
		}
	})

	t.Run("delete branch HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusForbidden)
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		err := provider.DeleteBranch(ctx, "owner/repo", "protected-branch")
		if err == nil {
			t.Error("expected error for HTTP 403")
		}
	})

	t.Run("get commit invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.GetCommit(ctx, "owner/repo", "abc123")
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("list commits invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("not an array"))
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.ListCommits(ctx, "owner/repo", "main", 1, 20)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("get file content invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.GetFileContent(ctx, "owner/repo", "README.md", "main")
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("register webhook invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.RegisterWebhook(ctx, "owner/repo", &WebhookConfig{
			URL:    "https://example.com/webhook",
			Secret: "secret",
			Events: []string{"push"},
		})
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("delete webhook HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusNotFound)
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		err := provider.DeleteWebhook(ctx, "owner/repo", "12345")
		if err == nil {
			t.Error("expected error for HTTP 404")
		}
	})
}
