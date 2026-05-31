package user

import (
	"context"
	"errors"
	"testing"
	"time"
)

func TestMockServiceAuthenticate(t *testing.T) {
	ctx := context.Background()
	mock := NewMockService()

	mock.Create(ctx, &CreateRequest{Email: "test@example.com", Username: "test"})

	t.Run("authenticates user", func(t *testing.T) {
		u, err := mock.Authenticate(ctx, "test@example.com", "password")
		if err != nil {
			t.Fatalf("Authenticate failed: %v", err)
		}
		if u.Email != "test@example.com" {
			t.Errorf("Email = %s, want test@example.com", u.Email)
		}
		if len(mock.AuthAttempts) != 1 {
			t.Errorf("AuthAttempts count = %d, want 1", len(mock.AuthAttempts))
		}
	})

	t.Run("configurable error", func(t *testing.T) {
		customErr := errors.New("auth error")
		mock.AuthenticateErr = customErr
		_, err := mock.Authenticate(ctx, "test@example.com", "password")
		if err != customErr {
			t.Errorf("Expected custom error, got %v", err)
		}
		mock.AuthenticateErr = nil
	})
}

func TestMockServiceGetOrCreateByOAuth(t *testing.T) {
	ctx := context.Background()
	mock := NewMockService()

	t.Run("creates new user", func(t *testing.T) {
		u, isNew, err := mock.GetOrCreateByOAuth(ctx, "github", "12345", "ghuser", "oauth@example.com", "OAuth User", "https://avatar.com")
		if err != nil {
			t.Fatalf("GetOrCreateByOAuth failed: %v", err)
		}
		if !isNew {
			t.Error("Should be new user")
		}
		if u.Email != "oauth@example.com" {
			t.Errorf("Email = %s, want oauth@example.com", u.Email)
		}
	})

	t.Run("returns existing user", func(t *testing.T) {
		u, isNew, err := mock.GetOrCreateByOAuth(ctx, "github", "12345", "ghuser", "oauth@example.com", "OAuth User", "")
		if err != nil {
			t.Fatalf("GetOrCreateByOAuth failed: %v", err)
		}
		if isNew {
			t.Error("Should not be new user")
		}
		if u.Email != "oauth@example.com" {
			t.Errorf("Email = %s, want oauth@example.com", u.Email)
		}
	})

	t.Run("configurable error", func(t *testing.T) {
		customErr := errors.New("oauth error")
		mock.GetOrCreateByOAuthErr = customErr
		_, _, err := mock.GetOrCreateByOAuth(ctx, "github", "999", "user", "new@example.com", "", "")
		if err != customErr {
			t.Errorf("Expected custom error, got %v", err)
		}
		mock.GetOrCreateByOAuthErr = nil
	})
}

func TestMockServiceRecordLogin(t *testing.T) {
	ctx := context.Background()
	mock := NewMockService()

	u, _ := mock.Create(ctx, &CreateRequest{Email: "test@example.com", Username: "test"})

	t.Run("records login call", func(t *testing.T) {
		mock.RecordLogin(ctx, u.ID)
		if len(mock.RecordLoginCalls) != 1 {
			t.Errorf("RecordLoginCalls count = %d, want 1", len(mock.RecordLoginCalls))
		}
		if mock.RecordLoginCalls[0] != u.ID {
			t.Errorf("RecordLoginCalls[0] = %d, want %d", mock.RecordLoginCalls[0], u.ID)
		}
	})

	t.Run("records multiple calls", func(t *testing.T) {
		mock.RecordLogin(ctx, u.ID)
		if len(mock.RecordLoginCalls) != 2 {
			t.Errorf("RecordLoginCalls count = %d, want 2", len(mock.RecordLoginCalls))
		}
	})
}

func TestMockServiceUpdateIdentityTokens(t *testing.T) {
	ctx := context.Background()
	mock := NewMockService()

	u, _ := mock.Create(ctx, &CreateRequest{Email: "test@example.com", Username: "test"})
	expiresAt := time.Now().Add(time.Hour)

	t.Run("updates tokens", func(t *testing.T) {
		err := mock.UpdateIdentityTokens(ctx, u.ID, "github", "access", "refresh", &expiresAt)
		if err != nil {
			t.Fatalf("UpdateIdentityTokens failed: %v", err)
		}
	})

	t.Run("configurable error", func(t *testing.T) {
		customErr := errors.New("identity error")
		mock.UpdateIdentityErr = customErr
		err := mock.UpdateIdentityTokens(ctx, u.ID, "github", "access", "refresh", nil)
		if err != customErr {
			t.Errorf("Expected custom error, got %v", err)
		}
		mock.UpdateIdentityErr = nil
	})
}
