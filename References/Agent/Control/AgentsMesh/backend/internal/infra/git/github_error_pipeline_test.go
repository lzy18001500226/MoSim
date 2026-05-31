package git

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGitHubPipelineErrorHandling(t *testing.T) {
	ctx := context.Background()

	t.Run("trigger pipeline invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.TriggerPipeline(ctx, "owner/repo", &TriggerPipelineRequest{Ref: "main"})
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("get pipeline invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.GetPipeline(ctx, "owner/repo", 1001)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("list pipelines invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.ListPipelines(ctx, "owner/repo", "main", "success", 1, 20)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("cancel pipeline HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusNotFound)
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.CancelPipeline(ctx, "owner/repo", 1001)
		if err == nil {
			t.Error("expected error for HTTP 404")
		}
	})

	t.Run("retry pipeline HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusForbidden)
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.RetryPipeline(ctx, "owner/repo", 1001)
		if err == nil {
			t.Error("expected error for HTTP 403")
		}
	})
}
