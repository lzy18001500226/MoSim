package user

import (
	"context"
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/backend/internal/infra"
)

func TestAuthenticate(t *testing.T) {
	db := setupTestDB(t)
	service := NewService(infra.NewUserRepository(db))
	ctx := context.Background()

	// Create a user with password
	req := &CreateRequest{
		Email:    "test@example.com",
		Username: "testuser",
		Password: "password123",
	}
	service.Create(ctx, req)

	// Authenticate
	user, err := service.Authenticate(ctx, "test@example.com", "password123")
	if err != nil {
		t.Fatalf("failed to authenticate: %v", err)
	}
	if user.Email != "test@example.com" {
		t.Errorf("expected Email 'test@example.com', got %s", user.Email)
	}
}

func TestAuthenticateInvalidPassword(t *testing.T) {
	db := setupTestDB(t)
	service := NewService(infra.NewUserRepository(db))
	ctx := context.Background()

	req := &CreateRequest{
		Email:    "test@example.com",
		Username: "testuser",
		Password: "password123",
	}
	service.Create(ctx, req)

	_, err := service.Authenticate(ctx, "test@example.com", "wrongpassword")
	if err != ErrInvalidCredentials {
		t.Errorf("expected ErrInvalidCredentials, got %v", err)
	}
}

func TestAuthenticateUserNotFound(t *testing.T) {
	db := setupTestDB(t)
	service := NewService(infra.NewUserRepository(db))
	ctx := context.Background()

	_, err := service.Authenticate(ctx, "nonexistent@example.com", "password")
	if err != ErrInvalidCredentials {
		t.Errorf("expected ErrInvalidCredentials, got %v", err)
	}
}

func TestAuthenticateNoPassword(t *testing.T) {
	db := setupTestDB(t)
	service := NewService(infra.NewUserRepository(db))
	ctx := context.Background()

	// Create user without password
	req := &CreateRequest{
		Email:    "test@example.com",
		Username: "testuser",
	}
	service.Create(ctx, req)

	_, err := service.Authenticate(ctx, "test@example.com", "password")
	if err != ErrInvalidCredentials {
		t.Errorf("expected ErrInvalidCredentials, got %v", err)
	}
}

func TestAuthenticateInactiveUser(t *testing.T) {
	db := setupTestDB(t)
	service := NewService(infra.NewUserRepository(db))
	ctx := context.Background()

	req := &CreateRequest{
		Email:    "inactive@example.com",
		Username: "inactiveuser",
		Password: "password123",
	}
	created, _ := service.Create(ctx, req)

	// Deactivate user
	db.Exec("UPDATE users SET is_active = 0 WHERE id = ?", created.ID)

	_, err := service.Authenticate(ctx, "inactive@example.com", "password123")
	if err != ErrUserInactive {
		t.Errorf("expected ErrUserInactive, got %v", err)
	}
}

func TestAuthenticateUpdatesLastLoginAt(t *testing.T) {
	db := setupTestDB(t)
	service := NewService(infra.NewUserRepository(db))
	ctx := context.Background()

	req := &CreateRequest{
		Email:    "login@example.com",
		Username: "loginuser",
		Password: "password123",
	}
	created, _ := service.Create(ctx, req)

	// Verify last_login_at is nil before first login
	u, _ := service.GetByID(ctx, created.ID)
	if u.LastLoginAt != nil {
		t.Error("expected LastLoginAt to be nil before first login")
	}

	before := time.Now()
	_, err := service.Authenticate(ctx, "login@example.com", "password123")
	if err != nil {
		t.Fatalf("failed to authenticate: %v", err)
	}

	// Re-fetch user to verify last_login_at was updated
	u, _ = service.GetByID(ctx, created.ID)
	if u.LastLoginAt == nil {
		t.Fatal("expected LastLoginAt to be set after login")
	}
	if u.LastLoginAt.Before(before) {
		t.Error("expected LastLoginAt to be >= time before authentication")
	}
}

func TestRecordLogin(t *testing.T) {
	db := setupTestDB(t)
	service := NewService(infra.NewUserRepository(db))
	ctx := context.Background()

	created, _ := service.Create(ctx, &CreateRequest{
		Email:    "record@example.com",
		Username: "recorduser",
		Password: "password123",
	})

	before := time.Now()
	service.RecordLogin(ctx, created.ID)

	u, _ := service.GetByID(ctx, created.ID)
	if u.LastLoginAt == nil {
		t.Fatal("expected LastLoginAt to be set after RecordLogin")
	}
	if u.LastLoginAt.Before(before) {
		t.Error("expected LastLoginAt to be >= time before RecordLogin")
	}
}

func TestRecordLoginMultipleCalls(t *testing.T) {
	db := setupTestDB(t)
	service := NewService(infra.NewUserRepository(db))
	ctx := context.Background()

	created, _ := service.Create(ctx, &CreateRequest{
		Email:    "multi@example.com",
		Username: "multiuser",
		Password: "password123",
	})

	// First login
	service.RecordLogin(ctx, created.ID)
	u1, _ := service.GetByID(ctx, created.ID)
	first := *u1.LastLoginAt

	// Small delay to ensure different timestamp
	time.Sleep(10 * time.Millisecond)

	// Second login
	service.RecordLogin(ctx, created.ID)
	u2, _ := service.GetByID(ctx, created.ID)
	second := *u2.LastLoginAt

	if !second.After(first) {
		t.Errorf("expected second login time %v to be after first %v", second, first)
	}
}

func TestRecordLoginNonExistentUser(t *testing.T) {
	db := setupTestDB(t)
	service := NewService(infra.NewUserRepository(db))
	ctx := context.Background()

	// Should not panic — errors are logged, not returned
	service.RecordLogin(ctx, 99999)
}

func TestUpdatePassword(t *testing.T) {
	db := setupTestDB(t)
	service := NewService(infra.NewUserRepository(db))
	ctx := context.Background()

	req := &CreateRequest{
		Email:    "test@example.com",
		Username: "testuser",
		Password: "oldpassword",
	}
	created, _ := service.Create(ctx, req)

	// Update password
	err := service.UpdatePassword(ctx, created.ID, "newpassword")
	if err != nil {
		t.Fatalf("failed to update password: %v", err)
	}

	// Should be able to authenticate with new password
	_, err = service.Authenticate(ctx, "test@example.com", "newpassword")
	if err != nil {
		t.Errorf("expected successful authentication, got %v", err)
	}
}
