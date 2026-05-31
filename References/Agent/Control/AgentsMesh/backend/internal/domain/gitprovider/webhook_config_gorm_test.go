package gitprovider

import (
	"database/sql/driver"
	"encoding/json"
	"testing"
)

// ===========================================
// WebhookConfig GORM Scanner/Valuer Tests
// These tests cover the JSONB serialization for PostgreSQL
// ===========================================

func TestWebhookConfig_Value(t *testing.T) {
	tests := []struct {
		name     string
		config   WebhookConfig
		wantErr  bool
		validate func(t *testing.T, val driver.Value)
	}{
		{
			name: "full config",
			config: WebhookConfig{
				ID:               "wh_123",
				URL:              "https://example.com/webhooks/org/gitlab/1",
				Secret:           "secret123",
				Events:           []string{"merge_request", "pipeline"},
				IsActive:         true,
				NeedsManualSetup: false,
				LastError:        "",
				CreatedAt:        "2026-02-06T10:00:00Z",
			},
			wantErr: false,
			validate: func(t *testing.T, val driver.Value) {
				bytes, ok := val.([]byte)
				if !ok {
					t.Fatalf("expected []byte, got %T", val)
				}
				var parsed WebhookConfig
				if err := json.Unmarshal(bytes, &parsed); err != nil {
					t.Fatalf("failed to unmarshal: %v", err)
				}
				if parsed.ID != "wh_123" {
					t.Errorf("expected ID 'wh_123', got %s", parsed.ID)
				}
				if parsed.URL != "https://example.com/webhooks/org/gitlab/1" {
					t.Errorf("expected URL, got %s", parsed.URL)
				}
				if parsed.Secret != "secret123" {
					t.Errorf("expected Secret 'secret123', got %s", parsed.Secret)
				}
				if len(parsed.Events) != 2 {
					t.Errorf("expected 2 events, got %d", len(parsed.Events))
				}
				if !parsed.IsActive {
					t.Error("expected IsActive to be true")
				}
			},
		},
		{
			name: "empty config",
			config: WebhookConfig{},
			wantErr: false,
			validate: func(t *testing.T, val driver.Value) {
				bytes, ok := val.([]byte)
				if !ok {
					t.Fatalf("expected []byte, got %T", val)
				}
				var parsed WebhookConfig
				if err := json.Unmarshal(bytes, &parsed); err != nil {
					t.Fatalf("failed to unmarshal: %v", err)
				}
				if parsed.ID != "" {
					t.Errorf("expected empty ID, got %s", parsed.ID)
				}
			},
		},
		{
			name: "manual setup config",
			config: WebhookConfig{
				URL:              "https://example.com/webhooks/org/gitlab/1",
				Secret:           "secret456",
				Events:           []string{"merge_request", "pipeline"},
				IsActive:         false,
				NeedsManualSetup: true,
				LastError:        "OAuth token not available",
			},
			wantErr: false,
			validate: func(t *testing.T, val driver.Value) {
				bytes, ok := val.([]byte)
				if !ok {
					t.Fatalf("expected []byte, got %T", val)
				}
				var parsed WebhookConfig
				if err := json.Unmarshal(bytes, &parsed); err != nil {
					t.Fatalf("failed to unmarshal: %v", err)
				}
				if parsed.ID != "" {
					t.Errorf("expected empty ID for manual setup, got %s", parsed.ID)
				}
				if !parsed.NeedsManualSetup {
					t.Error("expected NeedsManualSetup to be true")
				}
				if parsed.LastError != "OAuth token not available" {
					t.Errorf("expected LastError, got %s", parsed.LastError)
				}
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			val, err := tt.config.Value()
			if (err != nil) != tt.wantErr {
				t.Errorf("Value() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if tt.validate != nil {
				tt.validate(t, val)
			}
		})
	}
}

func TestWebhookConfig_Scan(t *testing.T) {
	tests := []struct {
		name     string
		input    interface{}
		wantErr  bool
		validate func(t *testing.T, wc *WebhookConfig)
	}{
		{
			name:    "nil value",
			input:   nil,
			wantErr: false,
			validate: func(t *testing.T, wc *WebhookConfig) {
				// After scanning nil, the config should remain at zero values
				if wc.ID != "" {
					t.Errorf("expected empty ID after nil scan, got %s", wc.ID)
				}
			},
		},
		{
			name:    "empty bytes",
			input:   []byte{},
			wantErr: false,
			validate: func(t *testing.T, wc *WebhookConfig) {
				// Empty bytes should not modify the config
				if wc.ID != "" {
					t.Errorf("expected empty ID after empty bytes scan, got %s", wc.ID)
				}
			},
		},
		{
			name:  "valid JSON bytes",
			input: []byte(`{"id":"wh_abc","url":"https://example.com/webhooks","secret":"mysecret","events":["merge_request","pipeline"],"is_active":true}`),
			wantErr: false,
			validate: func(t *testing.T, wc *WebhookConfig) {
				if wc.ID != "wh_abc" {
					t.Errorf("expected ID 'wh_abc', got %s", wc.ID)
				}
				if wc.URL != "https://example.com/webhooks" {
					t.Errorf("expected URL, got %s", wc.URL)
				}
				if wc.Secret != "mysecret" {
					t.Errorf("expected Secret 'mysecret', got %s", wc.Secret)
				}
				if len(wc.Events) != 2 {
					t.Errorf("expected 2 events, got %d", len(wc.Events))
				}
				if !wc.IsActive {
					t.Error("expected IsActive to be true")
				}
			},
		},
		{
			name:    "invalid type (not []byte)",
			input:   "string_value",
			wantErr: true,
			validate: nil,
		},
		{
			name:    "invalid JSON",
			input:   []byte(`{"id": invalid}`),
			wantErr: true,
			validate: nil,
		},
		{
			name:  "partial JSON (missing fields)",
			input: []byte(`{"id":"wh_partial"}`),
			wantErr: false,
			validate: func(t *testing.T, wc *WebhookConfig) {
				if wc.ID != "wh_partial" {
					t.Errorf("expected ID 'wh_partial', got %s", wc.ID)
				}
				// Other fields should be zero values
				if wc.URL != "" {
					t.Errorf("expected empty URL, got %s", wc.URL)
				}
				if wc.IsActive {
					t.Error("expected IsActive to be false (default)")
				}
			},
		},
		{
			name:  "manual setup config",
			input: []byte(`{"url":"https://example.com/webhooks","secret":"s3cr3t","events":["merge_request"],"is_active":false,"needs_manual_setup":true,"last_error":"no OAuth token"}`),
			wantErr: false,
			validate: func(t *testing.T, wc *WebhookConfig) {
				if wc.ID != "" {
					t.Errorf("expected empty ID, got %s", wc.ID)
				}
				if !wc.NeedsManualSetup {
					t.Error("expected NeedsManualSetup to be true")
				}
				if wc.LastError != "no OAuth token" {
					t.Errorf("expected LastError 'no OAuth token', got %s", wc.LastError)
				}
				if wc.IsActive {
					t.Error("expected IsActive to be false")
				}
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var wc WebhookConfig
			err := wc.Scan(tt.input)
			if (err != nil) != tt.wantErr {
				t.Errorf("Scan() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if tt.validate != nil {
				tt.validate(t, &wc)
			}
		})
	}
}

func TestWebhookConfig_ValueScanRoundTrip(t *testing.T) {
	original := WebhookConfig{
		ID:               "wh_roundtrip",
		URL:              "https://example.com/webhooks/org/gitlab/123",
		Secret:           "roundtrip_secret",
		Events:           []string{"merge_request", "pipeline", "push"},
		IsActive:         true,
		NeedsManualSetup: false,
		LastError:        "",
		CreatedAt:        "2026-02-06T12:00:00Z",
	}

	// Serialize
	val, err := original.Value()
	if err != nil {
		t.Fatalf("Value() error: %v", err)
	}

	// Deserialize
	var restored WebhookConfig
	if err := restored.Scan(val); err != nil {
		t.Fatalf("Scan() error: %v", err)
	}

	// Compare
	if restored.ID != original.ID {
		t.Errorf("ID mismatch: %s vs %s", restored.ID, original.ID)
	}
	if restored.URL != original.URL {
		t.Errorf("URL mismatch: %s vs %s", restored.URL, original.URL)
	}
	if restored.Secret != original.Secret {
		t.Errorf("Secret mismatch: %s vs %s", restored.Secret, original.Secret)
	}
	if len(restored.Events) != len(original.Events) {
		t.Errorf("Events length mismatch: %d vs %d", len(restored.Events), len(original.Events))
	}
	for i, event := range original.Events {
		if restored.Events[i] != event {
			t.Errorf("Events[%d] mismatch: %s vs %s", i, restored.Events[i], event)
		}
	}
	if restored.IsActive != original.IsActive {
		t.Errorf("IsActive mismatch: %v vs %v", restored.IsActive, original.IsActive)
	}
	if restored.NeedsManualSetup != original.NeedsManualSetup {
		t.Errorf("NeedsManualSetup mismatch: %v vs %v", restored.NeedsManualSetup, original.NeedsManualSetup)
	}
	if restored.LastError != original.LastError {
		t.Errorf("LastError mismatch: %s vs %s", restored.LastError, original.LastError)
	}
	if restored.CreatedAt != original.CreatedAt {
		t.Errorf("CreatedAt mismatch: %s vs %s", restored.CreatedAt, original.CreatedAt)
	}
}
