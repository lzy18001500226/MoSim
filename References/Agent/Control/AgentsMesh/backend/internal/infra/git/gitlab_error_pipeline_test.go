package git

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGitLabPipelineErrorHandling(t *testing.T) {
	ctx := context.Background()

	t.Run("trigger pipeline invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
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

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.GetPipeline(ctx, "owner/repo", 1001)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("list pipelines invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("not an array"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.ListPipelines(ctx, "owner/repo", "main", "success", 1, 20)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("cancel pipeline invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.CancelPipeline(ctx, "owner/repo", 1001)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("retry pipeline invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.RetryPipeline(ctx, "owner/repo", 1001)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})
}

func TestGitLabJobErrorHandling(t *testing.T) {
	ctx := context.Background()

	t.Run("get job invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.GetJob(ctx, "owner/repo", 2001)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("list pipeline jobs invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("not an array"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.ListPipelineJobs(ctx, "owner/repo", 1001)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("retry job invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.RetryJob(ctx, "owner/repo", 2001)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("cancel job invalid JSON", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Write([]byte("{invalid"))
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.CancelJob(ctx, "owner/repo", 2001)
		if err == nil {
			t.Error("expected error for invalid JSON")
		}
	})

	t.Run("get job trace HTTP error", func(t *testing.T) {
		server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusNotFound)
		}))
		defer server.Close()

		provider, _ := NewGitLabProvider(server.URL, "test-token")
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

		provider, _ := NewGitLabProvider(server.URL, "test-token")
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

		provider, _ := NewGitLabProvider(server.URL, "test-token")
		_, err := provider.DownloadJobArtifacts(ctx, "owner/repo", 2001)
		if err == nil {
			t.Error("expected error for HTTP 404")
		}
	})
}
