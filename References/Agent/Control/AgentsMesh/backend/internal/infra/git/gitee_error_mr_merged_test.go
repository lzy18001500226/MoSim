package git

import (
	"context"
	"encoding/json"
	"net/http"
	"testing"
	"time"
)

func TestGiteeMergeRequestWithMergedAt(t *testing.T) {
	ctx := context.Background()

	t.Run("get merge request with merged_at field", func(t *testing.T) {
		mergedAt := time.Now().Add(-1 * time.Hour)
		server, provider := setupGiteeMockServer(t, func(w http.ResponseWriter, r *http.Request) {
			json.NewEncoder(w).Encode(map[string]interface{}{
				"id":         1001,
				"number":     10,
				"title":      "Merged PR",
				"body":       "Description",
				"head":       map[string]interface{}{"ref": "feature"},
				"base":       map[string]interface{}{"ref": "main"},
				"state":      "merged",
				"html_url":   "https://gitee.com/owner/repo/pulls/10",
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
		if mr.MergedAt == nil {
			t.Error("expected merged_at to be set")
		}
	})

	t.Run("list merge requests with merged_at field", func(t *testing.T) {
		mergedAt := time.Now().Add(-1 * time.Hour)
		server, provider := setupGiteeMockServer(t, func(w http.ResponseWriter, r *http.Request) {
			json.NewEncoder(w).Encode([]map[string]interface{}{
				{
					"id":         1001,
					"number":     10,
					"title":      "Merged PR",
					"body":       "Description",
					"head":       map[string]interface{}{"ref": "feature"},
					"base":       map[string]interface{}{"ref": "main"},
					"state":      "merged",
					"merged_at":  mergedAt.Format(time.RFC3339),
					"user":       map[string]interface{}{"id": 123, "login": "testuser"},
					"created_at": time.Now().Format(time.RFC3339),
					"updated_at": time.Now().Format(time.RFC3339),
				},
			})
		})
		defer server.Close()

		mrs, err := provider.ListMergeRequests(ctx, "owner/repo", "merged", 1, 20)
		if err != nil {
			t.Fatalf("ListMergeRequests failed: %v", err)
		}
		if len(mrs) != 1 || mrs[0].MergedAt == nil {
			t.Error("expected merged_at to be set")
		}
	})
}
