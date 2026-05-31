package user

import (
	"context"
	"errors"
	"testing"
)

func TestNewMockService(t *testing.T) {
	mock := NewMockService()
	if mock == nil {
		t.Fatal("expected non-nil mock service")
	}
	if mock.users == nil {
		t.Error("users map should be initialized")
	}
	if mock.identities == nil {
		t.Error("identities map should be initialized")
	}
	if mock.nextID != 1 {
		t.Errorf("nextID = %d, want 1", mock.nextID)
	}
}

func TestMockServiceCreate(t *testing.T) {
	ctx := context.Background()
	mock := NewMockService()

	t.Run("creates user successfully", func(t *testing.T) {
		req := &CreateRequest{
			Email:    "test@example.com",
			Username: "testuser",
			Name:     "Test User",
		}

		u, err := mock.Create(ctx, req)
		if err != nil {
			t.Fatalf("Create failed: %v", err)
		}
		if u.Email != "test@example.com" {
			t.Errorf("Email = %s, want test@example.com", u.Email)
		}
		if u.Username != "testuser" {
			t.Errorf("Username = %s, want testuser", u.Username)
		}
		if u.Name == nil || *u.Name != "Test User" {
			t.Error("Name not set correctly")
		}
		if !u.IsActive {
			t.Error("User should be active")
		}
		if len(mock.CreatedUsers) != 1 {
			t.Errorf("CreatedUsers count = %d, want 1", len(mock.CreatedUsers))
		}
	})

	t.Run("creates user without name", func(t *testing.T) {
		mock2 := NewMockService()
		req := &CreateRequest{
			Email:    "noname@example.com",
			Username: "noname",
		}

		u, err := mock2.Create(ctx, req)
		if err != nil {
			t.Fatalf("Create failed: %v", err)
		}
		if u.Name != nil {
			t.Error("Name should be nil")
		}
	})

	t.Run("configurable error", func(t *testing.T) {
		customErr := errors.New("create error")
		mock.CreateErr = customErr

		_, err := mock.Create(ctx, &CreateRequest{Email: "err@test.com", Username: "err"})
		if err != customErr {
			t.Errorf("Expected custom error, got %v", err)
		}
		mock.CreateErr = nil
	})
}

func TestMockServiceGetByID(t *testing.T) {
	ctx := context.Background()
	mock := NewMockService()

	u, _ := mock.Create(ctx, &CreateRequest{Email: "test@example.com", Username: "test"})

	t.Run("existing user", func(t *testing.T) {
		result, err := mock.GetByID(ctx, u.ID)
		if err != nil {
			t.Fatalf("GetByID failed: %v", err)
		}
		if result.ID != u.ID {
			t.Errorf("ID = %d, want %d", result.ID, u.ID)
		}
	})

	t.Run("non-existent user", func(t *testing.T) {
		_, err := mock.GetByID(ctx, 999)
		if err != ErrUserNotFound {
			t.Errorf("Expected ErrUserNotFound, got %v", err)
		}
	})

	t.Run("configurable error", func(t *testing.T) {
		customErr := errors.New("get error")
		mock.GetByIDErr = customErr
		_, err := mock.GetByID(ctx, u.ID)
		if err != customErr {
			t.Errorf("Expected custom error, got %v", err)
		}
		mock.GetByIDErr = nil
	})
}

func TestMockServiceGetByEmail(t *testing.T) {
	ctx := context.Background()
	mock := NewMockService()

	mock.Create(ctx, &CreateRequest{Email: "test@example.com", Username: "test"})

	t.Run("existing email", func(t *testing.T) {
		result, err := mock.GetByEmail(ctx, "test@example.com")
		if err != nil {
			t.Fatalf("GetByEmail failed: %v", err)
		}
		if result.Email != "test@example.com" {
			t.Errorf("Email = %s, want test@example.com", result.Email)
		}
	})

	t.Run("non-existent email", func(t *testing.T) {
		_, err := mock.GetByEmail(ctx, "nonexistent@example.com")
		if err != ErrUserNotFound {
			t.Errorf("Expected ErrUserNotFound, got %v", err)
		}
	})

	t.Run("configurable error", func(t *testing.T) {
		customErr := errors.New("email error")
		mock.GetByEmailErr = customErr
		_, err := mock.GetByEmail(ctx, "test@example.com")
		if err != customErr {
			t.Errorf("Expected custom error, got %v", err)
		}
		mock.GetByEmailErr = nil
	})
}

func TestMockServiceGetByUsername(t *testing.T) {
	ctx := context.Background()
	mock := NewMockService()

	mock.Create(ctx, &CreateRequest{Email: "test@example.com", Username: "testuser"})

	t.Run("existing username", func(t *testing.T) {
		result, err := mock.GetByUsername(ctx, "testuser")
		if err != nil {
			t.Fatalf("GetByUsername failed: %v", err)
		}
		if result.Username != "testuser" {
			t.Errorf("Username = %s, want testuser", result.Username)
		}
	})

	t.Run("non-existent username", func(t *testing.T) {
		_, err := mock.GetByUsername(ctx, "nonexistent")
		if err != ErrUserNotFound {
			t.Errorf("Expected ErrUserNotFound, got %v", err)
		}
	})

	t.Run("configurable error", func(t *testing.T) {
		customErr := errors.New("username error")
		mock.GetByUsernameErr = customErr
		_, err := mock.GetByUsername(ctx, "testuser")
		if err != customErr {
			t.Errorf("Expected custom error, got %v", err)
		}
		mock.GetByUsernameErr = nil
	})
}

func TestMockServiceUpdate(t *testing.T) {
	ctx := context.Background()
	mock := NewMockService()

	u, _ := mock.Create(ctx, &CreateRequest{Email: "test@example.com", Username: "test"})

	t.Run("updates user", func(t *testing.T) {
		updates := map[string]interface{}{
			"name":       "New Name",
			"avatar_url": "https://example.com/avatar.png",
		}
		result, err := mock.Update(ctx, u.ID, updates)
		if err != nil {
			t.Fatalf("Update failed: %v", err)
		}
		if result.Name == nil || *result.Name != "New Name" {
			t.Error("Name not updated")
		}
		if result.AvatarURL == nil || *result.AvatarURL != "https://example.com/avatar.png" {
			t.Error("AvatarURL not updated")
		}
		if len(mock.UpdatedUsers) != 1 {
			t.Errorf("UpdatedUsers count = %d, want 1", len(mock.UpdatedUsers))
		}
	})

	t.Run("non-existent user", func(t *testing.T) {
		_, err := mock.Update(ctx, 999, map[string]interface{}{})
		if err != ErrUserNotFound {
			t.Errorf("Expected ErrUserNotFound, got %v", err)
		}
	})

	t.Run("configurable error", func(t *testing.T) {
		customErr := errors.New("update error")
		mock.UpdateErr = customErr
		_, err := mock.Update(ctx, u.ID, map[string]interface{}{})
		if err != customErr {
			t.Errorf("Expected custom error, got %v", err)
		}
		mock.UpdateErr = nil
	})
}

func TestMockServiceUpdatePassword(t *testing.T) {
	ctx := context.Background()
	mock := NewMockService()

	u, _ := mock.Create(ctx, &CreateRequest{Email: "test@example.com", Username: "test"})

	t.Run("updates password", func(t *testing.T) {
		err := mock.UpdatePassword(ctx, u.ID, "newpassword")
		if err != nil {
			t.Fatalf("UpdatePassword failed: %v", err)
		}
	})

	t.Run("configurable error", func(t *testing.T) {
		customErr := errors.New("password error")
		mock.UpdatePasswordErr = customErr
		err := mock.UpdatePassword(ctx, u.ID, "newpassword")
		if err != customErr {
			t.Errorf("Expected custom error, got %v", err)
		}
		mock.UpdatePasswordErr = nil
	})
}

func TestMockServiceDelete(t *testing.T) {
	ctx := context.Background()
	mock := NewMockService()

	u, _ := mock.Create(ctx, &CreateRequest{Email: "test@example.com", Username: "test"})

	t.Run("deletes user", func(t *testing.T) {
		err := mock.Delete(ctx, u.ID)
		if err != nil {
			t.Fatalf("Delete failed: %v", err)
		}

		_, err = mock.GetByID(ctx, u.ID)
		if err != ErrUserNotFound {
			t.Error("User should be deleted")
		}

		if len(mock.DeletedUserIDs) != 1 {
			t.Errorf("DeletedUserIDs count = %d, want 1", len(mock.DeletedUserIDs))
		}
	})

	t.Run("configurable error", func(t *testing.T) {
		customErr := errors.New("delete error")
		mock.DeleteErr = customErr
		err := mock.Delete(ctx, 1)
		if err != customErr {
			t.Errorf("Expected custom error, got %v", err)
		}
		mock.DeleteErr = nil
	})
}
