package git

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGitHubJobErrorHandling(t *testing.T) {
	ctx := context.Background()

	t.Run("get job invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.GetJob(ctx, "owner/repo", 2001)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("list pipeline jobs invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.ListPipelineJobs(ctx, "owner/repo", 1001)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("retry job HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusNotFound)
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.RetryJob(ctx, "owner/repo", 2001)
		if err == nil {
			t.Error("expected error for HTTP 404")
		}
	})

	t.Run("cancel job HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusForbidden)
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.CancelJob(ctx, "owner/repo", 2001)
		if err == nil {
			t.Error("expected error for HTTP 403")
		}
	})

	t.Run("get job trace HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusNotFound)
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.GetJobTrace(ctx, "owner/repo", 2001)
		if err == nil {
			t.Error("expected error for HTTP 404")
		}
	})

	t.Run("get job artifact HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusNotFound)
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.GetJobArtifact(ctx, "owner/repo", 2001, "artifact.zip")
		if err == nil {
			t.Error("expected error for HTTP 404")
		}
	})

	t.Run("download job artifacts HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusNotFound)
		}))
		defer server.Close()

		provider, _ := NewGitHubProvider(server.URL, "test-token")
		_, err := provider.DownloadJobArtifacts(ctx, "owner/repo", 2001)
		if err == nil {
			t.Error("expected error for HTTP 404")
		}
	})
}

func TestGitHubAdditionalStatusMapping(t *testing.T) {
	ctx := context.Background()

	// Test additional status mapping cases not covered in github_job_test.go
	statusTests := []struct {
		status     string
		conclusion string
		expected   string
	}{
		{"completed", "timed_out", PipelineStatusFailed},
		{"unknown", "", PipelineStatusPending},
	}

	for _, tc := range statusTests {
		t.Run(tc.status+"_"+tc.conclusion, func(t *testing.T) {
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				json.NewEncoder(w).Encode(map[string]interface{}{
					"id":          1001,
					"run_number":  1,
					"head_branch": "main",
					"head_sha":    "abc123",
					"status":      tc.status,
					"conclusion":  tc.conclusion,
					"event":       "push",
					"html_url":    "https://github.com/owner/repo/actions/runs/1001",
					"created_at":  "2024-01-01T00:00:00Z",
					"updated_at":  "2024-01-01T00:01:00Z",
				})
			}))
			defer server.Close()

			provider, _ := NewGitHubProvider(server.URL, "test-token")
			pipeline, err := provider.GetPipeline(ctx, "owner/repo", 1001)
			if err != nil {
				t.Fatalf("GetPipeline failed: %v", err)
			}
			if pipeline.Status != tc.expected {
				t.Errorf("status = %s, want %s", pipeline.Status, tc.expected)
			}
		})
	}
}
