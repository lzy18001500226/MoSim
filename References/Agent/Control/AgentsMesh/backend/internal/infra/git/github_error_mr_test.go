package git

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestGitHubMergeRequestStateMapping(t *testing.T) {
	ctx := context.Background()

	t.Run("list merge requests by branch with merged state", func(t *testing.T) {
		server, provider := setupGitHubMockServer(t, func(w http.ResponseWriter, r *http.Request) {
			if r.URL.Query().Get("state") != "closed" {
				t.Errorf("unexpected state: %s", r.URL.Query().Get("state"))
			}
			json.NewEncoder(w).Encode([]map[string]interface{}{})
		})
		defer server.Close()

		_, err := provider.ListMergeRequestsByBranch(ctx, "owner/repo", "feature", "merged")
		if err != nil {
			t.Fatalf("ListMergeRequestsByBranch failed: %v", err)
		}
	})

	t.Run("list merge requests by branch with closed state", func(t *testing.T) {
		server, provider := setupGitHubMockServer(t, func(w http.ResponseWriter, r *http.Request) {
			if r.URL.Query().Get("state") != "closed" {
				t.Errorf("unexpected state: %s", r.URL.Query().Get("state"))
			}
			json.NewEncoder(w).Encode([]map[string]interface{}{})
		})
		defer server.Close()

		_, err := provider.ListMergeRequestsByBranch(ctx, "owner/repo", "feature", "closed")
		if err != nil {
			t.Fatalf("ListMergeRequestsByBranch failed: %v", err)
		}
	})

	t.Run("list merge requests by branch with all state", func(t *testing.T) {
		server, provider := setupGitHubMockServer(t, func(w http.ResponseWriter, r *http.Request) {
			if r.URL.Query().Get("state") != "all" {
				t.Errorf("unexpected state: %s, want all", r.URL.Query().Get("state"))
			}
			json.NewEncoder(w).Encode([]map[string]interface{}{})
		})
		defer server.Close()

		_, err := provider.ListMergeRequestsByBranch(ctx, "owner/repo", "feature", "all")
		if err != nil {
			t.Fatalf("ListMergeRequestsByBranch failed: %v", err)
		}
	})

	t.Run("get merge request with merged_at field", func(t *testing.T) {
		mergedAt := time.Now().Add(-1 * time.Hour)
		server, provider := setupGitHubMockServer(t, func(w http.ResponseWriter, r *http.Request) {
			json.NewEncoder(w).Encode(map[string]interface{}{
				"id":         1001,
				"number":     10,
				"title":      "Merged PR",
				"body":       "Description",
				"head":       map[string]interface{}{"ref": "feature"},
				"base":       map[string]interface{}{"ref": "main"},
				"state":      "closed",
				"html_url":   "https://github.com/owner/repo/pull/10",
				"merged_at":  mergedAt.Format(time.RFC3339),
				"user":       map[string]interface{}{"id": 123, "login": "testuser"},
				"created_at": time.Now().Format(time.RFC3339),
				"updated_at": time.Now().Format(time.RFC3339),
			})
		})
		defer server.Close()

		mr, err := provider.GetMergeRequest(ctx, "owner/repo", 10)
		if err != nil {
			t.Fatalf("GetMergeRequest failed: %v", err)
		}
		if mr.State != "merged" {
			t.Errorf("expected state=merged, got %s", mr.State)
		}
	})

	t.Run("list merge requests by branch with merged_at items", func(t *testing.T) {
		mergedAt := time.Now().Add(-1 * time.Hour)
		server, provider := setupGitHubMockServer(t, func(w http.ResponseWriter, r *http.Request) {
			json.NewEncoder(w).Encode([]map[string]interface{}{
				{
					"id":         1001,
					"number":     10,
					"title":      "Merged PR",
					"head":       map[string]interface{}{"ref": "feature"},
					"base":       map[string]interface{}{"ref": "main"},
					"state":      "closed",
					"merged_at":  mergedAt.Format(time.RFC3339),
					"user":       map[string]interface{}{"id": 123, "login": "testuser"},
					"created_at": time.Now().Format(time.RFC3339),
					"updated_at": time.Now().Format(time.RFC3339),
				},
			})
		})
		defer server.Close()

		mrs, err := provider.ListMergeRequestsByBranch(ctx, "owner/repo", "feature", "all")
		if err != nil {
			t.Fatalf("ListMergeRequestsByBranch failed: %v", err)
		}
		if len(mrs) != 1 || mrs[0].State != "merged" {
			t.Error("expected merged state for PR with merged_at")
		}
	})
}

func TestGitHubMergeRequestHttpErrors(t *testing.T) {
	ctx := context.Background()

	t.Run("create merge request HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusUnauthorized)
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.CreateMergeRequest(ctx, &CreateMRRequest{
			ProjectID:    "owner/repo",
			Title:        "Test PR",
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

		provider, _ := NewGitHubProvider(server.URL, "test-token")
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

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.CloseMergeRequest(ctx, "owner/repo", 1)
		if err == nil {
			t.Error("expected error for HTTP 403")
		}
	})

	t.Run("merge merge request HTTP error on merge", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusNotFound)
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.MergeMergeRequest(ctx, "owner/repo", 1)
		if err == nil {
			t.Error("expected error for HTTP 404")
		}
	})
}

func TestGitHubMergeRequestErrorHandling(t *testing.T) {
	ctx := context.Background()

	t.Run("get merge request invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
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

		provider, _ := NewGitHubProvider(server.URL, "test-token")
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

		provider, _ := NewGitHubProvider(server.URL, "test-token")
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

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.CreateMergeRequest(ctx, &CreateMRRequest{
			ProjectID:    "owner/repo",
			Title:        "Test PR",
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

		provider, _ := NewGitHubProvider(server.URL, "test-token")
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

		provider, _ := NewGitHubProvider(server.URL, "test-token")
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

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.CloseMergeRequest(ctx, "owner/repo", 1)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})
}
