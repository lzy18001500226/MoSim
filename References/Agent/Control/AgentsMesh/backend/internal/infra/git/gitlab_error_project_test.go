package git

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGitLabErrorHandling_Project(t *testing.T) {
	ctx := context.Background()

	t.Run("get project HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusNotFound)
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
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

		provider, _ := NewGitLabProvider(server.URL, "test-token")
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

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.ListProjects(ctx, 1, 20)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("search projects invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("not an array"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.SearchProjects(ctx, "test", 1, 20)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})
}
