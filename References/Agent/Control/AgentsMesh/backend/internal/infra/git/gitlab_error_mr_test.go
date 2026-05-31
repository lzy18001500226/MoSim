package git

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGitLabMergeRequestHttpErrors(t *testing.T) {
	ctx := context.Background()

	t.Run("create merge request HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusUnauthorized)
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.CreateMergeRequest(ctx, &CreateMRRequest{
			ProjectID:    "owner/repo",
			Title:        "Test MR",
			SourceBranch: "feature",
			TargetBranch: "main",
		})
		if err == nil {
			t.Error("expected error for HTTP 401")
		}
	})

	t.Run("update merge request HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusNotFound)
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.UpdateMergeRequest(ctx, "owner/repo", 1, "Title", "Body")
		if err == nil {
			t.Error("expected error for HTTP 404")
		}
	})

	t.Run("close merge request HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusForbidden)
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.CloseMergeRequest(ctx, "owner/repo", 1)
		if err == nil {
			t.Error("expected error for HTTP 403")
		}
	})
}

func TestGitLabMergeRequestErrorHandling(t *testing.T) {
	ctx := context.Background()

	t.Run("get merge request invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.GetMergeRequest(ctx, "owner/repo", 1)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("list merge requests invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("not an array"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.ListMergeRequests(ctx, "owner/repo", "opened", 1, 20)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("list merge requests by branch invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("not an array"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.ListMergeRequestsByBranch(ctx, "owner/repo", "feature", "opened")
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("create merge request invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.CreateMergeRequest(ctx, &CreateMRRequest{
			ProjectID:    "owner/repo",
			Title:        "Test MR",
			SourceBranch: "feature",
			TargetBranch: "main",
		})
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("update merge request invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.UpdateMergeRequest(ctx, "owner/repo", 1, "Updated Title", "Updated Body")
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("merge merge request HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusConflict)
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.MergeMergeRequest(ctx, "owner/repo", 1)
		if err == nil {
			t.Error("expected error for HTTP 409")
		}
	})

	t.Run("close merge request invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.CloseMergeRequest(ctx, "owner/repo", 1)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})
}
