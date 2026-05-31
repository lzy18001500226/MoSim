package git

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"strings"
	"testing"
)

func TestGitLabWebhookOperations(t *testing.T) {
	ctx := context.Background()

	t.Run("register webhook", func(t *testing.T) {
		server, provider := setupGitLabMockServer(t, func(w http.ResponseWriter, r *http.Request) {
			if r.Method != "POST" {
				t.Errorf("unexpected method: %s", r.Method)
			}
			json.NewEncoder(w).Encode(map[string]interface{}{
				"id": 12345,
			})
		})
		defer server.Close()

		webhookID, err := provider.RegisterWebhook(ctx, "owner/repo", &WebhookConfig{
			URL:    "https://example.com/webhook",
			Secret: "secret",
			Events: []string{"push", "merge_request"},
		})
		if err != nil {
			t.Fatalf("RegisterWebhook failed: %v", err)
		}
		if webhookID != "12345" {
			t.Errorf("webhookID = %s, want 12345", webhookID)
		}
	})

	t.Run("register webhook with pipeline events", func(t *testing.T) {
		var requestBody string
		server, provider := setupGitLabMockServer(t, func(w http.ResponseWriter, r *http.Request) {
			if r.Method != "POST" {
				t.Errorf("unexpected method: %s", r.Method)
			}
			// Capture request body
			body, _ := io.ReadAll(r.Body)
			requestBody = string(body)
			json.NewEncoder(w).Encode(map[string]interface{}{
				"id": 67890,
			})
		})
		defer server.Close()

		webhookID, err := provider.RegisterWebhook(ctx, "owner/repo", &WebhookConfig{
			URL:    "https://example.com/webhook",
			Secret: "secret",
			Events: []string{"merge_request", "pipeline"},
		})
		if err != nil {
			t.Fatalf("RegisterWebhook failed: %v", err)
		}
		if webhookID != "67890" {
			t.Errorf("webhookID = %s, want 67890", webhookID)
		}

		// Verify pipeline_events is true in request body
		if !strings.Contains(requestBody, `"pipeline_events":true`) {
			t.Errorf("expected pipeline_events:true in request body, got: %s", requestBody)
		}
		if !strings.Contains(requestBody, `"merge_requests_events":true`) {
			t.Errorf("expected merge_requests_events:true in request body, got: %s", requestBody)
		}
		if !strings.Contains(requestBody, `"push_events":false`) {
			t.Errorf("expected push_events:false in request body, got: %s", requestBody)
		}
	})

	t.Run("register webhook with all events", func(t *testing.T) {
		var requestBody string
		server, provider := setupGitLabMockServer(t, func(w http.ResponseWriter, r *http.Request) {
			body, _ := io.ReadAll(r.Body)
			requestBody = string(body)
			json.NewEncoder(w).Encode(map[string]interface{}{
				"id": 11111,
			})
		})
		defer server.Close()

		webhookID, err := provider.RegisterWebhook(ctx, "owner/repo", &WebhookConfig{
			URL:    "https://example.com/webhook",
			Secret: "secret",
			Events: []string{"push", "merge_request", "pipeline"},
		})
		if err != nil {
			t.Fatalf("RegisterWebhook failed: %v", err)
		}
		if webhookID != "11111" {
			t.Errorf("webhookID = %s, want 11111", webhookID)
		}

		// Verify all events are true
		if !strings.Contains(requestBody, `"push_events":true`) {
			t.Errorf("expected push_events:true in request body, got: %s", requestBody)
		}
		if !strings.Contains(requestBody, `"merge_requests_events":true`) {
			t.Errorf("expected merge_requests_events:true in request body, got: %s", requestBody)
		}
		if !strings.Contains(requestBody, `"pipeline_events":true`) {
			t.Errorf("expected pipeline_events:true in request body, got: %s", requestBody)
		}
	})

	t.Run("register webhook with no events", func(t *testing.T) {
		var requestBody string
		server, provider := setupGitLabMockServer(t, func(w http.ResponseWriter, r *http.Request) {
			body, _ := io.ReadAll(r.Body)
			requestBody = string(body)
			json.NewEncoder(w).Encode(map[string]interface{}{
				"id": 22222,
			})
		})
		defer server.Close()

		webhookID, err := provider.RegisterWebhook(ctx, "owner/repo", &WebhookConfig{
			URL:    "https://example.com/webhook",
			Secret: "secret",
			Events: []string{},
		})
		if err != nil {
			t.Fatalf("RegisterWebhook failed: %v", err)
		}
		if webhookID != "22222" {
			t.Errorf("webhookID = %s, want 22222", webhookID)
		}

		// Verify all events are false
		if !strings.Contains(requestBody, `"push_events":false`) {
			t.Errorf("expected push_events:false in request body, got: %s", requestBody)
		}
		if !strings.Contains(requestBody, `"merge_requests_events":false`) {
			t.Errorf("expected merge_requests_events:false in request body, got: %s", requestBody)
		}
		if !strings.Contains(requestBody, `"pipeline_events":false`) {
			t.Errorf("expected pipeline_events:false in request body, got: %s", requestBody)
		}
	})

	t.Run("delete webhook", func(t *testing.T) {
		server, provider := setupGitLabMockServer(t, func(w http.ResponseWriter, r *http.Request) {
			if r.Method != "DELETE" {
				t.Errorf("unexpected method: %s", r.Method)
			}
			w.WriteHeader(http.StatusNoContent)
		})
		defer server.Close()

		err := provider.DeleteWebhook(ctx, "owner/repo", "12345")
		if err != nil {
			t.Fatalf("DeleteWebhook failed: %v", err)
		}
	})
}
