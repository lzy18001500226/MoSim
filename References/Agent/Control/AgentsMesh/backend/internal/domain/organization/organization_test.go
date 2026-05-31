package organization

import (
	"testing"
	"time"
)

// --- Test Constants ---

func TestRoleConstants(t *testing.T) {
	if RoleOwner != "owner" {
		t.Errorf("expected 'owner', got %s", RoleOwner)
	}
	if RoleAdmin != "admin" {
		t.Errorf("expected 'admin', got %s", RoleAdmin)
	}
	if RoleMember != "member" {
		t.Errorf("expected 'member', got %s", RoleMember)
	}
}

// --- Test Organization ---

func TestOrganizationTableName(t *testing.T) {
	org := Organization{}
	if org.TableName() != "organizations" {
		t.Errorf("expected 'organizations', got %s", org.TableName())
	}
}

func TestOrganizationStruct(t *testing.T) {
	now := time.Now()
	logo := "https://example.com/logo.png"

	org := Organization{
		ID:                 1,
		Name:               "Test Org",
		Slug:               "test-org",
		LogoURL:            &logo,
		SubscriptionPlan:   "pro",
		SubscriptionStatus: "active",
		CreatedAt:          now,
		UpdatedAt:          now,
	}

	if org.ID != 1 {
		t.Errorf("expected ID 1, got %d", org.ID)
	}
	if org.Name != "Test Org" {
		t.Errorf("expected Name 'Test Org', got %s", org.Name)
	}
	if org.Slug != "test-org" {
		t.Errorf("expected Slug 'test-org', got %s", org.Slug)
	}
	if *org.LogoURL != "https://example.com/logo.png" {
		t.Errorf("expected LogoURL 'https://example.com/logo.png', got %s", *org.LogoURL)
	}
}

func TestOrganizationGetID(t *testing.T) {
	org := &Organization{ID: 123}
	if org.GetID() != 123 {
		t.Errorf("expected GetID() = 123, got %d", org.GetID())
	}
}

func TestOrganizationGetSlug(t *testing.T) {
	org := &Organization{Slug: "my-org"}
	if org.GetSlug() != "my-org" {
		t.Errorf("expected GetSlug() = 'my-org', got %s", org.GetSlug())
	}
}

func TestOrganizationGetName(t *testing.T) {
	org := &Organization{Name: "My Organization"}
	if org.GetName() != "My Organization" {
		t.Errorf("expected GetName() = 'My Organization', got %s", org.GetName())
	}
}

// --- Test Member ---

func TestMemberTableName(t *testing.T) {
	m := Member{}
	if m.TableName() != "organization_members" {
		t.Errorf("expected 'organization_members', got %s", m.TableName())
	}
}

func TestMemberStruct(t *testing.T) {
	now := time.Now()

	m := Member{
		ID:             1,
		OrganizationID: 100,
		UserID:         50,
		Role:           RoleAdmin,
		JoinedAt:       now,
	}

	if m.ID != 1 {
		t.Errorf("expected ID 1, got %d", m.ID)
	}
	if m.OrganizationID != 100 {
		t.Errorf("expected OrganizationID 100, got %d", m.OrganizationID)
	}
	if m.UserID != 50 {
		t.Errorf("expected UserID 50, got %d", m.UserID)
	}
	if m.Role != "admin" {
		t.Errorf("expected Role 'admin', got %s", m.Role)
	}
}

// --- Benchmark Tests ---

func BenchmarkOrganizationTableName(b *testing.B) {
	org := Organization{}
	for i := 0; i < b.N; i++ {
		org.TableName()
	}
}

func BenchmarkOrganizationGetID(b *testing.B) {
	org := &Organization{ID: 123}
	for i := 0; i < b.N; i++ {
		org.GetID()
	}
}

func BenchmarkOrganizationGetSlug(b *testing.B) {
	org := &Organization{Slug: "my-org"}
	for i := 0; i < b.N; i++ {
		org.GetSlug()
	}
}

func BenchmarkOrganizationGetName(b *testing.B) {
	org := &Organization{Name: "My Organization"}
	for i := 0; i < b.N; i++ {
		org.GetName()
	}
}
