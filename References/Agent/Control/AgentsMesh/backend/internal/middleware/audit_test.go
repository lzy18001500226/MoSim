package middleware

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestParseAction(t *testing.T) {
	tests := []struct {
		name           string
		method         string
		path           string
		expectedAction string
		expectedType   string
		hasResourceID  bool
	}{
		{
			name:           "POST creates resource",
			method:         "POST",
			path:           "/api/v1/pods",
			expectedAction: "pods.created",
			expectedType:   "pods",
			hasResourceID:  false,
		},
		{
			name:           "PUT updates resource",
			method:         "PUT",
			path:           "/api/v1/users/123",
			expectedAction: "users.updated",
			expectedType:   "users",
			hasResourceID:  true,
		},
		{
			name:           "PATCH updates resource",
			method:         "PATCH",
			path:           "/api/v1/tickets/456",
			expectedAction: "tickets.updated",
			expectedType:   "tickets",
			hasResourceID:  true,
		},
		{
			name:           "DELETE deletes resource",
			method:         "DELETE",
			path:           "/api/v1/channels/789",
			expectedAction: "channels.deleted",
			expectedType:   "channels",
			hasResourceID:  true,
		},
		{
			name:           "GET returns empty action",
			method:         "GET",
			path:           "/api/v1/pods",
			expectedAction: "",
			expectedType:   "",
			hasResourceID:  false,
		},
		{
			name:           "terminate action",
			method:         "POST",
			path:           "/api/v1/pods/123/terminate",
			expectedAction: "pods.terminated",
			expectedType:   "pods",
			hasResourceID:  true,
		},
		{
			name:           "archive action",
			method:         "POST",
			path:           "/api/v1/channels/456/archive",
			expectedAction: "channels.archived",
			expectedType:   "channels",
			hasResourceID:  true,
		},
		{
			name:           "unarchive action",
			method:         "POST",
			path:           "/api/v1/channels/456/unarchive",
			expectedAction: "channels.unarchived",
			expectedType:   "channels",
			hasResourceID:  true,
		},
		{
			name:           "join action",
			method:         "POST",
			path:           "/api/v1/channels/456/join",
			expectedAction: "channels.joined",
			expectedType:   "channels",
			hasResourceID:  true,
		},
		{
			name:           "leave action",
			method:         "POST",
			path:           "/api/v1/channels/456/leave",
			expectedAction: "channels.left",
			expectedType:   "channels",
			hasResourceID:  true,
		},
		{
			name:           "register action",
			method:         "POST",
			path:           "/api/v1/auth/register",
			expectedAction: "users.registered",
			expectedType:   "users",
			hasResourceID:  false,
		},
		{
			name:           "login action",
			method:         "POST",
			path:           "/api/v1/auth/login",
			expectedAction: "users.logged_in",
			expectedType:   "users",
			hasResourceID:  false,
		},
		{
			name:           "oauth action",
			method:         "POST",
			path:           "/api/v1/auth/oauth/github",
			expectedAction: "users.oauth_login",
			expectedType:   "users",
			hasResourceID:  false,
		},
		{
			name:           "without api prefix",
			method:         "POST",
			path:           "/pods",
			expectedAction: "pods.created",
			expectedType:   "pods",
			hasResourceID:  false,
		},
		{
			name:           "empty path returns action for root",
			method:         "POST",
			path:           "/",
			expectedAction: ".created", // path "/" splits to [""] which becomes ".created"
			expectedType:   "",
			hasResourceID:  false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			action, resourceType, resourceID := parseAction(tt.method, tt.path)

			assert.Equal(t, tt.expectedAction, action)
			assert.Equal(t, tt.expectedType, resourceType)

			if tt.hasResourceID {
				assert.NotNil(t, resourceID)
			} else {
				// resourceID may be nil or not depending on path structure
			}
		})
	}
}

func TestSanitizeBody(t *testing.T) {
	sensitiveFields := []string{"password", "token", "secret", "api_key"}

	t.Run("should redact sensitive fields", func(t *testing.T) {
		body := map[string]interface{}{
			"username": "testuser",
			"password": "secret123",
			"email":    "test@example.com",
		}

		result := sanitizeBody(body, sensitiveFields)

		assert.Equal(t, "testuser", result["username"])
		assert.Equal(t, "[REDACTED]", result["password"])
		assert.Equal(t, "test@example.com", result["email"])
	})

	t.Run("should redact fields containing sensitive words", func(t *testing.T) {
		body := map[string]interface{}{
			"access_token":  "abc123",
			"refresh_token": "xyz789",
			"api_key":       "key123",
			"name":          "Test User",
		}

		result := sanitizeBody(body, sensitiveFields)

		assert.Equal(t, "[REDACTED]", result["access_token"])
		assert.Equal(t, "[REDACTED]", result["refresh_token"])
		assert.Equal(t, "[REDACTED]", result["api_key"])
		assert.Equal(t, "Test User", result["name"])
	})

	t.Run("should handle nested objects", func(t *testing.T) {
		body := map[string]interface{}{
			"user": map[string]interface{}{
				"name":     "Test User",
				"password": "secret",
			},
			"config": map[string]interface{}{
				"api_key": "key123",
				"timeout": 30,
			},
		}

		result := sanitizeBody(body, sensitiveFields)

		userMap := result["user"].(map[string]interface{})
		assert.Equal(t, "Test User", userMap["name"])
		assert.Equal(t, "[REDACTED]", userMap["password"])

		configMap := result["config"].(map[string]interface{})
		assert.Equal(t, "[REDACTED]", configMap["api_key"])
		assert.Equal(t, 30, configMap["timeout"])
	})

	t.Run("should handle empty body", func(t *testing.T) {
		body := map[string]interface{}{}

		result := sanitizeBody(body, sensitiveFields)

		assert.Empty(t, result)
	})

	t.Run("should be case insensitive", func(t *testing.T) {
		body := map[string]interface{}{
			"PASSWORD":   "secret1",
			"Password":   "secret2",
			"API_KEY":    "key1",
			"api_KEY":    "key2",
			"normalData": "visible",
		}

		result := sanitizeBody(body, sensitiveFields)

		assert.Equal(t, "[REDACTED]", result["PASSWORD"])
		assert.Equal(t, "[REDACTED]", result["Password"])
		assert.Equal(t, "[REDACTED]", result["API_KEY"])
		assert.Equal(t, "[REDACTED]", result["api_KEY"])
		assert.Equal(t, "visible", result["normalData"])
	})
}

func TestDefaultAuditConfig(t *testing.T) {
	t.Run("should return config with defaults", func(t *testing.T) {
		config := DefaultAuditConfig(nil)

		assert.NotNil(t, config)
		assert.Contains(t, config.SkipPaths, "/health")
		assert.Contains(t, config.SkipPaths, "/metrics")
		assert.Contains(t, config.SkipMethods, "GET")
		assert.Contains(t, config.SkipMethods, "HEAD")
		assert.Contains(t, config.SkipMethods, "OPTIONS")
		assert.True(t, config.CaptureBody)
		assert.Equal(t, int64(10*1024), config.MaxBodySize)
		assert.Contains(t, config.SensitiveFields, "password")
		assert.Contains(t, config.SensitiveFields, "token")
		assert.Contains(t, config.SensitiveFields, "secret")
	})
}

func TestAuditLog_TableName(t *testing.T) {
	log := AuditLog{}
	assert.Equal(t, "audit_logs", log.TableName())
}

func TestAuditActionConstants(t *testing.T) {
	// Verify audit action constants are defined
	assert.Equal(t, "users.created", string(AuditUserCreated))
	assert.Equal(t, "users.logged_in", string(AuditUserLoggedIn))
	assert.Equal(t, "organizations.created", string(AuditOrgCreated))
	assert.Equal(t, "pods.created", string(AuditPodCreated))
	assert.Equal(t, "pods.terminated", string(AuditPodTerminated))
	assert.Equal(t, "channels.created", string(AuditChannelCreated))
	assert.Equal(t, "tickets.created", string(AuditTicketCreated))
}
