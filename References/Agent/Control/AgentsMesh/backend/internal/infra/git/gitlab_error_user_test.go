package git

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGitLabDoRequestErrors(t *testing.T) {
	ctx := context.Background()

	t.Run("http client error", func(t *testing.T) {
		provider, _ := NewGitLabProvider("http://invalid-host-that-does-not-exist:99999", "test-token")
		_, err := provider.GetCurrentUser(ctx)
		if err == nil {
			t.Error("expected error for invalid host")
		}
	})
}

func TestGitLabErrorHandling_User(t *testing.T) {
	ctx := context.Background()

	t.Run("get current user HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusInternalServerError)
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
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

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.GetCurrentUser(ctx)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})
}
