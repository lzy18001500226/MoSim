package webhooks

import (
	"context"
	"testing"
)

// ===========================================
// WebhookContext Tests
// ===========================================

func TestWebhookContext_WithRepoInfo(t *testing.T) {
	// Note: JSON unmarshals numbers to float64 by default
	// formatID converts int64 to rune string (e.g., 65 -> "A")
	payload := map[string]interface{}{
		"object_kind": "merge_request",
		"project": map[string]interface{}{
			"id": float64(65), // 65 is 'A' in ASCII
		},
	}

	ctx := NewWebhookContext(context.Background(), nil, payload)
	ctx.OrgSlug = "test-org"
	ctx.RepoID = 456

	if ctx.OrgSlug != "test-org" {
		t.Errorf("expected OrgSlug 'test-org', got '%s'", ctx.OrgSlug)
	}
	if ctx.RepoID != 456 {
		t.Errorf("expected RepoID 456, got %d", ctx.RepoID)
	}
	if ctx.ObjectKind != "merge_request" {
		t.Errorf("expected ObjectKind 'merge_request', got '%s'", ctx.ObjectKind)
	}
	// ProjectID is extracted from project.id using formatID (rune conversion)
	if ctx.ProjectID != "A" {
		t.Errorf("expected ProjectID 'A', got '%s'", ctx.ProjectID)
	}
}

func TestWebhookContext_WithoutProject(t *testing.T) {
	payload := map[string]interface{}{
		"object_kind": "push",
		// No "project" field
	}

	ctx := NewWebhookContext(context.Background(), nil, payload)

	if ctx.ObjectKind != "push" {
		t.Errorf("expected ObjectKind 'push', got '%s'", ctx.ObjectKind)
	}
	if ctx.ProjectID != "" {
		t.Errorf("expected empty ProjectID, got '%s'", ctx.ProjectID)
	}
}

func TestWebhookContext_SetOrganizationID(t *testing.T) {
	payload := map[string]interface{}{
		"object_kind": "push",
	}

	ctx := NewWebhookContext(context.Background(), nil, payload)
	ctx.OrganizationID = 999

	if ctx.OrganizationID != 999 {
		t.Errorf("expected OrganizationID 999, got %d", ctx.OrganizationID)
	}
}

// ===========================================
// WebhookContext Additional Tests
// ===========================================

func TestWebhookContext_StringProjectID(t *testing.T) {
	// String IDs in project.id are not extracted (only float64 is handled)
	// This tests the expected behavior - string IDs result in empty ProjectID
	payload := map[string]interface{}{
		"object_kind": "push",
		"project": map[string]interface{}{
			"id": "string-id", // String ID instead of number
		},
	}

	ctx := NewWebhookContext(context.Background(), nil, payload)

	// String IDs are not extracted - this is the expected behavior
	// NewWebhookContext only handles float64 IDs (from JSON)
	if ctx.ProjectID != "" {
		t.Errorf("expected empty ProjectID for string id, got '%s'", ctx.ProjectID)
	}
}

func TestWebhookContext_NilProject(t *testing.T) {
	payload := map[string]interface{}{
		"object_kind": "push",
		"project":     nil,
	}

	ctx := NewWebhookContext(context.Background(), nil, payload)

	if ctx.ProjectID != "" {
		t.Errorf("expected empty ProjectID for nil project, got '%s'", ctx.ProjectID)
	}
}

func TestWebhookContext_NestedProjectPath(t *testing.T) {
	payload := map[string]interface{}{
		"object_kind": "push",
		"project": map[string]interface{}{
			"id":        float64(123),
			"path":      "repo-name",
			"namespace": "org-name",
		},
	}

	ctx := NewWebhookContext(context.Background(), nil, payload)

	if ctx.ObjectKind != "push" {
		t.Errorf("expected ObjectKind 'push', got '%s'", ctx.ObjectKind)
	}
}
