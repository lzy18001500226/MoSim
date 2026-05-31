package git

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGitLabErrorHandling_Commit(t *testing.T) {
	ctx := context.Background()

	t.Run("get commit invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
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

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.ListCommits(ctx, "owner/repo", "main", 1, 20)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("get file content HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusNotFound)
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.GetFileContent(ctx, "owner/repo", "README.md", "main")
		if err == nil {
			t.Error("expected error for HTTP 404")
		}
	})

	t.Run("register webhook invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.RegisterWebhook(ctx, "owner/repo", &WebhookConfig{
			URL:    "https://example.com/webhook",
			Secret: "secret",
			Events: []string{"push_events"},
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

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		err := provider.DeleteWebhook(ctx, "owner/repo", "12345")
		if err == nil {
			t.Error("expected error for HTTP 404")
		}
	})
}
