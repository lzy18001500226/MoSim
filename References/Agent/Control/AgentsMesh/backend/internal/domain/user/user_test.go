package user

import (
	"testing"
	"time"
)

// --- Test User ---

func TestUserTableName(t *testing.T) {
	u := User{}
	if u.TableName() != "users" {
		t.Errorf("expected 'users', got %s", u.TableName())
	}
}

func TestUserStruct(t *testing.T) {
	now := time.Now()
	name := "Test User"
	avatar := "https://example.com/avatar.png"

	u := User{
		ID:          1,
		Email:       "test@example.com",
		Username:    "testuser",
		Name:        &name,
		AvatarURL:   &avatar,
		IsActive:    true,
		LastLoginAt: &now,
		CreatedAt:   now,
		UpdatedAt:   now,
	}

	if u.ID != 1 {
		t.Errorf("expected ID 1, got %d", u.ID)
	}
	if u.Email != "test@example.com" {
		t.Errorf("expected Email 'test@example.com', got %s", u.Email)
	}
	if u.Username != "testuser" {
		t.Errorf("expected Username 'testuser', got %s", u.Username)
	}
	if *u.Name != "Test User" {
		t.Errorf("expected Name 'Test User', got %s", *u.Name)
	}
	if !u.IsActive {
		t.Error("expected IsActive true")
	}
}

func TestUserWithOptionalFieldsNil(t *testing.T) {
	u := User{
		ID:       1,
		Email:    "test@example.com",
		Username: "testuser",
		IsActive: true,
	}

	if u.Name != nil {
		t.Error("expected Name to be nil")
	}
	if u.AvatarURL != nil {
		t.Error("expected AvatarURL to be nil")
	}
	if u.PasswordHash != nil {
		t.Error("expected PasswordHash to be nil")
	}
	if u.LastLoginAt != nil {
		t.Error("expected LastLoginAt to be nil")
	}
}

// --- Test Identity ---

func TestIdentityTableName(t *testing.T) {
	i := Identity{}
	if i.TableName() != "user_identities" {
		t.Errorf("expected 'user_identities', got %s", i.TableName())
	}
}

func TestIdentityStruct(t *testing.T) {
	now := time.Now()
	providerUsername := "github_user"

	i := Identity{
		ID:               1,
		UserID:           100,
		Provider:         "github",
		ProviderUserID:   "12345",
		ProviderUsername: &providerUsername,
		TokenExpiresAt:   &now,
		CreatedAt:        now,
		UpdatedAt:        now,
	}

	if i.ID != 1 {
		t.Errorf("expected ID 1, got %d", i.ID)
	}
	if i.UserID != 100 {
		t.Errorf("expected UserID 100, got %d", i.UserID)
	}
	if i.Provider != "github" {
		t.Errorf("expected Provider 'github', got %s", i.Provider)
	}
	if i.ProviderUserID != "12345" {
		t.Errorf("expected ProviderUserID '12345', got %s", i.ProviderUserID)
	}
	if *i.ProviderUsername != "github_user" {
		t.Errorf("expected ProviderUsername 'github_user', got %s", *i.ProviderUsername)
	}
}

func TestIdentityWithNilOptionalFields(t *testing.T) {
	i := Identity{
		ID:             1,
		UserID:         100,
		Provider:       "google",
		ProviderUserID: "67890",
	}

	if i.ProviderUsername != nil {
		t.Error("expected ProviderUsername to be nil")
	}
	if i.AccessTokenEncrypted != nil {
		t.Error("expected AccessTokenEncrypted to be nil")
	}
	if i.RefreshTokenEncrypted != nil {
		t.Error("expected RefreshTokenEncrypted to be nil")
	}
	if i.TokenExpiresAt != nil {
		t.Error("expected TokenExpiresAt to be nil")
	}
}

// --- Test UserWithOrgs ---

func TestUserWithOrgsStruct(t *testing.T) {
	u := UserWithOrgs{
		User: User{
			ID:       1,
			Email:    "test@example.com",
			Username: "testuser",
		},
		Organizations: []UserOrganization{
			{ID: 1, Name: "Org 1", Slug: "org-1", Role: "owner"},
			{ID: 2, Name: "Org 2", Slug: "org-2", Role: "member"},
		},
	}

	if u.ID != 1 {
		t.Errorf("expected ID 1, got %d", u.ID)
	}
	if len(u.Organizations) != 2 {
		t.Errorf("expected 2 organizations, got %d", len(u.Organizations))
	}
}

// --- Test UserOrganization ---

func TestUserOrganizationStruct(t *testing.T) {
	org := UserOrganization{
		ID:       1,
		Name:     "Test Org",
		Slug:     "test-org",
		Role:     "admin",
		LogoURL:  "https://example.com/logo.png",
		JoinedAt: "2024-01-01T00:00:00Z",
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
	if org.Role != "admin" {
		t.Errorf("expected Role 'admin', got %s", org.Role)
	}
}

// --- Benchmark Tests ---

func BenchmarkUserTableName(b *testing.B) {
	u := User{}
	for i := 0; i < b.N; i++ {
		u.TableName()
	}
}

func BenchmarkIdentityTableName(b *testing.B) {
	identity := Identity{}
	for i := 0; i < b.N; i++ {
		identity.TableName()
	}
}
